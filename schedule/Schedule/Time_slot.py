from __future__ import annotations
import re
from warnings import warn

from ScheduleEnums import WeekDay, WeekDayNumber

from database.PonyDatabaseConnection import TimeSlot as dbTimeSlot
from pony.orm import *

# TODO: Print statements are not good in a gui app.  Maybe we should change them log?

""" SYNOPSIS/EXAMPLE:

    from Schedule.Time_slot import TimeSlot

    time_slot = TimeSlot(day = "Wed", start = "9:30", duration = 1.5, movable = True)
"""


class TimeSlot:
    """
    A time slot is specified by a day of the week, start time, length (in hours), and whether or
    not it is allowed to move.
    
    Example: The 'Block' object has a time slot used for teaching, whilst a 'Lab' object has a
    time slot indicating when it is not available.
    """
    # =================================================================
    # Class/Global Variables
    # =================================================================
    __instances = {}
    MAX_HOUR_DIV = 2
    DEFAULT_DAY = WeekDay.Monday.value
    DEFAULT_START = "8:00"
    DEFAULT_DURATION = 1.5

    # =================================================================
    # Constructor
    # =================================================================

    def __init__(self, day: str = DEFAULT_DAY,
                 start: str = DEFAULT_START,
                 duration: float = DEFAULT_DURATION,
                 movable=True, *, id: int = None):
        """
        Creates a new TimeSlot object.

        Parameters:
        ----------

        day: str
            'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat' or 'Sun'.
            Weekday
            Weekday.Monday, Weekday.Tuesday ...
        
        start: str
            Start time using the 24hr clock (i.e., 1PM is "13:00")

        duration: float
            How long this class lasts, in hours.

        movable: bool
            Whether this time_slot can be moved or not.
        """
        # NOTE: Doing this so that day_number will also be set
        #       The order that these are implemented is important
        # day = TimeSlot.DEFAULT_DAY
        self.day_number = 0
        self.start_number = 0
        self.day = day
        self.start = start
        self.duration = duration
        self.movable = movable

        self.__id = id if id else TimeSlot.__create_entity(self)
        TimeSlot.__instances[self.__id] = self

    @db_session
    @staticmethod
    def __create_entity(instance: TimeSlot):
        entity_block = dbTimeSlot(day=instance.day, duration=instance.duration,
                                  start=instance.start, movable=instance.movable)
        commit()
        return entity_block.get_pk()

    # ====================================
    # id
    # ====================================
    @property
    def id(self):
        """Returns the unique ID for this TimeSlot object."""
        return self.__id

    # ====================================
    # day
    # ====================================
    @property
    def day(self):
        """Get/set the day of the week for this TimeSlot."""
        return self.__day

    @day.setter
    def day(self, new_day: str):

        try:
            self.__day = WeekDay.validate(new_day)
            self.day_number = WeekDayNumber[self.__day].value

        # bad inputs, default to default_day
        except ValueError:
            warn(f"<{new_day}>: invalid day specified... setting to {TimeSlot.DEFAULT_DAY}",
                 UserWarning, stacklevel=2)
            self.__day = TimeSlot.DEFAULT_DAY
            self.day_number = WeekDayNumber[TimeSlot.DEFAULT_DAY].value

    # ====================================
    # start
    # ====================================
    @property
    def start(self):
        """Get/set the start time of the TimeSlot, in 24hr clock."""
        return self.__start

    @start.setter
    def start(self, new_value: str):
        if not re.match("^[12]?[0-9]:(00|15|30|45)$", str(new_value)):
            print(f"<{new_value}>: invalid start time\nchanged to {TimeSlot.DEFAULT_START}")
            new_value = TimeSlot.DEFAULT_START

        self.__start = new_value
        hour, minute = (int(x) for x in new_value.split(":"))
        self.start_number = hour + minute / 60

    # ====================================
    # end
    # ====================================

    def end(self):
        """Gets the TimeSlot's end time in 24-hour clock format."""
        current_start = self.start_number
        end = current_start + self.duration
        hour = f"{int(end)}"
        minute = f"{int((end * 60) % 60):02d}"
        return f"{hour}:{minute}"

    # ====================================
    # duration
    # ====================================
    @property
    def duration(self):
        """Gets and sets the length of the TimeSlot, in hours."""
        return self.__duration

    @duration.setter
    def duration(self, new_dur):
        if .25 > new_dur > 0:
            new_dur = .5
        else:
            temp = 2 * new_dur
            rounded = int(float(temp) + 0.5)
            new_dur = rounded / 2
        # No TimeSlot can be longer than 8 hours.
        if new_dur > 8:
            new_dur = 8
        # TimeSlots can't have a negative duration.
        if new_dur <= 0:
            print(f"<{new_dur}>: invalid duration\nchanged to {TimeSlot.DEFAULT_DURATION}")
            new_dur = TimeSlot.DEFAULT_DURATION
        self.__duration = new_dur

    # region movable, start_number & day_number

    # NOTE: Supposedly, it is not Pythonic to have dedicated properties for instance attributes
    # that don't require any special circumstances, such as having only a getter with no setter
    # or requiring detailed input validation in the setter. Will ask Sandy about this to see what
    # she thinks.

    # ====================================
    # movable
    # ====================================
    @property
    def movable(self):
        """Gets and sets the course section object which contains this time_slot."""
        return self.__movable

    @movable.setter
    def movable(self, movable: bool):
        self.__movable = bool(movable)

    # ====================================
    # start_number
    # ====================================
    @property
    def start_number(self):
        """
        Sets or returns the start time in hours (i.e., 1:30 pm = 13.5 hours)
        
        This time info is set every time the start method is invoked on the object. Modifying it
        directly does NOT modify the values stored in 'day'.

        To set the day according to the data in this hash, use the method "snap_to_time".
        """
        return self.__start_number

    @start_number.setter
    def start_number(self, new_val: float):
        self.__start_number = new_val

    # ====================================
    # day_number
    # ====================================
    @property
    def day_number(self):
        """Returns a real number that defines the day of the week, starting from Monday. E.g.,
        tuesday = 2.0.
        
        This info is set every time the day property is called. Modifying this property directly
        does NOT modify the values stored in 'day'.
        
        To set the day according to the data in this property, use the method snap_to_day()."""
        return self.__day_number

    # TODO: we should not allow someone to change the day_number without also changing
    #       the day string.
    #       question: do we want day_number to be only a getter, and let user's only set the day,
    #       or do we want to let the user specify day_number, and we update the day string
    #       appropriately?
    @day_number.setter
    def day_number(self, new_val: int):
        self.__day_number = new_val

    # endregion
    # ====================================
    # snap_to_time
    # ====================================
    def snap_to_time(self, *args: int):
        """
        Takes the start number, and converts it to the nearest fraction of an hour (if
        max_hour_div = 2, then snaps to every 1/2 hour).

        Resets the 'start' property to the new clock time.

        Returns true if the new time is different than the previous time.
        """
        hour = self._snap_to_time(*args)
        minute = int((hour - int(hour)) * 60)
        start = f"{int(hour)}:{minute:02d}"

        changed = False
        if start != self.start:
            changed = True
        self.start = start
        return changed

    def _snap_to_time(self, *time: int):
        # Classes can't start before 8 AM or after 6 PM.
        min_time = time[0] if len(time) >= 1 else 8
        max_time = time[1] if len(time) >= 2 else 18

        TimeSlot.MAX_HOUR_DIV = 1 if TimeSlot.MAX_HOUR_DIV < 1 else TimeSlot.MAX_HOUR_DIV

        r_hour = self.start_number

        # Get hour and fractional hour
        hour = int(r_hour)
        frac = r_hour - hour

        # Create array of allowed fractions.
        fracs = []
        for i in range(TimeSlot.MAX_HOUR_DIV + 1):
            fracs.append(i / TimeSlot.MAX_HOUR_DIV)

        # Sort according to which one is closest to our fraction. Based on experiments in the
        # terminal, this should works while the max_hour_div is 2.
        sorted_frac = sorted(fracs, key=lambda x: abs(x - frac))

        # add hour fraction to hour.
        hour = hour + sorted_frac[0]

        # Adjust hour to minimum or maximum if necessary
        hour = min_time if hour < min_time else hour
        hour = max_time - self.duration if hour > max_time - self.duration else hour

        return hour

    # =================================================================
    # snap_to_day
    # =================================================================
    def snap_to_day(self, *args: int):
        """
        Takes the start_day and converts it to the nearest day.

        Resets the 'day' property to the appropriate string.

        """
        day_of_week = self._snap_to_day(*args)
        self.day = WeekDayNumber(day_of_week).name

    def _snap_to_day(self, *args: int):
        min_day = args[0] if len(args) >= 1 else 1
        max_day = args[1] if len(args) >= 2 else 7

        r_day = self.day_number

        day_of_week = r_day if r_day == int(r_day) else int(r_day + 0.5)
        day_of_week = min_day if not day_of_week else day_of_week
        day_of_week = max_day if day_of_week > max_day else day_of_week
        return day_of_week

    # =================================================================
    # conflicts
    # =================================================================
    def conflicts_time(self, rhs):
        """
        Tests that the current Time_Slot conflicts with another TimeSlot.
        """
        # Detect time collisions up to this error factor. Also useful for graphical applications
        # that require a small error threshold when moving a block into place.
        delta = 0.05

        # detect date collisions. If the dates differ, there's no conflict, and we can leave.
        # Otherwise, continue.
        if abs(self.day_number - rhs.day_number) >= 1 - delta:
            return False

        # Calculate the start/end for each block with the error factor removed.
        self_start = self.start_number + delta
        self_end = self.start_number + self.duration - delta
        rhs_end = rhs.start_number + rhs.duration - delta
        rhs_start = rhs.start_number + delta

        return (self_start < rhs_end) and (rhs_start < self_end)

    @staticmethod
    def list() -> tuple[TimeSlot]:
        return tuple(TimeSlot.__instances.values())

    @staticmethod
    def get(id: int) -> TimeSlot:
        return TimeSlot.__instances.get(id, None)

    # =================================================================
    # save
    # =================================================================
    @db_session
    def save(self) -> dbTimeSlot:
        """Saves this TimeSlot to the database, updating its corresponding record.

        Returns the corresponding TimeSlot database entity."""
        d_slot = dbTimeSlot.get(
            id=self.__id)  # use the __id so it refers to the time slot's ID correctly, not block ID (when relevant)
        if not d_slot: d_slot = dbTimeSlot(day=self.day, duration=self.duration, start=self.start)
        d_slot.day = self.day
        d_slot.duration = self.duration
        d_slot.start = self.start
        d_slot.movable = self.movable
        return d_slot

    # =================================================================
    # reset
    # =================================================================
    @staticmethod
    def reset():
        """Reset the local list of time slots"""
        TimeSlot.__instances = dict()


# =================================================================
# footer
# =================================================================
'''
=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns

converted to python by Jacob Levy and Evan Laverdiere

=head1 COPYRIGHT

Copyright (c) 2016, Jack Burns, Sandy Bultena, Ian Clement. 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut
'''
