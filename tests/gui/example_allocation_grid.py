import os
import re
import sys
import tkinter as tk

bin_dir: str = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(bin_dir, "../../"))

from schedule.model import Schedule
from schedule.presenter.allocation_editor import AllocationEditor



mw = tk.Tk()
mw.geometry("800x400")
file = "/tests/unit_tests_presenter/data_fall.csv"
s = Schedule(file)

f = tk.Frame(mw, background="pink")
f.pack(expand=1, fill="both")
def set_dirty_flag(flag=False): ...

ae = AllocationEditor(set_dirty_flag, frame =f, schedule = s)

tk.mainloop()

