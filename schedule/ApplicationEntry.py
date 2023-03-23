import re
import tkinter
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.ttk import Progressbar
from functools import partial

import mysql.connector
import pony.orm
from pony.orm import Database, db_session, commit, select, flush

from Schedule.unit_tests.db_constants import DB_NAME, HOST, PROVIDER
import Schedule.database.PonyDatabaseConnection as PonyDatabaseConnection


# TODO: Fix import issues regarding this class.
# import Schedule.Schedule as ModelSchedule


class LoginWindow:
    def __init__(self, parent: Tk):
        self.parent = parent
        self.frame = self._setup_frame()
        self._setup_interface()

    def _setup_frame(self):
        frame = ttk.Frame(self.parent, padding=30)
        frame.grid()
        return frame

    def _setup_interface(self):
        ttk.Label(self.frame, text="Please login to access the scheduler.").grid(column=1, row=0)
        ttk.Label(self.frame, text="Username").grid(column=0, row=1)
        ttk.Label(self.frame, text="Password").grid(column=0, row=2)
        username_input = StringVar()
        password_input = StringVar()
        self.username_entry = ttk.Entry(self.frame, textvariable=username_input)
        self.username_entry.grid(column=1, row=1, columnspan=2)
        self.password_entry = ttk.Entry(self.frame, textvariable=password_input, show="*")
        self.password_entry.grid(column=1, row=2, columnspan=2)
        self.login_btn = ttk.Button(self.frame, text="Login", command=self._verify_login)
        self.login_btn.grid(column=1, row=3, columnspan=1)

    def _verify_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if len(username) == 0 or len(password) == 0:
            display_error_message("Username and password are required.")
            return
        try:
            # Attempt to connect to the database using these credentials.
            db = PonyDatabaseConnection.define_database(host=HOST, db=DB_NAME, user=username,
                                                        passwd=password, provider=PROVIDER)
            # If successful, make the LoginWindow's parent disappear. We don't want the window
            # hanging around as a distraction.
            self.parent.withdraw()
            # Then display the scenario selector window.
            _display_scenario_selector(db)
        except mysql.connector.DatabaseError as err:
            display_error_message(str(err))
        except TypeError as err:
            display_error_message(str(err))
        except mysql.connector.InterfaceError as err:
            display_error_message(str(err))


def check_num(newval):
    # Taken from the official tkinter documentation here:
    # https://tkdocs.com/tutorial/widgets.html#entry
    return re.match('^[0-9]*$', newval) is not None


@db_session
def _open_schedule(listbox: Listbox, schedule_dict: dict[str, PonyDatabaseConnection.Schedule]):
    # sched_id = db_schedule.id
    # schedule = ModelSchedule.Schedule.read_DB(sched_id)
    indexes = listbox.curselection()
    if len(indexes) < 1:
        return
    key = listbox.get(indexes[0])
    db_schedule: PonyDatabaseConnection.Schedule = schedule_dict[key]
    # TODO: Come back to this once the import issues with Schedule have been solved.
    flush()
    db_id = db_schedule.id
    # real_schedule: ModelSchedule.Schedule = ModelSchedule.Schedule.read_DB(db_id)
    # print(real_schedule)
    pass


@db_session
def _create_schedule(descript_var: StringVar, semester_var: StringVar, official_var: BooleanVar,
                     scenario_id: PonyDatabaseConnection.Scenario):
    """Create a database Schedule entity based on passed values."""
    description = descript_var.get()
    semester = semester_var.get()
    official = official_var.get()
    schedule = PonyDatabaseConnection.Schedule(description=description, semester=semester,
                                               official=official, scenario_id=scenario_id)
    commit()


