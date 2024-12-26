import multiprocessing
import random
import string
import os
from time import sleep

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


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")  # Windows için gerekli
    num_processes = os.cpu_count()
    print(f"Using {num_processes} processes...")

    processes = []
    for proccess_id in range(os.cpu_count()):
        processes.append(multiprocessing.Process(target=brute_force, args=(proccess_id,)))
        processes[proccess_id].start()
