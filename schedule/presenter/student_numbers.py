from __future__ import annotations

from functools import partial

from schedule.gui_pages.student_numbers_tk import StudentNumbersTk
from schedule.model import SemesterType, Section
from schedule.model.schedule import Schedule


class StudentNumbers:
    """StudentNumbers - provides methods / objects for entering number_of_students of students per course per section"""

    # =======================================================================================================
    # Constructor
    # =======================================================================================================

    def __init__(self, frame, schedule: Schedule):
        self.frame = frame
        self.data: StudentData = StudentData()
        self.schedule = schedule

        self.refresh()
        self.gui: StudentNumbersTk = StudentNumbersTk(self.frame, self.data.courses)

    # =======================================================================================================
    # gather data
    # =======================================================================================================
    def refresh(self):

        for course in (c for c in self.schedule.courses() if c.needs_allocation):
            self.data.add_course(course.title)

            for section in course.sections():
                section_data = SectionData(section.name, section.num_students, partial(event_handler, section))
                self.data.add_section(course.title, section_data)

        return self.data


def event_handler(section: Section, number:int):
    section.num_students = number

class StudentData:
    def __init__(self):
        self.courses: dict[str, list[SectionData]] = {}

    def add_course(self, course_name:str):
        self.courses[course_name] = []

    def add_section(self, course_name,  section_data):
        self.courses[course_name].append(section_data)

    def clear(self):
        self.courses.clear()

    def __iter__(self):
        return self.courses


class SectionData:
    def __init__(self, section_name, number_of_students, handler):
        self.name = section_name
        self.number_of_students = number_of_students
        self.handler = handler

