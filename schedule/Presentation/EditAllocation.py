# COMPLETED
from __future__ import annotations
from GUI.EditAllocationTk import EditAllocationTk
from CICalculator.CICalc import CICalc
from Presentation import globals
from functools import cmp_to_key, partial
import re

from Schedule.Course import Course
from Schedule.Schedule import Schedule

# constants
VALUE_KEY    = "value"
SECTION_KEY  = "section"
COURSE_KEY   = "course"
TEACHER_KEY  = "teacher"
CI_KEY       = "CI"
CI_TOTAL_KEY = "CI_total"
RELEASE_KEY  = "release"


class EditAllocation:
    def __init__(self, frame, schedule_ref: dict[str, Schedule]):
        self.frame = frame
        self.schedules = schedule_ref
        self.semesters = dict()

        self.data_semester_hash = dict()
        self.totals_semester_hash = dict()
        self.remaining_semester_hash = dict()

        self.bound_data_vars = dict()
        self.bound_remaining_hours = dict()

        self.gui: EditAllocationTk = None

        self.draw(schedule_ref)

    # ============================================================================
    # draw - setup and create the interface
    # ============================================================================
    def draw(self, schedules):
        allocation_info = []

        for semester in self._semesters:
            # clear out previous data
            self._reset_teacher_hours(semester)
            self._reset_totals(semester)
            self._reset_unused_hours(semester)

            # courses by semester
            schedule = self.schedules[semester]
            courses = Course.allocation_list()
            courses = list(filter(
                lambda a: a in schedule._courses(),
                courses
            ))
            self._semester_courses(semester, courses)

            # teacher_ids by semester
            teachers = sorted(self.schedules[semester].teacher_ids(),
                              key=cmp_to_key(
                                  lambda a, b:
                                  a.lastname > b.lastname
                                  if a.firstname == b.firstname else
                                  a.firstname > b.firstname
                              ))
            self._semester_teachers(semester, teachers)

            # sections of course by semester
            sections = []
            for course in courses:
                new_sections = sorted(course.sections(), key=lambda a: a.number)
                sections.extend(new_sections)
            self._semester_sections(semester, sections)

            col_numbers = map(lambda a: a.number_of_sections, courses)

            # save info
            allocation_info.append({
                'semester':        semester,
                'courses':         courses,
                'rows':            len(teachers),
                'columns_numbers': col_numbers,
                'totals_numbers':  [3]
            })

        # ------------------------------------------------------------------------
        # create the gui, or redraw if already exists
        # ------------------------------------------------------------------------
        if self.gui:
            self.gui.redraw(allocation_info)
        else:
            self.gui = EditAllocationTk(self.frame, allocation_info)

        # ------------------------------------------------------------------------
        # define text binding and callback routines
        # ------------------------------------------------------------------------
        for semester in self._semesters:
            # setup event handlers
            self.gui.set_cb_data_entry(semester, partial(self._cb_validate_number,
                                                         semester, schedules))
            self.gui.set_cb_process_data_change(semester,
                                                partial(self._cb_process_data_entry,
                                                        semester, schedules))
            self.gui.set_cb_bottom_row_ok(semester,
                                          partial(lambda a: not (a or 0), schedules))

            # bind variables to AllocationGrid
            self._define_data_binding(semester)

            # update the CI
            self._update_all_CI(semester)

    # ============================================================================
    # define all the data and bind to Allocation Grid
    # ============================================================================
    def _define_data_binding(self, semester):
        # ------------------------------------------------------------------------
        # create arrays for storing the 'constant' information for the
        # AllocationGrid
        # ------------------------------------------------------------------------
        teachers_text = map(lambda a: a.firstname, self._semester_teachers(semester))

        courses_text = map(lambda a: str(re.sub(r'\s*\d\d\d-', '', a.number)),
                           self._semester_courses(semester))

        courses_balloon = map(lambda a: a.name, self._semester_courses(semester))

        sections_text = map(lambda a: a.name, self._semester_sections(semester))

        # ------------------------------------------------------------------------
        # data array and binding arrays
        # ------------------------------------------------------------------------

        # create arrays that have the data for hrs / teacher / section,
        # based on ROW/COL,
        # and create arrays for binding this information to the allocationGrid

        col = 0

        # foreach course/section/teacher, holds the number of hours
        for course in self._semester_courses(semester):
            for section in sorted(course.sections(), key=lambda a: a.number):
                row = 0
                for teacher in self._semester_teachers(semester):
                    self._data_teacher_hours(semester).get(row, dict())[col] = {
                        TEACHER_KEY: teacher,
                        COURSE_KEY: course,
                        SECTION_KEY: section,
                        VALUE_KEY: ""
                    }

                    # NOTE: THIS PASSES THE REFERENCE TO THE VARIABLE IN PERL
                    # may cause issues, so experiment with this if need be
                    self.bound_data_vars.get(row, {})[col] =\
                        self._data_teacher_hours(semester)\
                            .get(row, {}).get(col, {}).get(VALUE_KEY)

                    # set the current hours based on info in the schedule
                    if section.has_teacher_with_id(teacher):
                        self._data_teacher_hours(semester).get(row, {})\
                            .get(col, {})[VALUE_KEY] = section.get_teacher_allocation(teacher)

                    row += 1
                col += 1

        # ------------------------------------------------------------------------
        # CI, release, etc arrays and binding info
        # ------------------------------------------------------------------------

        # foreach teacher, release, CI for semester, and CI for year
        bound_totals: dict[int, list[dict]] = {}

        row = 0
        for teacher in self._semester_teachers(semester):
            release = ""
            if teacher.release:
                release = "%6.3f" % teacher.release

            CI = CICalc(teacher).calculate(self.schedules.get(semester))

            info = {
                TEACHER_KEY: teacher,
                CI_KEY: CI,
                CI_TOTAL_KEY: '',
                RELEASE_KEY: release
            }

            self._data_totals(semester)[row] = info

            bound_totals[row] = []
            bound_totals[row].append(self._data_totals(semester).get(row, {}).get(RELEASE_KEY))
            bound_totals[row].append(self._data_totals(semester).get(row, {}).get(CI_KEY))
            bound_totals[row].append(self._data_totals(semester).get(row, {}).get(CI_TOTAL_KEY))

            row += 1

        # ------------------------------------------------------------------------
        # remaining hours to be allocated, arrays and binding
        # ------------------------------------------------------------------------
        # foreach course/section/teacher, holds the number of hours
        col = 0
        remaining_text = "Avail Hrs"

        for course in self._semester_courses(semester):
            for section in sorted(course.sections(), key=lambda a: a.number):
                self._data_unused_hours(semester)[col] = {
                    SECTION_KEY: section,
                    VALUE_KEY: ''
                }

                self.bound_remaining_hours[col] = self._data_unused_hours(semester)\
                    .get(col, {}).get(VALUE_KEY)
                col += 1

        # ------------------------------------------------------------------------
        # set up the binding of the data to the gui elements in gui_grid
        # ------------------------------------------------------------------------
        self.gui.bind_data_to_grid(
            semester, courses_text, courses_balloon, sections_text,
            teachers_text, self.bound_data_vars, [""], ["RT", "CI", "YEAR"],
            bound_totals, remaining_text, self.bound_remaining_hours
        )

    # ============================================================================
    # Update all the CI
    # ============================================================================
    def _update_all_CI(self, semester, totals = 0):
        totals = self._data_totals(semester)
        all_semesters = dict()

        # update for this semester only
        row = 0
        for total in totals.values():
            teacher = total[TEACHER_KEY]
            total[CI_KEY] = CICalc(teacher).calculate(self.schedules[semester])
            all_semesters[teacher] = total[CI_KEY]
            row += 1

        # update remaining hours for this semester only
        for remaining in self._data_unused_hours(semester).values():
            section = remaining[SECTION_KEY]
            remaining[VALUE_KEY] = section.hours - section.allocated_hours

        # get_by_id totals for all semesters
        for sem in self._semesters:
            if sem == semester:
                continue
            for tot in self._data_totals(sem).values():
                teacher = tot[TEACHER_KEY]

                if teacher not in all_semesters:
                    all_semesters[teacher] = float(0)

                all_semesters[teacher] += float(tot[CI_KEY])

        # update the total CI on the grid
        for sem in self._semesters:
            for tot in self._data_totals(sem).values():
                teacher = tot[TEACHER_KEY]
                tot[CI_TOTAL_KEY] = all_semesters.get(teacher)

    # ============================================================================
    # validate number callback routine
    # - make sure it is a number
    # - invalidate the CI calculations
    # ============================================================================
    def _cb_validate_number(self, semester, row, col, maybe_number):
        totals = self._data_totals(semester)[row]
        remainders = self._data_unused_hours(semester)[col]

        if re.match(r'\s*$', maybe_number) or re.match(r'(\s*\d*)(\.?)(\d*\s*)$', maybe_number):
            totals[CI_KEY]        = ""
            totals[CI_TOTAL_KEY]  = ""
            remainders[VALUE_KEY] = ""
            return True
        return False

    # ============================================================================
    # User has entered data... process it (this is a callback routine)
    # ============================================================================
    def _cb_process_data_entry(self, semester, row, col):
        remainders = self._data_unused_hours(semester)[col]
        data = self._data_teacher_hours(semester)[row][col]
        teacher = data[TEACHER_KEY]
        section = data[SECTION_KEY]
        hours = data[VALUE_KEY]

        section.set_teacher_allocation(teacher, hours)

        self._update_all_CI(semester)
        self._data_unused_hours(semester)[col][VALUE_KEY] = section.hours - section.allocated_hours

        globals.set_dirty_flag()

    # ============================================================================

    def _data_teacher_hours(self, semester) -> dict[int, dict]:
        if semester not in self.data_semester_hash:
            self.data_semester_hash[semester] = {}
        return self.data_semester_hash[semester]

    def _data_totals(self, semester) -> dict[int, dict]:
        if semester not in self.totals_semester_hash:
            self.totals_semester_hash[semester] = {}
        return self.totals_semester_hash[semester]

    def _data_unused_hours(self, semester) -> dict[int, dict]:
        if semester not in self.remaining_semester_hash:
            self.remaining_semester_hash[semester] = {}
        return self.remaining_semester_hash[semester]

    def _reset_teacher_hours(self, semester):
        self.data_semester_hash[semester] = {}

    def _reset_totals(self, semester):
        self.totals_semester_hash[semester] = {}

    def _reset_unused_hours(self, semester):
        self.remaining_semester_hash[semester] = {}

    # ============================================================================
    # Setters and Getters
    # ============================================================================
    def _semester_courses(self, semester, courses = None):
        if semester not in self.semesters:
            self.semesters[semester] = dict()
        if 'courses' not in self.semesters[semester]:
            self.semesters[semester]['courses'] = []

        if courses and len(courses):
            self.semesters[semester]['courses'] = courses

        return self.semesters[semester]['courses']

    def _semester_teachers(self, semester, teachers = None):
        if semester not in self.semesters:
            self.semesters[semester] = dict()
        if 'teacher_ids' not in self.semesters[semester]:
            self.semesters[semester]['teacher_ids'] = []

        if teachers and len(teachers):
            self.semesters[semester]['teacher_ids'] = teachers

        return self.semesters[semester]['teacher_ids']

    def _semester_sections(self, semester, sections = None):
        if semester not in self.semesters:
            self.semesters[semester] = dict()
        if 'sections' not in self.semesters[semester]:
            self.semesters[semester]['sections'] = []

        if sections and len(sections):
            self.semesters[semester]['sections'] = sections

        return self.semesters[semester]['sections']

    @property
    def _semesters(self):
        return sorted(self.schedules.keys())
