"""Dialog box to edit a 'section' object"""
from __future__ import annotations
import re

from tkinter import *
from tkinter.messagebox import askyesno, showerror
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


class EditCourseDialogTk(Dialog):
    def __init__(self, frame:Frame,
                 edit_or_add: Literal['edit','add'],
                 existing_course_numbers: list = None,
                 *,
                 course_number:str = "",
                 course_name: str = "",
                 course_hours: float = 3.0,
                 num_sections: int = 1,
                 assigned_teachers: list[Teacher] = None,
                 non_assigned_teachers: list[Teacher],
                 assigned_labs: list[Lab] = None,
                 non_assigned_labs: list[Lab],
                 current_blocks: list[tuple[str,str,str]] = None,
                 apply_changes: Callable[[str, str, int, int, list, list, list], None]):

        self.top_frame = frame
        self.edit_or_add = edit_or_add
        self.existing_course_numbers = [] if existing_course_numbers is None else existing_course_numbers
        self.course_number_tk = StringVar(value = course_number)
        self.course_name_tk = StringVar(value = course_name)
        self.course_hours_tk = StringVar(value=str(course_hours))
        self.num_sections_tk = StringVar(value = str(num_sections))
        self._assigned_teachers = assigned_teachers if assigned_teachers is not None else []
        self._non_assigned_teachers = non_assigned_teachers
        self._assigned_labs = assigned_labs  if assigned_labs is not None else []
        self._non_assigned_labs = non_assigned_labs
        self.current_blocks = current_blocks if current_blocks is not None else []
        self._apply_changes = apply_changes


        self.row_data = []
        self.block_frames = None
        self.course_name = course_name

        self._get_non_assigned_teachers = lambda : self._non_assigned_teachers
        self._get_assigned_teachers = lambda : self._assigned_teachers

        self._get_non_assigned_labs = lambda : self._non_assigned_labs
        self._get_assigned_labs = lambda : self._assigned_labs


        self.style = ttk.Style(frame.winfo_toplevel())
        self.style.configure("MyCustom.TCombobox",
                        fieldbackground='black',  # Background of the input field
                        background='black',  # Overall widget background
                        foreground='white',  # Text color in the input field
                        arrowcolor='white',  # Dropdown arrow color
                        )

        dialog_title = "Edit Course" if self.edit_or_add == "edit" else "Add Course"
        super().__init__(frame.winfo_toplevel(), dialog_title)

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
    # Number validation
    # ================================================================================================================
    def _is_float(self, number:str , _:str) -> bool:
        if number == "" or number == ".":
            return True
        try:
            float(number)
            return True
        except ValueError:
            self.top_frame.winfo_toplevel().bell()
            return False

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
    def body(self, frame:Frame):

        tk_validate_is_number = self.top_frame.register(self._is_int)
        tk_validate_is_float = self.top_frame.register(self._is_float)

        # ------------------------------------------------------------------------------------------------------------
        # Course
        # ------------------------------------------------------------------------------------------------------------
        course_info_frame = Frame(frame)
        course_number_frame = Frame(course_info_frame)
        course_number_frame.pack()
        Label(course_number_frame, text="Course number", anchor='e', width=20).pack(side='left', padx=10, pady=5)
        en_course_number = Entry(course_number_frame, textvariable=self.course_number_tk,)
        en_course_number.pack(side='left', padx=10, pady=5)
        if self.edit_or_add == 'edit':
            en_course_number.config(state='readonly')

        course_name_frame = Frame(course_info_frame)
        course_name_frame.pack()
        Label(course_name_frame, text="Course name", anchor='e', width=20).pack(side='left', padx=10, pady=5)
        en_course_name = Entry(course_name_frame, textvariable=self.course_name_tk,)
        en_course_name.pack(side='left', padx=10, pady=5)

        course_hours_frame = Frame(course_info_frame)
        course_hours_frame.pack()
        Label(course_hours_frame, text="Hours per week", anchor='e', width=20).pack(side='left', padx=10, pady=5)
        en_course_name = Entry(course_hours_frame, textvariable=self.course_hours_tk,
                               validate='key', validatecommand=(tk_validate_is_float,'%P', '%s'))
        en_course_name.pack(side='left', padx=10, pady=5)


        # ------------------------------------------------------------------------------------------------------------
        # Sections/Blocks
        # ------------------------------------------------------------------------------------------------------------
        section_info_frame = Frame(frame)
        Label(section_info_frame, text="Number of Sections", anchor='e', width=20).pack(side='left', padx=10, pady=5)
        description = Entry(section_info_frame, textvariable=self.num_sections_tk,
                            validate='key', validatecommand=(tk_validate_is_number,'%P', '%s'))
        description.pack(side='left', padx=10, pady=5)

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

        # ------------------------------------------------------------------------------------------------------------
        # layout
        # ------------------------------------------------------------------------------------------------------------
        course_info_frame.grid(row=0, column=0)
        section_info_frame.grid(row=1, column = 0)
        self.block_frames.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        teacher_assignments_frame.grid(row=3,column=0, sticky='nsew', padx=5, pady=5)
        lab_assignments_frame.grid(row=4,column=0, sticky='nsew', padx=5, pady=5)

        self.refresh()

        return description

    def add_new_block(self):
        self.row_data.append((StringVar(value="Monday"),StringVar(value="8:00"), StringVar(value="1.5")))
        self.refresh()

    def refresh(self):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        start_times = []
        for h in range(7, 24):
            for m in (0, 15, 30, 45):
                start_times.append(f"{h:2d}:{m:02d}")
        durations = [f"{x/2:4.1f} hrs" for x in range(1,13)]

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
            om_time = ttk.Combobox(row_frame,textvariable=opt_hour, state="readonly", values=start_times, style="MyCustom.TCombobox")
            om_duration = ttk.Combobox(row_frame,textvariable=opt_duration, state="readonly", values=durations, style="MyCustom.TCombobox")

            om_day.config(width=8)
            om_time.config(width=5)
            om_duration.config(width=8)

            om_day.pack(side='left', pady=0)
            om_time.pack(side='left', pady=0)
            om_duration.pack(side='left', pady=0)
            btn_delete.pack(side='left', pady=0)

        # ------------------------------------------------------------------------------------------------------------
        # Add
        # ------------------------------------------------------------------------------------------------------------
        Button(self.block_frames, text="Add New Class Time", command=self.add_new_block).pack(expand=1, fill='y')

    # ================================================================================================================
    # validate before applying
    # ================================================================================================================

    def validate(self):
        if self.edit_or_add == 'add':
            if self.course_number_tk.get() in self.existing_course_numbers:
                showerror("Course Number",f"Course number '{self.course_number_tk.get()}' already exists")
                return False
        try:
            float(self.course_hours_tk.get())
        except ValueError:
            showerror("Course hours", "The number of hours per week must be a valid float!")
            return False

        try:
            int(self.num_sections_tk.get())
        except ValueError:
            showerror("Number of Sections", "The number of sections must be an integer!")
            return False

        total = 0.0
        for block_info in self.row_data:
            duration=float(block_info[2].get().strip().split(" ")[0])
            if duration < 0:
                duration += 24
            total += duration

        if total == float(self.course_hours_tk.get()) or total == 0.0:
            return True

        else:
            return askyesno("Class Times",f"Total allocated class times ({total})\n"
                                   f"does not equal course time ({self.course_hours_tk.get()})"
                                   f"\n\nDo you wish to continue?")

    # ================================================================================================================
    # apply changes
    # ================================================================================================================
    def apply(self):
        new_blocks=[]
        for i,b in enumerate(self.row_data):
            d = [x.get() for x in b]
            d[2] = float(d[2].strip().split(" ")[0])
            new_blocks.append(tuple(d))
        self._apply_changes(self.course_number_tk.get(), self.course_name_tk.get(),
                            float(self.course_hours_tk.get()),
                            int(self.num_sections_tk.get()), self._assigned_teachers,
                    self._assigned_labs, new_blocks)

