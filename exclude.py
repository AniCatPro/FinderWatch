class ExcludeManager:
    def __init__(self):
        self.excluded_files = set()

    def add(self, file_path):
        self.excluded_files.add(file_path)

    def get_excluded_files(self):
        return self.excluded_files
