"""Dialog box to edit a 'section' object"""
from __future__ import annotations

from dataclasses import dataclass
from tkinter import *
from tkinter.simpledialog import Dialog, askfloat
from typing import Callable, Literal

from schedule.Tk import Scrolled
from schedule.gui_generics.add_remove_tk import AddRemoveTk
from schedule.model import Block, Stream, Lab, Teacher

class AddEditSectionDialogTk(Dialog):
    def __init__(self, frame:Frame,
                 add_edit_type: Literal['add', 'edit'],
                 section_description: str,
                 assigned_teachers: list[Teacher],
                 non_assigned_teachers: list[Teacher],
                 assigned_labs: list[Lab],
                 non_assigned_labs: list[Lab],
                 assigned_streams: list[Stream],
                 non_assigned_streams: list[Stream],

                 apply_changes: Callable[[list, list, list], None]):

        self.add_edit_type = add_edit_type
        self.top_frame = frame
        self._assigned_teachers = assigned_teachers
        self._assigned_labs = assigned_labs
        self._assigned_streams = assigned_streams
        self._non_assigned_teachers = non_assigned_teachers
        self._non_assigned_labs = non_assigned_labs
        self._non_assigned_streams = non_assigned_streams
        self._apply_changes = apply_changes

        self._get_non_assigned_teachers = lambda : self._non_assigned_teachers
        self._get_assigned_teachers = lambda : self._assigned_teachers

        self._get_non_assigned_streams = lambda : self._non_assigned_streams
        self._get_assigned_streams = lambda : self._assigned_streams

        self._get_non_assigned_labs = lambda : self._non_assigned_labs
        self._get_assigned_labs = lambda : self._assigned_labs

        self.description = StringVar(value = section_description)

        super().__init__(frame.winfo_toplevel(), "Edit Section")

    def _add_teacher(self, obj):
        self._assigned_teachers.append(obj)
        self._assigned_teachers.sort()
        self._non_assigned_teachers.remove(obj)

    def _remove_teacher(self, obj):
        self._non_assigned_teachers.append(obj)
        self._non_assigned_teachers.sort()
        self._assigned_teachers.remove(obj)

    def _add_stream(self, obj):
        self._assigned_streams.append(obj)
        self._assigned_streams.sort()
        self._non_assigned_streams.remove(obj)

    def _remove_stream(self, obj):
        self._non_assigned_streams.append(obj)
        self._non_assigned_streams.sort()
        self._assigned_streams.remove(obj)

    def _add_lab(self, obj):
        self._assigned_labs.append(obj)
        self._assigned_labs.sort()
        self._non_assigned_labs.remove(obj)

    def _remove_lab(self, obj):
        self._non_assigned_labs.append(obj)
        self._non_assigned_labs.sort()
        self._assigned_labs.remove(obj)

    # ================================================================================================================
    # The content of the main body of the dialog box
    # ================================================================================================================
    def body(self, frame:Frame):

        # ------------------------------------------------------------------------------------------------------------
        # Section
        # ------------------------------------------------------------------------------------------------------------
        title_frame = Frame(frame)
        Label(title_frame, text="Section Description", anchor='e', width=20).pack(side='left', padx=10, pady=5)
        description = Entry(title_frame, textvariable=self.description,)
        description.pack(side='left', padx=10, pady=5)

        # ------------------------------------------------------------------------------------------------------------
        # Teacher/Lab/Stream Add/Remove
        # ------------------------------------------------------------------------------------------------------------
        teacher_assignments_frame = Frame(frame)
        AddRemoveTk(teacher_assignments_frame, self._get_non_assigned_teachers, self._get_assigned_teachers,
                    self._add_teacher, self._remove_teacher, "Assign Teacher to all Blocks",
                                        "Remove Teacher from all Blocks")

        lab_assignments_frame = Frame(frame)
        AddRemoveTk(lab_assignments_frame, self._get_non_assigned_labs, self._get_assigned_labs,
                    self._add_lab, self._remove_lab, "Assign Lab to all Blocks",
                                        "Remove Lab from all Blocks")

        stream_assignments_frame = Frame(frame)
        AddRemoveTk(stream_assignments_frame, self._get_non_assigned_streams, self._get_assigned_streams,
                    self._add_stream, self._remove_stream, "Assign Stream to Section",
                                        "Remove Stream from Section")

        # ------------------------------------------------------------------------------------------------------------
        # layout
        # ------------------------------------------------------------------------------------------------------------
        title_frame.grid(row=0, column=0)
        teacher_assignments_frame.grid(row=1,column=0, sticky='nsew', padx=5, pady=5)
        lab_assignments_frame.grid(row=2,column=0, sticky='nsew', padx=5, pady=5)
        stream_assignments_frame.grid(row=3,column=0, sticky='nsew', padx=5, pady=5)

        return description

    # ================================================================================================================
    # apply changes
    # ================================================================================================================
    def apply(self):
        self._apply_changes( self._assigned_teachers, self._assigned_labs, self._assigned_streams )


