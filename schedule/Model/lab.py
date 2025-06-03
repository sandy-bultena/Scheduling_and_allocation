from __future__ import annotations
from typing import Generator

from . import _id_generator_code as id_gen
from . import TimeSlot
from .enums import ResourceType

""" SYNOPSIS/EXAMPLE:

    from Schedule.Lab import Lab
    
    lab = Lab(number = "P322")
    lab.add_unavailable_time(day = "Mon", time_start = "3:22", duration = 5)
"""

_lab_id_generator: Generator[int, int, None] = id_gen.get_id_generator()


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: _Lab (should never be instantiated directly)
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Lab:
    """
    Describes a lab (or resource if need be)

    Attributes:
    -----------
    number: str
        The room number.
    desc: str
        The title of the Lab.

    Properties:
        unavailable_slots: tuple[LabUnavailableTime]
        id: int
    """

    # =================================================================
    # constructor
    # =================================================================
    def __init__(self, number: str = "P100", description: str = '', *, lab_id: int = None):
        """Creates and returns a new Lab object."""
        self.number = number
        self.description = description
        self._unavailable: list[TimeSlot] = list()
        self.resource_type = ResourceType.lab

        self.__id = id_gen.set_id(_lab_id_generator, lab_id)

    # =================================================================
    # id
    # =================================================================
    @property
    def id(self) -> int:
        """Returns the unique ID for this Lab object."""
        return self.__id

    # =================================================
    # add_unavailable_slot
    # =================================================
    def add_unavailable_slot(self, slot: TimeSlot) -> TimeSlot:
        """Adds an existing time slot to this lab's unavailable times."""
        self._unavailable.append(slot)
        return slot

    # =================================================
    # remove_unavailable_slot
    # =================================================
    def remove_unavailable_slot(self, slot: TimeSlot) -> Lab:
        """Remove the unavailable time slot from this lab."""
        if slot in self._unavailable:
            self._unavailable.remove(slot)
        return self

    # =================================================================
    # unavailable
    # =================================================================
    @property
    def unavailable_slots(self) -> tuple[TimeSlot, ...]:
        """Returns all immutable list of unavailable time slot objects for this lab."""
        return tuple(set(self._unavailable))

    # =================================================================
    # __str__
    # =================================================================

    def __str__(self) -> str:
        """Returns a text string that describes the Lab."""
        if not self.description:
            return f"{self.number}"
        return f"{self.number}: {self.description}"

    def __repr__(self) -> str:
        return str(self)

    # ------------------------------------------------------------------------
    # for sorting
    # ------------------------------------------------------------------------
    def __lt__(self, other):
        return self.number < other.number


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
