"""Dialog box to edit a 'section' object"""
from __future__ import annotations

from tkinter import *
from tkinter.messagebox import  showerror
from tkinter.simpledialog import Dialog
from typing import Callable, Literal, TYPE_CHECKING

from schedule.gui_dialogs.utilities import set_style, entry_float, entry_int, validate_float, validate_int, \
    validate_class_times_equals_course_time, refresh_gui_blocks
from schedule.gui_generics.add_remove_tk import AddRemoveTk
if TYPE_CHECKING:
    from schedule.model import Lab, Teacher



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
                 apply_changes: Callable[[str, str, float, int, list, list, list], None]):

        set_style(frame)

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

        dialog_title = "Edit Course" if self.edit_or_add == "edit" else "Add Course"
        super().__init__(frame.winfo_toplevel(), dialog_title)


    # ================================================================================================================
    # The content of the main body of the dialog box
    # ================================================================================================================
    def body(self, frame:Frame):

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
        en_course_name = entry_float(course_hours_frame, textvariable=self.course_hours_tk)
        en_course_name.pack(side='left', padx=10, pady=5)


        # ------------------------------------------------------------------------------------------------------------
        # Sections/Blocks
        # ------------------------------------------------------------------------------------------------------------
        section_info_frame = Frame(frame)
        Label(section_info_frame, text="Number of Sections", anchor='e', width=20).pack(side='left', padx=10, pady=5)
        description = entry_int(section_info_frame, textvariable=self.num_sections_tk)
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
        AddRemoveTk(teacher_assignments_frame, self._non_assigned_teachers, self._assigned_teachers,
                    "Assign Teacher to all Classes", "Remove Teacher from all Classes",height=6)

        lab_assignments_frame = Frame(frame)
        AddRemoveTk(lab_assignments_frame, self._non_assigned_labs, self._assigned_labs,
                     "Assign Lab to all Classes","Remove Lab from all Classes", height=6)

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
        refresh_gui_blocks(self)
        Button(self.block_frames, text="Add New Class Time", command=self.add_new_block).pack(expand=1, fill='y')

    # ================================================================================================================
    # validate before applying
    # ================================================================================================================

    def validate(self):
        if self.edit_or_add == 'add':
            if self.course_number_tk.get() in self.existing_course_numbers:
                showerror("Course Number",f"Course number '{self.course_number_tk.get()}' already exists")
                return False
        if not validate_float(self.course_hours_tk.get(),"Course hours", "The number of hours per week must be a valid float!"):
            return False

        if not validate_int(self.num_sections_tk.get(),"Number of Sections", "The number of sections must be an integer!"):
            return False

        if not validate_class_times_equals_course_time(self.row_data, float(self.course_hours_tk.get())):
            return False

        return True

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

