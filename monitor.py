import time
import os
from file_handler import FileHandler
from exclude import ExcludeManager

class Monitor:
    def __init__(self):
        self.file_handler = FileHandler()
        self.exclude_manager = ExcludeManager()
        self.running = False
        self.interval = 30  # Период в секундах для проверки

    def start(self, source_folder, target_folder, exclude_manager):
        self.exclude_manager = exclude_manager
        self.running = True

        # Начинаем периодический мониторинг
        while self.running:
            self.check_changes(source_folder, target_folder)
            time.sleep(self.interval)  # Задержка между проверками (30 секунд)

    def stop(self):
        self.running = False

    def check_changes(self, source_folder, target_folder):
        # Проходим по всем файлам в исходной папке и копируем те, которые были изменены
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in self.exclude_manager.get_excluded_files():
                    self.file_handler.copy_file(file_path, target_folder)
                    print(f"Файл {file_path} скопирован в {target_folder}")
