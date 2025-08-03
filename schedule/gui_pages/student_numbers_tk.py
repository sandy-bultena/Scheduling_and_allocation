from __future__ import annotations
import tkinter as tk
from functools import partial
from typing import TYPE_CHECKING

from schedule.Tk.Scrolled import Scrolled
from schedule.gui_generics.number_validations import validate_int, entry_int

if TYPE_CHECKING:
    from schedule.presenter.student_numbers import SectionData


class StudentNumbersTk:
    # ============================================================================================
    # constructor
    # ============================================================================================
    def __init__(self, frame: tk.Frame, data:dict[str, list[SectionData]] = None):
        """creates the Panes for each semester"""

        self.frame = frame
        for w in frame.winfo_children():
            w.destroy()

        self.data = data
        self._update_handlers = []

        f = Scrolled(
            self.frame,
            "Frame",
            scrollbars='e',
            border=5,
            relief='flat',
        )

        self.pane = f

        # ----------------------------------------------------------------------------------------
        # put data into widget
        # ----------------------------------------------------------------------------------------
        self.refresh()
        self.pane.bind('<Leave>', func=self.save)


    def refresh(self):
        self._update_handlers.clear()

        if self.pane is None:
            return

        frame = self.pane.widget
        for w in frame.winfo_children():
            w.destroy()

        frame.columnconfigure(1, weight=5)
        frame.columnconfigure(0, weight=1)

        row = 1
        for course_name in self.data.keys():
            tk.Label(frame,
                     text=course_name,
                     anchor='w',
                     width=40
                     ).grid(column=0, row=row, columnspan=2, sticky='nsew')
            row += 1

            for section_data in self.data[course_name]:
                tk.Label(frame,
                         width=4,
                         text=section_data.name,
                         anchor='e',
                         ).grid(column=0, row=row, sticky='nsew')
                tk_var = tk.StringVar(value=section_data.number_of_students)
                entry = entry_int(frame, tk_var)
                entry.grid(column=1, row=row, sticky='nw')
                self._update_handlers.append(partial(_update_number, tk_var, section_data.handler))
                entry.bind("<Return>", lambda e: e.widget.tk_focusNext().focus())
                entry.bind("<FocusIn>", lambda e: self.pane.see(e.widget))
                row += 1

    def save(self, *_):
        for handler in self._update_handlers:
            handler()

def _update_number(tk_var: tk.StringVar, handler, *_):
    if validate_int(tk_var.get(),"Invalid Int","number of students must be a valid number"):
        handler(int(tk_var.get()))
