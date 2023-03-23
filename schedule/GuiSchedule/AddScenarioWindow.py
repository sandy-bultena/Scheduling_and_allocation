from tkinter import Toplevel, Frame, ttk, StringVar, IntVar, messagebox

import mysql.connector
from pony.orm import Database, flush

from GuiSchedule.GuiHelpers import check_num
from Schedule.database import PonyDatabaseConnection as PonyDatabaseConnection


class AddScenarioWindow:
    def __init__(self, parent: Toplevel, db: Database):
        self.parent = parent
        self.db = db
        self.check_num_wrapper = (self.parent.register(check_num), '%P')
        self.window = self._setup_window(parent)
        self.frame = self._setup_frame()
        self._setup_interface()
        self.window.grab_set()
        self.window.mainloop()
    pass

    @staticmethod
    def _setup_window(parent) -> Toplevel:
        window = Toplevel(parent)
        window.title("ADD NEW SCENARIO")
        return window

    def _setup_frame(self) -> Frame:
        frame = ttk.Frame(self.window, padding=25)
        frame.grid()
        return frame

    def _setup_interface(self):
        ttk.Label(self.frame, text="Name").grid(row=0, column=0)
        ttk.Label(self.frame, text="Description").grid(row=1, column=0)
        ttk.Label(self.frame, text="Year").grid(row=2, column=0)
        name_var = StringVar()
        descr_var = StringVar()
        year_var = IntVar()
        self.name_entry = ttk.Entry(self.frame, textvariable=name_var)
        self.name_entry.grid(row=0, column=1)
        self.description_entry = ttk.Entry(self.frame, textvariable=descr_var)
        self.description_entry.grid(row=1, column=1)
        self.year_entry = ttk.Entry(self.frame, textvariable=year_var, validate='key',
                                    validatecommand=self.check_num_wrapper)
        self.year_entry.grid(row=2, column=1)
        ttk.Button(self.frame, text="Confirm", command=self._create_scenario).grid(row=3, column=0)
        ttk.Button(self.frame, text="Cancel").grid(row=3, column=1)

    def _create_scenario(self):
        name = self.name_entry.get()
        description = self.description_entry.get()
        year = int(self.year_entry.get())
        try:
            scenario = PonyDatabaseConnection.Scenario(name=name, description=description,
                                                       year=year)
            flush()
            messagebox.showinfo("Success", "Successfully added this scenario to the database.")
        except mysql.connector.DatabaseError as err:
            pass
