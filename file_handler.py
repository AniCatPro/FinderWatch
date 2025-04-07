import shutil
import hashlib
import os


class FileHandler:
    def copy_file(self, src_path, target_folder):
        filename = os.path.basename(src_path)
        target_path = os.path.join(target_folder, filename)

        if os.path.exists(target_path):
            # Генерация хеша файла для версионности
            file_hash = self.generate_hash(src_path)
            target_path = os.path.join(target_folder, f"{file_hash}_{filename}")

        shutil.copy2(src_path, target_path)

    def generate_hash(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
