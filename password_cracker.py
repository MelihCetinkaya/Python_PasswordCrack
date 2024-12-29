import hashlib
import json
import multiprocessing
import os
import requests
import string
from itertools import product
from time import time

API_URL = "http://127.0.0.1:5000/get_password"  # API'nin çalıştığı URL


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def attempt_password(start_idx, end_idx, charset, length, target_hash, proccess_id, print_frequency=100000):
    count = 0

    for i in range(start_idx, end_idx):
        password = ''.join([charset[(i // (len(charset) ** j)) % len(charset)] for j in range(length - 1, -1, -1)])
        hashed = hash_password(password)

        count += 1

        if hashed == target_hash:
            return password

        if count % print_frequency == 0:
            print(f"{proccess_id}. Proccess -> Tried {count} possibilty: Last tried password: {password}")

    return None


def find_password(min_length : int, max_length : int, target_hash, num_processes=8, print_frequency=100000):
    # charset = string.ascii_letters + string.digits
    charset = string.digits

    for length in range(min_length, max_length):
        total_combinations = len(charset) ** length
        pool = multiprocessing.Pool(processes=num_processes)
        chunk_size = total_combinations // num_processes
        results = []

        for i in range(num_processes):
            start_idx = i * chunk_size
            end_idx = total_combinations if i == num_processes - 1 else (i + 1) * chunk_size
            results.append(
                pool.apply_async(attempt_password, (start_idx, end_idx, charset, length, target_hash, i, print_frequency)))

        password = None
        for res in results:
            password = res.get()
            if password:
                pool.close()
                pool.join()
                return password
    return ""


def get_password_from_api():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json().get("password")
    else:
        raise Exception("API'den şifre hash'i alınamadı.")


if __name__ == "__main__":
    min_length = 7
    max_length = 8 # max length will be max_length - 1
    start_time = time()

    target_hash = get_password_from_api()
    print(f"Target hash: {target_hash}")

    print("Password Found: " + find_password(min_length, max_length, target_hash, num_processes=os.cpu_count()))
    end_time = time()
    print(f"Time taken: {end_time - start_time} seconds")