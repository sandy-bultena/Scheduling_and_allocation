"""Dialog box to edit a 'block' object"""
from __future__ import annotations

import tkinter
from tkinter import *
from tkinter.simpledialog import Dialog
from typing import Callable

from schedule.gui_generics.add_remove_tk import AddRemove


class EditBlockDialogTk(Dialog):
    def __init__(self, frame:Frame,
                 duration: float,
                 assigned_teachers: list,
                 non_assigned_teachers: list,
                 assigned_labs: list,
                 non_assigned_labs: list,
                 apply_changes: Callable[[float,list,list], None]):

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

        self.tk_duration = tkinter.StringVar()
        self.tk_duration.set(str(duration))

        super().__init__(frame.winfo_toplevel(), "Edit Block")

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

        # ------------------------------------------------------------------------------------------------------------
        # duration
        # ------------------------------------------------------------------------------------------------------------
        tk_validate_is_number = self.top_frame.register(self._validate_is_number)

        entry_frame = Frame(frame)
        Label(entry_frame, text="Block Duration:", anchor='e', width=20).pack(side='left',padx=10,pady=5)
        duration_entry = Entry(entry_frame,
                               textvariable=self.tk_duration,
                               validate='key',
                               validatecommand=(tk_validate_is_number, '%P', '%s'))
        duration_entry.pack(side='left',padx=10, pady=5)


        # ------------------------------------------------------------------------------------------------------------
        # Teacher/Lab Add/Remove
        # ------------------------------------------------------------------------------------------------------------
        teacher_assignments_frame = Frame(frame)
        AddRemove(teacher_assignments_frame, self._get_non_assigned_teachers, self._get_assigned_teachers,
                  self._add_teacher, self._remove_teacher, "Assign Teacher to Block",
                                        "Remove Teacher from Block")

        lab_assignments_frame = Frame(frame)
        AddRemove(lab_assignments_frame, self._get_non_assigned_labs, self._get_assigned_labs,
                  self._add_lab, self._remove_lab, "Assign Lab to Block",
                                        "Remove Lab from Block")


        # ------------------------------------------------------------------------------------------------------------
        # layout
        # ------------------------------------------------------------------------------------------------------------
        entry_frame.grid(row=0, column = 0)
        teacher_assignments_frame.grid(row=1,column=0, sticky='nsew', padx=5, pady=5)
        lab_assignments_frame.grid(row=2,column=0, sticky='nsew', padx=5, pady=5)

        return duration_entry

    # ================================================================================================================
    # apply changes
    # ================================================================================================================
    def apply(self):
        try:
            duration = float(self.tk_duration.get())
        except ValueError:
            duration = self.old_duration
        self._apply_changes(duration, self._assigned_teachers, self._assigned_labs )

    # ================================================================================================================
    # Number validation
    # ================================================================================================================
    def _validate_is_number(self, number:str ,_:str) -> bool:
        if number == "" or number == ".":
            return True
        try:
            float(number)
            return True
        except ValueError:
            self.top_frame.winfo_toplevel().bell()
            return False


class Dialog(Toplevel):

    '''Class to open dialogs.

    This class is intended as a base class for custom dialogs
    '''

    def __init__(self, parent, title = None):
        '''Initialize a dialog.

        Arguments:

            parent -- a parent window (the application window)

            title -- the dialog title
        '''
        master = parent
        if master is None:
            master = _get_temp_root()

        print(f"calling Toplevel {master=}")
        Toplevel.__init__(self, master)

        self.withdraw() # remain invisible for now
        # If the parent is not viewable, don't
        # make the child transient, or else it
        # would be opened withdrawn
        if parent is not None and parent.winfo_viewable():
            self.transient(parent)

        if title:
            self.title(title)

        _setup_dialog(self)

        self.parent = parent

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        if self.initial_focus is None:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        _place_window(self, parent)

        self.initial_focus.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    def destroy(self):
        '''Destroy the window'''
        self.initial_focus = None
        Toplevel.destroy(self)
        _destroy_temp_root(self.master)

    #
    # construction hooks

    def body(self, master):
        '''create dialog body.

        return widget that should have initial focus.
        This method should be overridden, and is called
        by the __init__ method.
        '''
        pass

    def buttonbox(self):
        '''add standard button box.

        override if you do not want the standard buttons
        '''

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        try:
            self.apply()
        finally:
            self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        if self.parent is not None:
            self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):
        '''validate the data

        This method is called automatically to validate the data before the
        dialog is destroyed. By default, it always validates OK.
        '''

        return 1 # override

    def apply(self):
        '''process the data

        This method is called automatically to process the data, *after*
        the dialog is destroyed. By default, it does nothing.
        '''

        pass # override
