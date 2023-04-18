import tkinter
from functools import partial
from tkinter import Tk, Toplevel, Frame, ttk
from typing import Callable

from pony.orm import Database, db_session, flush

from ..Schedule.Schedule import Schedule
from ..Schedule.ScheduleWrapper import scenarios
from ..Schedule.database import PonyDatabaseConnection


class ScheduleSelector:
    """Class representing a window which allows the user to select one of several schedules from a
    passed Scenario.

    If the Scenario doesn't contain any Schedules, the window provides the functionality to
    create."""

    def __init__(self, parent: Tk, db: Database, scenario, callback: Callable = None):
        self.parent = parent
        self.db = db
        self.scenario = scenario
        self.callback = callback
        self.sched_dict = {}
        self.sched_list = []
        self.window: Toplevel = self._setup_window(parent)
        self.frame: Frame = self._setup_frame()
        self._setup_interface()
        self.window.grab_set()
        self.window.mainloop()

        pass

    @staticmethod
    def _setup_window(parent) -> Toplevel:
        """Initializes the window containing this ScheduleSelector object."""
        window = Toplevel(parent)
        window.title("SELECT SCHEDULE")
        return window

    def _setup_frame(self) -> Frame:
        frame = Frame(self.window, padx=20, pady=20)
        frame.grid()
        return frame

    def _setup_interface(self):
        ttk.Label(self.frame, text=f"Select a schedule from Scenario {self.scenario.name}:")\
            .grid(row=0, column=0, columnspan=2)
        self._get_schedules_for_scenario()
        sched_var = tkinter.StringVar(value=self.sched_list)
        self.listbox = tkinter.Listbox(self.frame, listvariable=sched_var)
        self.listbox.grid(row=1, column=0, columnspan=2)
        ttk.Button(self.frame, text="New", command=self.add_new_schedule).grid(row=2, column=0)
        ttk.Button(self.frame, text="Open", command=partial(
            self.callback, self.open_schedule) if self.callback
            else self.open_schedule).grid(row=2, column=1)

    @db_session
    def _get_schedules_for_scenario(self):
        """Retrieves all Schedules belonging to the passed Scenario."""
        scheds = []
        db_scen = PonyDatabaseConnection.Scenario[self.scenario.id]
        flush()
        scheds.extend(db_scen.schedules)
        self.sched_list = sorted(scheds, key=lambda s: s.id)
        for sched in self.sched_list:
            self.sched_dict[str(sched)] = sched

    def add_new_schedule(self):
        pass

    def open_schedule(self):
        # Get the selected index from the listbox.
        indices = self.listbox.curselection()
        if len(indices) != 1:
            # Print an error message stating that the user needs to select exactly 1 schedule.
            pass

        # Get the db Schedule corresponding to this index.
        index = indices[0]
        db_sched = self.sched_list[index]

        # Create a model Schedule object from the db_schedule.
        sched = Schedule.read_DB(db_sched.id)

        # Release the Window, destroy it, and quit its loop.
        self.window.grab_release()
        self.window.destroy()
        self.window.quit()

        # Return the selected Schedule object.
        return sched
