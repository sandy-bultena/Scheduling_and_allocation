from __future__ import annotations
from .exceptions import InvalidHoursForSectionError
import re
from typing import *
import schedule.Schedule.IDGeneratorCode as id_gen
from schedule.Schedule.Block import Block
from .TimeSlot import TimeSlot

"""
    from Schedule.Section import Section
    from Schedule.Block import Block
    from Schedule.Lab import Lab
    from Schedule.Teacher import Teacher

    block = Block(day = "Wed", start = "9:30", duration = 1.5)
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

DEFAULT_HOURS = 3


class ParentContainer(Protocol):
    @property
    def title(self) -> str: yield ...


class Lab(Protocol):
    number: str  # needed for __str__ method in Block

    def __lt__(self: Lab, other: Lab) -> bool:
        pass


class Stream(Protocol):
    def __lt__(self: Stream, other: Stream) -> bool:
        pass


class Teacher(Protocol):
    def __lt__(self: Teacher, other: Teacher) -> bool:
        pass


_section_id_generator: Generator[int, int, None] = id_gen.get_id_generator()


def _validate_hours(hours: float | int) -> float:
    hours = float(hours)
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

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, course: ParentContainer, number: str = "", hours: float = DEFAULT_HOURS, name: str = "",
                 section_id: int = None):
        """
        Creates an instance of the Section class.
        - Parameter number -> The section's number.
        - Parameter hours -> The hours of class the section has per week.
        - Parameter name -> The section's name.
        """

        # LEAVE IN:
        # Allows for teacher allocations to be tracked & calculated correctly in AllocationManager,
        # since Blocks are ignored there
        self._teachers: set[Teacher] = set()
        self._streams: set[Stream] = set()
        self._allocation: dict[Teacher:float] = dict()
        self._blocks: set[Block] = set()

        self.name = name
        self.number = str(number)
        self.hours = hours
        self.num_students: int = 0
        self.course = course

        self.__id = id_gen.set_id(_section_id_generator, section_id)

    # ========================================================
    # PROPERTIES
    # ========================================================
    # --------------------------------------------------------
    # hours
    # --------------------------------------------------------
    @property
    def hours(self) -> float:
        """
        Gets and sets the number of hours per week of the section
        - When setting, will automatically calculate the total hours if the section has blocks.
        """
        if self.blocks:
            self._hours = sum((b.duration for b in self.blocks))
        return self._hours

    @hours.setter
    def hours(self, val):
        if self.blocks:
            self._hours = sum((b.duration for b in self.blocks))
        else:
            val = _validate_hours(val)
            self._hours = val

    # --------------------------------------------------------
    # id
    # --------------------------------------------------------
    @property
    def id(self) -> int:
        """ Gets the section's ID """
        return self.__id

    # --------------------------------------------------------
    # blocks
    # --------------------------------------------------------
    @property
    def blocks(self) -> tuple[Block]:
        """ Gets list of section's blocks """
        return tuple(sorted(self._blocks))

    # --------------------------------------------------------
    # title
    # --------------------------------------------------------
    @property
    def title(self) -> str:
        """ Gets name if defined, otherwise 'Section num' """
        return self.name if self.name else f"Section {self.number}"

    # --------------------------------------------------------
    # labs
    # --------------------------------------------------------
    @property
    def labs(self) -> tuple[Lab]:
        """ Gets all labs assigned to all blocks in this section """
        labs: set[Lab] = set()
        for b in self.blocks:
            for lab in b.labs:
                labs.add(lab)
        return tuple(sorted(labs))

    # --------------------------------------------------------
    # teachers
    # --------------------------------------------------------
    @property
    def teachers(self) -> tuple[Teacher]:
        """ Gets all teachers assigned to all blocks in this section """
        teachers = set()
        teachers.update(self._teachers)
        for b in self.blocks:
            teachers.update(b.teachers)

        return tuple(sorted(teachers))

    # --------------------------------------------------------
    # teachers
    # --------------------------------------------------------
    @property
    def section_defined_teachers(self) -> tuple[Teacher]:
        """ Gets all teachers specifically assigned to the section """
        return self._teachers


    # --------------------------------------------------------
    # streams
    # --------------------------------------------------------
    @property
    def streams(self) -> tuple[Stream, ...]:
        """ Gets all streams in this section """
        return tuple(sorted(self._streams))

    # --------------------------------------------------------
    # allocated_hours
    # --------------------------------------------------------
    @property
    def allocated_hours(self) -> float:
        """
        Gets the total number of hours that have been allocated
        """
        return sum(self.get_teacher_allocation(t) for t in self.teachers)

    # ========================================================
    # METHODS
    # ========================================================

    # --------------------------------------------------------
    # add_hours
    # --------------------------------------------------------
    def add_hours(self, val: float | int):
        """ Adds hours to section's weekly total """
        val = _validate_hours(val)
        self.hours += val
        return self.hours

    # --------------------------------------------------------
    # add_lab
    # --------------------------------------------------------
    def add_lab(self, lab: Lab) -> Section:
        """
        Assign a lab to every block in the section
        - Parameter lab -> The lab to assign
        """
        for b in self.blocks:
            b.add_lab(lab)
        return self

    # --------------------------------------------------------
    # remove_lab
    # --------------------------------------------------------
    def remove_lab(self, lab: Lab) -> Section:
        """
        Remove a lab from every block in the section
        - Parameter lab -> The lab to remove
        """
        for b in self.blocks:
            b.remove_lab(lab)
        return self

    # --------------------------------------------------------
    # remove_all_labs
    # --------------------------------------------------------
    def remove_all_labs(self) -> Section:
        """Remove all labs from every block in the section"""
        for lab in self.labs:
            for b in self.blocks:
                b.remove_lab(lab)
        return self

    # --------------------------------------------------------
    # add_teacher
    # --------------------------------------------------------
    def add_teacher(self, teacher: Teacher) -> Section:
        """
        Assign a teacher to the section
        - Parameter teacher -> The teacher to be assigned
        """
        for b in self.blocks:
            b.add_teacher(teacher)
        self._teachers.add(teacher)
        self._allocation[teacher] = self.hours
        return self

    # --------------------------------------------------------
    # set_teacher_allocation
    # --------------------------------------------------------
    def set_teacher_allocation(self, teacher: Teacher, hours: float | int) -> Section:
        """
        Assign number of hours to teacher for this section. Set hours to 0 to remove teacher from this section
        - Parameter teacher -> The teacher to allocate hours to
        - Parameter hours -> The number of hours to allocate
        """
        if hours:
            hours = _validate_hours(hours)
            if not self.has_teacher(teacher):
                self.add_teacher(teacher)
            self._allocation[teacher] = float(hours)
        else:
            self.remove_teacher(teacher)

        return self

    # --------------------------------------------------------
    # get_teacher_allocation
    # --------------------------------------------------------
    def get_teacher_allocation(self, teacher: Teacher) -> float:
        """
        Get the number of hours assigned to this teacher for this section
        - Parameter teacher -> The teacher to find allocation hours for
        """
        # teacher not teaching this section
        if not self.has_teacher(teacher):
            return 0
        # allocation defined
        if teacher in self._allocation:
            return self._allocation[teacher]
        # hours not defined, assume total hours
        else:
            return self.hours

    # --------------------------------------------------------
    # remove_teacher
    # --------------------------------------------------------
    def remove_teacher(self, teacher: Teacher) -> Section:
        """
        Removes teacher from all blocks in this section
        - Parameter teacher -> The teacher to be removed
        """
        for b in self.blocks:
            b.remove_teacher(teacher)
        self._teachers.discard(teacher)
        if teacher in self._allocation:
            del self._allocation[teacher]

        return self

    # --------------------------------------------------------
    # remove_all_teachers
    # --------------------------------------------------------
    def remove_all_teachers(self) -> Section:
        """ Removes all teachers from all blocks in this section """
        for t in self.teachers:
            self.remove_teacher(t)
        return self

    # --------------------------------------------------------
    # has_teacher
    # --------------------------------------------------------
    def has_teacher(self, teacher: Teacher) -> bool:
        """
        Checks if section has teacher
        - Parameter teacher -> The teacher to check
        """
        return teacher in self._teachers

    # --------------------------------------------------------
    # add_stream
    # --------------------------------------------------------
    def add_stream(self, stream: Stream) -> Section:
        """
        Assign streams to this section.
        - Parameter stream -> The stream to be added.
        """
        self._streams.add(stream)
        return self

    # --------------------------------------------------------
    # remove_stream
    # --------------------------------------------------------
    def remove_stream(self, stream: Stream) -> Section:
        """
        Remove stream from this section.
        - Parameter stream -> The stream to remove.
        """
        self._streams.discard(stream)
        return self

    # --------------------------------------------------------
    # has_stream
    # --------------------------------------------------------
    def has_stream(self, stream: Stream) -> bool:
        """
        Check if a section has a stream
        - Parameter stream -> The stream to check
        """
        return stream in self._streams

    # --------------------------------------------------------
    # remove_all_streams
    # --------------------------------------------------------
    def remove_all_streams(self) -> Section:
        """ Removes all streams from this section """
        self._streams.clear()
        return self

    # --------------------------------------------------------
    # add_block
    # --------------------------------------------------------
    def add_block(self, time_slot: TimeSlot, block_id=None) -> Block:
        """ Creates and Assign a block to this section"""
        block = Block(self, time_slot, block_id)
        self._blocks.add(block)
        return block

    # --------------------------------------------------------
    # remove_block
    # --------------------------------------------------------
    def remove_block(self, block: Block) -> Section:
        """
        Remove a block from this section
        - Parameter block -> The block to remove
        """
        self._blocks.discard(block)
        return self

    # --------------------------------------------------------
    # get_block_by_id
    # --------------------------------------------------------
    def get_block_by_id(self, block_id: int) -> Block | None:
        """
        Gets block with given ID from this section
        - Parameter id -> The ID of the block to find
        """
        blocks = [b for b in self._blocks if b.id == block_id]
        if len(blocks) > 0:
            return blocks[0]
        return None

    # --------------------------------------------------------
    # has_block
    # --------------------------------------------------------
    def has_block(self, block: Block) -> bool:
        """Does this section have this block? """
        return block in self._blocks

    # --------------------------------------------------------
    # __str__
    # --------------------------------------------------------
    def __str__(self) -> str:
        """ Returns a text string that describes the section """
        if self.name and not re.match(r"Section\s*\d*$", self.name):
            return f"Section {self.number}: {self.name}"
        else:
            return f"Section {self.number}"

    def __repr__(self):
        return str(self)

    # --------------------------------------------------------
    # is_conflicted
    # --------------------------------------------------------
    def is_conflicted(self) -> bool:
        """ Checks if there is a conflict with this section """
        for b in self.blocks:
            if b.conflicted_number:
                return True
        return False

    # ------------------------------------------------------------------------
    # for sorting
    # ------------------------------------------------------------------------
    def __lt__(self, other):
        return self.number < other.number
