from Course import Course
from Stream import Stream
import re


class SectionMeta(type):
    """ Metaclass for Conflict, making it iterable """
    _sections = []
    
    def __iter__(self):
        return iter(getattr(self, '_sections', []))

class Section(metaclass=SectionMeta):
    """
    Describes a section (part of a course)
    """
    _max_id = 0

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, number : str = "", hours = 1.5, name : str = ""):
        """
        Creates an instance of the Section class.
        - Parameter number -> The section's number.
        - Parameter hours -> The hours of class the section has per week.
        - Parameter name -> The section's name.
        """
        
        self._teachers = {}
        self._allocation = {}
        self._streams = {}
        self._blocks = {}

        self.name = name
        self.number = number
        self.hours = hours
        Section._max_id += 1
        self.__id = Section._max_id
        Section._sections.append(self)
        self._num_students = 0
        self._course = None
    
    @staticmethod
    def __validate_hours(hours):
        try: hours = float(hours)
        except ValueError or TypeError: raise f"{hours}: hours must be a number"
        if hours <= 0: raise f"{hours}: hours must be > 0"
        return hours

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
    def blocks(self) -> dict:
        """ Gets list of section's blocks """
        return self._blocks

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
    def course(self, val : Course):
        if not isinstance(val, Course): raise f"{type(val)}: invalid course - must be a Course object"
        self._course = val

    # --------------------------------------------------------
    # num_students
    # --------------------------------------------------------
    @property
    def num_students(self) -> int:
        """ Gets and sets the number of students in this section """
        return self._num_students
    
    @num_students.setter
    # left default value even though setter can't be called without argument, since it can act as a hint to users
    def num_students(self, val : int = 30):
        self._num_students = val
    
    # --------------------------------------------------------
    # labs
    # --------------------------------------------------------
    @property
    def labs(self) -> set:
        """ Gets all labs assigned to all blocks in this section """
        labs = set()
        for b in self.blocks.values():
            for l in b.labs():
                labs.add(l)
        return labs
    
    # --------------------------------------------------------
    # teachers
    # --------------------------------------------------------
    @property
    def teachers(self) -> set:
        """ Gets all teachers assigned to all blocks in this section """
        teachers = set()
        for b in self.blocks.values():
            for t in b.teachers(): teachers.add(t)
        for t in self._teachers: teachers.add(t)
        return teachers

    # --------------------------------------------------------
    # streams
    # --------------------------------------------------------
    @property
    def streams(self) -> set:
        """ Gets all streams in this section """
        return set(self._streams.values())

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
    def get_block_by_id(self, id : int):
        """
        Gets block with given ID from this section
        - Parameter id -> The ID of the block to find
        """
        f = list(filter(lambda a : a.id == id, self.blocks.values()))
        return f[0] if len(f) > 0 else None
    
    # --------------------------------------------------------
    # get_block
    # --------------------------------------------------------
    def get_block(self, number : int):
        """
        Gets block with given block number from this section
        - Parameter number -> The number of the block to find
        """
        for b in self.blocks.values():
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
            for b in self.blocks.values(): b.assign_lab(lab)
        return self
    
    # --------------------------------------------------------
    # remove_lab
    # --------------------------------------------------------
    def remove_lab(self, lab):
        """
        Remove a lab from every block in the section
        - Parameter lab -> The lab to remove
        """
        for b in self.blocks.values(): b.remove_lab(lab)
        return self
    
    # --------------------------------------------------------
    # assign_teacher
    # --------------------------------------------------------
    def assign_teacher(self, teacher):
        """
        Assign a teacher to the section
        - Parameter teacher -> The teacher to be assigned
        """
        if teacher:
            for b in self.blocks.values():
                b.assign_teacher(teacher)
            self.teachers.add(teacher)
            self._allocation[teacher.id] = self.hours
        return self
    
    # --------------------------------------------------------
    # set_teacher_allocation
    # --------------------------------------------------------
    def set_teacher_allocation(self, teacher, hours):
        """
        Assign number of hours to teacher for this section
        - Parameter teacher -> The teacher to allocate hours to
        - Parameter hours -> The number of hours to allocate
        """
        if (hours):
            hours = Section.__validate_hours(hours)
            if not self.has_teacher(teacher): self.assign_teacher(teacher)
            self._allocation[teacher.id] = hours
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
        if teacher.id in self._allocation: return self._allocation[teacher.id]
        # hours not defined, assume total hours
        else: return self.hours
    
    # --------------------------------------------------------
    # allocated_hours
    # --------------------------------------------------------
    def allocated_hours(self) -> float:
        """
        Gets the total number of hours that have been allocated
        """
        return sum(self.get_teacher_allocation(t) for t in self.teachers)
    
    # --------------------------------------------------------
    # remove_teacher
    # --------------------------------------------------------
    def remove_teacher(self, teacher):
        """
        Removes teacher from all blocks in this section
        - Parameter teacher -> The teacher to be removed
        """
        for b in self.blocks.values(): b.remove_teacher(teacher)
        if teacher in self.teachers: self.teachers.remove(teacher)
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
        if not teacher: return False
        return len(list(filter(lambda a : a.id == teacher.id, self.teachers))) > 0
    
    # --------------------------------------------------------
    # assign_stream
    # --------------------------------------------------------
    def assign_stream(self, *streams : Stream):
        """
        Assign streams to this section.
        - Parameter streams -> The stream(s) to be added. Streams can be added all at once
        """
        for s in streams:
            if not isinstance(s, Stream): raise f"{s}: invalid stream - must be a Stream object"
            self.streams.add(s)
        return self
    
    # --------------------------------------------------------
    # remove_stream
    # --------------------------------------------------------
    def remove_stream(self, stream : Stream):
        """
        Remove stream from this section.
        - Parameter stream -> The stream to remove.
        """
        if not isinstance(stream, Stream): raise f"{stream}: invalid stream - must be a Stream object"
        if stream.id in self.streams: self.streams.remove(stream)
        return self
    
    # --------------------------------------------------------
    # has_stream
    # --------------------------------------------------------
    def has_stream(self, stream : Stream) -> bool:
        """
        Check if a section has a stream
        - Parameter stream -> The stream to check
        """
        if not stream: return False
        return len(list(filter(lambda a : a.id == stream.id, self.streams))) > 0
    
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
            #if not isinstance(b, Block): raise f"{b}: invalid block - must be a Block object"
            if not hasattr(b, 'id'): raise f"{b}: invalid block - no id found"
            self.blocks[b.id] = b
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
        if not hasattr(block, 'id') or not hasattr(block, 'delete'): f"{block}: invalid block - must be a Block object"
        if block.id in self.blocks: del self.blocks[block.id]
        block.delete()
        return self
    
    # --------------------------------------------------------
    # delete
    # --------------------------------------------------------
    def delete(self) -> None:
        """ Delete this object and all its dependants """
        # TODO: Confirm that Python objects can't be manually deleted
            # Relies on all references being gone, something we can't control from here
        for b in self.blocks.values():
            self.remove_block(b)
    
    # --------------------------------------------------------
    # block
    # --------------------------------------------------------
    def block(self, block_id : int):
        """
        Get block by ID.
        - Parameter block_id -> ID of the block to retrieve.
        """
        return self.blocks[block_id]
    
    # --------------------------------------------------------
    # __str__
    # --------------------------------------------------------
    def __str__(self) -> str:
        """ Returns a text string that describes the section """
        if self.name and not re.match("Section\s*\d*$", self.name): return f"Section {self.number}: {self.name}"
        else: return f"Section {self.number}"
    
    # --------------------------------------------------------
    # is_conflicted
    # --------------------------------------------------------
    def is_conflicted(self) -> bool:
        """ Checks if there is a conflict with this section """
        return len(list(filter(lambda b : hasattr(b, 'is_conflicted') and b.is_conflicted, self.blocks.values())))
    
    # --------------------------------------------------------
    # conflicts
    # --------------------------------------------------------
    def conflicts(self) -> list:
        """ Gets a list of conflicts related to this section """
        conflicts = []
        for b in self.blocks.values():
            if hasattr(b, 'conflicts'): conflicts.extend(b.conflicts())
        return conflicts
    
    # --------------------------------------------------------
    # get_new_number
    # --------------------------------------------------------
    def get_new_number(self) -> int:
        """ Gets the first unused block number """
        number = 1
        while (self.get_block(number)):
            number += 1
        return number