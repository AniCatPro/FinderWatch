import tkinter as tk
from tkinter import messagebox

class SettingsWindow:
    def __init__(self, master, database):
        self.master = master
        self.database = database
        self.settings_window = tk.Toplevel(master)
        self.settings_window.title("Настройки")

        self.create_widgets()

    def create_widgets(self):
        self.date_format_var = tk.StringVar()
        self.time_format_var = tk.StringVar()
        self.version_var = tk.BooleanVar()

        self.date_label = tk.Label(self.settings_window, text="Формат даты:")
        self.date_label.pack(anchor=tk.W)
        self.date_entry = tk.Entry(self.settings_window, textvariable=self.date_format_var)
        self.date_entry.pack(fill=tk.X)

        self.time_label = tk.Label(self.settings_window, text="Формат времени:")
        self.time_label.pack(anchor=tk.W)
        self.time_entry = tk.Entry(self.settings_window, textvariable=self.time_format_var)
        self.time_entry.pack(fill=tk.X)

        self.version_check = tk.Checkbutton(self.settings_window, text="Добавить версию (хеш)", variable=self.version_var)
        self.version_check.pack(anchor=tk.W)

        self.save_button = tk.Button(self.settings_window, text="Сохранить", command=self.save_settings)
        self.save_button.pack()

        self.load_settings()

    def load_settings(self):
        self.date_format_var.set(self.database.get_setting("date_format") or "дд.мм.гггг")
        self.time_format_var.set(self.database.get_setting("time_format") or "чч.мм")
        stored_version = self.database.get_setting("version")
        if stored_version is not None:
            self.version_var.set(stored_version == 'True')

    def save_settings(self):
        self.database.set_setting("date_format", self.date_format_var.get())
        self.database.set_setting("time_format", self.time_format_var.get())
        self.database.set_setting("version", str(self.version_var.get()))
        messagebox.showinfo("Информация", "Настройки сохранены")
        self.settings_window.destroy()