# -*- coding: utf-8 -*-
"""
Created on Mon May  1 23:01:36 2023

@author: Mahadev
"""

import tkinter as tk
import time
import winsound

class ReminderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Reminder")

        self.reminder_label = tk.Label(master, text="Enter Reminder:")
        self.reminder_label.pack()

        self.reminder_entry = tk.Entry(master)
        self.reminder_entry.pack()

        self.duration_label = tk.Label(master, text="Enter Duration (in seconds):")
        self.duration_label.pack()

        self.duration_entry = tk.Entry(master)
        self.duration_entry.pack()

        self.set_reminder_button = tk.Button(master, text="Set Reminder", command=self.set_reminder)
        self.set_reminder_button.pack()

        self.quit_button = tk.Button(master, text="Quit", command=master.quit)
        self.quit_button.pack()

    def set_reminder(self):
        duration = int(self.duration_entry.get())
        time.sleep(duration)
        reminder_text = self.reminder_entry.get()
        winsound.Beep(500, 1000)
        tk.messagebox.showinfo(title="Reminder", message=reminder_text)

root = tk.Tk()
my_gui = ReminderGUI(root)
root.mainloop()
S