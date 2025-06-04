from __future__ import annotations
import re


def get_hour_minutes_from_hours(hours: float) -> (int, int):
    """converts number of hours (as a float) to integer hour and integer minutes"""
    hour = int(hours)
    minute = (hours % 1) * 60
    return hour, int(minute)


class ScheduleTime:
    def __init__(self, hours: float):
        self._hours = hours

    @property
    def hours(self) -> float:
        return self._hours

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

    def update_clock(self, hours: float):
        self._hours = hours

    def snap_to_time(self, round_to_minutes: int,
                     duration: float,
                     min_start_time: float,
                     max_end_time: float,
                     ) -> bool:
        """
        Forces the stop and time_start time of this time slot to "snap" to
        the nearest fraction of an hour
        :param round_to_minutes:  "unit" of time to be rounded to
        :param duration:  time to reserve
        :param min_start_time: hours past midnight
        :param max_end_time: hours past midnight
        :return: True if the time_start time or duration were modified
        """

        # snap to the number of minutes in the block size
        hours = self.hours
        hours = max(hours, min_start_time)
        if hours + duration > max_end_time:
            hours = max_end_time - duration
        hour, minute = get_hour_minutes_from_hours(hours)
        minute = round(minute / round_to_minutes) * round_to_minutes

        # not changed
        if minute == self.minute and self.hour == hour:
            return False

        # update scheduled_time
        self.update_clock(hour + minute/60)
        return True

    def __sub__(self, other) -> float:
        return self.hours - other.hours

    def __eq__(self, other):
        return self.hour == other.hour and self.minute == other.minute

    def __lt__(self, other):
        return (self.hour, self.minute) < (other.hour, other.minute)

    def __str__(self):
        return f"{self.hour}:{self.minute:02d}"


class ClockTime(ScheduleTime):
    """
    Manage time by starting with the string representation
    """

    def __init__(self, string_time: str, default_start: str = "8:00"):
        """
        :param string_time: a string representation of the 24-clock
        """
        string_time = string_time.strip()

        if not re.match(r"^[12]?\d:\d{2}$", string_time):
            string_time = default_start
        hour, minute = (int(x) for x in string_time.split(":"))
        hours = hour + minute / 60
        super().__init__(hours)


