import time
import os
from file_handler import FileHandler

class Monitor:
    def __init__(self, log_callback=None):
        self.file_handler = FileHandler()
        self.running = False
        self.interval = 30  # Период в секундах для проверки
        self.log_callback = log_callback

    def start(self, source_folders, target_folders, exclude_managers):
        self.running = True
        while self.running:
            for source_folder, target_folder, exclude_manager in zip(source_folders, target_folders, exclude_managers):
                self.check_changes(source_folder, target_folder, exclude_manager)
            time.sleep(self.interval)

    def stop(self):
        self.running = False

    def check_changes(self, source_folder, target_folder, exclude_manager):
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.basename(file_path) in exclude_manager.get_excluded_files():
                    continue
                if self.file_handler.copy_file(source_folder, file_path, target_folder, exclude_manager):
                    message = f"Файл {file_path} скопирован в {target_folder}"
                    if self.log_callback:
                        self.log_callback(message)