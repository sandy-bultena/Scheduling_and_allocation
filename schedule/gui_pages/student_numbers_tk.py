import tkinter as tk
from functools import partial
from typing import Generator

from schedule.Tk.Scrolled import Scrolled
from schedule.model import SemesterType
from schedule.presenter.student_numbers import StudentData, CourseData, SectionData
from schedule.gui_generics.number_validations import validate_int, entry_int


class StudentNumbersTk:
    # ============================================================================================
    # constructor
    # ============================================================================================
    def __init__(self, frame, data: dict[SemesterType, dict[CourseData, list[SectionData]]] = None):
        """creates the Panes for each semester"""

        panes: dict[SemesterType, Scrolled] = dict()
        self.frame = frame
        self.data = data

        # make as many panes as required
        for col, semester in enumerate( (s for s in SemesterType if len(data.get(s, {})) != 0)):
            frame.columnconfigure(col, weight=1)

            f = Scrolled(
                self.frame,
                "Frame",
                scrollbars='e',
                border=5,
                relief='flat',
            )
            f.grid(column=col, row=0, sticky="nsew")
            panes[semester] = f

        frame.rowconfigure(0, weight=1)
        self.panes: dict[SemesterType, Scrolled] = panes

        # ----------------------------------------------------------------------------------------
        # put data into widget
        # ----------------------------------------------------------------------------------------
        self.refresh()

    def _active_semesters(self) -> Generator:
        return (s for s in SemesterType if len(self.data.get(s,{})) != 0)

    def refresh(self):

        for col, semester in enumerate(self._active_semesters()):
            pane = self.panes.get(semester, None)
            if pane is None:
                continue

            frame = pane.widget
            frame.columnconfigure(1, weight=2)
            frame.columnconfigure(0, weight=1)

            for w in frame.winfo_children():
                w.destroy()

            tk.Label(frame,
                     text=semester.name,
                     anchor='center',
                     ).grid(column=0, row=0, columnspan=2, sticky='nsew')

            for row,course in enumerate(self.data[semester].keys(), start=1):
                tk.Label(frame,
                         text=course.name,
                         anchor='w',
                         width=40
                         ).grid(column=0, row=row, columnspan=2, sticky='nsew')

                for section in self.data[semester][course]:
                    tk.Label(frame,
                             width=4,
                             text=section.name,
                             anchor='e',
                             ).grid(column=0, row=row, sticky='nsew')
                    tk_var = tk.StringVar(value=section.number_of_students)
                    entry = entry_int(frame, tk_var)
                    entry.grid(column=1, row=row, sticky='nw')
                    entry.bind("<Leave>", partial(_update_number, tk_var, section.handler))
                    entry.bind("<Return>", lambda e: e.widget.tk_focusNext().focus())
                    entry.bind("<FocusIn>", lambda e: self.panes[semester].see(e.widget))

def _update_number(tk_var: tk.StringVar, handler, *_):
    if validate_int(tk_var.get()):
        handler(int(tk_var.get()))
