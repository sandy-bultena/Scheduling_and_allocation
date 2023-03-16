from __future__ import annotations
import Time_slot
from ScheduleEnums import WeekDay
from pony.orm import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import Schedule
from database.PonyDatabaseConnection import LabUnavailableTime as dbUnavailableTime, \
    Schedule as dbSchedule


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
        self.__id = id if id else LabUnavailableTime.__create_entity(self, schedule.id)
        LabUnavailableTime.__instances[self.id] = self

    @db_session
    @staticmethod
    def __create_entity(instance: LabUnavailableTime, schedule_id: int) -> int:
        """Creates a database record of a passed LabUnavailableTime object.

        Returns the record's automatically-generated id."""
        # TODO: Fill me in once the database class has been defined.
        d_sched = dbSchedule[schedule_id]
        entity_time = dbUnavailableTime(day=instance.day, duration=instance.duration,
                                        start=instance.start, movable=instance.movable,
                                        schedule_id=d_sched)
        commit()
        return entity_time.get_pk()

    # ====================================
    # id
    # ====================================
    @property
    def id(self):
        """Returns the unique ID for this LabUnavailableTime object."""
        return self.__id

    # ====================================
    # delete
    # ====================================
    def delete(self):
        """Removes this LabUnavailableTime object from the application and deletes its
        corresponding database record. """
        if self in LabUnavailableTime.__instances.values():
            LabUnavailableTime.__delete_entity(self)
            del LabUnavailableTime.__instances[self.id]

    @db_session
    @staticmethod
    def __delete_entity(instance: LabUnavailableTime):
        """Removes the corresponding record of a passed LabUnavailableTime from the database."""
        # TODO: Implement me once the database LabUnavailableTime has been created.
        pass

    # ====================================
    # save
    # ====================================
    @db_session
    def save(self):
        """Saves this LabUnavailableTime object to the database."""
        # TODO: Implement me once the database LUT class is implemented.
        pass

    # ====================================
    # list
    # ====================================
    @staticmethod
    def list() -> tuple[LabUnavailableTime]:
        return tuple(LabUnavailableTime.__instances.values())

    # ====================================
    # get
    # ====================================
    @staticmethod
    def get(id: int) -> LabUnavailableTime:
        return LabUnavailableTime.__instances.get(id)
