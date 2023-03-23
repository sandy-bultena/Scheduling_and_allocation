import re
from tkinter import messagebox


def display_error_message(msg: str):
    """Displays a passed error message in a new window."""
    messagebox.showerror("ERROR", msg)


def check_num(newval):
    # Taken from the official tkinter documentation here:
    # https://tkdocs.com/tutorial/widgets.html#entry
    return re.match('^[0-9]*$', newval) is not None
