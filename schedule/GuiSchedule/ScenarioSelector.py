from tkinter import Tk, Frame, ttk, Toplevel, StringVar, Listbox

from pony.orm import Database, db_session, flush

from Schedule.database import PonyDatabaseConnection as PonyDatabaseConnection


class ScenarioSelector:
    """Class representing a window which allows the user to pick from one of several scenarios.

    Scenarios are retrieved from the database. If no scenarios exist, the selector gives the user
    the functionality to create new ones. """

    def __init__(self, parent: Tk, db: Database):
        self.parent = parent
        self.db = db
        self.scen_dict = {}
        self.window = self._setup_window(parent)
        self.frame = self._setup_frame()
        self._setup_interface()
        self.window.grab_set()
        self.window.mainloop()

    def _setup_frame(self) -> Frame:
        frame = ttk.Frame(self.window, padding=40)
        frame.grid()
        return frame

    @staticmethod
    def _setup_window(parent) -> Toplevel:
        window = Toplevel(parent)
        window.title("SELECT SCENARIO")
        return window

    def _setup_interface(self):
        ttk.Label(self.frame, text="Select a scenario:").grid(row=0, column=0, columnspan=2)
        self._get_all_scenarios()
        self.scenario_var = StringVar(value=self.scen_list)
        self.listbox = Listbox(self.frame, listvariable=self.scenario_var)
        self.listbox.grid(row=1, column=0, columnspan=2)
        ttk.Button(self.frame, text="New", command=self.add_new_scenario).grid(row=2, column=0)
        ttk.Button(self.frame, text="Open", command=self.open_scenario).grid(row=2, column=1)
        self.window.protocol("WM_DELETE_WINDOW", self.parent.destroy)
        pass

    @db_session
    def _get_all_scenarios(self):
        """Retrieves all scenario records from the database, storing them within this
        ScenarioSelector object."""
        db_scenarios = PonyDatabaseConnection.Scenario.select()
        flush()
        self.scen_list = [s for s in db_scenarios]
        for scen in self.scen_list:
            self.scen_dict[str(scen)] = scen

    @db_session
    def add_new_scenario(self):
        """Opens a window in which the user can add a new scenario to the database by filling out
        a form."""
        pass

    def open_scenario(self):
        pass
