from ..model.schedule import Schedule
from ..gui_pages.OverviewTk import OverviewTk
from typing import *


class Overview:
    def __init__(self, frame, schedule: Optional[Schedule], test_gui=None):
        """
        Prints an overview of the schedule, 2 parts, by course or by teacher
        :param frame: gui parent
        :param schedule: schedule
        :param test_gui: for testing purposes only
        """
        self.schedule = schedule
        if not test_gui:
            self.gui = OverviewTk(frame)
        else:
            self.gui = test_gui

    def refresh(self):
        """Refreshes the overview text"""
        courses_text: list[str] = list()
        teachers_text: list[str] = list()

        # no schedule
        if self.schedule is None:
            self.gui.refresh(
                ('There is no schedule, please open one',),
                ('There is no schedule, please open one',)
            )
            return

        # course info
        if not self.schedule.courses:
            courses_text.append('No courses defined in this schedule')
        else:
            for c in self.schedule.courses:
                courses_text.append(str(c))

        # teacher info
        if not self.schedule.teachers:
            teachers_text.append('No teachers defined in this schedule')
        else:
            for t in self.schedule.teachers:
                teachers_text.append(self.schedule.teacher_details(t))

        self.gui.refresh(tuple(courses_text), tuple(teachers_text))
