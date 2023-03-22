import re
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Progressbar
from functools import partial

import mysql.connector
from pony.orm import Database, db_session, commit, select, flush

from Schedule.unit_tests.db_constants import DB_NAME, HOST, PROVIDER
import Schedule.database.PonyDatabaseConnection as PonyDatabaseConnection
# import Schedule.Schedule as ModelSchedule


def check_num(newval):
    # Taken from the official tkinter documentation here:
    # https://tkdocs.com/tutorial/widgets.html#entry
    return re.match('^[0-9]*$', newval) is not None


@db_session
def _open_scenario(listbox: Listbox, db: Database):
    # Have to jump through some complex hoops to get the Scenario entity corresponding to the
    # selected index of the Listbox.
    scenarios = listbox.curselection()
    if len(scenarios) < 1:
        return
    # Listbox.get() returns a string in this context.
    scenario_string = listbox.get(0)
    # Use that string to query the database and get the corresponding entity.
    scenario = eval(f"PonyDatabaseConnection.{scenario_string}")
    sc_id = scenario.id
    db_schedules = select(s for s in PonyDatabaseConnection.Schedule if s.scenario_id == scenario)
    flush()
    pass


@db_session
def _display_scenario_selector(db: Database):
    """Displays a window where the user can select an existing Scenario from the database,
    or create a new one."""
    scenario_window = Toplevel(root)
    scenario_window.title = "SELECT SCENARIO"
    scenario_window.grab_set()
    scen_frm = ttk.Frame(scenario_window, padding=40)
    scen_frm.grid()
    ttk.Label(scen_frm, text="Select a scenario:").grid(row=0, column=0, columnspan=2)
    db_scenarios = PonyDatabaseConnection.Scenario.select()
    commit()
    scen_list: list[PonyDatabaseConnection.Scenario] = [s for s in db_scenarios]
    scenario_var = StringVar(value=scen_list)
    l_box = Listbox(scen_frm, listvariable=scenario_var)
    l_box.grid(row=0, column=0, columnspan=2)
    ttk.Button(scen_frm, text="New", command=add_new_scenario).grid(row=2, column=0)
    ttk.Button(scen_frm, text="Open", command=partial(
        _open_scenario, l_box, db)).grid(row=2, column=1)
    ttk.Button(scen_frm, text="Delete").grid(row=3, column=0)
    ttk.Button(scen_frm, text="Cancel", command=scenario_window.destroy).grid(row=3, column=1)
    scenario_window.mainloop()
    pass


def add_new_scenario():
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
        _create_scenario, scen_name, scen_descr, scen_year)) \
        .grid(row=3, column=0)
    ttk.Button(add_frm, text="Cancel", command=add_window.destroy).grid(row=3, column=1)
    add_window.mainloop()


@db_session
def _create_scenario(name: StringVar, description: StringVar, year: IntVar):
    """Create a new database Scenario object."""
    # TODO: Refactor this later once changes have been merged from the code_review branch.
    scenario = PonyDatabaseConnection.Scenario(name=name.get(), description=description.get(),
                                               year=year.get())
    commit()


def _verify_login(**kwargs: StringVar):
    """Verifies the user's credentials and tries to connect to the database.

    Displays an error message if anything goes wrong."""
    # Do something to verify the user's credentials.
    username = kwargs['username'].get()
    passwd = kwargs['passwd'].get()
    if username is None or len(username) == 0 or passwd is None or len(passwd) == 0:
        # Display an error message.
        display_error_message("Username and password are required.")
    else:
        try:
            connect_msg = "Connecting..."
            statusString.set(connect_msg)
            root.update()
            pb = ttk.Progressbar(frm, orient='horizontal', length=200, mode='indeterminate')
            pb.grid(column=0, row=5, columnspan=2)
            pb.start()
            root.update()
            # TODO: To make the ProgressBar display properly, we would need to make this into an
            #  async call. Ultimately, it may not be worth the effort.
            db = PonyDatabaseConnection.define_database(host=HOST, db=DB_NAME, user=username,
                                                        passwd=passwd, provider=PROVIDER)
            success_msg = f"Connection Successful."
            pb.stop()
            pb.destroy()
            print(success_msg)
            statusString.set(success_msg)
            _display_scenario_selector(db)
        except mysql.connector.DatabaseError as err:
            # Display a relevant error message for anything else that might go wrong with the
            # connection.
            statusString.set(" ")
            if pb is not None:
                pb.stop()
                pb.destroy()
            display_error_message(str(err))
        except TypeError as err:
            statusString.set(" ")
            if pb is not None:
                pb.stop()
                pb.destroy()
            display_error_message(str(err))
            # root.update()


def display_error_message(msg: str):
    """Displays a passed error message in a new window."""
    error_window = Toplevel(root)
    error_window.title("ERROR")
    err_frm = ttk.Frame(error_window, padding=20)
    err_frm.grid()
    ttk.Label(err_frm, text=msg).grid(row=0, column=0)
    ttk.Button(err_frm, text="Okay", command=error_window.destroy).grid(row=1, column=0)
    # Disables the main window so the user can't click on it while this error message is displayed.
    # Control will be restored when this window is closed.
    error_window.grab_set()
    error_window.mainloop()


if __name__ == "__main__":
    root = Tk()
    root.title("Scheduling Application -  Login")
    frm = ttk.Frame(root, padding=30)
    frm.grid()
    ttk.Label(frm, text="Please login to access the scheduler").grid(column=1, row=0)
    ttk.Label(frm, text="Username").grid(column=0, row=1)
    usernameInput = StringVar()
    ttk.Entry(frm, textvariable=usernameInput).grid(column=1, row=1, columnspan=2)
    ttk.Label(frm, text="Password").grid(column=0, row=2)
    passwdInput = StringVar()
    ttk.Entry(frm, textvariable=passwdInput, show="*").grid(column=1, row=2, columnspan=2)
    ttk.Button(frm, text="Login",
               command=partial(_verify_login, username=usernameInput, passwd=passwdInput)) \
        .grid(column=1, row=3, columnspan=1)
    statusString = StringVar()
    ttk.Label(frm, textvariable=statusString).grid(column=0, row=4, columnspan=2)
    check_num_wrapper = (root.register(check_num), '%P')
    root.mainloop()
