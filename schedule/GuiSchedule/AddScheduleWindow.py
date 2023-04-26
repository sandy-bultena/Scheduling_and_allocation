from tkinter import Toplevel, Frame, ttk, StringVar, IntVar, messagebox

import mysql.connector
from pony.orm import Database, commit

from GuiSchedule.GuiHelpers import check_num
from Schedule.database import PonyDatabaseConnection as PonyDatabaseConnection
from Schedule.Schedule import Schedule


class AddScheduleWindow:
    def __init__(self, parent: Toplevel, db: Database, scenario, callback):
        self.parent = parent
        self.db = db
        self.scenario = scenario
        self.check_num_wrapper = (self.parent.register(check_num), '%P')
        self.window = self._setup_window(parent)
        self.frame = self._setup_frame()
        self._setup_interface()
        self.callback = callback
        self.window.grab_set()
        self.window.mainloop()

    @staticmethod
    def _setup_window(parent) -> Toplevel:
        window = Toplevel(parent)
        window.title("ADD NEW SCHEDULE")
        return window

    def _setup_frame(self) -> Frame:
        frame = ttk.Frame(self.window, padding=25)
        frame.grid()
        return frame

    def _setup_interface(self):
        ttk.Label(self.frame, text="Description").grid(row=0, column=0)
        descr_var = StringVar()
        self.description_entry = ttk.Entry(self.frame, textvariable=descr_var)
        self.description_entry.grid(row=0, column=1)
        ttk.Button(self.frame, text="Confirm", command=self._create_schedule).grid(row=3, column=0)
        ttk.Button(self.frame, text="Cancel").grid(row=3, column=1)

    def _create_schedule(self):
        description = self.description_entry.get()
        try:
            Schedule(None, False, self.scenario.id, description)
            messagebox.showinfo("Success", "Successfully added this schedule to the database.")
            self.callback(True)
            self.window.destroy()  # TODO: Figure out why the list isn't updating.
            self.window.quit()
        except mysql.connector.DatabaseError as err:
            return
