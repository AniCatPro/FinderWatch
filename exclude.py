import os

class ExcludeManager:
    def __init__(self):
        self.excluded_files = set()

    def add(self, file_path):
        filename = os.path.basename(file_path)
        self.excluded_files.add(filename)

    def get_excluded_files(self):
        return self.excluded_files
