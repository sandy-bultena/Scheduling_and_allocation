from __future__ import annotations
from .Streams import Stream
from .Teachers import Teacher
from .Block import Block
from .Labs import Lab
from .exceptions import InvalidHoursForSectionError
import re
from typing import *
import schedule.Schedule.IDGeneratorCode as id_gen


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
    
    section.assign_teacher(teacher)
    section.remove_teacher(teacher)
    section.teachers

    section.add_lab(lab)
    section.remove_lab(lab)
    section.labs()
"""

DEFAULT_HOURS: float = 1.5


# ============================================================================
# keep track of all the instances of 'Sections' class, and define the generator
# that keeps track of which new id to use
# ============================================================================
_instances: dict[int, Lab] = dict()
_section_id_generator: Generator[int, int, None] = id_gen.get_id_generator()


# =====================================================================================
# get_section_with_this_block
# =====================================================================================
def get_section_with_this_block(block: Block) -> Section | None:
    """A block belongs to a stream, which stream is it?"""
    if block.id in _block_id_to_section_id:
        section_id = _block_id_to_section_id[block.id]
        if section_id in _all_sections:
            return _all_sections[section_id]
    return None


_block_id_to_section_id: dict[int, int] = dict()
_all_sections: dict[id, Section] = dict()


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
    def __init__(self, number: str = "", hours: float = DEFAULT_HOURS, name: str = "",
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
        self._teachers: dict[int, Teacher] = dict()
        self._allocation: dict[int, float] = dict()
        self._streams: dict[int, Stream] = dict()
        self._blocks: dict[int, Block] = dict()

        self.name = name
        self.number = str(number)
        self.hours = hours
        self.num_students: int = 0

        self.__id = id_gen.set_id(_section_id_generator, section_id)
        _all_sections[self.__id] = self

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
        return tuple(self._blocks.values())

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
        return tuple(labs)

    # --------------------------------------------------------
    # teachers
    # --------------------------------------------------------
    @property
    def teachers(self) -> tuple[Teacher]:
        """ Gets all teachers assigned to all blocks in this section """
        teachers: set[Teacher] = set()
        for b in self.blocks:
            for teacher in b.teachers:
                teachers.add(teacher)

        for t in self._teachers.values():
            teachers.add(t)
        return tuple(teachers)

    # --------------------------------------------------------
    # streams
    # --------------------------------------------------------
    @property
    def streams(self) -> tuple[Stream]:
        """ Gets all streams in this section """
        return tuple(set(self._streams.values()))

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
    # assign_lab
    # --------------------------------------------------------
    def assign_lab(self, lab: Lab) -> Section:
        """
        Assign a lab to every block in the section
        - Parameter lab -> The lab to assign
        """
        for b in self.blocks:
            b.assign_lab(lab)
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
    # assign_teacher
    # --------------------------------------------------------
    def assign_teacher(self, teacher: Teacher) -> Section:
        """
        Assign a teacher to the section
        - Parameter teacher -> The teacher to be assigned
        """
        for b in self.blocks:
            b.assign_teacher(teacher)
        self._teachers[teacher.id] = teacher
        self._allocation[teacher.id] = self.hours
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
                self.assign_teacher(teacher)
            self._allocation[teacher.id] = float(hours)
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
        if teacher.id in self._allocation:
            return self._allocation[teacher.id]
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
        if teacher in self.teachers:
            del self._teachers[teacher.id]
        if teacher.id in self._allocation:
            del self._allocation[teacher.id]

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
        return len([t for t in self.teachers if t.id == teacher.id]) > 0

    # --------------------------------------------------------
    # assign_stream
    # --------------------------------------------------------
    def assign_stream(self, *streams: Stream) -> Section:
        """
        Assign streams to this section.
        - Parameter streams -> The stream(s) to be added. Streams can be added all at once
        """
        for s in streams:
            self._streams[s.id] = s
        return self

    # --------------------------------------------------------
    # remove_stream
    # --------------------------------------------------------
    def remove_stream(self, stream: Stream) -> Section:
        """
        Remove stream from this section.
        - Parameter stream -> The stream to remove.
        """
        if stream.id in self._streams:
            del self._streams[stream.id]
        return self

    # --------------------------------------------------------
    # has_stream
    # --------------------------------------------------------
    def has_stream(self, stream: Stream) -> bool:
        """
        Check if a section has a stream
        - Parameter stream -> The stream to check
        """
        return len([s for s in self.streams if s.id == stream.id]) > 0

    # --------------------------------------------------------
    # remove_all_streams
    # --------------------------------------------------------
    def remove_all_streams(self) -> Section:
        """ Removes all streams from this section """
        for s in self.streams:
            self.remove_stream(s)
        return self

    # --------------------------------------------------------
    # add_block
    # --------------------------------------------------------
    def add_block(self, *blocks: Block) -> Section:
        """
        Assign blocks to this section
        - Parameter blocks -> The block(s) to assign. Block(s) can be added all at once
        """
        for b in blocks:
            self._blocks[b.id] = b
            _block_id_to_section_id[b.id] = self.id
        return self

    # --------------------------------------------------------
    # remove_block
    # --------------------------------------------------------
    def remove_block(self, block: Block) -> Section:
        """
        Remove a block from this section
        - Parameter block -> The block to remove
        """
        if block.id in self._blocks:
            del self._blocks[block.id]
        if block.id in _block_id_to_section_id:
            del _block_id_to_section_id[block.id]
        return self

    # --------------------------------------------------------
    # get_block_by_id
    # --------------------------------------------------------
    def get_block_by_id(self, block_id: int) -> Block | None:
        """
        Gets block with given ID from this section
        - Parameter id -> The ID of the block to find
        """
        if block_id in self._blocks.keys():
            return self._blocks[block_id]
        return None

    # --------------------------------------------------------
    # has_block
    # --------------------------------------------------------
    def has_block(self, block: Block) -> bool:
        """Does this section have this block? """
        return self.get_block_by_id(block.id) is not None

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
