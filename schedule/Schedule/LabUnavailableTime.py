from __future__ import annotations
import Time_slot
import Schedule
from ScheduleEnums import WeekDay
from pony.orm import *


class LabUnavailableTime(Time_slot.TimeSlot):
    """TimeSlot class representing a time in which a particular Lab is unavailable."""
    # =================================================================
    # Class/Global Variables
    # =================================================================
    __instances: dict[int, LabUnavailableTime] = {}

    # =================================================================
    # Constructor
    # =================================================================
    def __init__(self, day: (WeekDay | str) = Time_slot.TimeSlot.DEFAULT_DAY,
                 start: str = Time_slot.TimeSlot.DEFAULT_START,
                 duration: float = Time_slot.TimeSlot.DEFAULT_DURATION, movable: bool = True, *,
                 id: int = None,
                 schedule: Schedule.Schedule):
        super().__init__(day, start, duration, movable, id=id)
        self.schedule = schedule
        self.__id = id if id else LabUnavailableTime.__create_entity(self)
        LabUnavailableTime.__instances[self.id] = self

    @db_session
    @staticmethod
    def __create_entity(instance: LabUnavailableTime) -> int:
        """Creates a database record of a passed LabUnavailableTime object.

        Returns the record's automatically-generated id."""
        # TODO: Fill me in once the database class has been defined.
        pass

    # ====================================
    # id
    # ====================================
    @property
    def id(self):
        """Returns the unique ID for this LabUnavailableTime object."""
        return self.__id
