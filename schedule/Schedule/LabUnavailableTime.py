from __future__ import annotations
import Time_slot
from .ScheduleEnums import WeekDay
import Schedule


def lab_unavailable_id_generator(max_id: int = 0):
    the_id = max_id + 1
    while True:
        yield the_id
        the_id = the_id + 1


class LabUnavailableTime(Time_slot.TimeSlot):
    """TimeSlot class representing a time in which a particular Lab is unavailable."""

    lab_unavail_id = lab_unavailable_id_generator()

    # =================================================================
    # Constructor
    # =================================================================
    def __init__(self, day: (WeekDay | str) = Time_slot.TimeSlot.DEFAULT_DAY,
                 start: str = Time_slot.TimeSlot.DEFAULT_START,
                 duration: float = Time_slot.TimeSlot.DEFAULT_DURATION, movable: bool = True, *,
                 lab_unavail_id: int = None,
                 schedule: Schedule.Schedule):
        super().__init__(day, start, duration, movable)
        self.schedule = schedule
        self.__id = lab_unavail_id if id else next(LabUnavailableTime.lab_unavail_id)

    # ====================================
    # id
    # ====================================
    @property
    def id(self):
        """Returns the unique ID for this LabUnavailableTime object."""
        return self.__id
