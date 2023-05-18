from __future__ import annotations

from .LabUnavailableTime import LabUnavailableTime
from .ScheduleEnums import WeekDay
from typing import *

""" SYNOPSIS/EXAMPLE:

    from Schedule.Lab import Lab
    
    lab = Lab(number = "P322")
    lab.add_unavailable_time(day = "Mon", start = "3:22", duration = 5)
"""

# ============================================================================
# keep track of all the instances of 'Lab' class, and define the generator
# that keeps track of which new id to use
# ============================================================================
_instances: dict[int, Lab] = dict()


def lab_id_generator(max_id: int = 0):
    the_id = max_id + 1
    while True:
        yield the_id
        the_id = the_id + 1


# ============================================================================
# list [tuple]
# ============================================================================
def get_all() -> tuple[Lab]:
    """Returns an immutable tuple containing all instances of the Lab class."""
    return tuple(_instances.values())


# ============================================================================
# get_by_number
# ============================================================================
def get_by_number(number: str) -> Lab | None:
    """Returns the Lab which matches this Lab number, if it exists."""
    found = [lab for lab in _instances.values() if lab.number == number]
    return found[0] if found else None


# =================================================================
# get_by_id
# =================================================================
def get_by_id(lab_id: int) -> Lab | None:
    """Returns the Lab object matching the specified ID, if it exists."""
    if lab_id in _instances.keys():
        return _instances[lab_id]
    return None


# ============================================================================
# reset
# ============================================================================
def clear_all():
    """Reset the local list of labs"""
    _instances.clear()


id_generator: Generator[int, Any, None] = lab_id_generator()


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: Lab
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Lab:
    """
    Describes a distinct, contiguous course/section/class.

    Attributes:
    -----------
    number: str
        The room number.
    desc: str
        The description of the Lab.
    """

    # =================================================================
    # constructor
    # =================================================================
    def __init__(self, number: str = "P100", descr: str = '', *, lab_id: int = None):
        """Creates and returns a new Lab object."""
        self.number = number
        self.descr = descr
        self._unavailable: list[LabUnavailableTime] = list()

        self.__id = lab_id if lab_id else next(id_generator)
        _instances[self.__id] = self

    # =================================================================
    # id
    # =================================================================
    @property
    def id(self) -> int:
        """Returns the unique ID for this Lab object."""
        return self.__id

    # =================================================
    # add_unavailable_time
    # =================================================
    def add_unavailable_time(self, day: WeekDay | str, start: str,
                             duration: float) -> Lab:
        """Creates a time slot where this lab is not available.
        
        - Parameter day => 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'

        - Parameter start => start time using 24 h clock (i.e., 1pm is "13:00")

        - Parameter duration => how long does this class last, in hours
        """
        return self.add_unavailable_slot(LabUnavailableTime(day, start, duration))

    def add_unavailable_slot(self, slot: LabUnavailableTime) -> Lab:
        """Adds an existing time slot to this lab's unavailable times."""
        self._unavailable.append(slot)
        return self

    # =================================================
    # remove_unavailable_slot
    # =================================================
    def remove_unavailable_slot(self, slot: LabUnavailableTime) -> Lab:
        """Remove the unavailable time slot from this lab."""
        if slot in self._unavailable:
            self._unavailable.remove(slot)
        return self

    # =================================================================
    # unavailable
    # =================================================================
    @property
    def unavailable_slots(self) -> tuple[LabUnavailableTime]:
        """Returns all immutable list of unavailable time slot objects for this lab."""
        return tuple(set(self._unavailable))

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

    # =================================================================
    # remove lab / delete
    # =================================================================

    def delete(self):
        """Removes this Lab from the Labs object, along with its unavailable TimeSlots."""

        # Remove the passed Lab object only if it's actually contained in the list of instances.
        if self in _instances.values():
            del _instances[self.__id]

    def remove(self):
        self.delete()


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
