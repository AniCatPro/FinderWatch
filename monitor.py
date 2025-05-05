import time
import os
from file_handler import FileHandler


class Monitor:
    def __init__(self, database, log_callback=None):
        self.file_handler = FileHandler()
        self.running = False
        self.database = database
        self.interval = self.database.get_monitoring_period_seconds()
        self.log_callback = log_callback

    def start(self, source_folders, target_folders, exclude_managers):
        self.running = True
        while self.running:
            for source_folder, target_folder, exclude_manager in zip(source_folders, target_folders, exclude_managers):
                if not target_folder.endswith("АРХИВ"):
                    archive_folder = os.path.normpath(os.path.join(target_folder, "АРХИВ"))
                else:
                    archive_folder = os.path.normpath(target_folder)
                if not os.path.exists(archive_folder):
                    os.makedirs(archive_folder, exist_ok=True)
                    if self.log_callback:
                        self.log_callback(f"Создана папка архива: {archive_folder}")
                    exclude_manager.add(archive_folder)

                self.check_changes(source_folder, target_folder, exclude_manager)
            time.sleep(self.interval)

    def stop(self):
        self.running = False

    def check_changes(self, source_folder, target_folder, exclude_manager):
        norm = lambda path: os.path.normpath(path).replace('\\', '/')
        for root, dirs, files in os.walk(source_folder):
            if root != source_folder:
                continue
            for file in files:
                src_file_path = norm(os.path.join(root, file))
                if not exclude_manager.is_excluded(src_file_path):
                    if self.log_callback:
                        self.log_callback(f"Обработка файла: {src_file_path}")
                    if self.file_handler.copy_file(source_folder, src_file_path, target_folder, exclude_manager):
                        if self.log_callback:
                            message = f"Файл {src_file_path} скопирован в {target_folder}"
                            self.log_callback(message)