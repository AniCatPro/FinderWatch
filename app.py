import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import threading
from monitor import Monitor
from exclude import ExcludeManager
from database import FileDatabase

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Мониторинг папок")
        self.root.geometry("1000x700")
        self.source_folders = {}
        self.monitoring_thread = None
        self.monitor = None
        self.exclude_managers = {}
        self.database = FileDatabase()
        self.create_widgets()
        self.load_tasks()

    def load_tasks(self):
        tasks = self.database.get_tasks()
        for source, target in tasks:
            self.source_folders[source] = target
            self.exclude_managers[source] = ExcludeManager()
        self.update_tree()

    def create_widgets(self):
        toolbar_frame = tk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X)

        self.add_task_button = tk.Button(toolbar_frame, text="Новая задача", command=self.add_task)
        self.add_task_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.remove_task_button = tk.Button(toolbar_frame, text="Удалить", command=self.remove_task)
        self.remove_task_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.add_exclude_button = tk.Button(toolbar_frame, text="Добавить исключение", command=self.add_exclude)
        self.add_exclude_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.remove_exclude_button = tk.Button(toolbar_frame, text="Удалить исключение", command=self.remove_exclude)
        self.remove_exclude_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.tree = ttk.Treeview(self.root, columns=("Source", "Target", "Exclusions"), show="headings", height=10)
        self.tree.heading("Source", text="Исходная папка")
        self.tree.heading("Target", text="Целевая папка")
        self.tree.heading("Exclusions", text="Исключения")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_text = tk.Text(self.root, height=10, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, pady=5)

        self.start_button = tk.Button(bottom_frame, text="Старт", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.stop_button = tk.Button(bottom_frame, text="Стоп", command=self.stop_monitoring)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.status_label = tk.Label(bottom_frame, text="Статус: Приостановлен", fg="red")
        self.status_label.pack(side=tk.LEFT, padx=20)

    def add_task(self):
        source_folder = filedialog.askdirectory(title="Выберите исходную папку")
        target_folder = filedialog.askdirectory(title="Выберите целевую папку")
        if source_folder and target_folder:
            self.source_folders[source_folder] = target_folder
            self.exclude_managers[source_folder] = ExcludeManager()
            self.database.add_task(source_folder, target_folder)
            self.update_tree()

    def update_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for source, target in self.source_folders.items():
            exclusions = ', '.join(self.exclude_managers[source].get_excluded_files())
            self.tree.insert("", tk.END, values=(source, target, exclusions))

    def remove_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            source_folder = values[0]
            del self.source_folders[source_folder]
            del self.exclude_managers[source_folder]
            self.update_tree()

    def add_exclude(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            source_folder = values[0]
            exclude_item = filedialog.askopenfilename(title="Выберите файл для исключения")
            if exclude_item:
                self.exclude_managers[source_folder].add(exclude_item)
                self.update_tree()

    def remove_exclude(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            source_folder = values[0]
            excludes = list(self.exclude_managers[source_folder].get_excluded_files())
            if excludes:
                exclude_to_remove = filedialog.askopenfilename(title="Выберите файл для удаления из исключений", initialdir=excludes)
                if exclude_to_remove in excludes:
                    self.exclude_managers[source_folder].excluded_files.discard(exclude_to_remove)
                    self.update_tree()

    def start_monitoring(self):
        if not self.source_folders:
            messagebox.showwarning("Предупреждение", "Пожалуйста, добавьте хотя бы одну задачу!")
            return

        self.monitor = Monitor(log_callback=self.add_log)

        source_list = list(self.source_folders.keys())
        target_list = list(self.source_folders.values())
        threading_exclude_managers = [self.exclude_managers[src] for src in source_list]

        self.monitoring_thread = threading.Thread(target=self.monitor.start, args=(source_list, target_list, threading_exclude_managers), daemon=True)
        self.monitoring_thread.start()

        self.status_label.config(text="Статус: Запущен", fg="green")
        messagebox.showinfo("Информация", "Мониторинг начался")

    def stop_monitoring(self):
        if self.monitor:
            self.monitor.stop()
            self.status_label.config(text="Статус: Приостановлен", fg="red")
            messagebox.showinfo("Информация", "Мониторинг остановлен")

    def add_log(self, message):
        with open("monitor_log.txt", "a") as log_file:
            log_file.write(message + "\n")
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state='disabled')
        self.log_text.yview(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()