import re
from dataclasses import dataclass

from schedule.gui_pages.allocation_grid_tk import AllocationGridTk
from schedule.model import Schedule, Course, Section, Teacher
from schedule.ci_calculator.ci_calculation import calculate_ci

# =====================================================================================================================
# InnerData and SummaryRow data classes
# =====================================================================================================================
@dataclass
class InnerData:
    teacher: Teacher
    course: Course
    section: Section
    hours: float

@dataclass
class SummaryRow:
    release: str
    total_hrs: str
    semester_ci: str
    year_ci: str
    teacher:Teacher

# =====================================================================================================================
# Allocation Editor
# =====================================================================================================================
class AllocationEditor:

    # -----------------------------------------------------------------------------------------------------------------
    # constructor
    # -----------------------------------------------------------------------------------------------------------------
    def __init__(self, frame, schedule: Schedule):
        self.frame = frame
        self.schedule = schedule

        self.teachers = schedule.teachers()


        self.remaining_text = "Avail Hrs"
        self.summary_headings = ["RT", "hrs", "CI", "YEAR"]
        self.inner_data: dict[tuple[int,int],InnerData] = {}
        self.bottom_data: dict[tuple[int], dict] = {}
        self.data_numbers_only: dict[tuple[int,int], float] = {}

        self.gui = AllocationGridTk(frame,
                        rows=len(schedule.teachers()),
                        col_merge=[c.number_of_sections() for c in schedule.courses()] ,
                        summary_merge = [len(self.summary_headings)],
                        cb_process_data_change=lambda *args: self.data_change_handler(*args),
                        bottom_cell_valid = lambda c: float(c) == 0.0,
                        )
        self.populate()


    # -----------------------------------------------------------------------------------------------------------------
    # using schedule, construct data that can be used to populate the gui allocation grid
    # -----------------------------------------------------------------------------------------------------------------
    def populate(self):

        teachers = self.schedule.teachers()
        courses = self.schedule.courses()

        teachers_text = list(map(lambda a: a.firstname, teachers))
        courses_text = list(map(lambda a: str(re.sub(r'\s*\d\d\d-', '', a.number)), courses))
        courses_balloon = list(map(lambda a: f" {a.name} ({a.hours_per_week})" , courses))

        teacher_summaries:list[list[str]] = []
        inner_data: dict[tuple[int,int],InnerData] = {}
        data_numbers_only: dict[tuple[int,int], float] = {}

        # loop over the courses/sections, and save info into appropriate data structures
        col = 0
        sections_text: list[str] = []
        for course in courses:
            for section in course.sections():
                sections_text.append(section.number)

                # save info for each teacher ( for each course/sections)
                for row, teacher in enumerate(teachers):
                    inner_data[(row,col)]=InnerData(teacher=teacher,
                                                    course=course,
                                                    section=section,
                                                    hours=section.get_teacher_allocation(teacher))
                    data_numbers_only[(row,col)] = inner_data[row,col].hours
                    teacher_stats = self._calculate_summary(row)
                    teacher_summaries.append([teacher_stats.release,
                                             teacher_stats.total_hrs,
                                              teacher_stats.semester_ci,
                                              teacher_stats.year_ci])

                col += 1

        # get unallocated hours for each course/section
        remaining_hours = AllocationEditor._calculate_unallocated_hours(inner_data)

        # add all the data to the gui Allocation Grid
        self.gui.populate(
            courses_text, courses_balloon, sections_text,
            teachers_text, data_numbers_only, [""], self.summary_headings,
            teacher_summaries, self.remaining_text,
            remaining_hours
        )


    # -----------------------------------------------------------------------------------------------------------------
    # data change handler
    # -----------------------------------------------------------------------------------------------------------------
    def data_change_handler(self, row, col, value):

        # update schedule
        info = self.inner_data[row,col]
        self.inner_data[row,col].hours = float(value)
        info.section.set_teacher_allocation(self.teachers[row], float(value))

        summary = self._calculate_summary(row)
        self.gui.update_data('summary',row,0, summary.release)
        self.gui.update_data('summary',row,1, summary.total_hrs)
        self.gui.update_data('summary',row,2, summary.semester_ci)
        self.gui.update_data('summary',row,3, summary.year_ci)

        remaining_hours = AllocationEditor._calculate_unallocated_hours(self.inner_data)
        self.gui.update_data('bottom', 0, col, remaining_hours[col])

    # -----------------------------------------------------------------------------------------------------------------
    # calculate the summary for a particular row (ci/ total hrs/ etc)
    # -----------------------------------------------------------------------------------------------------------------
    def _calculate_summary(self, row):
        teacher = self.teachers[row]
        hrs = 0
        for course in self.schedule.get_courses_for_teacher(teacher):
            for section in course.sections():
                hrs += section.get_teacher_allocation(teacher)
        semester_ci = calculate_ci(teacher=teacher, schedule=self.schedule)
        yearly_ci = 0

        # convert all the numbers into their appropriate string variations
        return (SummaryRow(release="" if teacher.release == 0 else f"{teacher.release:6.3f}",
                                            semester_ci="" if semester_ci == 0 else f"{semester_ci:6.2f}",
                                            teacher=teacher,
                                            total_hrs="" if hrs == 0 else f"{hrs:6.2f}",
                                            year_ci="" if yearly_ci == 0 else f"{hrs:6.2f}"))


    # -----------------------------------------------------------------------------------------------------------------
    # calculate all the unallocated hours per section
    # -----------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _calculate_unallocated_hours(data:dict[tuple[int,int],InnerData]):
        total_per_col:dict[int, float] = {}
        req_per_col:dict[int,float] = {}
        remaining_hours:dict[int, float] = {}
        for location,datum in data.items():
            row,col = location
            total_per_col[col] = total_per_col.get(col, 0) + datum.hours
            req_per_col[col] = datum.course.hours_per_week
        for col in total_per_col.keys():
            remaining_hours[col] = req_per_col[col] - total_per_col[col]

        remaining = sorted(remaining_hours.items())
        return [value for key, value in remaining]

