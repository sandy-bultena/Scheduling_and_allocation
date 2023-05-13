from __future__ import annotations

import Block
import Schedule
import LabUnavailableTime
from .ScheduleEnums import WeekDay

""" SYNOPSIS/EXAMPLE:

    from Schedule.Lab import Lab
    from Schedule.Section import Section

    lab = Lab(number = "P322")
    lab.add_unavailable(day = "Mon", start = "3:22", duration = 5)
"""


def lab_id_generator(max_id: int = 0):
    the_id = max_id + 1
    while True:
        yield the_id
        the_id = the_id + 1


class Lab:
    """
    Describes a distinct, contiguous course/section/class.

    Attributes:
    -----------
    number: int
        The room number.
    desc: str
        The description of the Lab.
    """
    __instances: dict[int, Lab] = {}
    lab_id = lab_id_generator()

    # -------------------------------------------------------------------
    # new
    # --------------------------------------------------------------------
    def __init__(self, number: str = "100", descr: str = '', *, lab_id: int = None):
        """Creates and returns a new Lab object."""
        self.number = number
        self.descr = descr
        self._unavailable: dict[int, LabUnavailableTime.LabUnavailableTime] = dict()

        self.__id = lab_id if lab_id else next(Lab.lab_id)
        Lab.__instances[self.__id] = self

    # =================================================================
    # id
    # =================================================================
    @property
    def id(self) -> int:
        """Returns the unique ID for this Lab object."""
        return self.__id

    # =================================================
    # add_unavailable
    # =================================================
    def add_unavailable(self, day: WeekDay | str, start: str,
                        duration: float, schedule: Schedule.Schedule) -> Lab:
        """Creates a time slot where this lab is not available.
        
        - Parameter day => 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'

        - Parameter start => start time using 24 h clock (i.e., 1pm is "13:00")

        - Parameter duration => how long does this class last, in hours
        """
        return self.add_unavailable_slot(
            LabUnavailableTime.LabUnavailableTime(day, start, duration, schedule=schedule))

    def add_unavailable_slot(self, slot: LabUnavailableTime.LabUnavailableTime) -> Lab:
        """Adds an existing time slot to this lab's unavailable times."""
        self._unavailable[slot.id] = slot
        return self

    # =================================================
    # remove_unavailable
    # =================================================
    def remove_unavailable(self, target_id: int) -> Lab:
        """Remove the unavailable time slot from this lab.
        
        - Parameter target_id -> The ID of the time slot to be removed.

        Returns the modified Lab object.
        """
        if target_id in self._unavailable.keys():
            del self._unavailable[target_id]

        return self

    # =================================================================
    # get_unavailable
    # =================================================================

    def get_unavailable(self, target_id: int) -> LabUnavailableTime.LabUnavailableTime | None:
        """Return the unavailable time slot object for this Lab.
        
        - Parameter target_id: int -> The ID of the TimeSlot to be returned.
             
        Returns the TimeSlot object if found, None otherwise.
        """
        if target_id in self._unavailable.keys():
            return self._unavailable[target_id]
        return None

    # =================================================================
    # unavailable
    # =================================================================
    def unavailable(self) -> tuple[LabUnavailableTime.LabUnavailableTime]:
        """Returns all unavailable time slot objects for this lab."""
        return tuple(self._unavailable.values())

    # =================================================================
    # __str__
    # =================================================================

    def __str__(self) -> str:
        """Returns a text string that describes the Lab."""
        if not self.descr:
            return f"{self.number}"
        return f"{self.number}: {self.descr}"

    def __repr__(self) -> str:
        return str(self)

    # ===================================
    # list [tuple]
    # ===================================
    @staticmethod
    def list() -> tuple[Lab]:
        """Returns an immutable tuple containing all instances of the Lab class."""
        return tuple(Lab.__instances.values())

    # =================================================================
    # get_by_number
    # =================================================================
    @staticmethod
    def get_by_number(number: str) -> Lab | None:
        """Returns the Lab which matches this Lab number, if it exists."""
        found = [lab for lab in Lab.list() if lab.number == number]
        return found[0] if found else None

    # =================================================================
    # get
    # =================================================================
    @staticmethod
    def get(lab_id: int) -> Lab | None:
        """Returns the Lab object matching the specified ID, if it exists."""
        if lab_id in Lab.__instances.keys():
            return Lab.__instances[lab_id]
        return None

    # =================================================================
    # share_blocks
    # =================================================================
    @staticmethod
    def share_blocks(block1: Block.Block, block2: Block.Block) -> bool:
        """Checks whether there are Labs which share the two specified Blocks."""

        # Count occurrences in both sets and ensure that all values are < 2
        occurrences = {}
        for lab in block1.labs():
            if lab.id not in occurrences.keys():
                occurrences[lab.id] = 0
            occurrences[lab.id] += 1
        for lab in block2.labs():
            if lab.id not in occurrences.keys():
                occurrences[lab.id] = 0
            occurrences[lab.id] += 1

        # A count of 2 means that they are in both sets.
        for lab_count in occurrences.values():
            if lab_count >= 2:
                return True

        return False

    # =================================================================
    # remove lab / delete
    # =================================================================

    def delete(self):
        """Removes this Lab from the Labs object, along with its unavailable TimeSlots."""

        # Remove the passed Lab object only if it's actually contained in the list of instances.
        if self in Lab.__instances.values():
            del Lab.__instances[self.__id]

    def remove(self):
        self.delete()

    # =================================================================
    # reset
    # =================================================================
    @staticmethod
    def reset():
        """Reset the local list of labs"""
        Lab.__instances = dict()


# =================================================================
# footer
# =================================================================

'''
=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns

Translated to Python by Evan Laverdiere

=head1 COPYRIGHT

Copyright (c) 2016, Jack Burns, Sandy Bultena, Ian Clement. 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut

1;
'''