@db_session
def add_new_schedule(scenario: PonyDatabaseConnection.Scenario):
    """Opens a window where the user can enter values to create a new Schedule object."""
    sched_window = Toplevel(root)
    sched_window.title("Add new Schedule")
    sched_window.grab_set()
    sched_frm = ttk.Frame(sched_window, padding=35)
    sched_frm.grid()
    ttk.Label(sched_frm, text="Description (Optional)").grid(row=0, column=0)
    descr_var = StringVar()
    semester_var = StringVar()
    official_var = BooleanVar()
    semesters = ["winter", "summer", "fall"]
    ttk.Entry(sched_frm, textvariable=descr_var).grid(row=0, column=1)
    ttk.Label(sched_frm, text="Semester").grid(row=1, column=0)
    semester_box = ttk.Combobox(sched_frm, textvariable=semester_var)
    semester_box['values'] = semesters
    semester_box.grid(row=1, column=1)
    ttk.Label(sched_frm, text="Official?").grid(row=2, column=0)
    ttk.Checkbutton(sched_frm, text="Yes", variable=official_var, onvalue=True, offvalue=False) \
        .grid(row=2, column=1)
    ttk.Button(sched_frm, text="Confirm", command=partial(
        _create_schedule, descr_var, semester_var, official_var, scenario
    )).grid(row=3, column=0)
    ttk.Button(sched_frm, text="Cancel", command=sched_window.destroy).grid(row=3, column=1)
    sched_window.mainloop()


@db_session
def _display_selected_scenario(scenario: PonyDatabaseConnection.Scenario):
    """Opens a window displaying detailed information about a passed Scenario.

    Also allows the user to select an existing Schedule from the database, or create a new one."""
    scen_window = Toplevel(root)
    scen_window.title(f"Scenario: {scenario.name} {scenario.year}")
    scen_window.grab_set()
    scen_frm = ttk.Frame(scen_window, padding=40)
    scen_frm.grid()
    name_frm = ttk.Labelframe(scen_frm, text="Name:")
    name_frm.grid(row=0, column=0, sticky="ew")
    ttk.Label(name_frm, text=scenario.name).grid(row=0, column=0)
    year_frm = ttk.Labelframe(scen_frm, text="Year")
    year_frm.grid(row=0, column=1, sticky="ew")
    ttk.Label(year_frm, text=scenario.year).grid(row=0, column=0)

    desc_frm = ttk.Labelframe(scen_frm, text="Description")
    desc_frm.grid(row=1, column=0, columnspan=2, sticky="ew")
    ttk.Label(desc_frm, text=scenario.description).grid(row=0, column=0)

    # List all the Schedules belonging to this section.
    db_schedules = select(sch for sch in PonyDatabaseConnection.Schedule
                          if sch.scenario_id == scenario)
    flush()
    sched_list = [s for s in db_schedules]
    sched_dict: dict[str, PonyDatabaseConnection.Schedule] = {}
    for sched in sched_list:
        sched_dict[str(sched)] = sched
    schedule_var = StringVar(value=sched_list)
    ttk.Label(scen_frm, text=f"Schedules for {scenario.name}:").grid(row=3, column=0, columnspan=2)
    sched_listbox = Listbox(scen_frm, listvariable=schedule_var)
    sched_listbox.grid(row=4, column=0, columnspan=2)
    ttk.Button(scen_frm, text="New", command=partial(
        add_new_schedule, scenario)).grid(row=5, column=0)
    ttk.Button(scen_frm, text="Open", command=partial(
        _open_schedule, sched_listbox, sched_dict)).grid(row=5, column=1)
    scen_window.mainloop()


@db_session
def _open_scenario(listbox: Listbox, db: Database,
                   scenario_dict: dict[str, PonyDatabaseConnection.Scenario]):
    # Have to jump through some complex hoops to get the Scenario entity corresponding to the
    # selected index of the Listbox.
    scenarios = listbox.curselection()
    if len(scenarios) < 1:
        return
    # Listbox.get() returns a string in this context.
    scenario_string = listbox.get(scenarios[0])
    # Use that string to get the corresponding Scenario entity from the passed dictionary.
    scenario = scenario_dict[scenario_string]
    flush()
    _display_selected_scenario(scenario)


