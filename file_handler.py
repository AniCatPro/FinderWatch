from datetime import datetime
import shutil
import hashlib
import os
from database import FileDatabase


class FileHandler:
    def copy_file(self, src_path, target_folder):
        file_hash = self.generate_hash(src_path)

        # Создаём новое соединение с БД
        database = FileDatabase()
        existing_hash = database.get_file_hash(src_path)

        # Получение текущих настроек
        date_format = database.get_setting("date_format") or "%d.%m.%Y"
        time_format = database.get_setting("time_format") or "%H.%M"
        add_version = database.get_setting("version") == 'True'

        # Формирование дополнительных частей имени
        date_str = datetime.now().strftime(date_format)
        time_str = datetime.now().strftime(time_format)
        version_str = f"_{file_hash}" if add_version else ""

        # Формирование нового имени файла
        filename = os.path.basename(src_path)
        name, ext = os.path.splitext(filename)
        new_name = f"{date_str}_{time_str}{version_str}_{name}{ext}"

        target_path = os.path.join(target_folder, new_name)

        if (existing_hash != file_hash) or (not os.path.exists(target_path)):
            database.update_file_hash(src_path, file_hash)
            shutil.copy2(src_path, target_path)
            return True

        return False

    def generate_hash(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()