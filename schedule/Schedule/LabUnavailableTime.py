from __future__ import annotations
from .Time_slot import TimeSlot
from .ScheduleEnums import WeekDay
import Schedule


class LabUnavailableTime(TimeSlot):
    """TimeSlot class representing a time in which a particular Lab is unavailable."""

    # =================================================================
    # Constructor
    # =================================================================
    def __init__(self, day: (WeekDay | str) = TimeSlot.DEFAULT_DAY,
                 start: str = TimeSlot.DEFAULT_START,
                 duration: float = TimeSlot.DEFAULT_DURATION, movable: bool = True):
        super().__init__(day, start, duration, movable)

