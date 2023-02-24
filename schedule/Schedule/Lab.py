from __future__ import annotations
from Time_slot import TimeSlot

from database.PonyDatabaseConnection import Lab as dbLab, TimeSlot as dbTimeSlot
from pony.orm import *

""" SYNOPSIS/EXAMPLE:

    from Schedule.Lab import Lab
    from Schedule.Section import Section

    lab = Lab(number = "P322")
    lab.add_unavailable(day = "Mon", start = "3:22", duration = 5)
"""


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
    __instances = {}

    # -------------------------------------------------------------------
    # new
    # --------------------------------------------------------------------

    def __init__(self, number: str = "100", descr: str = '', id: int = None):
        """Creates and returns a new Lab object."""
        self.number = number
        self.descr = descr
        self._unavailable: dict[int, TimeSlot] = {}

        self.__id = id if id else Lab.__create_entity(self)
        Lab.__instances[self.__id] = self

    @db_session
    @staticmethod
    def __create_entity(instance: Lab):
        entity_lab = dbLab(number=instance.number,
                           description=instance.descr)
        commit()
        return entity_lab.get_pk()

    # =================================================================
    # id
    # =================================================================

    @property
    def id(self):
        """Returns the unique ID for this Lab object."""
        return self.__id

    # =================================================================
    # number
    # =================================================================

    @property
    def number(self):
        """Sets/returns the room number for this Lab object."""
        return self.__number

    @number.setter
    def number(self, new_value):
        self.__number = new_value

    # =================================================================
    # descr
    # =================================================================

    @property
    def descr(self):
        """Sets/returns the description for this Lab object."""
        return self.__descr

    @descr.setter
    def descr(self, new_value: str):
        self.__descr = new_value

    # =================================================
    # add_unavailable
    # =================================================
    def add_unavailable(self, day: str, start: str, duration: float):
        """Creates a time slot where this lab is not available.
        
        - Parameter day => 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'

        - Parameter start => start time using 24 h clock (i.e., 1pm is "13:00")

        - Parameter duration => how long does this class last, in hours
        """
        # if not hasattr(self, '_unavailable'):
        #     self._unavailable: dict[int, TimeSlot] = {}

        # Create a TimeSlot.
        return self.add_unavailable_slot(TimeSlot(day, start, duration))
    
    def add_unavailable_slot(self, slot : TimeSlot) -> Lab:
        """Adds an existing time slot to this lab's unavailable times."""
        self._unavailable[slot.id] = slot
        self.__add_entity_unavailable(slot)
        return self

    @db_session
    def __add_entity_unavailable(self, instance: TimeSlot):
        """Links the passed TimeSlot's entity to this Lab's corresponding entity in the database."""
        entity_lab = dbLab.get(id=self.id)
        entity_slot = dbTimeSlot.get(id=instance.id)
        if entity_lab is not None and entity_slot is not None:
            entity_slot.unavailable_lab_id = entity_lab

    # =================================================
    # remove_unavailable
    # =================================================
    def remove_unavailable(self, target_id: int):
        """Remove the unavailable time slot from this lab.
        
        - Parameter target_id -> The ID of the time slot to be removed.

        Returns the modified Lab object.
        """
        if target_id in self._unavailable.keys():
            self.__delete_unavailable_entity(target_id)
            del self._unavailable[target_id]

        return self

    @db_session
    def __delete_unavailable_entity(self, slot_id: int):
        """Removes a TimeSlot entity with the passed ID from the database."""
        entity_slot = dbTimeSlot.get(id=slot_id)
        if entity_slot is not None:
            entity_slot.delete()

    # =================================================================
    # get_unavailable
    # =================================================================

    def get_unavailable(self, target_id: int):
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

    def unavailable(self):
        """Returns all unavailable time slot objects for this lab."""
        return list(self._unavailable.values())

    # =================================================================
    # __str__
    # =================================================================

    def __str__(self) -> str:
        """Returns a text string that describes the Lab."""
        if not self.__descr:
            return f"{self.__number}"
        return f"{self.__number}: {self.__descr}"

    # =================================================================
    # print_description
    # =================================================================
    def print_description(self) -> str:
        """Returns a text string that describes the Lab."""
        return self.__str__()

    # ===================================
    # list [tuple]
    # ===================================
    @staticmethod
    def list():
        """Returns an immutable tuple containing all instances of the Lab class."""
        return tuple(Lab.__instances.values())

    # =================================================================
    # get_by_number
    # =================================================================
    @staticmethod
    def get_by_number(number: str) -> Lab | None:
        """Returns the Lab which matches this Lab number, if it exists."""
        if not number:
            return

        for lab in Lab.list():
            if lab.number == number:
                return lab
        return None

    # =================================================================
    # get
    # =================================================================
    @staticmethod
    def get(lab_id: int) -> Lab | None:
        """Returns the Lab object matching the specified ID, if it exists."""
        # for lab in Lab.__instances.values():
        #     if lab.id == lab_id:
        #         return lab
        if lab_id in Lab.__instances.keys():
            return Lab.__instances[lab_id]
        return None

    # =================================================================
    # share_blocks
    # =================================================================
    @staticmethod
    def share_blocks(block1, block2):
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
            # Remove any TimeSlots associated with this Lab.
            for slot in self.unavailable():
                TimeSlot._TimeSlot__instances.remove(slot)
                del self._unavailable[slot.id]

            # Then remove the Lab entity and its TimeSlot entities from the database.
            Lab.__delete_entity(self)

            # Finally, remove the Lab itself from the list of instances.
            del Lab.__instances[self.__id]

    @db_session
    @staticmethod
    def __delete_entity(instance: Lab):
        """Removes the Lab's corresponding records from the Lab and TimeSlot tables of the
        database. """
        entity_lab = dbLab.get(id=instance.id)
        if entity_lab is not None:
            # Cannot get the database to enact a cascade delete of the timeslots when lab is
            # deleted, so the unavailable timeslots must be deleted manually.
            for slot in entity_lab.unavailable_slots:
                slot.delete()
            entity_lab.delete()


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
