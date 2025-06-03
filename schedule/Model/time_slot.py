""" SYNOPSIS/EXAMPLE:

    from Schedule.Time_slot import TimeSlot

    time_slot = TimeSlot(day = "Wed", time_start = "9:30", duration = 1.5, movable = True)
"""

from __future__ import annotations
import re
from .enums import WeekDay

MINUTE_BLOCK_SIZE = 30
MINIMUM_DURATION = 0.5
DEFAULT_DAY = WeekDay.Monday
DEFAULT_START = "8:00"
DEFAULT_HOURS = 8
DEFAULT_DURATION = 1.5
MIN_START_TIME = 8
MAX_END_TIME = 18
MAXIMUM_DURATION = 8


def get_hour_minutes_from_hours(hours: float) -> (int, int):
    """converts number of hours (as a float) to integer hour and integer minutes"""
    hour = int(hours)
    minute = (hours % 1) * 60
    return hour, int(minute)


def get_string_clock_time(hours: int, minutes: int) -> str:
    """converts hours and minutes into something that can be used as input to ClockTime"""
    return f"{hours}:{minutes:02d}"


class ClockTime:
    """
    Manage time by starting with the string representation
    """

    def __init__(self, string_time: str):
        """
        :param string_time: a string representation of the 24-clock
        """
        string_time = string_time.strip()

        if not re.match(r"^[12]?\d:\d{2}$", string_time):
            string_time = DEFAULT_START
        hour, minute = (int(x) for x in string_time.split(":"))
        self.hours = hour + minute / 60

    @property
    def hour(self) -> int:
        """number of integer hours for this particular time"""
        hr, _ = get_hour_minutes_from_hours(self.hours)
        return hr

    @property
    def minute(self) -> int:
        """number of integer minutes for this particular time"""
        _, m = get_hour_minutes_from_hours(self.hours)
        return m

    def __sub__(self, other) -> float:
        return self.hours - other.hours

    def __eq__(self, other):
        return self.hour == other.hour and self.minute == other.minute

    def __lt__(self, other):
        return (self.hour, self.minute) < (other.hour, other.minute)

    def __str__(self):
        return get_string_clock_time(self.hour, self.minute)


class TimeSlot:
    """
    A time slot is specified by a day of the week, time_start time, length (in hours), and whether
        it is allowed to move.
    """

    def __init__(self, day: WeekDay = DEFAULT_DAY,
                 start: ClockTime = DEFAULT_START,
                 duration: float = DEFAULT_DURATION,
                 movable: bool = True):
        """
        :param day: Day of the week expressed as a string or as a Weekday
        :param start: Start time using the 24hr clock (i.e., 1PM is "13:00")
        :param duration: How long this class lasts, in hours.
        :param movable: Whether this time_slot can be moved or not.
        """
        self.day: WeekDay = day
        self.time_start: ClockTime = start
        self.duration: float = min(max(duration, MINIMUM_DURATION), MAXIMUM_DURATION)
        self.movable: bool = movable

    @property
    def time_end(self) -> ClockTime:
        hours = self.time_start.hours + self.duration
        h, m = get_hour_minutes_from_hours(hours)
        return ClockTime(get_string_clock_time(h, m))

    # ====================================
    # snap_to_time
    # ====================================
    def snap_to_time(self, round_to: int = MINUTE_BLOCK_SIZE) -> bool:
        """
        Forces the stop and time_start time of this time slot to "snap" to
        the nearest fraction of an hour
        :Returns: True if the time_start time or duration were modified
        """

        # it's not movable!
        if not self.movable:
            return False

        # snap to the number of minutes in the block size
        duration = max(MINIMUM_DURATION, (self.duration / round_to) * round_to)
        hours = self.time_start.hours
        hours = max(hours, MIN_START_TIME)
        if hours + self.duration > MAX_END_TIME:
            hours = MAX_END_TIME - duration
        hour, minute = get_hour_minutes_from_hours(hours)
        minute = round(minute / round_to) * round_to

        # not changed
        if (minute == self.time_start.minute
                and self.time_start.hour == hour
                and duration == self.duration):
            return False

        # update time for time slot
        self.duration = duration
        self.time_start = ClockTime(get_string_clock_time(hour, minute))

        return True

    # =================================================================
    # snap_to_day
    # =================================================================
    def snap_to_day(self, fractional_day: float,
                    min_day: WeekDay = WeekDay.Monday,
                    max_day: WeekDay = WeekDay.Friday):
        """
        :param fractional_day: an FLOAT that indicates where the day should be
        :param min_day: first day of the workweek
        :param max_day: last day of the workweek
        """
        day = round(fractional_day)
        day = max(min(day, max_day.value), min_day.value)
        self.day = WeekDay(day)
        return self.day

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
                and self.time_start == other.time_end
                and self.duration == other.duration)

    def __lt__(self, other):
        return ((self.day, self.time_start, self.duration) <
                (other.day, other.time_start, other.duration))

    def __str__(self):
        return f"{self.day.value}: {self.time_start} to {self.time_end}"

    def __repr__(self):
        return str(self)


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
