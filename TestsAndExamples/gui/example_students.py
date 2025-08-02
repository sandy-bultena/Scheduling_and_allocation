from schedule.gui_pages.num_students_tk import NumStudentsTk
from schedule.model import Schedule
import tkinter as tk

file = ("/Users/sandy/PycharmProjects/Scheduling_and_allocation/"
            "TestsAndExamples/unit_tests_presenter/data_test.csv")
schedule = Schedule(file)
mw = tk.Tk()
frame = tk.Frame(mw)
frame.pack()
ns = NumStudentsTk(frame)


mw.mainloop()
