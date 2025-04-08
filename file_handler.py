from datetime import datetime
import shutil
import hashlib
import os
from database import FileDatabase


class FileHandler:
    def copy_file(self, src_path, target_folder):
        # Получение текущей версии из БД
        database = FileDatabase()
        existing_versions = database.get_file_versions(src_path)

        # Генерация следующей версии
        next_version = 1
        if existing_versions:
            version_list = [int(v) for v in existing_versions.split(',')]
            next_version = max(version_list) + 1

        # Формирование нового имени файла
        filename = os.path.basename(src_path)
        name, ext = os.path.splitext(filename)
        new_name = f"v{next_version}_{name}{ext}"

        target_path = os.path.join(target_folder, new_name)

        # Копируем файл, если он не существует или необходимо обновление
        if not os.path.exists(target_path):
            # Обновление версий в БД
            new_versions = existing_versions + f",{next_version}" if existing_versions else str(next_version)
            database.update_file_versions(src_path, new_versions)

            shutil.copy2(src_path, target_path)
            return True

        return False

    def generate_hash(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()