@db_session
def _display_scenario_selector(db: Database):
    """Displays a window where the user can select an existing Scenario from the database,
    or create a new one."""
    scenario_window = Toplevel(root)
    scenario_window.title("SELECT SCENARIO")
    scenario_window.grab_set()
    scen_frm = ttk.Frame(scenario_window, padding=40)
    scen_frm.grid()
    ttk.Label(scen_frm, text="Select a scenario:").grid(row=0, column=0, columnspan=2)
    scen_dict, scen_list = _get_all_scenarios()
    scenario_var = tkinter.Variable(value=scen_list)
    l_box = Listbox(scen_frm, listvariable=scenario_var)
    l_box.grid(row=0, column=0, columnspan=2)
    ttk.Button(scen_frm, text="New", command=partial(
        add_new_scenario, scen_dict, scen_list, scenario_var)).grid(row=2, column=0)
    ttk.Button(scen_frm, text="Open", command=partial(
        _open_scenario, l_box, db, scen_dict)).grid(row=2, column=1)
    ttk.Button(scen_frm, text="Delete").grid(row=3, column=0)
    ttk.Button(scen_frm, text="Cancel", command=root.destroy).grid(row=3, column=1)
    # Close the program if this window is closed or destroyed.
    scenario_window.protocol("WM_DELETE_WINDOW", root.destroy)
    scenario_window.mainloop()
    pass


def _get_all_scenarios() -> tuple[
    dict[str, PonyDatabaseConnection.Scenario], list[PonyDatabaseConnection.Scenario]]:
    """Retrieve all scenarios from the database.

    Returns both a dictionary containing the scenario records keyed to their string representations,
    and a list of the scenario records."""
    db_scenarios = PonyDatabaseConnection.Scenario.select()
    commit()
    scen_list: list[PonyDatabaseConnection.Scenario] = [s for s in db_scenarios]
    scen_dict: dict[str, PonyDatabaseConnection.Scenario] = {}
    for scen in scen_list:
        scen_dict[str(scen)] = scen
    return scen_dict, scen_list


def add_new_scenario(s_dict: dict[str, PonyDatabaseConnection.Scenario],
                     s_list: list[PonyDatabaseConnection.Scenario],
                     s_var: StringVar):
    """Create a window in which the user can fill out various entry fields to create a new
    Scenario database object. """
    add_window = Toplevel(root)
    add_window.title("Add New Scenario")
    add_window.grab_set()
    add_frm = ttk.Frame(add_window, padding=25)
    add_frm.grid()
    scen_name = StringVar()
    scen_descr = StringVar()
    scen_year = IntVar()
    ttk.Label(add_frm, text="Name").grid(row=0, column=0)
    name_entry = ttk.Entry(add_frm, textvariable=scen_name)
    name_entry.grid(row=0, column=1)
    ttk.Label(add_frm, text="Description").grid(row=1, column=0)
    descr_entry = ttk.Entry(add_frm, textvariable=scen_descr)
    descr_entry.grid(row=1, column=1)
    ttk.Label(add_frm, text="Year").grid(row=2, column=0)
    # Validation ensures that the user can only enter integer numbers into this field.
    year_entry = ttk.Entry(add_frm, textvariable=scen_year, validate='key',
                           validatecommand=check_num_wrapper)
    year_entry.grid(row=2, column=1)
    ttk.Button(add_frm, text="Confirm", command=partial(
        _create_scenario, scen_name, scen_descr, scen_year, add_window, s_dict, s_list, s_var)) \
        .grid(row=3, column=0)
    ttk.Button(add_frm, text="Cancel", command=add_window.destroy).grid(row=3, column=1)
    add_window.mainloop()


