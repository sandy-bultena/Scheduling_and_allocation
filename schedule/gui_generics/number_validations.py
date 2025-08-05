import tkinter as tk
from tkinter import messagebox
from functools import partial


# ================================================================================================================
# Number validation
# ================================================================================================================

def register_number_funcs(frame:tk.Frame):
    """this allows us to pass extra stuff from Entry validation
    :param frame: any Tk object
    """
    tk_is_int = frame.winfo_toplevel().register(partial(_is_int, frame))
    tk_is_float = frame.winfo_toplevel().register(partial(_is_float, frame))
    return tk_is_int, tk_is_float

def entry_float(frame: tk.Frame, textvariable: tk.StringVar, **kwargs ) -> tk.Entry:
    """
    An entry widget that only accepts floats (note... '' and '.' would be valid, so you still need to check later)
    :param frame:
    :param textvariable:
    :return: the entry widget with validation
    """
    _,tk_is_float = register_number_funcs(frame)

    if "justify" not in kwargs:
        kwargs["justify"] = "right"

    return tk.Entry(frame,
                           textvariable=textvariable,
                           validate='key',
                           validatecommand=(tk_is_float, '%P', '%s'),
                            **kwargs)

def entry_int(frame: tk.Frame, textvariable: tk.StringVar ) -> tk.Entry:
    """
    An entry widget that only accepts ints (note... '' and would be valid, so you still need to check later)
    :param frame:
    :param textvariable:
    :return: the entry widget with validation
    """
    tk_is_int,_ = register_number_funcs(frame)
    return tk.Entry(frame,
                           textvariable=textvariable,
                           validate='key',
                           validatecommand=(tk_is_int, '%P', '%s'),
                           justify='right')

def _is_int(frame: tk.Frame, number: str, *_) -> bool:
    """
    Validation for the string that is currently in an Entry widget
    :param number: the number_of_students that would result if this validation returns True
    :return: is this a valid int, or the start of a valid int
    """
    if number == "":
        return True
    try:
        int(number)
        return True
    except ValueError:
        frame.winfo_toplevel().bell()
        return False


def _is_float(frame: tk.Frame, number: str, _: str) -> bool:
    """
    Validation for the string that is currently in an Entry widget
    :param number: the number that would result if this validation returns True
    :return: is this a valid float, or the start of a valid float
    """
    if number == "" or number == ".":
        return True
    try:
        float(number)
        return True
    except ValueError:
        frame.winfo_toplevel().bell()
        return False

# ================================================================================================================
# general validations
# ================================================================================================================
def validate_float(number:str, title, msg)-> bool:
    """
    is this number a float
    :param number: the str version of the number to test
    :param title: dialog box title
    :param msg: dialog box message
    :return: True/False
    """
    try:
        float(number)
    except ValueError:
        messagebox.showerror(title, msg)
        return False
    return True

def validate_int(number:str, title, msg)-> bool:
    """
    is this number a int
    :param number: the str version of the number to test
    :param title: dialog box title
    :param msg: dialog box message
    :return: True/False
    """
    try:
        int(number)
    except ValueError:
        messagebox.showerror(title, msg)
        return False
    return True

