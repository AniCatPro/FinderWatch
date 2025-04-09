import tkinter as tk
from tkinter import messagebox
import os

class ExcludeWindow:
    def __init__(self, master, source_folder, database, app):
        self.master = master
        self.source_folder = source_folder
        self.database = database
        self.app = app
        self.window = tk.Toplevel(master)
        self.window.title("Управление исключениями")
        self.file_vars = {}
        self.create_widgets()
    def create_widgets(self):
        frame = tk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True)
        files = os.listdir(self.source_folder)
        existing_exclusions = self.database.get_exclusions(self.source_folder)
        for file in files:
            file_path = os.path.join(self.source_folder, file)
            var = tk.BooleanVar(value=file in existing_exclusions)
            chk = tk.Checkbutton(frame, text=file, variable=var)
            chk.pack(anchor=tk.W)
            self.file_vars[file] = var
        apply_button = tk.Button(self.window, text="Применить", command=self.apply_exclusions)
        apply_button.pack(side=tk.LEFT, padx=5, pady=5)
        close_button = tk.Button(self.window, text="Закрыть", command=self.window.destroy)
        close_button.pack(side=tk.RIGHT, padx=5, pady=5)
    def apply_exclusions(self):
        exclusions = [file for file, var in self.file_vars.items() if var.get()]
        self.database.set_exclusions(self.source_folder, exclusions)
        if self.source_folder in self.app.exclude_managers:
            self.app.exclude_managers[self.source_folder].excluded_files = set(exclusions)
        self.app.update_tree()
        messagebox.showinfo("Информация", "Исключения обновлены")
        self.window.destroy()

    def remove_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            source_folder = values[0]
            if source_folder in self.source_folders:
                del self.source_folders[source_folder]
                del self.exclude_managers[source_folder]
                self.database.remove_task(source_folder)
                self.update_tree()
            else:
                messagebox.showerror("Ошибка", "Элемент не найден.")