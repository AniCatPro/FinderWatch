import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from monitor import Monitor
from exclude import ExcludeManager  # Импортируем ExcludeManager

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Мониторинг папок")
        self.root.geometry("600x400")

        # Переменные
        self.source_folder = ""
        self.target_folder = ""

        # Инициализация мониторинга и менеджера исключений
        self.monitor = None
        self.exclude_manager = ExcludeManager()  # Инициализируем ExcludeManager

        # GUI элементы
        self.create_widgets()

    def create_widgets(self):
        # Исходная папка
        self.source_label = tk.Label(self.root, text="Исходная папка:")
        self.source_label.pack(pady=5)

        self.source_button = tk.Button(self.root, text="Выбрать", command=self.select_source_folder)
        self.source_button.pack(pady=5)

        # Целевая папка
        self.target_label = tk.Label(self.root, text="Целевая папка:")
        self.target_label.pack(pady=5)

        self.target_button = tk.Button(self.root, text="Выбрать", command=self.select_target_folder)
        self.target_button.pack(pady=5)

        # Исключения
        self.exclude_label = tk.Label(self.root, text="Исключения:")
        self.exclude_label.pack(pady=5)

        self.exclude_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        self.exclude_listbox.pack(pady=5)

        self.add_exclude_button = tk.Button(self.root, text="Добавить исключение", command=self.add_exclude)
        self.add_exclude_button.pack(pady=5)

        # Старт/Стоп мониторинга
        self.start_button = tk.Button(self.root, text="Старт", command=self.start_monitoring)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(self.root, text="Стоп", command=self.stop_monitoring)
        self.stop_button.pack(pady=5)

    def select_source_folder(self):
        folder = filedialog.askdirectory(title="Выберите исходную папку")
        if folder:
            self.source_folder = folder
            messagebox.showinfo("Информация", f"Вы выбрали исходную папку: {folder}")

    def select_target_folder(self):
        folder = filedialog.askdirectory(title="Выберите целевую папку")
        if folder:
            self.target_folder = folder
            messagebox.showinfo("Информация", f"Вы выбрали целевую папку: {folder}")

    def add_exclude(self):
        exclude_item = filedialog.askopenfilename(title="Выберите файл для исключения")
        if exclude_item:
            self.exclude_manager.add(exclude_item)  # Добавляем исключение
            self.exclude_listbox.insert(tk.END, exclude_item)  # Отображаем в Listbox

    def start_monitoring(self):
        if not self.source_folder or not self.target_folder:
            messagebox.showwarning("Предупреждение", "Пожалуйста, укажите исходную и целевую папки!")
            return
        # Создаем и запускаем мониторинг с периодом 30 секунд
        self.monitor = Monitor()
        threading.Thread(target=self.monitor.start, args=(self.source_folder, self.target_folder, self.exclude_manager), daemon=True).start()
        messagebox.showinfo("Информация", "Мониторинг начался")

    def stop_monitoring(self):
        if self.monitor:
            self.monitor.stop()
            messagebox.showinfo("Информация", "Мониторинг остановлен")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
