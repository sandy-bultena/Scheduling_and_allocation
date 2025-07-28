"""
SYNOPSIS

    from Schedule.Section import Section
    from Schedule.Block import Block
    from Schedule.Lab import Lab
    from Schedule.Teacher import Teacher

    block = Block(day = "Wed", time_start = "9:30", duration = 1.5)
    section = Section(number = 1, hours = 6)
    course = Course(name = "Basket Weaving")
    teacher = Teacher("Jane", "Doe")
    lab = Lab("P327")

    course.add_section(section)
    section.add_block(block)

    print("Section consists of the following blocks: ")
    for b in section.blocks:
        # print info about block

    section.add_teacher(teacher)
    section.remove_teacher(teacher)
    section.teachers

    section.add_lab(lab)
    section.remove_lab(lab)
    section.labs()
"""

from __future__ import annotations
import re
from typing import TYPE_CHECKING, Optional
from schedule.Utilities.id_generator import IdGenerator
from . import WeekDay
from .block import Block, DEFAULT_DURATION, DEFAULT_START, DEFAULT_DAY
from .model_exceptions import InvalidHoursForSectionError

# stuff that we need just for type checking, not for actual functionality
if TYPE_CHECKING:
    from .teacher import Teacher
    from .lab import Lab
    from .stream import Stream
    from .course import Course

DEFAULT_HOURS = 3

section_ids = IdGenerator()


