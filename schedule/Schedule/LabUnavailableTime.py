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
        super().__init__(day, start, duration, movable)
        self.schedule = schedule
        self.__id = id if id else LabUnavailableTime.__create_entity(self, schedule.id)
        LabUnavailableTime.__instances[self.id] = self

    @db_session
    @staticmethod
    def __create_entity(instance: LabUnavailableTime, schedule_id: int) -> int:
        """Creates a database record of a passed LabUnavailableTime object.

        Returns the record's automatically-generated id."""
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
        entity_time = dbUnavailableTime.get(id=instance.id)
        if entity_time:
            entity_time.delete()

    # ====================================
    # save
    # ====================================
    @db_session
    def save(self) -> dbUnavailableTime:
        """Saves this LabUnavailableTime object to the database.

        Returns the corresponding LabUnavailableTime entity."""
        # TODO: Consider passing in the Schedule as an argument.
        d_time = dbUnavailableTime.get(id=self.id)
        if not d_time:
            d_sched = dbSchedule.get(id=self.schedule.id)
            d_time = dbUnavailableTime(day=self.day, duration=self.duration, start=self.start,
                                       schedule_id=d_sched)
        d_time.day = self.day
        d_time.duration = self.duration
        d_time.start = self.start
        d_time.movable = self.movable
        return d_time

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
    def get(id: int) -> LabUnavailableTime | None:
        return LabUnavailableTime.__instances.get(id)

    # ====================================
    # get
    # ====================================
    @staticmethod
    def reset():
        """Resets the local list of unavailable times."""
        LabUnavailableTime.__instances = dict()
