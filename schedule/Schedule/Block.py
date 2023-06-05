from __future__ import annotations
from typing import *
from .TimeSlot import TimeSlot
import schedule.Schedule.IDGeneratorCode as id_gen

""" SYNOPSIS:

from Schedule.Course import Course
from Schedule.Block import Block
from Schedule.Teacher import Teacher
from Schedule.Lab import Lab

block = Block(day = "Wed", start = "9:30", duration = 1.5)
teacher = Teacher("Jane", "Doe")
lab = Lab("P327")

block.add_teacher(teacher)
block.remove_teacher(teacher)
block.teachers()

block.add_lab(lab)
block.remove_lab(lab)
block.labs()
"""

_block_id_generator: Generator[int, Any, None] = id_gen.get_id_generator()


class Lab(Protocol):
    number: str  # needed for __str__ method


class Teacher(Protocol):
    pass


class Stream(Protocol):
    pass


class ParentContainer(Protocol):
    @property
    def id(self) -> int: yield ...

    @property
    def title(self) -> str: yield ...


class Block:
    """
    Describes a block which is a specific time slot for teaching part of a section of a course.
    """

    # =================================================================
    # Class Variables
    # =================================================================

    # =================================================================
    # Constructor
    # =================================================================

    def __init__(self, section: ParentContainer, time_slot: TimeSlot, block_id=None) -> None:
        """Creates a new Block object.
        """
        self._sync: list[Block] = list()
        self.section = section
        self.time_slot = time_slot

        self._teachers: set[Teacher] = set()
        self._labs: set[Lab] = set()
        self._conflicted = 0
        self.__block_id = id_gen.set_id(_block_id_generator, block_id)

    # =================================================================
    # Properties
    # =================================================================

    @property
    def conflicted_number(self) -> int:
        """Gets and sets conflicted_number field."""
        return self._conflicted

    def adjust_conflicted_number(self, new_conflict_number: int):
        self._conflicted = self.conflicted_number | new_conflict_number

    def reset_conflicted(self):
        """Resets conflicted_number field."""
        self._conflicted = 0

    @property
    def is_conflicted(self) -> bool:
        """Returns true if there is a conflict with this Block, false otherwise."""
        return self.conflicted_number != 0

    @property
    def description(self) -> str:
        """Returns text string that describes this Block."""
        text = f"{self.time_slot.day}, {self.time_slot.start} {self.time_slot.duration:.1f} hour(s)"
        return text

    @property
    def start(self) -> str:
        """Get/set the start time of the Block, in 24hr clock."""
        return self.time_slot.start

    @property
    def day_number(self) -> int:
        """Get/set the day of the week."""
        return self.time_slot.day_number

    @property
    def start_number(self) -> float:
        """Get/set the start time as a float"""
        return self.time_slot.start_number

    @start.setter
    def start(self, new_start: str):
        self.time_slot.start = new_start

        # If there are synchronized blocks, we must change them too.
        # Beware infinite loops!
        for other in self.synced_blocks:
            old = other.start
            if old != self.start:
                other.start = self.start

    @property
    def day(self) -> str:
        """Get/set the day of the block."""
        return self.time_slot.day

    @day.setter
    def day(self, new_day: str):
        self.time_slot.day = new_day

        # If there are synchronized blocks, change them too.
        # Once again, beware the infinite loop!
        for other in self.synced_blocks:
            old = other.day
            if old != self.day:
                other.day = self.day

    @property
    def duration(self) -> float:
        """Get/set the duration of the block."""
        return self.time_slot.duration

    @duration.setter
    def duration(self, new_duration: float):
        self.time_slot.duration = new_duration

        # If there are synchronized blocks, change them too.
        # Once again, beware the infinite loop!
        for other in self.synced_blocks:
            old = other.duration
            if old != self.duration:
                other.duration = self.duration

    @property
    def id(self) -> int:
        """Gets the Block id."""
        return self.__block_id

    # =================================================================
    # All about labs
    # =================================================================
    @property
    def labs(self) -> tuple[Lab, ...]:
        """Returns an immutable list of the labs assigned to this block."""
        return tuple(self._labs)

    def add_lab(self, lab: Lab) -> Block:
        """Assign a new lab, to this block"""
        self._labs.add(lab)
        return self

    def remove_lab(self, lab: Lab) -> Block:
        """Removes the specified Lab from this Block."""
        self._labs.discard(lab)
        return self

    def remove_all_labs(self) -> Block:
        """Removes ALL Labs from this Block."""
        self._labs.clear()
        return self

    def has_lab(self, lab: Lab) -> bool:
        """Returns true if the Block has the specified Lab."""
        return lab in self._labs

    # =================================================================
    # All about Teachers
    # =================================================================
    @property
    def teachers(self) -> tuple[Teacher, ...]:
        """Returns an immutable list of the teachers assigned to this block."""
        return tuple(self._teachers)

    def add_teacher(self, teacher: Teacher) -> Block:
        """Assign a new teacher, to this block"""
        self._teachers.add(teacher)
        return self

    def remove_teacher(self, teacher: Teacher) -> Block:
        """Removes the specified teacher from this Block."""
        self._teachers.discard(teacher)
        return self

    def remove_all_teachers(self) -> Block:
        """Removes ALL Teachers from this Block."""
        self._teachers.clear()
        return self

    def has_teacher(self, teacher: Teacher) -> bool:
        """Returns true if the Block has the specified Lab."""
        return teacher in self._teachers

    # =================================================================
    # All about syncing
    # =================================================================
    @property
    def synced_blocks(self) -> tuple[Block, ...]:
        """Returns a tuple of the Blocks which are synced_blocks to this Block."""
        return tuple(self._sync)

    def sync_block(self, block: Block) -> Block:
        """The new Block object will be synced_blocks with this one
        (i.e., changing the start time of this Block will change the start time of the
        synced_blocks block)."""
        self._sync.append(block)
        block._sync.append(self)
        return self

    def unsync_block(self, block: Block) -> Block:
        """Removes syncing of Block from this Block."""

        if block in self._sync:
            self._sync.remove(block)
        if self in block._sync:
            block._sync.remove(self)

        return self

    # =================================================================
    # string representation of object
    # =================================================================
    def __str__(self) -> str:
        """Returns a text string that describes the Block."""
        text = ""
        text += f"{self.day} {self.start} for {self.duration} hours, in "
        text += ", ".join(str(lab.number) for lab in self.labs)
        text += f" for {self.section.title}"

        return text

    def __repr__(self) -> str:
        return self.description


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
'''
