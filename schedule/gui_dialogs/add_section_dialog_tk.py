"""Dialog box to edit a 'section' object"""
from __future__ import annotations
import re

from tkinter import *
from tkinter.messagebox import askyesno, showerror
import tkinter.font as tkFont
from tkinter import ttk
from tkinter.simpledialog import Dialog
from typing import Callable


def time_to_hours(string_time:str) -> float:
    string_time = string_time.strip()

    if not re.match(r"^[12]?\d:\d{2}$", string_time):
        string_time = 8
    hour, minute = (int(x) for x in string_time.split(":"))
    hours = hour + minute / 60
    return hours


class AddSectionDialogTk(Dialog):
    def __init__(self, frame:Frame,
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

        self.description = StringVar(value = "")
        self.number_of_sections = StringVar(value="1")

        self.style = ttk.Style(frame.winfo_toplevel())
        self.style.configure("MyCustom.TCombobox",
                        fieldbackground='black',  # Background of the input field
                        background='black',  # Overall widget background
                        foreground='white',  # Text color in the input field
                        arrowcolor='white',  # Dropdown arrow color
                        )

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
    def body(self, frame:Frame):
        tk_validate_is_number = self.top_frame.register(self._is_int)

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

        Label(section_info_frame, text="How many sections?", anchor='e', width=20).pack(side='left', padx=10, pady=5)
        en_number = Entry(section_info_frame, textvariable=self.number_of_sections, validate='key',
                            validatecommand=(tk_validate_is_number, '%P', '%s'))
        en_number.pack(side='left', padx=10, pady=5)

        # ------------------------------------------------------------------------------------------------------------
        # Blocks
        # ------------------------------------------------------------------------------------------------------------
        self.block_frames = Frame(frame)

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
        Button(self.block_frames, text="Add New Class", command=self.add_new_block).pack(expand=1, fill='y')


    # ================================================================================================================
    # are blocks set up properly?
    # ================================================================================================================

    def validate(self):
        if self.number_of_sections.get == "":
            showerror("Number of Sections", "Number of sections must be a number!")
            return False

        total = 0.0
        for block_info in self.row_data:
            duration=float(block_info[2].get().strip().split(" ")[0])
            if duration < 0:
                duration += 24
            total += duration

        if total == self.course_hours or total == 0.0:
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
        for i,b in enumerate(self.row_data):
            d = [x.get() for x in b]
            d[2] = float(d[2].strip().split(" ")[0])
            new_blocks.append(tuple(d))
        self._apply_changes( int(self.number_of_sections.get()), new_blocks )


