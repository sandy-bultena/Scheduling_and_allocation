from tkinter import *
from tkinter import ttk
from functools import partial

import mysql.connector

from Schedule.unit_tests.db_constants import DB_NAME, HOST, PROVIDER
import Schedule.database.PonyDatabaseConnection as PonyDatabaseConnection


# TODO: Import the database constants so we can use/change them for the login and initial
#  connection.


def verify_login(**kwargs: StringVar):
    # Do something to verify the user's credentials.
    print(kwargs)
    for arg in kwargs:
        print(kwargs[arg])
    username = kwargs['username'].get()
    passwd = kwargs['passwd'].get()
    if username is None or len(username) == 0 or passwd is None or len(passwd) == 0:
        # Display an error message.
        display_error_message("Username and password are required.")
    else:
        try:
            db = PonyDatabaseConnection.define_database(host=HOST, db=DB_NAME, user=username,
                                                        passwd=passwd, provider=PROVIDER)
        except mysql.connector.DatabaseError as err:
            display_error_message(str(err))


def display_error_message(msg: str):
    error_window = Toplevel(root)
    error_window.title("ERROR")
    err_frm = ttk.Frame(error_window, padding=20)
    err_frm.grid()
    ttk.Label(err_frm, text=msg).grid(row=0, column=0)
    ttk.Button(err_frm, text="Okay", command=error_window.destroy).grid(row=1, column=0)
    error_window.mainloop()


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
ttk.Entry(frm, textvariable=passwdInput).grid(column=1, row=2, columnspan=2)
ttk.Button(frm, text="Login",
           command=partial(verify_login, username=usernameInput, passwd=passwdInput))\
    .grid(column=1, row=3, columnspan=1)

root.mainloop()
