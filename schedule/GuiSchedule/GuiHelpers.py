from tkinter import messagebox


def display_error_message(msg: str):
    """Displays a passed error message in a new window."""
    messagebox.showerror("ERROR", msg)
