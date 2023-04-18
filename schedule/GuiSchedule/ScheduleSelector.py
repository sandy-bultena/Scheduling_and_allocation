import tkinter
from tkinter import Tk, Toplevel, Frame, ttk
from typing import Callable

from pony.orm import Database


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
        listbox = tkinter.Listbox(self.frame, listvariable=sched_var)
        listbox.grid(row=1, column=0, columnspan=2)

    def _get_schedules_for_scenario(self):
        """Retrieves all Schedules belonging to the passed Scenario."""
        scheds = []
        scheds.extend(self.scenario.schedules)
        self.sched_list = sorted(scheds, key=lambda s: s.id)
        for sched in self.sched_list:
            self.sched_dict[str(sched)] = sched
