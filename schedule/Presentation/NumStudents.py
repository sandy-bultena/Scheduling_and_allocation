# COMPLETED
from __future__ import annotations
import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__)))
import GUI.NumStudentsTk as gui_form
from . import globals
import Schedule.Schedule as Schedule
import Schedule.Course as Course
import Schedule.Section as Section


# =======================================================================================================
# Define callback for validation for data entry
# =======================================================================================================
def validate_factory(section):
    def validate(entry_input: str):
        if entry_input.isdigit():
            section.num_students = int(entry_input)
            globals.set_dirty_flag()
            return True
        if entry_input == "":
            section.num_students = 0
            globals.set_dirty_flag()
            return True
        return False

    return validate


class NumStudents:
    """NumStudents - provides methods / objects for entering number of students per course per section"""

    # =======================================================================================================
    # Constructor
    # =======================================================================================================

    def __init__(self, frame, schedules: list[Schedule.Schedule]):
        """
        Gathers data to present to the NumStudents gui form

        Inputs
        ------
        frame - a gui frame which will be the container object for the new form
        schedules - dictionary
                  - Key = semester name, value = schedule object
        """
        self.frame = frame
        data = self._gather_data(schedules)
        self.form = gui_form.NumStudentsTk(self.frame, data)

    # =======================================================================================================
    # update the data
    # =======================================================================================================
    def _refresh(self, schedules: list[Schedule.Schedule]):
        """
        Re-draw the student numbers for semesters/courses/section

        Inputs
        ------
        schedules - dictionary
                  - Key = semester name, value = schedule object
        """

        data = self._gather_data(schedules)
        self.form.NumStudentsTk(data)

    # =======================================================================================================
    # gather data
    # =======================================================================================================
    def _gather_data(self, schedules: list[Schedule.Schedule]):
        """
        gather all the data for the required for the form

        Inputs
        ------
        schedules - dictionary
                  - Key = semester name, value = schedule object
        """

        data = gui_form.NumStudentsData()

        # --------------------------------------------------------------------------------------------------
        # for each semester
        # --------------------------------------------------------------------------------------------------
        for semester_name in ("fall", "winter", "summer"):
            if semester_name not in schedules.keys(): continue
            semester = gui_form.NumStudentsDataSemester(name=semester_name)
            data.semesters.append(semester)

            schedule: Schedule.Schedule = schedules[semester_name]

            # --------------------------------------------------------------------------------------------------
            # for each course in the semester
            # --------------------------------------------------------------------------------------------------
            courses: list[Course.Course] = sorted(
                (c for c in schedule._courses() if c.needs_allocation),
                key=lambda x: x.description)
            for course in courses:
                course_data = gui_form.NumStudentsDataCourse(name=course.description)
                semester._courses.append(course_data)

                # --------------------------------------------------------------------------------------------------
                # for each section in the course
                # --------------------------------------------------------------------------------------------------
                sections: list[Section.Section] = sorted(course.sections(), key=lambda x: x.number)
                for section in sections:
                    section_data = gui_form.NumStudentsDataSection(
                        name=section.number, num_students=section.num_students)
                    section_data.data_validate = validate_factory(section)
                    course_data.sections.append(section_data)

        return data
