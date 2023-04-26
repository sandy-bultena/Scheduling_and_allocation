from functools import partial
from tkinter import Tk, Frame, ttk, Toplevel, StringVar, Listbox

from pony.orm import Database, db_session, flush

from Schedule.database import PonyDatabaseConnection as PonyDatabaseConnection

from .AddScenarioWindow import AddScenarioWindow
from Schedule.ScheduleWrapper import scenarios


class ScenarioSelector:
    """Class representing a window which allows the user to pick from one of several scenarios.

    Scenarios are retrieved from the database. If no scenarios exist, the selector gives the user
    the functionality to create new ones. """

    def __init__(self, parent: Tk, db: Database, callback=None):
        self.parent = parent
        self.db = db
        self.callback = callback
        self.scen_dict = {}
        self.scen_list = []
        self.window = self._setup_window(parent)
        self.frame = self._setup_frame()
        self.listbox: Listbox
        self.scenario_var: StringVar = StringVar()
        self._setup_interface()
        self.window.grab_set()
        self.window.mainloop()

    def _setup_frame(self) -> Frame:
        frame = ttk.Frame(self.window, padding=20)
        frame.grid()
        return frame

    @staticmethod
    def _setup_window(parent) -> Toplevel:
        window = Toplevel(parent)
        window.title("SELECT SCENARIO")
        return window

    def _setup_interface(self):
        ttk.Label(self.frame, text="Select a scenario:").grid(row=0, column=0, columnspan=2)
        self._setup_scenario_picker()
        ttk.Button(self.frame, text="New", command=self.add_new_scenario) \
            .grid(row=2, column=0)
        ttk.Button(self.frame, text="Open", command=partial(self.callback, self.open_scenario) if self.callback
                   else self.open_scenario) \
            .grid(row=2, column=1)
        self.window.protocol("WM_DELETE_WINDOW", self.parent.destroy)

    def _setup_scenario_picker(self):
        self._get_all_scenarios()
        self.listbox = Listbox(self.frame, listvariable=self.scenario_var)
        self.listbox.grid(row=1, column=0, columnspan=2)

    @db_session
    def _get_all_scenarios(self, force=False):
        """Retrieves all scenario records from the database, storing them within this
        ScenarioSelector object."""
        if force or not self.scen_list:
            self.scen_list = sorted(scenarios(ignore_schedules=True), key=lambda a: a.id)
        for scen in self.scen_list:
            self.scen_dict[str(scen)] = scen

        self.scenario_var.set(value=self.scen_list)

    @db_session
    def add_new_scenario(self):
        """Opens a window in which the user can add a new scenario to the database by filling out
        a form."""
        AddScenarioWindow(self.window, self.db, self._get_all_scenarios)
        self.window.update()

    def open_scenario(self):
        # self.boxes[0].get() produces a string in this case. Not useful for our purposes.

        # Get the selected index.
        selected_index = self.listbox.curselection()[0]

        # Get the scenario(s) corresponding to that index or those indices.
        selected_scenario = self.scen_list[selected_index]

        self.window.grab_release()
        # Calling the quit() method stops the window's mainloop from executing.
        # Discovered this fact here:
        # https://stackoverflow.com/questions/29363363/destroying-toplevel-window-doesnt-let-the-application-come-out-of-the-main-loop#:~:text=destroy%20does%20not%20exit%20the%20mainloop%2C%20it%20only,well%20as%20root1.destroy%20%28%29%20on%20clicking%20the%20button.
        self.window.destroy()
        self.window.quit()
        return selected_scenario
