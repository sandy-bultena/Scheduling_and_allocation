from functools import partial
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as message_box

from schedule.model import WeekDay
import pprint


# ================================================================================================================
# clock conversion
# ================================================================================================================
def get_hour_minutes_from_hours(hours: float) -> (int, int):
    """converts number of hours (as a float) to integer hour and integer minutes"""
    hour = int(hours)
    minute = (hours % 1) * 60
    return hour, int(minute)

def get_clock_string_from_hours(hours: float)->str:
    hour,minute = get_hour_minutes_from_hours(hours)
    return f"{hour}:{minute:02d}"

def get_hours_from_str(hours:str)->float:
    hour = hours
    minute = 0
    if ":" in hours:
        hour,minute = hours.split(":")
    return int(float(hour)) + int(float(minute))/60

# ================================================================================================================
# Number validation
# ================================================================================================================

def register_number_funcs(frame:tk.Frame):
    """this allows us to pass extra stuff from Entry validation
    :param frame: any Tk object
    """
    tk_is_int = frame.winfo_toplevel().register(partial(_is_int, frame))
    tk_is_float = frame.winfo_toplevel().register(partial(_is_float, frame))
    return tk_is_int, tk_is_float

def entry_float(frame: tk.Frame, textvariable: tk.StringVar ) -> tk.Entry:
    """
    An entry widget that only accepts floats (note... '' and '.' would be valid, so you still need to check later)
    :param frame:
    :param textvariable:
    :return: the entry widget with validation
    """
    _,tk_is_float = register_number_funcs(frame)
    return tk.Entry(frame,
                           textvariable=textvariable,
                           validate='key',
                           validatecommand=(tk_is_float, '%P', '%s'))

def entry_int(frame: tk.Frame, textvariable: tk.StringVar ) -> tk.Entry:
    """
    An entry widget that only accepts ints (note... '' and would be valid, so you still need to check later)
    :param frame:
    :param textvariable:
    :return: the entry widget with validation
    """
    tk_is_int,_ = register_number_funcs(frame)
    return tk.Entry(frame,
                           textvariable=textvariable,
                           validate='key',
                           validatecommand=(tk_is_int, '%P', '%s'))

def _is_int(frame: tk.Frame, number: str, *_) -> bool:
    """
    Validation for the string that is currently in an Entry widget
    :param number: the number that would result if this validation returns True
    :return: is this a valid int, or the start of a valid int
    """
    if number == "":
        return True
    try:
        int(number)
        return True
    except ValueError:
        frame.winfo_toplevel().bell()
        return False


def _is_float(frame: tk.Frame, number: str, _: str) -> bool:
    """
    Validation for the string that is currently in an Entry widget
    :param number: the number that would result if this validation returns True
    :return: is this a valid float, or the start of a valid float
    """
    if number == "" or number == ".":
        return True
    try:
        float(number)
        return True
    except ValueError:
        frame.winfo_toplevel().bell()
        return False

# ================================================================================================================
# general validations
# ================================================================================================================
def validate_float(number:str, title, msg)-> bool:
    """
    is this number a float
    :param number: the str version of the number to test
    :param title: dialog box title
    :param msg: dialog box message
    :return: True/False
    """
    try:
        float(number)
    except ValueError:
        message_box.showerror(title, msg)
        return False
    return True

def validate_int(number:str, title, msg)-> bool:
    """
    is this number a int
    :param number: the str version of the number to test
    :param title: dialog box title
    :param msg: dialog box message
    :return: True/False
    """
    try:
        int(number)
    except ValueError:
        message_box.showerror(title, msg)
        return False
    return True

def validate_class_times_equals_course_time(block_row_data, course_hours: float)-> bool:
    """
    Compares the total duration of all the blocks and compares to the hours assigned to the course
    :param block_row_data: list of tuples with string reprs of day, start_time, and duration
    :param course_hours: the hours assigned to this course
    :return: true if no blocks defined, or if duration is equal to assigned hours, or user oks the discrepancy
    """
    total = 0.0
    for block_info in block_row_data:
        duration = float(block_info[2].get().strip().split(" ")[0])
        if duration < 0:
            duration += 24
        total += duration

    if total == course_hours or total == 0.0:
        return True

    else:
        return message_box.askyesno("Class Times", f"Total allocated class times ({total})\n"
                                       f"does not equal course time ({course_hours})"
                                       f"\n\nDo you wish to continue?")


# ================================================================================================================
# style for combo boxes
# ================================================================================================================
def set_style(frame):
    """
    set style for combo boxes
    :param frame: any Tk object
    :return:
    """
    style = ttk.Style(frame.winfo_toplevel())
    style.configure("MyCustom.TCombobox",
                         fieldbackground='black',  # Background of the input field
                         background='black',  # Overall widget background
                         foreground='white',  # Text color in the input field
                         arrowcolor='white',  # Dropdown arrow color
                         )

# ================================================================================================================
# blocks
# ================================================================================================================
def get_block_info_from_row_data(block_row_data: list[tk.StringVar]) -> list[tuple[float,float,float]]:
    """
    Convert string (day, start_time, duration) to int(day), float(start_time), float(duration)
    :param block_row_data:
    :return: updated list
    """
    new_blocks = []
    print("\n\n==========")
    for i, b in enumerate(block_row_data):
        d = [x.get() for x in b]
        pprint.pp(d)
        day = WeekDay[d[0]].value
        start_str = (d[1].strip().split(" ")[0])
        start = get_hours_from_str(start_str)
        duration = float(d[2].strip().split(" ")[0])
        new_blocks.append((day,start,duration))
    print("==========")
    pprint.pp(new_blocks)
    print("==========\n\n")

    return new_blocks

def refresh_gui_blocks(self,):
    """
    Create all the drop-down boxes etc for blocks
    :param self: the object that contains all the block info, frame, etc
    :return:
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    start_times = []
    for h in range(7, 24):
        for m in (0, 15, 30, 45):
            start_times.append(f"{h:2d}:{m:02d}")
    durations = [f"{x / 2:4.1f} hrs" for x in range(1, 13)]

    # remove any pre-existing stuff
    for w in self.block_frames.winfo_children():
        w.destroy()

    row_frames = []
    for index, block_info in enumerate(self.row_data):
        def remove_block(instance=self, i=index):
            instance.row_data.pop(i)
            instance.refresh_blocks()

        row_frame = tk.Frame(self.block_frames)
        row_frames.append(row_frame)
        row_frame.pack(expand=1, fill='both', padx=10, pady=2)

        opt_day, opt_hour, opt_duration = block_info

        btn_delete = tk.Button(row_frame, text="remove", command=remove_block)
        om_day = ttk.Combobox(row_frame, textvariable=opt_day, state="readonly", values=days,
                              style="MyCustom.TCombobox")
        om_time = ttk.Combobox(row_frame, textvariable=opt_hour, state="readonly", values=start_times,
                               style="MyCustom.TCombobox")
        om_duration = ttk.Combobox(row_frame, textvariable=opt_duration, state="readonly", values=durations,
                                   style="MyCustom.TCombobox")

        om_day.config(width=8)
        om_time.config(width=5)
        om_duration.config(width=8)

        om_day.pack(side='left', pady=0)
        om_time.pack(side='left', pady=0)
        om_duration.pack(side='left', pady=0)
        btn_delete.pack(side='left', pady=0)



