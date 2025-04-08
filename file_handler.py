from datetime import datetime
import shutil
import hashlib
import os
from database import FileDatabase


class FileHandler:
    def copy_file(self, src_path, target_folder):
        database = FileDatabase()
        existing_versions = database.get_file_versions(src_path)
        next_version = 1
        if existing_versions:
            version_list = [int(v) for v in existing_versions.split(',')]
            next_version = max(version_list) + 1
        file_mod_time = os.path.getmtime(src_path)
        date_str = datetime.fromtimestamp(file_mod_time).strftime("%d.%m.%Y")
        time_str = datetime.fromtimestamp(file_mod_time).strftime("%H.%M")
        version_str = f"v{next_version}"
        filename = os.path.basename(src_path)
        name, ext = os.path.splitext(filename)
        new_name = f"{time_str}_{date_str}_{version_str}_{name}{ext}"

        target_path = os.path.join(target_folder, new_name)

        if not os.path.exists(target_path):
            new_versions = f"{existing_versions},{next_version}" if existing_versions else str(next_version)
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