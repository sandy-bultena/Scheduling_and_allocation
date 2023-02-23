from __future__ import annotations
from Course import Course
from Stream import Stream
from Teacher import Teacher
import re

from database.PonyDatabaseConnection import Section as dbSection
from pony.orm import *

"""
    from Schedule.Section import Section
    from Schedule.Course import Course
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


class Section():
    """
    Describes a section (part of a course)
    """
    __instances = dict()

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, number: str = "", hours=1.5, name: str = "", course : Course = None, *args, id: int = None,
                 schedule_id: int = None):
        """
        Creates an instance of the Section class.
        - Parameter number -> The section's number.
        - Parameter hours -> The hours of class the section has per week.
        - Parameter name -> The section's name.
        """
        if len(args) > 0: raise ValueError("Error: too many positional arguments")
        if not id and not schedule_id: raise ValueError("Error: id or schedule_id must be defined")

        # LEAVE IN:
        # Allows for teacher allocations to be tracked & calculated correctly in AllocationManager,
        # since Blocks are ignored there
        self._teachers = {}
        self._allocation = {}

        self._streams = {}
        self._blocks = {}

        self.name = name
        self.number = number
        self.hours = hours
        self._num_students = 0
        self._course = course

        self.__id = id if id else Section.__create_entity(self, schedule_id)
        Section.__instances[self.__id] = self

    @db_session
    @staticmethod
    def __create_entity(instance: Section, schedule_id: int):
        entity_section = dbSection(name=instance.name, number=instance.number, hours=instance.hours,
                                 num_students=instance.num_students,
                                 course_id=instance._course.id,
                                 schedule_id=schedule_id)
        commit()
        return entity_section.get_pk()

    @staticmethod
    def __validate_hours(hours):
        try:
            hours = float(hours)
        except ValueError or TypeError:
            raise TypeError(f"{hours}: hours must be a number")
        if hours <= 0: raise TypeError(f"{hours}: hours must be larger than 0")
        return hours

    # ========================================================
    # ITERATING RELATED (STATIC)
    # ========================================================
    # --------------------------------------------------------
    # list
    # --------------------------------------------------------
    @staticmethod
    def list() -> tuple[Section]:
        """ Gets all instances of Section. Returns a tuple object. """
        return tuple(Section.__instances.values())

    # --------------------------------------------------------
    # get
    # --------------------------------------------------------
    @staticmethod
    def get(id: int) -> Section:
        """ Gets a Section with a given ID. If ID doesn't exist, returns None."""
        return Section.__instances[id] if id in Section.__instances else None

    # --------------------------------------------------------
    # reset
    # --------------------------------------------------------
    @staticmethod
    def reset():
        """ Deletes all Sections """
        for s in Section.list(): s.delete()

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
        return self._hours

    @hours.setter
    def hours(self, val):
        val = Section.__validate_hours(val)
        self._hours = val

        if self.blocks:
            self._hours = 0
            for b in self.blocks:
                self._hours += b.duration

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
    def blocks(self) -> list:
        """ Gets list of section's blocks """
        return list(self._blocks.values())

    # --------------------------------------------------------
    # title
    # --------------------------------------------------------
    @property
    def title(self) -> str:
        """ Gets name if defined, otherwise 'Section num' """
        return self.name if self.name else f"Section {self.number}"

    # --------------------------------------------------------
    # course
    # --------------------------------------------------------
    @property
    def course(self) -> Course:
        """ Gets and sets the course that contains this section """
        return self._course

    @course.setter
    def course(self, val: Course):
        if not isinstance(val, Course): raise TypeError(
            f"{type(val)}: invalid course - must be a Course object")
        self._course = val

    # --------------------------------------------------------
    # num_students
    # --------------------------------------------------------
    @property
    def num_students(self) -> int:
        """ Gets and sets the number of students in this section """
        return self._num_students

    @num_students.setter
    def num_students(self, val: int):
        self._num_students = val

    # --------------------------------------------------------
    # labs
    # --------------------------------------------------------
    @property
    def labs(self) -> set:
        """ Gets all labs assigned to all blocks in this section """
        labs = set()
        for b in self.blocks:
            for l in b.labs():
                labs.add(l)
        print(labs)
        return labs

    # --------------------------------------------------------
    # teachers
    # --------------------------------------------------------
    @property
    def teachers(self) -> set:
        """ Gets all teachers assigned to all blocks in this section """
        teachers = set()
        for b in self.blocks:
            for t in b.teachers(): teachers.add(t)
        for t in self._teachers.values(): teachers.add(t)
        return teachers

    # --------------------------------------------------------
    # streams
    # --------------------------------------------------------
    @property
    def streams(self) -> set:
        """ Gets all streams in this section """
        return set(self._streams.values())

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
    def add_hours(self, val):
        """ Adds hours to section's weekly total """
        val = Section.__validate_hours(val)
        self.hours += val
        return self.hours

    # --------------------------------------------------------
    # get_block_by_id
    # --------------------------------------------------------
    def get_block_by_id(self, id: int):
        """
        Gets block with given ID from this section
        - Parameter id -> The ID of the block to find
        """
        f = list(filter(lambda a: a.id == id, self.blocks))
        return f[0] if len(f) > 0 else None

    # --------------------------------------------------------
    # get_block
    # --------------------------------------------------------
    def get_block(self, number: int):
        """
        Gets block with given block number from this section
        - Parameter number -> The number of the block to find
        """
        for b in self.blocks:
            if not b.number: b.number = 0
            if b.number == number: return b
        return None

    # --------------------------------------------------------
    # assign_lab
    # --------------------------------------------------------
    def assign_lab(self, lab):
        """
        Assign a lab to every block in the section
        - Parameter lab -> The lab to assign
        """
        if lab:
            for b in self.blocks: b.assign_lab(lab)
        return self

    # --------------------------------------------------------
    # remove_lab
    # --------------------------------------------------------
    def remove_lab(self, lab):
        """
        Remove a lab from every block in the section
        - Parameter lab -> The lab to remove
        """
        for b in self.blocks: b.remove_lab(lab)
        return self

    # --------------------------------------------------------
    # assign_teacher
    # --------------------------------------------------------
    def assign_teacher(self, teacher):
        """
        Assign a teacher to the section
        - Parameter teacher -> The teacher to be assigned
        """
        if not isinstance(teacher, Teacher): raise TypeError(
            f"{type(teacher)}: invalid teacher - must be a Teacher object")
        if teacher:
            for b in self.blocks:
                b.assign_teacher(teacher)
            self._teachers[teacher.id] = teacher
            self._allocation[teacher.id] = self.hours
        return self

    # --------------------------------------------------------
    # set_teacher_allocation
    # --------------------------------------------------------
    def set_teacher_allocation(self, teacher, hours):
        """
        Assign number of hours to teacher for this section. Set hours to 0 to remove teacher from this section
        - Parameter teacher -> The teacher to allocate hours to
        - Parameter hours -> The number of hours to allocate
        """
        if (hours):
            hours = Section.__validate_hours(hours)
            if not self.has_teacher(teacher): self.assign_teacher(teacher)
            self._allocation[teacher.id] = float(hours)
        else:
            self.remove_teacher(teacher)

        return self

    # --------------------------------------------------------
    # get_teacher_allocation
    # --------------------------------------------------------
    def get_teacher_allocation(self, teacher) -> float:
        """
        Get the number of hours assigned to this teacher for this section
        - Parameter teacher -> The teacher to find allocation hours for
        """
        # teacher not teaching this section
        if not self.has_teacher(teacher): return 0
        # allocation defined
        if teacher.id in self._allocation:
            return self._allocation[teacher.id]
        # hours not defined, assume total hours
        else:
            return self.hours

    # --------------------------------------------------------
    # remove_teacher
    # --------------------------------------------------------
    def remove_teacher(self, teacher):
        """
        Removes teacher from all blocks in this section
        - Parameter teacher -> The teacher to be removed
        """
        if not isinstance(teacher, Teacher): raise TypeError(
            f"{type(teacher)}: invalid teacher - must be a Teacher object")
        for b in self.blocks: b.remove_teacher(teacher)
        if teacher in self.teachers: del self._teachers[teacher.id]
        if teacher.id in self._allocation: del self._allocation[teacher.id]

        return self

    # --------------------------------------------------------
    # remove_all_teachers
    # --------------------------------------------------------
    def remove_all_teachers(self):
        """ Removes all teachers from all blocks in this section """
        for t in self.teachers: self.remove_teacher(t)
        return self

    # --------------------------------------------------------
    # has_teacher
    # --------------------------------------------------------
    def has_teacher(self, teacher) -> bool:
        """
        Checks if section has teacher
        - Parameter teacher -> The teacher to check
        """
        if not isinstance(teacher, Teacher): raise TypeError(
            f"{type(teacher)}: invalid teacher - must be a Teacher object")
        if not teacher: return False
        return len(list(filter(lambda a: a.id == teacher.id, self.teachers))) > 0

    # --------------------------------------------------------
    # assign_stream
    # --------------------------------------------------------
    def assign_stream(self, *streams: Stream):
        """
        Assign streams to this section.
        - Parameter streams -> The stream(s) to be added. Streams can be added all at once
        """
        for s in streams:
            if not isinstance(s, Stream): raise TypeError(
                f"{s}: invalid stream - must be a Stream object")
            self._streams[s.id] = (s)
        return self

    # --------------------------------------------------------
    # remove_stream
    # --------------------------------------------------------
    def remove_stream(self, stream: Stream):
        """
        Remove stream from this section.
        - Parameter stream -> The stream to remove.
        """
        if not isinstance(stream, Stream): raise TypeError(
            f"{stream}: invalid stream - must be a Stream object")
        if stream.id in self._streams: del self._streams[stream.id]
        return self

    # --------------------------------------------------------
    # has_stream
    # --------------------------------------------------------
    def has_stream(self, stream: Stream) -> bool:
        """
        Check if a section has a stream
        - Parameter stream -> The stream to check
        """
        if not isinstance(stream, Stream): raise TypeError(
            f"{stream}: invalid stream - must be a Stream object")
        if not stream: return False
        return len(list(filter(lambda a: a.id == stream.id, self.streams))) > 0

    # --------------------------------------------------------
    # remove_all_streams
    # --------------------------------------------------------
    def remove_all_streams(self):
        """ Removes all streams from this section """
        for s in self.streams: self.remove_stream(s)
        return self

    # --------------------------------------------------------
    # add_block
    # --------------------------------------------------------
    def add_block(self, *blocks):
        """
        Assign blocks to this section
        - Parameter blocks -> The block(s) to assign. Block(s) can be added all at once
        """
        for b in blocks:
            # removed check to avoid circular dependency
            # if not isinstance(b, Block): raise f"{b}: invalid block - must be a Block object"
            if not hasattr(b, 'id'): raise TypeError(f"{b}: invalid block - no id found")
            self._blocks[b.id] = b
            b.section = self
        return self

    # --------------------------------------------------------
    # remove_block
    # --------------------------------------------------------
    def remove_block(self, block):
        """
        Remove a block from this section
        - Parameter block -> The block to remove
        """
        if not hasattr(block, 'id') or not hasattr(block, 'delete'): raise TypeError(
            f"{block}: invalid block - must be a Block object")
        if block.id in self._blocks: del self._blocks[block.id]
        block.delete()
        return self

    # --------------------------------------------------------
    # delete
    # --------------------------------------------------------
    @db_session
    def delete(self) -> None:
        """ Delete this object and all its dependants """
        for b in self.blocks:
            self.remove_block(b)
        if dbSection.get(id = self.id): dbSection.get(id = self.id).delete()    # should cascade and delete all associated blocks
        if self.id in Section.__instances: del Section.__instances[self.id]

    # NOTE: There's another method here called "block" in the Perl version, but from what I can tell it's the same thing as get_block_by_id with a different implementation

    # --------------------------------------------------------
    # __str__
    # --------------------------------------------------------
    def __str__(self) -> str:
        """ Returns a text string that describes the section """
        if self.name and not re.match(r"Section\s*\d*$", self.name):
            return f"Section {self.number}: {self.name}"
        else:
            return f"Section {self.number}"

    # --------------------------------------------------------
    # is_conflicted
    # --------------------------------------------------------
    def is_conflicted(self) -> bool:
        """ Checks if there is a conflict with this section """
        for b in self.blocks:
            if b.conflicted: return True
        return False

        # --------------------------------------------------------
        # conflicts - seemingly unused and/or abandoned
        # --------------------------------------------------------
        # def conflicts(self) -> list:
        """ Gets a list of conflicts related to this section """
        """conflicts = []
        for b in self.blocks:
            if hasattr(b, 'conflicts'): conflicts.extend(b.conflicts())
        return conflicts"""

    # --------------------------------------------------------
    # get_new_number
    # --------------------------------------------------------
    def get_new_number(self) -> int:
        """ Gets the first unused block number """
        number = 1
        if not self.blocks: return number
        while (self.get_block(number)):
            number += 1
        return number
