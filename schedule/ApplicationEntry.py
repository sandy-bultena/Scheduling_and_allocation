from tkinter import *
from tkinter import ttk
from functools import partial


def verify_login(*args: StringVar):
    # Do something to verify the user's credentials.
    print(args)
    for arg in args:
        print(arg.get())
    pass


root = Tk()
root.title("Scheduling Application -  Login")
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="Please login to access the scheduler").grid(column=1, row=0)
ttk.Label(frm, text="Username").grid(column=0, row=1)
usernameInput = StringVar()
ttk.Entry(frm, textvariable=usernameInput).grid(column=1, row=1, columnspan=2)
ttk.Label(frm, text="Password").grid(column=0, row=2)
passwdInput = StringVar()
ttk.Entry(frm, textvariable=passwdInput).grid(column=1, row=2, columnspan=2)
ttk.Button(frm, text="Login", command=partial(verify_login, usernameInput, passwdInput)).grid(column=1, row=3, columnspan=1)

root.mainloop()
