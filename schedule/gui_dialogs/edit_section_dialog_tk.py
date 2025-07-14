"""Dialog box to edit a 'section' object"""
from __future__ import annotations
import re

from tkinter import *
from tkinter.messagebox import askyesno
import tkinter.font as tkFont
from tkinter import ttk
from tkinter.simpledialog import Dialog
from typing import Callable, Literal, TYPE_CHECKING


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


class AddEditSectionDialogTk(Dialog):
    def __init__(self, frame:Frame,
                 add_edit_type: Literal['add', 'edit'],
                 *,
                 course_description: str,
                 section_description: str,
                 assigned_teachers: list[Teacher],
                 non_assigned_teachers: list[Teacher],
                 assigned_labs: list[Lab],
                 non_assigned_labs: list[Lab],
                 assigned_streams: list[Stream],
                 non_assigned_streams: list[Stream],
                 current_blocks: list[tuple[str,str,str]],
                 course_hours,

                 apply_changes: Callable[[list, list, list, list], None]):

        self.row_data = []
        self.course_hours = course_hours
        self.current_blocks = current_blocks
        self.block_frames = None
        self.add_edit_type = add_edit_type
        self.course_description = course_description
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

        self.style = ttk.Style(frame.winfo_toplevel())
        self.style.configure("MyCustom.TCombobox",
                        fieldbackground='black',  # Background of the input field
                        background='black',  # Overall widget background
                        foreground='white',  # Text color in the input field
                        arrowcolor='white',  # Dropdown arrow color
                        )

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
        AddRemoveTk(teacher_assignments_frame, self._get_non_assigned_teachers, self._get_assigned_teachers,
                    self._add_teacher, self._remove_teacher, "Assign Teacher to all Classes",
                                        "Remove Teacher from all Classes",height=6)

        lab_assignments_frame = Frame(frame)
        AddRemoveTk(lab_assignments_frame, self._get_non_assigned_labs, self._get_assigned_labs,
                    self._add_lab, self._remove_lab, "Assign Lab to all Classes",
                                        "Remove Lab from all Classes", height=6)

        stream_assignments_frame = Frame(frame)
        AddRemoveTk(stream_assignments_frame, self._get_non_assigned_streams, self._get_assigned_streams,
                    self._add_stream, self._remove_stream, "Assign Stream to Section",
                                        "Remove Stream from Section", height=6)

        # ------------------------------------------------------------------------------------------------------------
        # layout
        # ------------------------------------------------------------------------------------------------------------
        course_info_frame.grid(row=0, column=0)
        section_info_frame.grid(row=1, column = 0)
        self.block_frames.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        teacher_assignments_frame.grid(row=3,column=0, sticky='nsew', padx=5, pady=5)
        lab_assignments_frame.grid(row=4,column=0, sticky='nsew', padx=5, pady=5)
        stream_assignments_frame.grid(row=5,column=0, sticky='nsew', padx=5, pady=5)

        self.refresh()

        return description

    def add_new_block(self):
        self.row_data.append((StringVar(value="Monday"),StringVar(value="8:00"), StringVar(value="9:30")))
        self.refresh()

    def refresh(self):
        pass
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        times = []
        for h in range(7, 24):
            for m in (0, 15, 30, 45):
                times.append(f"{h:2d}:{m:02d}")

        # remove any pre-existing stuff
        for w in self.block_frames.winfo_children():
            w.destroy()

        row_frames = []
        for index, block_info in enumerate(self.row_data):

            def remove_block(i = index):
                self.row_data.pop(i)
                self.refresh()

            row_frame = Frame(self.block_frames)
            row_frames.append(row_frame)
            row_frame.pack(expand=1, fill='both', padx=10,pady=2)

            opt_day, opt_hour, opt_duration = block_info

            btn_delete = Button(row_frame, text="remove", command=remove_block)
            om_day = ttk.Combobox(row_frame,textvariable=opt_day, state="readonly", values=days, style="MyCustom.TCombobox")
            om_time = ttk.Combobox(row_frame,textvariable=opt_hour, state="readonly", values=times, style="MyCustom.TCombobox")
            om_end_time = ttk.Combobox(row_frame,textvariable=opt_duration, state="readonly", values=times, style="MyCustom.TCombobox")

            om_day.config(width=8)
            om_time.config(width=5)
            om_end_time.config(width=5)

            om_day.pack(side='left', pady=0)
            om_time.pack(side='left', pady=0)
            om_end_time.pack(side='left', pady=0)
            btn_delete.pack(side='left', pady=0)

        # ------------------------------------------------------------------------------------------------------------
        # Add
        # ------------------------------------------------------------------------------------------------------------
        Button(self.block_frames, text="Add New Class Time", command=self.add_new_block).pack(expand=1, fill='y')


    # ================================================================================================================
    # are blocks set up properly?
    # ================================================================================================================

    def validate(self):
        total = 0
        for block_info in self.row_data:
            duration=time_to_hours(block_info[2].get()) - time_to_hours(block_info[1].get())
            if duration < 0:
                duration += 24
            total += duration

        if total == self.course_hours or total == 0:
            return True

        else:
            return askyesno("Class Times",f"Total allocated class times ({total})\n"
                                   f"does not equal course time ({self.course_hours})"
                                   f"\n\nDo you wish to continue?")

    # ================================================================================================================
    # apply changes
    # ================================================================================================================
    def apply(self):
        new_blocks=[]
        for b in self.row_data:
            new_blocks.append(tuple(x.get() for x in b))
        self._apply_changes( self._assigned_teachers, self._assigned_labs, self._assigned_streams, new_blocks )


