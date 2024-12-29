import multiprocessing
import hashlib
import string
import os
import json
import requests
import time

# Paylaşılan değişkenler
#shared_chars = string.digits
shared_chars = string.ascii_letters + string.digits

lock = multiprocessing.Lock()

def generate_password() -> str:
    def recursive_generate(current, remaining_length):
        #charset = string.ascii_letters + string.digits
        charset = string.digits
        if remaining_length == 0:
            yield current
        else:
            for char in charset:
                yield from recursive_generate(current + char, remaining_length - 1)

    #for length in range(8, 16 + 1):
    yield from recursive_generate("", 6)

def brute_force(process_id: int, target_hash: str, last_index, passwd_found):
    """Şifre kombinasyonlarını deneyerek doğru olanı bulmaya çalışır."""
    global shared_chars
    while True:
        # Şifre bulunduysa işlemi sonlandır
        if passwd_found.value:
            return

        # Paylaşılan index değerini güvenli şekilde al
        with lock:
            if last_index.value >= len(shared_chars):
                break  # Tüm karakterler işlendi, çık
            first_char = shared_chars[last_index.value]
            last_index.value += 1  # İndeksi artır
            #print(f"Proccess id: {process_id} " + first_char + f" {last_index.value}")

        #time.sleep(5)
        # Kombinasyonları üret ve kontrol et
        for combination in generate_password():
            if passwd_found.value:
                return
            passwd = first_char + combination
            password_hash = hashlib.md5(passwd.encode()).hexdigest()

            #print(f"[Process {process_id}] Trying password: {passwd} ")

            if password_hash == target_hash:
                check_response = requests.post(
                    "http://127.0.0.1:5000/check_password",
                    json={"password": passwd}
                )
                if check_response.status_code == 200:
                    with lock:  # Şifre bulunduğunu işaretle
                        result = check_response.json()
                        print(f"Password check result: {result['message']} " + f"[Process {process_id}] Password is: {passwd} ")
                        passwd_found.value = True
                        return  # İşlemi sonlandır


if __name__ == "__main__":
    password_found = multiprocessing.Value('b', False)  # Şifre bulunduğunda True olacak
    shared_index = multiprocessing.Value('i', 0)

    response = requests.get("http://127.0.0.1:5000/get_password")
    if response.status_code == 200:
        with open("password.json", "r") as f:
            stored_data = json.load(f)
            target_hash = stored_data["password"]
            print("Target Hash: " + target_hash)

    print(f"Target Hash: {target_hash}")

    # Çoklu işlemleri başlat
    num_processes = os.cpu_count()
    print(f"Using {num_processes} processes...")

    processes = []
    for process_id in range(num_processes):
        p = multiprocessing.Process(target=brute_force, args=(process_id, target_hash, shared_index, password_found))
        processes.append(p)
        p.start()
        #time.sleep(0.2)

    # Tüm işlemlerin tamamlanmasını bekle
    for process in processes:
        process.join()
    print("All processes completed.")
