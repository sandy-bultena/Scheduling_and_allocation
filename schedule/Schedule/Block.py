from __future__ import annotations
from .Time_slot import TimeSlot
from .Lab import Lab
from .Section import Section
from .Teacher import Teacher
from .ScheduleEnums import WeekDay

""" SYNOPSIS:

from Schedule.Course import Course
from Schedule.Section import Section
from Schedule.Block import Block
from Schedule.Teacher import Teacher
from Schedule.Lab import Lab

block = Block(day = "Wed", start = "9:30", duration = 1.5)
course = Course(name = "Basket Weaving")
section = Section(number = 1)
teacher = Teacher("Jane", "Doe")
lab = Lab("P327")

section.add_block(block)

print(f"Block belongs to section {block.section}")

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

    def __init__(self, day: str | WeekDay, start: str, duration: float, movable: bool = True) -> None:
        """Creates a new Block object.
        
        Parameters:
            day: str -> a valid Weekday enum, ex: Weekday.Monday
            start: str -> start time using 24 h clock (i.e. 1pm is "13:00")
            duration: float -> how long does this class last, in hours
            movable: bool -> Whether this Block can be moved.
        """
        self.__sync: list[Block] = list()

        if isinstance(day, str) and len(day) == 3:
            day = day.lower()
        day = WeekDay.validate(day)
        super().__init__(day, start, duration, movable)

        self.__section: Section | None = None
        self.__teachers: dict[int, Teacher] = dict()
        self.__labs: dict[int, Lab] = dict()
        self.__conflicted = 0
        self._block_id = next(Block.block_id)

    # =================================================================
    # Properties
    # =================================================================

    @property
    def conflicted(self) -> int:
        """Gets and sets conflicted field."""
        return self.__conflicted

    @conflicted.setter
    def conflicted(self, new_conflict_number: int):
        self.__conflicted = self.conflicted | new_conflict_number

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
        super(Block, self.__class__).start.set(self, new_start)

        # If there are synchronized blocks, we must change them too.
        # Beware infinite loops!
        for other in self.synced():
            old = other.start
            if old != super().start:
                other.start = super().start

    @property
    def day(self) -> str:
        """Get/set the day of the block."""
        return super().day

    @day.setter
    def day(self, new_day: str):
        super(Block, self.__class__).day.fset(self, new_day)

        # If there are synchronized blocks, change them too.
        # Once again, beware the infinite loop!
        for other in self.synced():
            old = other.day
            if old != super().day:
                other.day = super().day

    @property
    def id(self) -> int:
        """Gets the Block id."""
        return self._block_id

    @property
    def section(self) -> Section | None:
        """Gets and sets the course Section object which contains this Block."""
        return self.__section

    @section.setter
    def section(self, section: Section | None):
        self.__section = section

    # =================================================================
    # assign_lab
    # =================================================================
    def assign_lab(self, *args: Lab) -> Block:
        """Assign a lab, or labs, to this block"""
        for lab in args:
            if not isinstance(lab, Lab):
                raise TypeError(f"<{lab}>: invalid lab - must be a Lab object.")

            self.__labs[lab.id] = lab

        return self

    # =================================================================
    # remove_lab
    # =================================================================
    def remove_lab(self, lab: Lab) -> Block:
        """Removes the specified Lab from this Block."""

        if lab.id in self.__labs.keys():
            del self.__labs[lab.id]
        return self

    # =================================================================
    # remove_all_labs
    # =================================================================
    def remove_all_labs(self) -> Block:
        """Removes ALL Labs from this Block."""
        self.__labs.clear()
        return self

    # =================================================================
    # labs
    # =================================================================
    def labs(self) -> tuple[Lab]:
        """Returns an immutable list of the labs assigned to this block."""
        return tuple(self.__labs.values())

    # =================================================================
    # has_lab
    # =================================================================
    def has_lab(self, lab: Lab) -> bool:
        """Returns true if the Block has the specified Lab."""
        if not lab or not isinstance(lab, Lab):
            return False
        return lab.id in self.__labs

    # =================================================================
    # assign_teacher
    # =================================================================
    def assign_teacher(self, *args: Teacher) -> Block:
        """Assigns a new teacher, or new teachers to this Block."""

        for teacher in args:
            # Verify that this teacher is, in fact, a Teacher.
            if not isinstance(teacher, Teacher):
                raise TypeError(f"<{teacher}>: invalid teacher - must be a Teacher object.")

            self.__teachers[teacher.id] = teacher

        return self

    # =================================================================
    # remove_teacher
    # =================================================================
    def remove_teacher(self, teacher: Teacher) -> Block:
        """Removes the specified Teacher from this Block."""
        # If the teachers dict contains an entry for this Teacher, remove it.
        if teacher.id in self.__teachers.keys():
            del self.__teachers[teacher.id]

        return self

    # =================================================================
    # remove_all_teachers
    # =================================================================
    def remove_all_teachers(self) -> Block:
        """Removes ALL teachers from this Block."""
        self.__teachers.clear()
        return self

    # =================================================================
    # teachers
    # =================================================================
    def teachers(self) -> tuple[Teacher]:
        """Returns a list of teachers assigned to this Block."""
        return tuple(self.__teachers.values())

    # =================================================================
    # has_teacher
    # =================================================================
    def has_teacher(self, teacher: Teacher) -> bool:
        """Returns True if this Block has the specified Teacher."""
        if not teacher or not isinstance(teacher, Teacher):
            return False
        return teacher.id in self.__teachers

    # =================================================================
    # sync_block
    # =================================================================
    def sync_block(self, block: Block) -> Block:
        """The new Block object will be synced with this one 
        (i.e., changing the start time of this Block will change the start time of the
        synced block)."""
        self.__sync.append(block)
        return self

    # =================================================================
    # unsync_block
    # =================================================================
    def unsync_block(self, block: Block) -> Block:
        """Removes syncing of Block from this Block."""

        if block in self.__sync:
            self.__sync.remove(block)
        block.unsync_block(self)

        return self

    # =================================================================
    # synced
    # =================================================================
    def synced(self) -> tuple[Block]:
        """Returns an array ref of the Blocks which are synced to this Block."""
        return tuple(self.__sync)

    # =================================================================
    # reset_conflicted
    # =================================================================
    def reset_conflicted(self):
        """Resets conflicted field."""
        self.__conflicted = 0

    # =================================================================
    # is_conflicted  # existential crisis :)
    # =================================================================
    def is_conflicted(self) -> bool:
        """Returns true if there is a conflict with this Block, false otherwise."""
        return self.conflicted != 0

    # =================================================================
    # string representation of object
    # =================================================================
    def __str__(self) -> str:
        """Returns a text string that describes the Block.

        Includes information on any Section and Labs related to this Block."""
        text = ""

        if self.section:
            if self.section.course:
                text += self.section.course.name + " "
            text += f"{self.section.number} "

        text += f"{self.day} {self.start} for {self.duration} hours, in "
        text += ", ".join(str(lab) for lab in self.labs())

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
