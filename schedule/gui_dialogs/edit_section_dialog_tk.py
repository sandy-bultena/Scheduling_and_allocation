"""Dialog box to edit a 'section' object"""
from __future__ import annotations
import re

from tkinter import *
import tkinter.font as tkFont
from tkinter import ttk
from tkinter.simpledialog import Dialog
from typing import Callable, TYPE_CHECKING

from schedule.gui_dialogs.utilities import validate_class_times_equals_course_time, get_block_info_from_row_data, \
    refresh_gui_blocks
from schedule.gui_generics.add_remove_tk import AddRemoveTk
if TYPE_CHECKING:
    from schedule.model import Stream, Lab, Teacher


def time_to_hours(string_time:str) -> float:
    string_time = string_time.strip()

    if not re.match(r"^[12]?\d:\d{2}$", string_time):
        string_time = 8
    hour, minute = (int(x) for x in string_time.split(":"))
    hours = hour + minute / 60
    return hours


class EditSectionDialogTk(Dialog):
    def __init__(self, frame:Frame,
                 *,
                 course_description: str,
                 section_description: str = "",
                 assigned_teachers: list[Teacher] = None,
                 non_assigned_teachers: list[Teacher],
                 assigned_labs: list[Lab] = None,
                 non_assigned_labs: list[Lab],
                 assigned_streams: list[Stream] = None,
                 non_assigned_streams: list[Stream],
                 current_blocks: list[tuple[str,str,str]] = None,
                 course_hours: float,

                 apply_changes: Callable[[str, list, list, list, list], None]):

        self.row_data = []
        self.course_hours = course_hours
        self.current_blocks = current_blocks if current_blocks is not None else []
        self.block_frames = None
        self.course_description = course_description
        self.top_frame = frame
        self._assigned_teachers = assigned_teachers if assigned_teachers is not None else []
        self._assigned_labs = assigned_labs  if assigned_labs is not None else []
        self._assigned_streams = assigned_streams  if assigned_streams is not None else []
        self._non_assigned_teachers = non_assigned_teachers
        self._non_assigned_labs = non_assigned_labs
        self._non_assigned_streams = non_assigned_streams
        self._apply_changes = apply_changes

        self.description = StringVar(value = section_description)

        self.style = ttk.Style(frame.winfo_toplevel())
        self.style.configure("MyCustom.TCombobox",
                        fieldbackground='black',  # Background of the input field
                        background='black',  # Overall widget background
                        foreground='white',  # Text color in the input field
                        arrowcolor='white',  # Dropdown arrow color
                        )

        dialog_title = "Edit Section"
        super().__init__(frame.winfo_toplevel(), dialog_title)

    # ================================================================================================================
    # The content of the main body of the dialog box
    # ================================================================================================================
    def body(self, frame:Frame):

        # ------------------------------------------------------------------------------------------------------------
        # Info
        # ------------------------------------------------------------------------------------------------------------
        course_info_frame = Frame(frame)
        section_info_frame = Frame(frame)
        lbl = Label(course_info_frame,text=self.course_description, anchor='center',width=20)
        lbl.pack(expand=1,fill='both',padx=15,pady=5)
        default_font = tkFont.nametofont(lbl.cget("font"))
        family = default_font["family"]
        size = default_font["size"] + 2
        lbl.config(font=(family, size))
        Label(section_info_frame, text="Section Description", anchor='e', width=20).pack(side='left', padx=10, pady=5)
        description = Entry(section_info_frame, textvariable=self.description,)
        description.pack(side='left', padx=10, pady=5)

        # ------------------------------------------------------------------------------------------------------------
        # Blocks
        # ------------------------------------------------------------------------------------------------------------
        self.block_frames = Frame(frame)
        for index, block_info in enumerate(self.current_blocks):
            opt_day = StringVar(value=block_info[0])
            opt_hour = StringVar(value=block_info[1])
            opt_duration = StringVar(value=block_info[2])
            self.row_data.append((opt_day, opt_hour, opt_duration))


        # ------------------------------------------------------------------------------------------------------------
        # Teacher/Lab/Stream Add/Remove
        # ------------------------------------------------------------------------------------------------------------
        teacher_assignments_frame = Frame(frame)
        AddRemoveTk(teacher_assignments_frame, self._non_assigned_teachers, self._assigned_teachers,
                    "Assign Teacher to all Classes", "Remove Teacher from all Classes",height=6)

        lab_assignments_frame = Frame(frame)
        AddRemoveTk(lab_assignments_frame, self._non_assigned_labs, self._assigned_labs,
                    "Assign Lab to all Classes","Remove Lab from all Classes", height=6)

        stream_assignments_frame = Frame(frame)
        AddRemoveTk(stream_assignments_frame, self._non_assigned_streams, self._assigned_streams,
                     "Assign Stream to Section","Remove Stream from Section", height=6)

        # ------------------------------------------------------------------------------------------------------------
        # layout
        # ------------------------------------------------------------------------------------------------------------
        course_info_frame.grid(row=0, column=0)
        section_info_frame.grid(row=1, column = 0)
        self.block_frames.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        teacher_assignments_frame.grid(row=3,column=0, sticky='nsew', padx=5, pady=5)
        lab_assignments_frame.grid(row=4,column=0, sticky='nsew', padx=5, pady=5)
        stream_assignments_frame.grid(row=5,column=0, sticky='nsew', padx=5, pady=5)

        self.refresh_blocks()

        return description

    def add_new_block(self):
        self.row_data.append((StringVar(value="Monday"),StringVar(value="8:00"), StringVar(value="1.5")))
        self.refresh_blocks()

    def refresh_blocks(self):
        refresh_gui_blocks(self)
        Button(self.block_frames, text="Add New Class Time", command=self.add_new_block).pack(expand=1, fill='y')

    # ================================================================================================================
    # are blocks set up properly?
    # ================================================================================================================

    def validate(self):
        if not validate_class_times_equals_course_time(self.row_data, float(self.course_hours)):
            return False
        return True

    # ================================================================================================================
    # apply changes
    # ================================================================================================================
    def apply(self):
        new_blocks=get_block_info_from_row_data(self.row_data)
        self._apply_changes( self.description.get(), self._assigned_teachers, self._assigned_labs, self._assigned_streams, new_blocks )


