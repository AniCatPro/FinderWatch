import tkinter as tk
from tkinter import messagebox
import re

class SettingsWindow:
    def __init__(self, master, database, monitor, on_save_callback=None):
        self.master = master
        self.database = database
        self.monitor = monitor
        self.on_save_callback = on_save_callback
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

        self.monitoring_period_label = tk.Label(self.settings_window, text="Периодичность мониторинга (ЧЧ:ММ:СС):")
        self.monitoring_period_label.pack(anchor=tk.W)

        self.monitoring_period_var = tk.StringVar(value="00:00:30")
        self.monitoring_period_entry = tk.Entry(self.settings_window, textvariable=self.monitoring_period_var)
        self.monitoring_period_entry.pack(anchor=tk.W)

        vcmd = (self.settings_window.register(self.validate_time_format), '%d', '%P')
        self.monitoring_period_entry.config(validate="all", validatecommand=vcmd)

        self.save_button = tk.Button(self.settings_window, text="Сохранить", command=self.save_settings)
        self.save_button.pack()

        self.load_settings()

    def load_settings(self):
        self.add_date_var.set(self.database.get_setting("add_date") == "True")
        self.add_time_var.set(self.database.get_setting("add_time") == "True")
        monitoring_period = self.database.get_setting("monitoring_period")
        if monitoring_period:
            self.monitoring_period_var.set(monitoring_period)

    def save_settings(self):
        time_val = self.monitoring_period_var.get()
        # Строгая проверка перед сохранением (иначе вернем "00:00:30")
        import re
        if not re.fullmatch(r"\d{2}:\d{2}:\d{2}", time_val):
            messagebox.showwarning("Ошибка",
                                   "Периодичность мониторинга должна быть в формате ЧЧ:ММ:СС (например 01:00:00)!")
            return
        self.database.set_setting("add_date", str(self.add_date_var.get()))
        self.database.set_setting("add_time", str(self.add_time_var.get()))
        self.database.set_setting("monitoring_period", time_val)
        messagebox.showinfo("Информация", "Настройки сохранены")
        if self.on_save_callback:
            self.on_save_callback()
        self.settings_window.destroy()

    def validate_time_format(self, action, new_value):
        pattern = re.compile(r"^\d{0,2}(:\d{0,2}){0,2}$")
        if action == '0':  # удаление — всегда разрешать
            return True
        # проверяем только что вводится текст
        if pattern.match(new_value):
            return True
        return False