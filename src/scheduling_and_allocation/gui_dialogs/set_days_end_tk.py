"""
Change the default hour that specifies the end of day
"""
from __future__ import annotations

import tkinter as tk
from tkinter.simpledialog import Dialog
from tkinter.messagebox import showinfo

from docutils.parsers.rst.directives.tables import align

from ..Utilities.Preferences import Preferences


class ChangeDaysEnd(Dialog):
    def __init__(self, mw: tk.Tk, preferences: Preferences, title="Change the 'end-of-day'"):
        self.warning_label = None
        self.label_big = None
        self.label_normal = None
        self.label_small = None
        self.preferences = preferences
        self.current_end_of_day_tk = tk.StringVar(value=str(self.preferences.end_of_day()))

        super().__init__(mw, title)

    # ================================================================================================================
    # The content of the main body of the dialog box
    # ================================================================================================================
    def body(self, frame:tk.Frame):
        """
        :param frame: the frame where you are gonna put stuff
        """
        subframe = tk.Frame(frame)
        self.frame=frame

        modify_days_end = frame.winfo_toplevel().register(self._change_days_end)
        label=tk.Label(subframe, text="Latest Scheduable Hour:", justify='left')
        entry = tk.Entry(subframe, textvariable=self.current_end_of_day_tk,
                                   validate='key',
                                   validatecommand=(modify_days_end, '%P', '%s')
                                   )

        # layout
        label.pack(side="left",fill='x',expand=1, padx=20,pady=50)
        entry.pack(side="left",fill='x',expand=1, padx=20,pady=50)
        subframe.pack(side="top", expand=1, fill='x', pady=20)

        return entry

    # ================================================================================================================
    # change the displayed days end number
    # ================================================================================================================
    def _change_days_end(self, number: str, *_):
        """is the number being entered a valid float"""
        if number == "":
            return True
        if number == ".":
            return True
        try:
            float(number)
            return True
        except ValueError:
            return False

    # ================================================================================================================
    # validate before applying
    # ================================================================================================================
    def validate(self):
        """
        Is the data, as entered by the user, valid?
        :return: True if data is good (changes are applied), false otherwise (nothing happens)
        """
        try:
            float(self.current_end_of_day_tk.get() )
            return True
        except ValueError:
            return False

    # ================================================================================================================
    # apply changes
    # ================================================================================================================
    def apply(self):
        """apply the changes and close the dialog"""
        try:
            hour = float(self.current_end_of_day_tk.get())
            self.preferences.end_of_day(hour)
            self.preferences.save()

        except ValueError:
            pass
