import hashlib
import json
import multiprocessing
import requests
from time import time

API_URL = "http://127.0.0.1:5000/get_password"  # API'nin çalıştığı URL

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def attempt_password(start_idx, end_idx, target_hash, print_frequency=1000000, result_queue=None):
    count = 0  

    for i in range(start_idx, end_idx):
        password = f"{i:07d}"  # Sayıyı 7 basamaklı olarak formatla
        hashed = hash_password(password)

        count += 1

        # Debugging output to verify hash comparison
        if count % print_frequency == 0:
            print(f"Trying password: {password}, Hashed: {hashed}, Target: {target_hash}")
        
        if hashed == target_hash:
            if result_queue:
                result_queue.put(password)  # Found password, add to queue
            print(f"Found password: {password}")
            return password

    return None

def find_password(target_hash, num_processes=8, print_frequency=1000000):
    total_combinations = 10 ** 7  # 7 basamaklı toplam kombinasyon: 10^7
    manager = multiprocessing.Manager()
    result_queue = manager.Queue()
    pool = multiprocessing.Pool(processes=num_processes)
    chunk_size = total_combinations // num_processes
    results = []

    for i in range(num_processes):
        start_idx = i * chunk_size
        end_idx = total_combinations if i == num_processes - 1 else (i + 1) * chunk_size
        results.append(pool.apply_async(attempt_password, (start_idx, end_idx, target_hash, print_frequency, result_queue)))

    found_password = None
    while True:
        if not result_queue.empty():
            found_password = result_queue.get()
            break

        all_done = all(res.ready() for res in results)
        if all_done:
            break

    for res in results:
        res.wait()  # Ensure all processes finish

    if found_password:
        print(f"Şifre bulunmuştur: {found_password}")

    pool.close()
    pool.join()

def get_password_from_api():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json().get("password")
    else:
        raise Exception("API'den şifre hash'i alınamadı.")

if __name__ == "__main__":
    start_time = time()
    
    target_hash = get_password_from_api()
    print(f"Target hash: {target_hash}")
    
    find_password(target_hash)
    end_time = time()
    print(f"Time taken: {end_time - start_time} seconds")



