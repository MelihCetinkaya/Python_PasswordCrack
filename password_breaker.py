import multiprocessing
import requests
import hashlib
import string
import os

def generate_password() -> str:
    def recursive_generate(current, remaining_length):
        charset = string.ascii_letters + string.digits
        if remaining_length == 0:
            yield current
        else:
            for char in charset:
                yield from recursive_generate(current + char, remaining_length - 1)

    for length in range(8, 16 + 1):
        yield from recursive_generate("", length)


def brute_force(id : int):
    for combination in generate_password():
        print(str(id) + "th Core Working... " + combination)
        response = requests.get("http://127.0.0.1:5000/get_password")

        if response.status_code == 200:
            print(f"Generated password: {combination}")

            # Şifreyi MD5 hash'ine çevir
            password_hash = hashlib.md5(combination.encode()).hexdigest()

            # Flask uygulamasına /check_password isteğini göndererek doğru olup olmadığını kontrol et
            check_response = requests.post(
                "http://127.0.0.1:5000/check_password",
                json={"password": combination}
            )

            if check_response.status_code == 200:
                result = check_response.json()
                print(f"Password check result: {result['message']}")
            else:
                print("Error occurred while checking password.")
        else:
            print("Failed to retrieve password.")


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")  # Windows için gerekli
    num_processes = os.cpu_count()
    print(f"Using {num_processes} processes...")

    processes = []
    for proccess_id in range(os.cpu_count()):
        processes.append(multiprocessing.Process(target=brute_force, args=(proccess_id,)))
        processes[proccess_id].start()
