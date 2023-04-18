from tkinter import Tk
from typing import Callable

from pony.orm import Database


class ScheduleSelector:
    """Class representing a window which allows the user to select one of several schedules from a
    passed Scenario.

    If the Scenario doesn't contain any Schedules, the window provides the functionality to
    create."""

    def __init__(self, parent: Tk, db: Database, scenario: Scenario, callback: Callable = None):
        self.parent = parent
        self.db = db
        self.scenario = scenario
        self.callback = callback
        self.sched_dict = {}
        self.sched_list = []
        self.window = self._setup_window(parent)
        self.frame = self._setup_frame()
        self._setup_interface()
        self.window.grab_set()
        self.window.mainloop()

        pass
