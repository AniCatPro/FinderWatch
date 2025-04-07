import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import threading
from monitor import Monitor
from exclude import ExcludeManager

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Мониторинг папок")
        self.root.geometry("800x600")

        self.source_folders = {}
        self.target_folders = {}
        self.monitoring_thread = None

        self.monitor = None
        self.exclude_manager = ExcludeManager()

        self.create_widgets()

    def create_widgets(self):
        toolbar_frame = tk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X)

        self.add_task_button = tk.Button(toolbar_frame, text="Новая задача", command=self.add_task)
        self.add_task_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.remove_task_button = tk.Button(toolbar_frame, text="Удалить", command=self.remove_task)
        self.remove_task_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.start_button = tk.Button(toolbar_frame, text="Старт", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.stop_button = tk.Button(toolbar_frame, text="Стоп", command=self.stop_monitoring)
        self.stop_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.tree = ttk.Treeview(self.root, columns=("Source", "Target"), show="headings")
        self.tree.heading("Source", text="Исходная папка")
        self.tree.heading("Target", text="Целевая папка")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.exclude_frame = tk.LabelFrame(self.root, text="Исключения")
        self.exclude_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.exclude_listbox = tk.Listbox(self.exclude_frame, selectmode=tk.MULTIPLE)
        self.exclude_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        self.add_exclude_button = tk.Button(self.exclude_frame, text="Добавить исключение", command=self.add_exclude)
        self.add_exclude_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.remove_exclude_button = tk.Button(self.exclude_frame, text="Удалить исключение", command=self.remove_exclude)
        self.remove_exclude_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.status_label = tk.Label(self.root, text="Статус: Приостановлен", fg="red")
        self.status_label.pack(pady=5)

    def add_task(self):
        source_folder = filedialog.askdirectory(title="Выберите исходную папку")
        target_folder = filedialog.askdirectory(title="Выберите целевую папку")
        if source_folder and target_folder:
            self.source_folders[source_folder] = target_folder
            self.tree.insert("", tk.END, values=(source_folder, target_folder))

    def remove_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            source_folder = values[0]
            del self.source_folders[source_folder]
            self.tree.delete(selected_item)

    def add_exclude(self):
        exclude_item = filedialog.askopenfilename(title="Выберите файл для исключения")
        if exclude_item:
            self.exclude_manager.add(exclude_item)
            self.exclude_listbox.insert(tk.END, exclude_item)

    def remove_exclude(self):
        selected_items = self.exclude_listbox.curselection()
        for index in reversed(selected_items):
            exclude_item = self.exclude_listbox.get(index)
            self.exclude_manager.excluded_files.discard(exclude_item)
            self.exclude_listbox.delete(index)

    def start_monitoring(self):
        if not self.source_folders:
            messagebox.showwarning("Предупреждение", "Пожалуйста, добавьте хотя бы одну задачу!")
            return

        self.monitor = Monitor()

        source_list = list(self.source_folders.keys())
        target_list = list(self.source_folders.values())

        self.monitoring_thread = threading.Thread(target=self.monitor.start, args=(source_list, target_list, self.exclude_manager), daemon=True)
        self.monitoring_thread.start()

        self.status_label.config(text="Статус: Запущен", fg="green")
        messagebox.showinfo("Информация", "Мониторинг начался")

    def stop_monitoring(self):
        if self.monitor:
            self.monitor.stop()
            self.status_label.config(text="Статус: Приостановлен", fg="red")
            messagebox.showinfo("Информация", "Мониторинг остановлен")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()