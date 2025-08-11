import tkinter as tk
from functools import partial
from tkinter import ttk
import tkinter.messagebox as message_box

from schedule.gui_generics.number_validations import entry_float
from schedule.model import WeekDay


# ================================================================================================================
# clock conversion
# ================================================================================================================
def get_hour_minutes_from_hours(hours: float) -> (int, int):
    """converts number_of_students of hours (as a float) to integer hour and integer minutes"""
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
    if "." in hours:
        return float(hours)
    return int(float(hour)) + int(float(minute))/60

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
    for i, b in enumerate(block_row_data):
        d = [x.get() for x in b]
        day = WeekDay[d[0]].value
        start_str = (d[1].strip().split(" ")[0])
        start = get_hours_from_str(start_str)
        duration = float(d[2].strip().split(" ")[0])
        new_blocks.append((day,start,duration))

    return new_blocks

def refresh_gui_blocks(self,):
    """
    Create the drop-down and entry boxes etc for blocks
    :param self: the object that contains all the block info, frame, etc
    :return:
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # remove any pre-existing stuff
    for w in self.block_frames.winfo_children():
        w.destroy()

    row_frames = []
    for index, block_info in enumerate(self.row_data):
        def remove_block(instance=self, i=index):
            instance.row_data.pop(i)
            instance.refresh()

        row_frame = tk.Frame(self.block_frames)
        if row_frame.winfo_toplevel().tk.call('tk', 'windowingsystem') == 'aqua':
            padx=2
            pady = 0
        else:
            padx = 2
            pady = 0
        row_frames.append(row_frame)
        row_frame.pack(expand=1, fill='both', padx=10, pady=2)

        opt_day, opt_hour, opt_duration = block_info

        btn_delete = tk.Button(row_frame, text="remove",  command=remove_block, padx=2*padx)
        om_day = ttk.Combobox(row_frame, textvariable=opt_day,  values=days, state="readonly" )
        om_time = entry_float(row_frame, textvariable=opt_hour)
        om_duration = entry_float(row_frame, textvariable=opt_duration)

        om_day.config(width=8)
        om_time.config(width=5)
        om_duration.config(width=5)

        om_day.pack(side='left', pady=pady, padx=padx)
        tk.Label(row_frame, text="start:", anchor='e',width=5,).pack(side='left', expand=1, fill='x')
        om_time.pack(side='left', pady=pady, padx=padx, expand=1, fill='x')
        tk.Label(row_frame, text="duration:", anchor='e',width=8,).pack(side='left', expand=1, fill='x')
        om_duration.pack(side='left', pady=pady, padx=padx, expand=1, fill='x')
        btn_delete.pack(side='left', pady=pady, padx=padx, ipadx=padx, expand=1, fill='x')

        om_time.bind("<Leave>", partial(_validate_start_time, opt_hour))
        om_time.bind("<FocusOut>", partial(_validate_start_time, opt_hour))
        om_duration.bind("<Leave>", partial(_validate_duration, opt_duration))
        om_duration.bind("<FocusOut>",  partial(_validate_duration, opt_duration))

def _validate_start_time(tkvar: tk.StringVar,  _: tk.Event):
    try:
        value = float(tkvar.get())
    except ValueError:
        tk.messagebox.showerror(message="Class Start Time", title="Invalid Float",
                                detail=f"'{tkvar.get()}' is not a valid number")
        tkvar.set("8.0")
        return

    if value < 8 or value > 18:
        tk.messagebox.showerror(title="Invalid Class Start Time", detail="Resetting to 8:00 am",
                                message=f"'{tkvar.get()}' is outside of operational hours")
        return

    tkvar.set(str(round(4*value)/4))

def _validate_duration(tkvar: tk.StringVar, _: tk.Event):

    try:
        value = float(tkvar.get())
    except ValueError:
        tk.messagebox.showerror(message="Class Duration", title="Invalid Float",
                                detail=f"'{tkvar.get()}' is not a valid number")
        return

    if value < 0.5 or value > 8:
        tk.messagebox.showerror(title="Invalid Class Duration", detail="Resetting to 1.5 hrs",
                                message=f"'{tkvar.get()}' is not a valid class duration")
        return

    tkvar.set(str(round(4*value)/4))






