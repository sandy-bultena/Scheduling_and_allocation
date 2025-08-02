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

    def __init__(self, frame, schedules: dict[SemesterType, Schedule]):
        self.frame = frame
        self.data: StudentData = StudentData()
        self.schedules: dict[SemesterType, Schedule] = schedules

        self.refresh()
        self.gui: StudentNumbersTk = StudentNumbersTk(self.frame, self.data.semesters)

    # =======================================================================================================
    # gather data
    # =======================================================================================================
    def refresh(self):

        for semester in SemesterType:
            if semester not in self.schedules.keys():
                continue

            schedule: Schedule = self.schedules[semester]

            for course in schedule.courses():
                self.data.add_course(course)

                for section in course.sections():
                    self.data.add_section(course,section, partial(event_handler, section))
        return self.data


def event_handler(section: Section, number:int):
    section.num_students = number

class StudentData:
    def __init__(self):
        self.semesters:dict[SemesterType, dict[CourseData, list[SectionData]]] = {}
        for semester in SemesterType:
            self.semesters[semester] = {}

    def add_course(self, semester, course):
        self.semesters[semester][CourseData(course)] = []

    def add_section(self, semester, course, section, number, handler):
        self.semesters[semester][course].append(SectionData(section, number, handler))
    def clear(self):
        for semester in SemesterType:
            self.semesters[semester].clear()


class CourseData:
    def __init__(self, course_name):
        self.name = course_name
        self.sections:dict[SectionData, list[SectionData]] = {}

class SectionData:
    def __init__(self, section_name, number, handler):
        self.name = section_name
        self.number_of_students = number
        self.handler = handler

