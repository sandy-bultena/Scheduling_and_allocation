""" SYNOPSIS/EXAMPLE:
    tbd
"""

from __future__ import annotations
import re
from .enums import WeekDay
from .schedule_time import ScheduleTime, ClockTime

MINUTE_BLOCK_SIZE = 30
MINIMUM_DURATION = 0.5
DEFAULT_DAY = WeekDay.Monday
DEFAULT_START = "8:00"
DEFAULT_HOURS = 8
DEFAULT_DURATION = 1.5
MIN_START_TIME = 8
MAX_END_TIME = 18
MAXIMUM_DURATION = 8


class TimeSlot:
    """
    A time slot is specified by a day of the week, time_start time, length (in hours), and whether
        it is allowed to move.
    """

    def __init__(self, day: WeekDay = DEFAULT_DAY,
                 start: ScheduleTime = DEFAULT_START,
                 duration: float = DEFAULT_DURATION,
                 movable: bool = True):
        """
        :param day: Day of the week expressed as a string or as a Weekday
        :param start: Start time using the 24hr clock (i.e., 1PM is "13:00")
        :param duration: How long this class lasts, in hours.
        :param movable: Whether this time_slot can be moved or not.
        """
        self.day: WeekDay = day
        self.time_start: ScheduleTime = start
        self.duration: float = min(max(duration, MINIMUM_DURATION), MAXIMUM_DURATION)
        self.movable: bool = movable

    @property
    def time_end(self) -> ScheduleTime:
        hours = self.time_start.hours + self.duration
        return ScheduleTime(hours)

    # ====================================
    # snap_to_time
    # ====================================
    def snap_to_time(self) -> bool:
        """
        :return: True if the time_start time or duration were modified
        """

        # it's not movable!
        if not self.movable:
            return False

        hour_fraction = int(60/MINUTE_BLOCK_SIZE)
        # duration needs to be snapped to the same time span
        duration = max(MINIMUM_DURATION, round(self.duration * hour_fraction) / hour_fraction)
        changed = abs(duration - self.duration) > 0.01
        self.duration = duration

        # snap the scheduled time
        changed = changed or self.time_start.snap_to_time(duration=duration,
                                                          round_to_minutes=MINUTE_BLOCK_SIZE,
                                                          min_start_time=MIN_START_TIME,
                                                          max_end_time=MAX_END_TIME)

        return changed

    # =================================================================
    # snap_to_day
    # =================================================================
    def snap_to_day(self, fractional_day: float,
                    min_day: WeekDay = WeekDay.Monday,
                    max_day: WeekDay = WeekDay.Friday) -> bool:
        """
        :param fractional_day: an FLOAT that indicates where the day should be
        :param min_day: first day of the workweek
        :param max_day: last day of the workweek
        :return: True if modifications were made
        """
        day = round(fractional_day)
        day = max(min(day, max_day.value), min_day.value)
        if self.day.value == day:
            return False
        self.day = WeekDay(day)
        return True

    # =================================================================
    # conflicts
    # =================================================================
    def conflicts_time(self, other: TimeSlot, delta: float = 0.05) -> bool:
        """
        Tests if the current Time_Slot conflicts with another TimeSlot.
        :param other: other timeslot
        :param delta: the amount of leeway that we are allowing for in floating pt arithmetic
        """

        # detect date collisions.
        if self.day != other.day:
            return False

        # Calculate the time_start/end for each blocks within error factor.
        self_start = self.time_start.hours + delta
        self_end = self.time_start.hours + self.duration - delta
        other_start = other.time_start.hours + delta
        other_end = other.time_start.hours + other.duration - delta

        return other_start < self_start < other_end or other_start < self_end < other_end

    def __eq__(self, other):
        return (self.day == other.day
                and self.time_start == other.time_start
                and self.duration == other.duration)

    def __lt__(self, other):
        return ((self.day, self.time_start, self.duration) <
                (other.day, other.time_start, other.duration))

    def __str__(self):
        return f"{self.day.name}: {self.time_start} to {self.time_end}"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))


# =================================================================
# footer
# =================================================================
__copyright__ = '''
Sandy Bultena, Ian Clement, Jack Burns
Copyright (c) 2016, Jack Burns, Sandy Bultena, Ian Clement. 
Copyright (c) 2020, Sandy Bultena

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut
'''