@db_session
def _create_scenario(name: StringVar, description: StringVar, year: IntVar, parent: Toplevel,
                     scen_dict: dict[str, PonyDatabaseConnection.Scenario], scen_list: list,
                     scen_var: StringVar):
    """Create a new database Scenario object."""
    # TODO: Refactor this later once changes have been merged from the code_review branch.
    try:
        scenario = PonyDatabaseConnection.Scenario(name=name.get(), description=description.get(),
                                                   year=year.get())
        commit()
        messagebox.showinfo("Success", "Successfully added this scenario to the database")
        # Update the list of scenarios displayed in the main window.
        s_dict, scen_list = _get_all_scenarios()
        scen_dict = s_dict
        scen_var.set(scen_list)
        parent.destroy()
    except mysql.connector.DatabaseError as err:
        # Display an error message if anything goes wrong while creating this Scenario.
        display_error_message(str(err))
    except pony.orm.OperationalError as err:
        display_error_message(str(err))


# def _verify_login(**kwargs: StringVar):
#     """Verifies the user's credentials and tries to connect to the database.
#
#     Displays an error message if anything goes wrong."""
#     # Do something to verify the user's credentials.
#     username = kwargs['username'].get()
#     passwd = kwargs['passwd'].get()
#     if username is None or len(username) == 0 or passwd is None or len(passwd) == 0:
#         # Display an error message.
#         display_error_message("Username and password are required.")
#     else:
#         try:
#             connect_msg = "Connecting..."
#             statusString.set(connect_msg)
#             root.update()
#             pb = ttk.Progressbar(frm, orient='horizontal', length=200, mode='indeterminate')
#             pb.grid(column=0, row=5, columnspan=2)
#             pb.start()
#             root.update()
#             # TODO: To make the ProgressBar display properly, we would need to make this into an
#             #  async call. Ultimately, it may not be worth the effort.
#             db = PonyDatabaseConnection.define_database(host=HOST, db=DB_NAME, user=username,
#                                                         passwd=passwd, provider=PROVIDER)
#             success_msg = f"Connection Successful."
#             pb.stop()
#             pb.destroy()
#             print(success_msg)
#             statusString.set(success_msg)
#             root.withdraw()
#             _display_scenario_selector(db)
#         except mysql.connector.DatabaseError as err:
#             # Display a relevant error message for anything else that might go wrong with the
#             # connection.
#             statusString.set(" ")
#             if pb is not None:
#                 pb.stop()
#                 pb.destroy()
#             display_error_message(str(err))
#         except TypeError as err:
#             statusString.set(" ")
#             if pb is not None:
#                 pb.stop()
#                 pb.destroy()
#             display_error_message(str(err))
#         except mysql.connector.InterfaceError as err:
#             statusString.set(" ")
#             if pb is not None:
#                 pb.stop()
#                 pb.destroy()
#             display_error_message(str(err))
#             # root.update()


def display_error_message(msg: str):
    """Displays a passed error message in a new window."""
    messagebox.showerror("ERROR", msg)


if __name__ == "__main__":
    root = Tk()
    root.title("Scheduling Application -  Login")
    # frm = ttk.Frame(root, padding=30)
    # frm.grid()
    # ttk.Label(frm, text="Please login to access the scheduler").grid(column=1, row=0)
    # ttk.Label(frm, text="Username").grid(column=0, row=1)
    # usernameInput = StringVar()
    # ttk.Entry(frm, textvariable=usernameInput).grid(column=1, row=1, columnspan=2)
    # ttk.Label(frm, text="Password").grid(column=0, row=2)
    # passwdInput = StringVar()
    # ttk.Entry(frm, textvariable=passwdInput, show="*").grid(column=1, row=2, columnspan=2)
    # ttk.Button(frm, text="Login",
    #            command=partial(_verify_login, username=usernameInput, passwd=passwdInput)) \
    #     .grid(column=1, row=3, columnspan=1)
    # ttk.Separator(frm, orient=HORIZONTAL).grid(column=0, row=4, columnspan=3, sticky="ew")
    # statusString = StringVar()
    # ttk.Label(frm, textvariable=statusString).grid(column=0, row=5, columnspan=2)
    frm = LoginWindow(root)
    check_num_wrapper = (root.register(check_num), '%P')
    root.mainloop()
