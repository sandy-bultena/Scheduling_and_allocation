from tkinter import *
from tkinter import ttk
from tkinter.ttk import Progressbar
from functools import partial

import mysql.connector
from pony.orm import Database, db_session, commit

from Schedule.unit_tests.db_constants import DB_NAME, HOST, PROVIDER
import Schedule.database.PonyDatabaseConnection as PonyDatabaseConnection


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
    ttk.Button(scen_frm, text="New", command=create_scenario).grid(row=2, column=0)
    ttk.Button(scen_frm, text="Select").grid(row=2, column=1)
    ttk.Button(scen_frm, text="Delete").grid(row=3, column=0)
    ttk.Button(scen_frm, text="Cancel", command=scenario_window.destroy).grid(row=3, column=1)
    scenario_window.mainloop()
    pass


@db_session
def create_scenario():
    """Create a new database Scenario object."""
    # TODO: Refactor this later once changes have been merged from the code_review branch.
    scenario = PonyDatabaseConnection.Scenario(name="Test", description="This is a test.",
                                               year=2023)
    commit()


def _verify_login(**kwargs: StringVar):
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
            # root.update()


def display_error_message(msg: str):
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

    root.mainloop()
