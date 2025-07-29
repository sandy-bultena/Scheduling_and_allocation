"""Dialog box to edit a 'block' object"""
from __future__ import annotations

import tkinter as tk

from tkinter.simpledialog import Dialog
from typing import Callable, Literal
from schedule.gui_dialogs.utilities import  entry_float, entry_int, validate_float, validate_int

from schedule.gui_generics.add_remove_tk import AddRemoveTk


class AddEditBlockDialogTk(Dialog):
    def __init__(self, frame:tk.Frame,
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

        self.tk_duration = tk.StringVar(value=str(duration))
        self.tk_new_blocks = tk.StringVar(value="1")
        if add_edit_type == 'edit':
            self.tk_new_blocks.set("0")

        title = "Edit Class Time(s)" if add_edit_type == 'edit' else "Add Class"
        super().__init__(frame.winfo_toplevel(), title)

    # ================================================================================================================
    # The content of the main body of the dialog box
    # ================================================================================================================
    def body(self, frame:tk.Frame):

        # ------------------------------------------------------------------------------------------------------------
        # for adding blocks only
        # ------------------------------------------------------------------------------------------------------------
        number_of_blocks_frame = tk.Frame(frame)
        if self.add_edit_type == 'add':
            tk.Label(number_of_blocks_frame, text="Number of Classes:", anchor='e', width=20).pack(side='left', padx=10, pady=5)
            duration_entry = entry_float(number_of_blocks_frame,textvariable=self.tk_new_blocks)
            duration_entry.pack(side='left', padx=10, pady=5)

        # ------------------------------------------------------------------------------------------------------------
        # duration
        # ------------------------------------------------------------------------------------------------------------
        entry_frame = tk.Frame(frame)
        tk.Label(entry_frame, text="Duration:", anchor='e', width=20).pack(side='left',padx=10,pady=5)
        duration_entry = entry_int(entry_frame, textvariable=self.tk_duration)
        duration_entry.pack(side='left',padx=10, pady=5)


        # ------------------------------------------------------------------------------------------------------------
        # Teacher/Lab Add/Remove
        # ------------------------------------------------------------------------------------------------------------
        teacher_assignments_frame = tk.Frame(frame)
        AddRemoveTk(teacher_assignments_frame, self._non_assigned_teachers, self._assigned_teachers,
                     "Assign Teacher to Class", "Remove Teacher from Class")

        lab_assignments_frame = tk.Frame(frame)
        AddRemoveTk(lab_assignments_frame, self._non_assigned_labs, self._assigned_labs,
                     "Assign Lab to Class","Remove Lab from Class")


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
        if not validate_float(self.tk_duration.get(), "Class Duration", "Duration of class must be a valid float!"):
            return False
        if not validate_int(self.tk_new_blocks.get(),"Number of Classes", "Number of classes must be a valid int!"):
            return False
        return True

    # ================================================================================================================
    # apply changes
    # ================================================================================================================
    def apply(self):
        duration = float(self.tk_duration.get())
        number_new_blocks = int(float(self.tk_new_blocks.get()))
        self._apply_changes(number_new_blocks, duration, self._assigned_teachers, self._assigned_labs )



