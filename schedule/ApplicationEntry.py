from tkinter import *
from tkinter import ttk
from tkinter.ttk import Progressbar
from functools import partial

import mysql.connector

from Schedule.unit_tests.db_constants import DB_NAME, HOST, PROVIDER
import Schedule.database.PonyDatabaseConnection as PonyDatabaseConnection


def verify_login(**kwargs: StringVar):
    # Do something to verify the user's credentials.
    # print(kwargs)
    # for arg in kwargs:
    #     print(kwargs[arg])
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
               command=partial(verify_login, username=usernameInput, passwd=passwdInput)) \
        .grid(column=1, row=3, columnspan=1)
    statusString = StringVar()
    ttk.Label(frm, textvariable=statusString).grid(column=0, row=4, columnspan=2)

    root.mainloop()
