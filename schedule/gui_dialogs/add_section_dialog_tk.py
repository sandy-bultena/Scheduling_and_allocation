"""Dialog box to edit a 'section' object"""
from __future__ import annotations
import re

import tkinter as tk
import tkinter.font as tkFont
from tkinter.simpledialog import Dialog
from typing import Callable

from schedule.gui_generics.number_validations import validate_int
from schedule.gui_dialogs.dialog_utilities import set_style, validate_class_times_equals_course_time, \
    get_block_info_from_row_data, refresh_gui_blocks


def time_to_hours(string_time:str) -> float:
    string_time = string_time.strip()

    if not re.match(r"^[12]?\d:\d{2}$", string_time):
        string_time = 8
    hour, minute = (int(x) for x in string_time.split(":"))
    hours = hour + minute / 60
    return hours


class AddSectionDialogTk(Dialog):
    def __init__(self, frame:tk.Frame,
                 *,
                 course_description: str,
                 course_hours: float,
                 apply_changes: Callable[[int, list], None]):

        self.row_data = []
        self.course_hours = course_hours
        self.current_blocks =  []
        self.block_frames = None
        self.course_description = course_description
        self.top_frame = frame
        self._apply_changes = apply_changes

        self.description = tk.StringVar(value = "")
        self.number_of_sections = tk.StringVar(value="1")

        set_style(frame)
        dialog_title = "Add Section(s)"
        super().__init__(frame.winfo_toplevel(), dialog_title)

    def _is_int(self, number: str, *_) -> bool:
        if number == "":
            return True
        try:
            int(number)
            return True
        except ValueError:
            self.top_frame.winfo_toplevel().bell()
            return False

    # ================================================================================================================
    # The content of the main body of the dialog box
    # ================================================================================================================
    def body(self, frame:tk.Frame):
        tk_validate_is_number = self.top_frame.register(self._is_int)

        # ------------------------------------------------------------------------------------------------------------
        # Info
        # ------------------------------------------------------------------------------------------------------------
        course_info_frame = tk.Frame(frame)
        section_info_frame = tk.Frame(frame)
        lbl = tk.Label(course_info_frame,text=self.course_description, anchor='center',width=20)
        lbl.pack(expand=1,fill='both',padx=15,pady=5)
        default_font = tkFont.nametofont(lbl.cget("font"))
        family = default_font["family"]
        size = default_font["size"] + 2
        lbl.config(font=(family, size))

        tk.Label(section_info_frame, text="How many sections?", anchor='e', width=20).pack(side='left', padx=10, pady=5)
        en_number = tk.Entry(section_info_frame, textvariable=self.number_of_sections, validate='key',
                            validatecommand=(tk_validate_is_number, '%P', '%s'))
        en_number.pack(side='left', padx=10, pady=5)

        # ------------------------------------------------------------------------------------------------------------
        # Blocks
        # ------------------------------------------------------------------------------------------------------------
        self.block_frames = tk.Frame(frame)

        # ------------------------------------------------------------------------------------------------------------
        # layout
        # ------------------------------------------------------------------------------------------------------------
        course_info_frame.grid(row=0, column=0)
        section_info_frame.grid(row=1, column = 0)
        self.block_frames.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)

        self.refresh()

        return en_number

    # ================================================================================================================
    # refresh blocks
    # ================================================================================================================
    def add_new_block(self):
        self.row_data.append((tk.StringVar(value="Monday"),tk.StringVar(value="8.0"), tk.StringVar(value="1.5")))
        self.refresh()

    def refresh(self):
        refresh_gui_blocks(self)
        tk.Button(self.block_frames, text="Add New Class Time", command=self.add_new_block,padx=5).pack(expand=1, fill='y')


    # ================================================================================================================
    # are blocks set up properly?
    # ================================================================================================================

    def validate(self):
        if not validate_int(self.number_of_sections.get(),"Number of Sections", "Number of sections must be a number!"):
            return False

        if not validate_class_times_equals_course_time(self.row_data, float(self.course_hours)):
            return False

        return True

    # ================================================================================================================
    # apply changes
    # ================================================================================================================
    def apply(self):
        new_blocks=get_block_info_from_row_data(self.row_data)
        self._apply_changes( int(self.number_of_sections.get()), new_blocks )


