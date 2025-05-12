"""
ПОЯСНЕНИЯ:
Проходит по всем файлам и папкам в root_dir и переводит их имена в NFC-форму Unicode.
Переименует ФАЙЛЫ и ПАПКИ (директории) только если имя реально изменится.
В случае конфликта (имя уже занято) — пишет в лог.
"""
import os
import unicodedata

def normalize_filenames(root_dir, log_callback=None):
    changes = 0
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        for name in filenames:
            normalized_name = unicodedata.normalize('NFC', name)
            if name != normalized_name:
                src = os.path.join(dirpath, name)
                dst = os.path.join(dirpath, normalized_name)
                if not os.path.exists(dst):
                    os.rename(src, dst)
                    msg = f'[Unicode Fix] "{src}" → "{dst}"'
                    print(msg)
                    if log_callback:
                        log_callback(msg)
                    changes += 1
                else:
                    msg = f"[Unicode Fix] Конфликт: {dst} уже существует, файл {src} не переименован!"
                    print(msg)
                    if log_callback:
                        log_callback(msg)
        for name in dirnames:
            normalized_name = unicodedata.normalize('NFC', name)
            if name != normalized_name:
                src = os.path.join(dirpath, name)
                dst = os.path.join(dirpath, normalized_name)
                if not os.path.exists(dst):
                    os.rename(src, dst)
                    msg = f'[Unicode Fix] Директория: "{src}" → "{dst}"'
                    print(msg)
                    if log_callback:
                        log_callback(msg)
                    changes += 1
                else:
                    msg = f"[Unicode Fix] Конфликт: директория {dst} уже существует! {src} не переименована."
                    print(msg)
                    if log_callback:
                        log_callback(msg)
    if changes == 0:
        msg = f"[Unicode Fix] В папке '{root_dir}' не найдено ни одного файла/папки для нормализации."
        print(msg)
        if log_callback:
            log_callback(msg)
    else:
        msg = f"[Unicode Fix] Всего нормализовано (файлов + папок): {changes}"
        print(msg)
        if log_callback:
            log_callback(msg)