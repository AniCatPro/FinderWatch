import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import getpass
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image, ImageTk

from monitor import Monitor
from exclude import ExcludeManager
from database import FileDatabase
from settings import SettingsWindow
from exclude_manager import ExcludeWindow
import shutil

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Мониторинг папок (by anicatpro)")
        self.root.geometry("1000x700")

        self.source_folders = {}
        self.monitoring_thread = None
        self.exclude_managers = {}
        self.database = FileDatabase()
        self.monitor = Monitor(self.database, log_callback=self.add_log)

        load_dotenv()
        self.version = os.getenv("APP_VERSION")

        self.create_widgets()
        self.load_tasks()
        self.initialize_automod()

    def load_tasks(self):
        tasks = self.database.get_tasks()
        for source, target, exclusion_str in tasks:
            self.source_folders[source] = target
            exclude_manager = ExcludeManager(source)
            if exclusion_str:
                exclusions = exclusion_str.split(',')
                for exclusion in exclusions:
                    exclude_manager.add(exclusion)
            self.exclude_managers[source] = exclude_manager
        self.update_tree()

    def create_widgets(self):
        toolbar_frame = tk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X)

        self.add_task_button = tk.Button(toolbar_frame, text="Новая задача", command=self.add_task)
        self.add_task_button.pack(side=tk.LEFT, padx=2, pady=2)
        self.edit_task_button = tk.Button(toolbar_frame, text="Изменить", command=self.edit_task)
        self.edit_task_button.pack(side=tk.LEFT, padx=2, pady=2)
        self.remove_task_button = tk.Button(toolbar_frame, text="Удалить", command=self.remove_task)
        self.remove_task_button.pack(side=tk.LEFT, padx=2, pady=2)
        self.exclude_button = tk.Button(toolbar_frame, text="Исключения", command=self.open_exclude_window)
        self.exclude_button.pack(side=tk.LEFT, padx=2, pady=2)
        self.settings_button = tk.Button(toolbar_frame, text="Настройки", command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT, padx=2, pady=2)
        self.move_archive_button = tk.Button(toolbar_frame, text="Перенести архив", command=self.move_archive)
        self.move_archive_button.pack(side=tk.LEFT, padx=2, pady=2)

        # Версия (можно добавить иконку)
        version_label = tk.Label(toolbar_frame, text=f"Версия: {self.version}", fg="grey")
        version_label.pack(side=tk.RIGHT, padx=10, pady=2)

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
        self.automod_button = tk.Button(bottom_frame, text="Автомод", command=self.toggle_automod)
        self.automod_button.pack(side=tk.RIGHT, padx=10, pady=5)
        self.status_label = tk.Label(bottom_frame, text="Статус: Приостановлен", fg="red")
        self.status_label.pack(side=tk.LEFT, padx=20)
        self.counter_label = tk.Label(
            bottom_frame,
            text=f"Следующее обновление через: {self.format_time_dynamic(self.monitor.interval)}"
        )
        self.counter_label.pack(side=tk.RIGHT, padx=20)

    def add_task(self):
        source_folder = filedialog.askdirectory(title="Выберите исходную папку")
        if source_folder:
            target_folder = os.path.normpath(os.path.join(source_folder, "АРХИВ")).replace("\\", "/")
            self.source_folders[source_folder] = target_folder
            exclude_manager = ExcludeManager(source_folder)
            exclude_manager.add("АРХИВ")
            self.exclude_managers[source_folder] = exclude_manager
            self.database.add_task(source_folder, target_folder)
            self.database.set_exclusions(source_folder, [target_folder])
            self.update_tree()
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                messagebox.showinfo("Перезапуск службы",
                                    "Вы добавили новую задачу. Пожалуйста, перезапустите мониторинг.")

    def edit_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            source_folder = values[0]
            new_source_folder = filedialog.askdirectory(title="Выберите новую исходную папку", initialdir=source_folder)
            if new_source_folder:
                new_target_folder = self.database.get_target_folder(new_source_folder)  # Получаем путь к АРХИВУ внутри new_source_folder
                del self.source_folders[source_folder]
                del self.exclude_managers[source_folder]
                self.database.add_task(new_source_folder, new_target_folder)
                self.update_tree()

    def update_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        tasks = self.database.get_tasks()
        for source, target, exclusions in tasks:
            exclusion_list = exclusions.split(',') if exclusions else []
            exclusion_names = ', '.join(exclusion_list)
            self.tree.insert("", tk.END, values=(source, target, exclusion_names))

    def remove_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            source_folder = values[0]
            if source_folder in self.source_folders:
                print(f"Удаление задачи: {source_folder}")
                del self.source_folders[source_folder]
                del self.exclude_managers[source_folder]
                self.database.remove_task(source_folder)
                self.update_tree()
            else:
                messagebox.showerror("Ошибка", "Элемент не найден.")

    def remove_exclude(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            source_folder = values[0]
            exclude_path = filedialog.askdirectory(title="Выберите исключение для удаления")
            if exclude_path:
                self.exclude_managers[source_folder].remove(exclude_path)
                self.database.remove_exclude(source_folder, exclude_path)
                self.update_tree()

    def move_archive(self):
        from exclude import ExcludeManager
        import shutil, os

        new_parent_dir = filedialog.askdirectory(title="Выберите новую директорию для архива")
        if not new_parent_dir:
            return

        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите задачу для переноса архива.")
            return

        values = self.tree.item(selected_item, "values")
        source_folder = values[0]
        current_archive = self.database.get_target_folder(source_folder)
        new_archive = os.path.normpath(os.path.join(new_parent_dir, "АРХИВ")).replace("\\", "/")
        print(f"Текущее положение архива: {current_archive}")
        print(f"Новое положение архива: {new_archive}")

        if not os.path.exists(current_archive):
            messagebox.showerror(
                "Ошибка",
                f"Исходная папка архива не найдена:\n{current_archive}"
            )
            return
        if os.path.exists(new_archive):
            messagebox.showerror(
                "Ошибка",
                f"Папка АРХИВ уже существует в целевой директории:\n{new_archive}"
            )
            return

        try:
            shutil.move(current_archive, new_archive)
            print("Архив ПЕРЕМЕЩЕН.")
            self.database.add_task(source_folder, new_archive)
            old_exclusions = self.database.get_exclusions(source_folder)
            new_exclusions = []
            for exc in old_exclusions:
                if exc.startswith(current_archive):
                    new_exc = exc.replace(current_archive, new_archive, 1)
                    new_exclusions.append(new_exc)
                else:
                    new_exclusions.append(exc)
            self.database.set_exclusions(source_folder, new_exclusions)
            exclude_manager = ExcludeManager(source_folder)
            for exc in new_exclusions:
                exclude_manager.add(exc)
            self.exclude_managers[source_folder] = exclude_manager
            self.update_tree()
            messagebox.showinfo(
                "Успех",
                f"Архив для '{source_folder}' успешно перемещён в {new_archive}\n"
                f"Все исключения обновлены."
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Ошибка", f"Ошибка при перемещении архива: {e}")

    def start_monitoring(self):
        if not self.source_folders:
            messagebox.showwarning("Предупреждение", "Пожалуйста, добавьте хотя бы одну задачу!")
            return

        # ------------------- unicode_normalizer.py -------------------
        from unicode_normalizer import normalize_filenames
        for folder in self.source_folders.keys():
            normalize_filenames(folder, log_callback=self.add_log)
        # -------------------------------------------------------------

        self.monitor = Monitor(self.database, log_callback=self.add_log)
        source_list = list(self.source_folders.keys())
        target_list = list(self.source_folders.values())
        threading_exclude_managers = [self.exclude_managers[src] for src in source_list]
        self.monitoring_thread = threading.Thread(
            target=self.monitor.start, args=(source_list, target_list, threading_exclude_managers), daemon=True
        )
        self.monitoring_thread.start()
        self.status_label.config(text="Статус: Запущен", fg="green")
        self.update_counter()
        messagebox.showinfo("Информация", "Мониторинг начался")

    def stop_monitoring(self):
        if self.monitor:
            self.monitor.stop()
            self.status_label.config(text="Статус: Приостановлен", fg="red")
            messagebox.showinfo("Информация", "Мониторинг остановлен")

    def add_log(self, message):
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user = getpass.getuser()
            formatted_message = f"[{current_time}] [User: {user}] {message}"
            with open("monitor_log.txt", "a") as log_file:
                log_file.write(formatted_message + "\n")
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, formatted_message + "\n")
            self.log_text.config(state='disabled')
            self.log_text.yview(tk.END)
        except Exception as e:
            print(f"Ошибка при добавлении логов: {e}")

    def initialize_automod(self):
        current_state = self.database.get_automod_state()
        state_text = "Вкл" if current_state else "Выкл"
        self.automod_button.config(text=f"Автомод: {state_text}")
        if current_state:
            self.start_monitoring()

    def toggle_automod(self):
        current_state = self.database.get_automod_state()
        new_state = not current_state
        self.database.set_automod_state(new_state)
        state_text = "Вкл" if new_state else "Выкл"
        self.automod_button.config(text=f"Автомод: {state_text}")
        if new_state:
            self.start_monitoring()

    def update_counter(self):
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            if self.monitor.interval > 0:
                self.monitor.interval -= 1
            else:
                new_interval = self.database.get_monitoring_period_seconds()
                self.monitor.interval = int(new_interval)
            self.counter_label.config(
                text=f"Следующее обновление через: {self.format_time_dynamic(self.monitor.interval)}"
            )
            self.root.after(1000, self.update_counter)

    def format_time_dynamic(self, seconds):
        if seconds >= 3600:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            if minutes == 0:
                return f"{hours} ч"
            else:
                return f"{hours}:{minutes:02d}"
        elif seconds >= 60:
            minutes = seconds // 60
            sec = seconds % 60
            if minutes <= 2:  # последние 2 минуты детализируем до минут:секунд
                return f"{minutes}:{sec:02d}"
            else:
                return f"{minutes} м"
        else:
            return f"{seconds} с"

    def open_settings(self):
        SettingsWindow(self.root, self.database, self.monitor, on_save_callback=self.on_settings_saved)

    def on_settings_saved(self):
        self.monitor.interval = self.database.get_monitoring_period_seconds()
        self.counter_label.config(
            text=f"Следующее обновление через: {self.format_time_dynamic(self.monitor.interval)}"
        )

    def open_exclude_window(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            source_folder = values[0]
            ExcludeWindow(self.root, source_folder, self.database, self)

    def open_url(self, url):
        import webbrowser
        webbrowser.open_new(url)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()