import hashlib
import random
import string
import json
import multiprocessing
from itertools import product
from time import time

PASSWORD_FILE = "password.json"

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def attempt_password(start_idx, end_idx, charset, length, target_hash, print_frequency=1000000):
    count = 0  
    
    for i in range(start_idx, end_idx):
       
        password = ''.join([charset[(i // (len(charset) ** j)) % len(charset)] for j in range(length-1, -1, -1)])
        hashed = hash_password(password)

        count += 1
        
        if hashed == target_hash:
            return password
        
        if count % print_frequency == 0:
            print(f"Deneme {count}: {password}")

    return None

def find_password(length, num_processes=8, print_frequency=1000000):
    
    with open(PASSWORD_FILE, "r") as f:
        stored_data = json.load(f)
        target_hash = stored_data["password"]

    charset = string.ascii_letters + string.digits
   
    total_combinations = len(charset) ** length

    pool = multiprocessing.Pool(processes=num_processes)
    chunk_size = total_combinations // num_processes
    results = []

    for i in range(num_processes):
        start_idx = i * chunk_size
    
        end_idx = total_combinations if i == num_processes - 1 else (i + 1) * chunk_size
        results.append(pool.apply_async(attempt_password, (start_idx, end_idx, charset, length, target_hash, print_frequency)))

    for res in results:
        password = res.get()
        if password:
            print(f"Password found: {password}")
            break
    pool.close()
    pool.join()

if __name__ == "_main_":
    length = 8
    start_time = time()
    find_password(length)
    end_time = time()
    print(f"Time taken: {end_time - start_time} seconds")

#password.json dosyası
{"password": "md5hash"}