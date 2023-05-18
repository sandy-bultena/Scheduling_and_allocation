from __future__ import annotations
from .Time_slot import TimeSlot
from .Labs import Lab
from .Teacher import Teacher
from .Stream import Stream
from .ScheduleEnums import WeekDay

""" SYNOPSIS:

from Schedule.Course import Course
from Schedule.Section import Section
from Schedule.Block import Block
from Schedule.Teacher import Teacher
from Schedule.Lab import Lab

block = Block(day = "Wed", start = "9:30", duration = 1.5)
teacher = Teacher("Jane", "Doe")
lab = Lab("P327")

section.add_block(block)

block.assign_teacher(teacher)
block.remove_teacher(teacher)
block.teachers()

block.assign_lab(lab)
block.remove_lab(lab)
block.labs()
"""


def block_id_generator(max_id: int = 0):
    the_id = max_id + 1
    while True:
        yield the_id
        the_id = the_id + 1


class Block(TimeSlot):
    """
    Describes a block which is a specific time slot for teaching part of a section of a course.
    """

    # =================================================================
    # Class Variables
    # =================================================================
    _DEFAULT_DAY = 'mon'
    __instances: dict[int, Block] = {}
    block_id = block_id_generator()

    # =================================================================
    # Constructor
    # =================================================================

    def __init__(self, day: str | WeekDay, start: str, duration: float, movable: bool = True, block_id=0) -> None:
        """Creates a new Block object.
        
        Parameters:
            day: str -> a valid Weekday enum, ex: Weekday.Monday
            start: str -> start time using 24 h clock (i.e. 1pm is "13:00")
            duration: float -> how long does this class last, in hours
            movable: bool -> Whether this Block can be moved.
        """
        self._sync: list[Block] = list()

        if isinstance(day, str) and len(day) == 3:
            day = day.lower()
        day = WeekDay.validate(day)
        super().__init__(day, start, duration, movable)

        self._teachers: list[Teacher] = list()
        self._labs: list[Lab] = list()
        self._streams: list[Stream] = list()
        self._conflicted = 0
        self._block_id = block_id if block_id else next(Block.block_id)

    # =================================================================
    # Properties
    # =================================================================

    @property
    def conflicted_number(self) -> int:
        """Gets and sets conflicted_number field."""
        return self._conflicted

    @conflicted_number.setter
    def conflicted_number(self, new_conflict_number: int):
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
        text = f"{self.day}, {self.start} {self.duration} hour(s)"
        return text

    @property
    def start(self) -> str:
        """Get/set the start time of the Block, in 24hr clock."""
        return super().start

    @start.setter
    def start(self, new_start: str):
        TimeSlot.start.fset(self, new_start)

        # If there are synchronized blocks, we must change them too.
        # Beware infinite loops!
        for other in self.synced_blocks:
            old = other.start
            if old != super().start:
                other.start = super().start

    @property
    def day(self) -> str:
        """Get/set the day of the block."""
        return super().day

    @day.setter
    def day(self, new_day: str):
        TimeSlot.day.fset(self, new_day)

        # If there are synchronized blocks, change them too.
        # Once again, beware the infinite loop!
        for other in self.synced_blocks:
            old = other.day
            if old != super().day:
                other.day = super().day

    @property
    def id(self) -> int:
        """Gets the Block id."""
        return self._block_id

    # =================================================================
    # All about labs
    # =================================================================
    @property
    def labs(self) -> tuple[Lab]:
        """Returns an immutable list of the labs assigned to this block."""
        return tuple(self._labs)

    def assign_lab(self, lab: Lab) -> Block:
        """Assign a new lab, to this block"""
        if lab not in self._labs:
            self._labs.append(lab)
        return self

    def remove_lab(self, lab: Lab) -> Block:
        """Removes the specified Lab from this Block."""
        if lab in self.labs:
            self._labs.remove(lab)
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
    def teachers(self) -> tuple[Teacher]:
        """Returns an immutable list of the teachers assigned to this block."""
        return tuple(self._teachers)

    def assign_teacher(self, teacher: Teacher) -> Block:
        """Assign a new teacher, to this block"""
        if teacher not in self._teachers:
            self._teachers.append(teacher)
        return self

    def remove_teacher(self, teacher: Teacher) -> Block:
        """Removes the specified teacher from this Block."""
        if teacher in self.teachers:
            self._teachers.remove(teacher)
        return self

    def remove_all_teachers(self) -> Block:
        """Removes ALL Teachers from this Block."""
        self._teachers.clear()
        return self

    def has_teacher(self, teacher: Teacher) -> bool:
        """Returns true if the Block has the specified Lab."""
        return teacher in self._teachers

    # =================================================================
    # All about Streams
    # =================================================================
    @property
    def streams(self) -> tuple[Stream]:
        """Returns an immutable list of the streams assigned to this block."""
        return tuple(self._streams)

    def assign_stream(self, stream: Stream) -> Block:
        """Assign a new stream, to this block"""
        if stream not in self._streams:
            self._streams.append(stream)
        return self

    def remove_stream(self, stream: Teacher) -> Block:
        """Removes the specified Stream from this Block."""
        if stream in self.teachers:
            self._teachers.remove(stream)
        return self

    def remove_all_streams(self) -> Block:
        """Removes ALL streams from this Block."""
        self._teachers.clear()
        return self

    def has_stream(self, stream: Stream) -> bool:
        """Returns true if the Block has the specified Lab."""
        return stream in self._teachers

    # =================================================================
    # All about syncing
    # =================================================================
    @property
    def synced_blocks(self) -> tuple[Block]:
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
        text += ", ".join(str(lab) for lab in self.labs)

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
