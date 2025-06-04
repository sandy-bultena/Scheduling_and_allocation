""" SYNOPSIS:

from Schedule.Course import Course
from Schedule.Block import Block
from Schedule.Teacher import Teacher
from Schedule.Lab import Lab

block = Block(day = "Wed", time_start = "9:30", duration = 1.5)
teacher = Teacher("Jane", "Doe")
lab = Lab("P327")

block.add_teacher(teacher)
block.remove_teacher(teacher)
block.teachers()

block.add_lab(lab)
block.remove_lab(lab)
block.labs()
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Optional
from .id_generator import IdGenerator
from .conflicts import ConflictType
OptionalId = Optional[int]

# stuff that we need just for type checking, not for actual functionality
if TYPE_CHECKING:
    from .time_slot import TimeSlot, ClockTime
    from .lab import Lab
    from .teacher import Teacher
    from .section import Section


class Block:
    """
    Describes a block which is a specific time slot for teaching part of a section of a course.
    """

    # =================================================================
    # Class Variables
    # =================================================================
    block_ids = IdGenerator()

    # =================================================================
    # Constructor
    # =================================================================

    def __init__(self, section: Section, time_slot: TimeSlot, block_id: OptionalId = None) -> None:
        """Creates a new Block object.
        """
        self._sync: list[Block] = []
        self.section = section
        self.time_slot = time_slot

        self._teachers: set[Teacher] = set()
        self._labs: set[Lab] = set()
        self.conflict = ConflictType.NONE
        self._block_id = Block.block_ids.get_new_id(block_id)

    @property
    def id(self):
        """block id"""
        return self._block_id

    def description(self) -> str:
        """Returns text string that describes this Block."""
        return str(self.time_slot)

    def movable(self) -> bool:
        """Can the block be moved, yes or no"""
        return self.time_slot.movable

    # ------------------------------------------------------------------------
    # Conflicts
    # ------------------------------------------------------------------------
    def add_conflict(self, conflict: ConflictType):
        """add a conflict to any pre-existing conflict"""
        self.conflict |= conflict

    def clear_conflicts(self):
        """remove any and all conflicts"""
        self.conflict = ConflictType.NONE

    # ------------------------------------------------------------------------
    # All about labs
    # ------------------------------------------------------------------------
    def labs(self) -> tuple[Lab, ...]:
        """Returns an immutable list of the labs assigned to this block."""
        return tuple(self._labs)

    def add_lab(self, lab: Lab):
        """Assign a new lab, to this block"""
        self._labs.add(lab)

    def remove_lab(self, lab: Lab):
        """Removes the specified Lab from this Block."""
        self._labs.discard(lab)

    def remove_all_labs(self):
        """Removes ALL Labs from this Block."""
        self._labs.clear()

    def has_lab(self, lab: Lab) -> bool:
        """Returns true if the Block has the specified Lab."""
        return lab in self._labs

    # ------------------------------------------------------------------------
    # All about Teachers
    # ------------------------------------------------------------------------
    def teachers(self) -> tuple[Teacher, ...]:
        """Returns an immutable list of the teachers assigned to this block."""
        return tuple(self._teachers)

    def add_teacher(self, teacher: Teacher):
        """Assign a new teacher, to this block"""
        self._teachers.add(teacher)

    def remove_teacher(self, teacher: Teacher):
        """Removes the specified teacher from this Block."""
        self._teachers.discard(teacher)

    def remove_all_teachers(self):
        """Removes ALL Teachers from this Block."""
        self._teachers.clear()

    def has_teacher(self, teacher: Teacher) -> bool:
        """Returns true if the Block has the specified Lab."""
        return teacher in self._teachers

    # ------------------------------------------------------------------------
    # All about syncing
    # ------------------------------------------------------------------------
    def synced_blocks(self) -> tuple[Block, ...]:
        """Returns a tuple of the Blocks which are synced_blocks to this Block."""
        return tuple(self._sync)

    def sync_block(self, block: Block):
        """The new Block object will be synced_blocks with this one
        (i.e., changing the time_start time of this Block will change the time_start time of the
        synced_blocks block)."""
        self._sync.append(block)
        block.time_slot = self.time_slot
        for b in self._sync:
            b._sync.append(self)

    def unsync_block(self, block: Block):
        """Removes syncing of Block from this Block."""

        for b in self._sync:
            if self in b._sync:
                b._sync.remove(self)
        if block in self._sync:
            self._sync.remove(block)
            block.time_slot = copy.copy(block.time_slot)

    # ------------------------------------------------------------------------
    # string representation of object
    # ------------------------------------------------------------------------
    def __str__(self) -> str:
        """Returns a text string that describes the Block."""
        text = ""
        text += f"{self.time_slot} "
        text += ", ".join(str(lab.number) for lab in self.labs())
        text += f" for {self.section.title}"

        return text

    def __repr__(self) -> str:
        return f"{self.id} - {self.description()}"

    def __lt__(self,other):
        return self.time_slot < other.time_slot

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self._block_id)


# =================================================================
# footer
# =================================================================
__copyright__ = '''

=head1 AUTHOR

Sandy Bultena

=head1 COPYRIGHT

Copyright (c) 2016, Jack Burns, Sandy Bultena, Ian Clement. 
Copyright (c) 2025, Sandy Bultena

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)
'''
