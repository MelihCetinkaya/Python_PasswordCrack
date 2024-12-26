import multiprocessing
import string

# Karakter seti
charset = string.ascii_letters + string.digits


# Kombinasyonları üreten fonksiyon
def generate_combinations_worker(task_queue, charset, max_length, current_combination):
    """
    Bu işçi fonksiyon, belirli bir noktadan başlayarak şifre kombinasyonlarını üretir.
    Args:
        task_queue: Kombinasyon başlangıç görevlerini alır.
        charset: Kullanılacak karakter kümesi.
        max_length: Kombinasyonların maksimum uzunluğu.
        current_combination: Şu anda hangi kombinasyon üzerinde çalışıldığını tutan paylaşılan değişken.
    """
    while True:
        # Şu anki kombinasyonu güncelle
        combination = current_combination.value
        if len(combination) == max_length:
            # Şifre uzunluğuna ulaşmışsa işlemi bitir
            break

        # Kombinasyonları üret
        for char in charset:
            current_combination.value = combination + char
            print(f"Process {multiprocessing.current_process().name} generated: {current_combination.value}")


def main():
    # Her işlem için başlangıçta boş bir kombinasyon
    manager = multiprocessing.Manager()
    current_combination = manager.Value('s', "")  # 's' string türünde, başlangıçta boş bir string

    num_processes = multiprocessing.cpu_count()  # Kullanılacak işlemci sayısı

    processes = []

    # İşlemleri başlat
    for _ in range(num_processes):
        p = multiprocessing.Process(
            target=generate_combinations_worker,
            args=(None, charset, 8, current_combination)  # Burada charset ve max_length de veriliyor
        )
        processes.append(p)
        p.start()

    # İşlemleri bitir
    for p in processes:
        p.join()


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')  # Windows için gerekli
    main()