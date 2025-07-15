"""Dialog box to edit a 'block' object"""
from __future__ import annotations

import tkinter
from tkinter import *
from tkinter.messagebox import showerror
from tkinter.simpledialog import Dialog
from typing import Callable, Literal

from schedule.gui_generics.add_remove_tk import AddRemoveTk


class AddEditBlockDialogTk(Dialog):
    def __init__(self, frame:Frame,
                 add_edit_type: Literal['add', 'edit'],
                 duration: float,
                 assigned_teachers: list,
                 non_assigned_teachers: list,
                 assigned_labs: list,
                 non_assigned_labs: list,
                 apply_changes: Callable[[int,float,list,list], None]):

        self.add_edit_type = add_edit_type
        self.old_duration = duration
        self.top_frame = frame
        self._assigned_teachers = assigned_teachers
        self._assigned_labs = assigned_labs
        self._non_assigned_teachers = non_assigned_teachers
        self._non_assigned_labs = non_assigned_labs
        self._apply_changes = apply_changes

        self._get_non_assigned_teachers = lambda : self._non_assigned_teachers
        self._get_assigned_teachers = lambda : self._assigned_teachers

        self._get_non_assigned_labs = lambda : self._non_assigned_labs
        self._get_assigned_labs = lambda : self._assigned_labs

        self.tk_duration = tkinter.StringVar(value=str(duration))
        self.tk_new_blocks = tkinter.StringVar(value="1")
        if add_edit_type == 'edit':
            self.tk_new_blocks.set("0")

        title = "Edit Class Time(s)" if add_edit_type == 'edit' else "Add Class"
        super().__init__(frame.winfo_toplevel(), title)

    def _add_teacher(self, obj):
        self._assigned_teachers.append(obj)
        self._assigned_teachers.sort()
        self._non_assigned_teachers.remove(obj)

    def _remove_teacher(self, obj):
        self._non_assigned_teachers.append(obj)
        self._non_assigned_teachers.sort()
        self._assigned_teachers.remove(obj)

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
        tk_validate_is_number = self.top_frame.register(self._validate_is_number)

        # ------------------------------------------------------------------------------------------------------------
        # for adding blocks only
        # ------------------------------------------------------------------------------------------------------------
        number_of_blocks_frame = Frame(frame)
        if self.add_edit_type == 'add':
            Label(number_of_blocks_frame, text="Number of Classes:", anchor='e', width=20).pack(side='left', padx=10, pady=5)
            duration_entry = Entry(number_of_blocks_frame,
                                   textvariable=self.tk_new_blocks,
                                   validate='key',
                                   validatecommand=(tk_validate_is_number, '%P', '%s')
                                   )
            duration_entry.pack(side='left', padx=10, pady=5)

        # ------------------------------------------------------------------------------------------------------------
        # duration
        # ------------------------------------------------------------------------------------------------------------
        entry_frame = Frame(frame)
        Label(entry_frame, text="Duration:", anchor='e', width=20).pack(side='left',padx=10,pady=5)
        duration_entry = Entry(entry_frame,
                               textvariable=self.tk_duration,
                               validate='key',
                               validatecommand=(tk_validate_is_number, '%P', '%s'))
        duration_entry.pack(side='left',padx=10, pady=5)


        # ------------------------------------------------------------------------------------------------------------
        # Teacher/Lab Add/Remove
        # ------------------------------------------------------------------------------------------------------------
        teacher_assignments_frame = Frame(frame)
        AddRemoveTk(teacher_assignments_frame, self._get_non_assigned_teachers, self._get_assigned_teachers,
                    self._add_teacher, self._remove_teacher, "Assign Teacher to Class",
                                        "Remove Teacher from Class")

        lab_assignments_frame = Frame(frame)
        AddRemoveTk(lab_assignments_frame, self._get_non_assigned_labs, self._get_assigned_labs,
                    self._add_lab, self._remove_lab, "Assign Lab to Class",
                                        "Remove Lab from Class")


        # ------------------------------------------------------------------------------------------------------------
        # layout
        # ------------------------------------------------------------------------------------------------------------
        number_of_blocks_frame.grid(row=0, column=0)
        entry_frame.grid(row=1, column = 0)
        teacher_assignments_frame.grid(row=2,column=0, sticky='nsew', padx=5, pady=5)
        lab_assignments_frame.grid(row=3,column=0, sticky='nsew', padx=5, pady=5)

        return duration_entry

    # ================================================================================================================
    # validate before applying
    # ================================================================================================================
    def validate(self):
        try:
            float(self.tk_duration.get())
        except ValueError:
            showerror("Class Duration", "Duration of class must be a valid float!")
            return False
        try:
            int(float(self.tk_new_blocks.get()))
        except ValueError:
            showerror("Number of Classes", "Number of classes must be a valid int!")
            return False
        return True

    # ================================================================================================================
    # apply changes
    # ================================================================================================================
    def apply(self):
        duration = float(self.tk_duration.get())
        number_new_blocks = int(float(self.tk_new_blocks.get()))
        self._apply_changes(number_new_blocks, duration, self._assigned_teachers, self._assigned_labs )

    # ================================================================================================================
    # Number validation
    # ================================================================================================================
    def _validate_is_number(self, number:str , _:str) -> bool:
        if number == "" or number == ".":
            return True
        try:
            float(number)
            return True
        except ValueError:
            self.top_frame.winfo_toplevel().bell()
            return False


