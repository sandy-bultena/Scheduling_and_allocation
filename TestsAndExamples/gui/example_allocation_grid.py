import os
import re
import sys
import tkinter as tk
import tkinter.ttk as ttk
from dataclasses import dataclass
from typing import Literal

bin_dir: str = os.path.dirname(os.path.realpath(__file__))
print (bin_dir)
sys.path.append(os.path.join(bin_dir, "../../"))


from schedule.Tk.Pane import Pane
from schedule.gui_pages.allocation_grid_tk import AllocationGridTk
from schedule.model import Schedule, Course, Section, Teacher
from schedule.CICalculator.CICalc import calculate_ci

@dataclass
class InnerData:
    row: int
    col: int
    teacher: Teacher
    course: Course
    section: Section
    hours: float

@dataclass
class BottomRow:
    teacher: Course
    teacher: Section
    total_hours: float


@dataclass
class SummaryRow:
    release: str
    total_hrs: str
    semester_ci: str
    year_ci: str
    teacher:Teacher

def calculate_remaining_hours(data:list[InnerData]):
    total_per_col = {}
    for datum in data:
        col = datum.col
        total_per_col[col] = total_per_col.get(col, 0) + datum.hours

    totals_tuple = sorted(total_per_col.items())
    return [value for key, value in totals_tuple]

def calculate_summaries():
    teacher_summaries: list[SummaryRow] = []
    for teacher in teachers:
        hrs = 0
        for course in schedule.get_courses_for_teacher(teacher):
            for section in course.sections():
                hrs += section.get_teacher_allocation(teacher)
        semester_ci = calculate_ci(teacher=teacher, schedule=schedule)
        yearly_ci = 0
        teacher_summaries.append(SummaryRow(release="" if teacher.release == 0 else f"{teacher.release:6.3f}",
                                       semester_ci="" if semester_ci == 0 else f"{semester_ci:6.2f}",
                                       teacher=teacher,
                                            total_hrs="" if hrs==0 else f"{hrs:6.2f}",
                                            year_ci="" if yearly_ci==0 else f"{hrs:6.2f}"))

    return teacher_summaries

mw = tk.Tk()
mw.geometry("400x400")
file = "/Users/sandy/PycharmProjects/Scheduling_and_allocation/TestsAndExamples/unit_tests_presenter/data_fall.csv"
schedule = Schedule(file)

frame = tk.Frame(mw, background="pink")
frame.pack(expand=1, fill="both")

teachers = schedule.teachers()
teachers_text = list(map(lambda a: a.firstname, schedule.teachers()))
courses_text = list(map(lambda a: str(re.sub(r'\s*\d\d\d-', '', a.number)),schedule.courses()))
courses_balloon = list(map(lambda a: a.name, schedule.courses()))
sections_text = list(map(lambda a: a.number, schedule.sections()))
inner_data: list[InnerData] = []
bottom_data: dict[tuple[int], dict] = {}
data_numbers_only: dict[tuple[int,int], float] = {}

# constants
keys = Literal['value', 'section', 'course', 'teacher', 'release']

col = 0
for course in schedule.courses():

    for section in sorted(course.sections(), key=lambda a: a.number):
        row = 0
        total_assigned = 0
        for teacher in schedule.teachers():
            inner_data.append(InnerData(row=row, col=col, teacher=teacher, course=course,
                                              section=section, hours=section.get_teacher_allocation(teacher)))
            data_numbers_only[(row,col)] = inner_data[-1].hours
            row += 1

        col += 1

remaining_hours = calculate_remaining_hours(inner_data)
remaining_text = "Avail Hrs"
summary_headings = ["RT", "hrs", "CI", "YEAR"]

grid = AllocationGridTk(frame,
                        rows=len(schedule.teachers()),
                        col_merge=[c.number_of_sections() for c in schedule.courses()] ,
                        summary_merge = [len(summary_headings)],
                        )

summary_strs = [(a.release, a.total_hrs, a.semester_ci, a.year_ci) for a in calculate_summaries()]
grid.populate(
    courses_text, courses_balloon, sections_text,
    teachers_text, data_numbers_only, [""], summary_headings,
    summary_strs, remaining_text,
    remaining_hours
)


tk.mainloop()

