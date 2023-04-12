from tkinter import Tk, Frame, ttk, Toplevel
from .ScenarioSelector import ScenarioSelector
from Presentation import AllocationManager
from functools import partial

class ApplicationSelector:
    def __init__(self, par : Tk, db):
        self.parent = par
        self.database = db
        self.window = Toplevel(self.parent)
        self.window.title("App Select")
        self.window.protocol("WM_DELETE_WINDOW", self.parent.destroy)
        (frame := ttk.Frame(self.window, padding=20)).grid()
        ttk.Label(frame, text="Select application to open:").grid(row=0, column=0, columnspan=2)
        ttk.Button(frame, text="Schedule Manager", command=self.open_scheduler)\
            .grid(row=1, column=0)
        ttk.Button(frame, text="Allocation Manager", command=self.open_allocation)\
            .grid(row=1, column=1)

    def open_allocation(self):
        scen = ScenarioSelector(self.window, self.database, two = True, callback = AllocationManager.main)
        print(scen.results)

    def open_scheduler(self):
        ScenarioSelector(self.window, self.database)