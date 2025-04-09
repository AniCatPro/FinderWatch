from datetime import datetime
import shutil
import hashlib
import os
from database import FileDatabase

class FileHandler:
    def copy_file(self, src_path, target_folder, exclude_manager):
        if src_path.startswith(target_folder):
            return False
        if os.path.basename(src_path) in exclude_manager.get_excluded_files():
            return False
        database = FileDatabase()
        current_hash = self.generate_hash(src_path)
        filename = os.path.basename(src_path)
        name, ext = os.path.splitext(filename)
        subfolder_path = os.path.join(target_folder, name)
        os.makedirs(subfolder_path, exist_ok=True)
        for file in os.listdir(subfolder_path):
            target_file_path = os.path.join(subfolder_path, file)
            if os.path.isfile(target_file_path):
                target_hash = self.generate_hash(target_file_path)
                if current_hash == target_hash:
                    return False
        existing_versions = database.get_file_versions(src_path)
        next_version = 1
        if existing_versions:
            version_list = [int(v) for v in existing_versions.split(',')]
            next_version = max(version_list) + 1
        add_date = database.get_setting("add_date") == "True"
        add_time = database.get_setting("add_time") == "True"
        file_mod_time = os.path.getmtime(src_path)
        date_str = datetime.fromtimestamp(file_mod_time).strftime("%d.%m.%Y") if add_date else ""
        time_str = datetime.fromtimestamp(file_mod_time).strftime("%H.%M") if add_time else ""
        new_name = f"v{next_version}_{name}{f'_{time_str}' if add_time else ''}{f'_{date_str}' if add_date else ''}{ext}"
        target_path = os.path.join(subfolder_path, new_name)
        database.update_file_hash(src_path, current_hash)
        new_versions = f"{existing_versions},{next_version}" if existing_versions else str(next_version)
        database.update_file_versions(src_path, new_versions)

        shutil.copy2(src_path, target_path)
        return True

    def generate_hash(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()