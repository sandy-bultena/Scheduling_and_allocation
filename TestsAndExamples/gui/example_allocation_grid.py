import os
import re
import sys
import tkinter as tk
import tkinter.ttk as ttk
bin_dir: str = os.path.dirname(os.path.realpath(__file__))
print (bin_dir)
sys.path.append(os.path.join(bin_dir, "../../"))


from schedule.Tk.Pane import Pane
from schedule.gui_pages.allocation_grid_tk import AllocationGridTk
from schedule.model import Schedule, Course

mw = tk.Tk()
mw.geometry("400x400")
file = "/Users/sandy/PycharmProjects/Scheduling_and_allocation/TestsAndExamples/unit_tests_presenter/data_fall.csv"
schedule = Schedule(file)

frame = tk.Frame(mw, background="pink")
frame.pack(expand=1, fill="both")

grid = AllocationGridTk(frame,
                        rows=len(schedule.teachers()),
                        col_merge=[c.number_of_sections() for c in schedule.courses()] ,
                        summary_merge = [3],
                        )
#tk.mainloop()
teachers_text = list(map(lambda a: a.firstname, schedule.teachers()))
courses_text = list(map(lambda a: str(re.sub(r'\s*\d\d\d-', '', a.number)),schedule.courses()))
courses_balloon = list(map(lambda a: a.name, schedule.courses()))
sections_text = list(map(lambda a: a.number, schedule.sections()))


col = 0
data_teacher_hours = {}

# constants
VALUE_KEY    = "value"
SECTION_KEY  = "section"
COURSE_KEY   = "course"
TEACHER_KEY  = "teacher"
CI_KEY       = "CI"
CI_TOTAL_KEY = "CI_total"
RELEASE_KEY  = "release"
bound_data_vars = {}
bound_summaries = []

# foreach course/section/teacher, holds the number of hours
data_unused_hours = {}
bound_remaining_hours = []
for course in schedule.courses():
    bound_summaries.append(["", "", ""])

    for section in sorted(course.sections(), key=lambda a: a.number):
        row = 0
        total_assigned = 0
        for teacher in schedule.teachers():
            data_teacher_hours.get(row, {})[col] = {
                TEACHER_KEY: teacher,
                COURSE_KEY: course,
                SECTION_KEY: section,
                VALUE_KEY: section.get_teacher_allocation(teacher)
            }
            total_assigned += section.get_teacher_allocation(teacher)
            bound_data_vars[row,col]=section.get_teacher_allocation(teacher)
            row += 1
        data_unused_hours[col] = {
            SECTION_KEY: section,
            VALUE_KEY: str(course.hours_per_week-total_assigned)
        }

        col += 1

        bound_remaining_hours.append(str(course.hours_per_week-total_assigned))

remaining_text = "Avail Hrs"


grid.populate(
    courses_text, courses_balloon, sections_text,
    teachers_text, bound_data_vars, [""], ["RT", "CI", "YEAR"],
    bound_summaries, remaining_text,
    bound_remaining_hours
)


tk.mainloop()

