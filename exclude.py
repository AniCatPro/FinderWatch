import os


class ExcludeManager:
    def __init__(self, source_folder):
        self.excluded_paths = set()
        self.source_folder = source_folder

    def add(self, file_path):
        full_path = os.path.normpath(os.path.join(self.source_folder, file_path)).replace('\\', '/')
        print('Добавляем в исключения:', full_path)
        if os.path.isfile(full_path):
            self.excluded_paths.add(full_path)
        elif os.path.isdir(full_path):
            for root, _, files in os.walk(full_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_path = os.path.normpath(file_path).replace('\\', '/')
                    self.excluded_paths.add(file_path)
            self.excluded_paths.add(full_path)

    def is_excluded(self, file_path):
        path = os.path.normpath(file_path).replace('\\', '/')
        print('Проверяем файл:', path)
        for exc in self.excluded_paths:
            exc_path = os.path.normpath(exc).replace('\\', '/')
            if os.path.isfile(exc_path):
                if path == exc_path:
                    return True
            elif os.path.isdir(exc_path):
                if path.startswith(exc_path + '/'):
                    return True
        return False