def _validate_hours(hours: float) -> float:
    if hours <= 0:
        raise InvalidHoursForSectionError(f"{hours}: hours must be larger than 0")
    return hours


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: Section
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Section:
    """
    Describes a section (part of a course)
    """
    section_ids = IdGenerator()

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, course: Course, number: str = "", name: str = "",
                 section_id: Optional[int] = None):
        """
        Creates an instance of the Section class.
        :param number: The section's number.
        :param name:
        """

        # LEAVE IN:
        # Allows for teacher allocations to be tracked & calculated correctly in AllocationManager,
        # since Blocks are ignored there
        self._teachers: set[Teacher] = set()
        self._streams: set[Stream] = set()
        self._allocation: dict[Teacher:float] = dict()
        self._blocks: set[Block] = set()

        self.name = name
        self.number = number
        self.num_students: int = 0
        self.course = course

        self._section_id = Section.section_ids.get_new_id(section_id)

    # ========================================================
    # PROPERTIES
    # ========================================================
    @property
    def hours(self) -> float:
        """
        Gets and sets the number of hours per week of the section
        - When setting, will automatically calculate the total hours if the section has blocks.
        """
        if self.blocks():
            return sum((b.duration for b in self.blocks()))
        return self.course.hours_per_week

    @hours.setter
    def hours(self, val):
        if self.blocks():
            self._hours = sum((b.duration for b in self.blocks()))
        else:
            val = _validate_hours(val)
            self._hours = val

    @property
    def id(self) -> int:
        """ Gets the section's ID """
        return self._section_id

    @property
    def title(self) -> str:
        """ Gets name if defined, otherwise 'Section num' """
        return self.name if self.name else f"Section {self.number}"

    # --------------------------------------------------------
    # conflicts
    # --------------------------------------------------------
    def is_conflicted(self) -> bool:
        """ Checks if there is a conflict with this section """
        return any(map(lambda block: block.conflict.is_conflicted(), self.blocks()))

    # --------------------------------------------------------
    # blocks
    # --------------------------------------------------------
    def blocks(self) -> tuple[Block, ...]:
        """ Gets list of section's blocks """
        return tuple(sorted(self._blocks))

    def remove_block(self, block: Block):
        """ Remove a block from this section """
        self._blocks.discard(block)

    def remove_all_blocks(self):
        for block in self.blocks():
            self.remove_block(block)

    def add_block(self, day: WeekDay = DEFAULT_DAY, start: float = DEFAULT_START,
                  duration: float=DEFAULT_DURATION, movable=True, block_id=None)->Block:
        """ Creates and Assign a block to this section"""
        block = Block(self, day, start, duration, movable=movable, block_id=block_id)
        self._blocks.add(block)
        return block

    def get_block_by_id(self, block_id: int) -> Optional[Block]:
        """ Gets block with given ID from this section """
        blocks = [b for b in self._blocks if b.id == block_id]
        if len(blocks) > 0:
            return blocks[0]
        return None

    def has_block(self, block: Block) -> bool:
        """Does this section have this block? """
        return block in self._blocks

    # --------------------------------------------------------
    # labs
    # --------------------------------------------------------
    def labs(self) -> tuple[Lab, ...]:
        """ Gets all labs assigned to all blocks in this section """
        labs: set[Lab] = set()
        for b in self.blocks():
            labs.update(b.labs())
        return tuple(sorted(labs))

    def add_lab(self, lab: Lab):
        """ Assign a lab to every block in the section """
        for b in self.blocks():
            b.add_lab(lab)
        return self

    def has_lab(self, lab: Lab):
        """Is this lab attached to any of the labs in the blocks? """
        return lab in self.labs()

    def remove_lab(self, lab: Lab):
        """ Remove a lab from every block in the section """
        for b in self.blocks():
            b.remove_lab(lab)

    def remove_all_labs(self):
        """Remove all labs from every block in the section"""
        for lab in self.labs():
            for b in self.blocks():
                b.remove_lab(lab)

    # --------------------------------------------------------
    # teachers
    # --------------------------------------------------------
    def teachers(self) -> tuple[Teacher, ...]:
        """ Gets all teachers assigned to all blocks in this section and
        any teachers that were explicitly assigned to this section"""
        teachers = set()
        teachers.update(self._teachers)
        for b in self.blocks():
            teachers.update(b.teachers())
        return tuple(sorted(teachers))

    def section_defined_teachers(self) -> tuple[Teacher, ...]:
        """gets only teachers that were explicitly assigned to this section in allocation manager"""
        teachers = set()
        teachers.update(self._teachers)
        return tuple(sorted(teachers))


    def add_teacher(self, teacher: Teacher):
        """ Assign a teacher to the section """
        for b in self.blocks():
            b.add_teacher(teacher)
        self._teachers.add(teacher)
        self._allocation[teacher] = self.hours

    def remove_teacher(self, teacher: Teacher):
        """ Removes teacher from all blocks in this section """
        for b in self.blocks():
            b.remove_teacher(teacher)
        self._teachers.discard(teacher)
        if teacher in self._allocation:
            del self._allocation[teacher]

    def remove_all_teachers(self):
        """ Removes all teachers from all blocks in this section """
        for t in self.teachers():
            self.remove_teacher(t)

    def has_teacher(self, teacher: Teacher) -> bool:
        """ Checks if section has teacher """
        answer = teacher in self._teachers
        for b in self.blocks():
            answer = answer or b.has_teacher(teacher)
        return answer

    # --------------------------------------------------------
    # teacher_allocation
    # --------------------------------------------------------
    def set_teacher_allocation(self, teacher: Teacher, hours: float) :
        """Assign number of hours to teacher for this section. Set hours to 0 to remove
        teacher from this section """
        if hours == 0:
            self.remove_teacher(teacher)
        else:
            hours = _validate_hours(hours)
            if not self.has_teacher(teacher):
                self.add_teacher(teacher)
            self._allocation[teacher] = float(hours)

    def get_teacher_allocation(self, teacher: Teacher) -> float:
        """ Get the number of hours assigned to this teacher for this section """

        # teacher not teaching this section
        if not self.has_teacher(teacher):
            return 0

        # allocation defined
        if teacher in self._allocation:
            return self._allocation[teacher]

        # hours not defined, assume total hours
        else:
            return self.hours

    def allocated_hours(self) -> float:
        """ Gets the total number of hours that have been allocated """
        return sum(self.get_teacher_allocation(t) for t in self.teachers())

    # --------------------------------------------------------
    # streams
    # --------------------------------------------------------
    def streams(self) -> tuple[Stream, ...]:
        """ Gets all streams in this section """
        return tuple(sorted(self._streams))

    def add_stream(self, stream: Stream):
        """ Assign streams to this section. """
        self._streams.add(stream)

    def remove_stream(self, stream: Stream):
        """ Remove stream from this section. """
        self._streams.discard(stream)

    def has_stream(self, stream: Stream) -> bool:
        """Check if a section has a stream """
        return stream in self._streams

    def remove_all_streams(self):
        """ Removes all streams from this section """
        self._streams.clear()

    # --------------------------------------------------------
    # add_hours
    # --------------------------------------------------------
    def add_hours(self, val: float | int):
        """ Adds hours to section's weekly total """
        val = _validate_hours(val)
        self.hours += val
        return self.hours

    # --------------------------------------------------------
    # string representation
    # --------------------------------------------------------
    def __str__(self) -> str:
        """ Returns a text string that describes the section """
        if self.name and not re.match(r"Section\s*\d*$", self.name):
            return f"Section {self.number}: {self.name}"
        else:
            return f"Section {self.number}"

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return self.number < other.number

    def __hash__(self):
        return hash(self._section_id)

    def __eq__(self, other):
        return self.id == other.number
