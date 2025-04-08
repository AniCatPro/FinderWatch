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
        self.add_date_var = tk.BooleanVar(value=True)
        self.add_time_var = tk.BooleanVar(value=True)

        self.date_check = tk.Checkbutton(
            self.settings_window, text="Добавить дату", variable=self.add_date_var
        )
        self.date_check.pack(anchor=tk.W)

        self.time_check = tk.Checkbutton(
            self.settings_window, text="Добавить время", variable=self.add_time_var
        )
        self.time_check.pack(anchor=tk.W)

        self.save_button = tk.Button(self.settings_window, text="Сохранить", command=self.save_settings)
        self.save_button.pack()

        self.load_settings()

    def load_settings(self):
        self.add_date_var.set(self.database.get_setting("add_date") == "True")
        self.add_time_var.set(self.database.get_setting("add_time") == "True")

    def save_settings(self):
        self.database.set_setting("add_date", str(self.add_date_var.get()))
        self.database.set_setting("add_time", str(self.add_time_var.get()))
        messagebox.showinfo("Информация", "Настройки сохранены")
        self.settings_window.destroy()