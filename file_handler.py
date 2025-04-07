import shutil
import hashlib
import os
from database import FileDatabase


class FileHandler:
    def copy_file(self, src_path, target_folder):
        file_hash = self.generate_hash(src_path)

        # Создать новое соединение для каждого вызова
        database = FileDatabase()
        existing_hash = database.get_file_hash(src_path)

        if existing_hash != file_hash:
            database.update_file_hash(src_path, file_hash)
            filename = os.path.basename(src_path)
            target_path = os.path.join(target_folder, filename)

            if os.path.exists(target_path):
                target_path = os.path.join(target_folder, f"{file_hash}_{filename}")

            shutil.copy2(src_path, target_path)
            return True
        return False

    def generate_hash(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()