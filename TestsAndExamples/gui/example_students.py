import os
import sys
from functools import partial


bin_dir: str = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(bin_dir, "../../"))
from schedule.gui_pages.student_numbers_tk import StudentNumbersTk, SectionData
from schedule.presenter.student_numbers import StudentData

from schedule.model import Schedule
import tkinter as tk

file = ("/Users/sandy/PycharmProjects/Scheduling_and_allocation/"
            "TestsAndExamples/unit_tests_presenter/data_fall.csv")
schedule = Schedule(file)

data: StudentData = StudentData()

def refresh():
    for course in (c for c in schedule.courses() if c.needs_allocation):
        data.add_course(course.title)

        for section in course.sections():
            section_data = SectionData(section.name, section.num_students, partial(data_changed_handler, section))
            data.add_section(course.title, section_data)

    return data

def data_changed_handler(section, number:int):
    section.num_students = number
refresh()


mw = tk.Tk()
frame = tk.Frame(mw)
frame.pack(expand=1, fill='both')

ns = StudentNumbersTk(frame, data.courses)


mw.mainloop()
