from __future__ import annotations
from Lab import Lab
from Section import Section
from Teacher import Teacher
from Time_slot import TimeSlot

from database.PonyDatabaseConnection import Block as dbBlock, TimeSlot as dbTimeSlot, Lab as dbLab, \
    Teacher as dbTeacher, Section as dbSection
from pony.orm import *

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


class Block(TimeSlot):
    """
    Describes a block which is a specific time slot for teaching part of a section of a course.
    """

    # =================================================================
    # Class Variables
    # =================================================================

    _DEFAULT_DAY = 'mon'
    __instances = {}

    # =================================================================
    # Constructor
    # =================================================================

    def __init__(self, day: str, start: str, duration: float, number: int, *args, id: int = None,
                 time_slot_id: int = None) -> None:
        """Creates a new Block object.
        
        - Parameter day: str -> 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'
        - Parameter start: str -> start time using 24 h clock (i.e 1pm is "13:00")
        - Parameter duration: float -> how long does this class last, in hours
        - Parameter number: int -> A number representing this specific Block.
        """
        self._sync = list()
        if (id and not time_slot_id) or (time_slot_id and not id): raise ValueError(
            "Error: id and time_slot_id must be both defined or neither defined")
        if len(args) > 0: raise ValueError("Error: too many positional arguments")
        super().__init__(day, start, duration, id=time_slot_id)
        self.number = number  # NOTE: Based on the code found in CSV.pm and Section.pm
        self.__section = None
        self._teachers = dict()
        self._labs = {}
        self._conflicted = 0

        self._block_id = id if id else Block.__create_entity(self)
        Block.__instances[self._block_id] = self

    @db_session
    @staticmethod
    def __create_entity(instance: Block):
        entity_block = dbBlock(time_slot_id=instance.time_id, number=instance.number)
        commit()
        return entity_block.get_pk()

    # =================================================================
    # number
    # =================================================================

    @property
    def number(self):
        """Gets and sets the Block number."""
        return self.__number

    @number.setter
    def number(self, new_num: int):
        # NOTE: The reason it checks for strings in the Perl code is because Perl doesn't
        # distinguish between strings and numbers: A value of "0" registers as 0, and vice versa.
        if new_num is None or not isinstance(new_num, int):
            raise Exception(f"<{new_num}>: section number must be an integer and cannot be null.")
        self.__number = new_num

    # =================================================================
    # delete
    # =================================================================
    def delete(self):
        """Delete this Block object and all its dependents."""
        # self = None NOTE: So far as I can tell, the only place this method is being called is
        # in Section's remove_block( ) method, to destroy the reference to a local Block
        # parameter after said Block has already been removed from Section's array/hash of
        # Blocks. Because of this, and because it doesn't seem possible to make an object delete
        # itself in Python, I don't believe that this method is needed. Block._instances.remove(
        # self) self = None
        if self in Block.__instances.values():
            Block.__delete_entity(self)
            Block._TimeSlot__instances.remove(self)
            del Block.__instances[self._block_id]

    @db_session
    @staticmethod
    def __delete_entity(instance: Block):
        """Removes the corresponding records for a passed Block object from the Block and
        TimeSlot tables of the database. """
        entity_block = dbBlock.get(id=instance.id)
        if entity_block is not None:
            # Contrary to what you might expect, entity_block.time_slot_id is a TimeSlot entity
            # reference, not an integer.
            entity_slot: dbTimeSlot = entity_block.time_slot_id
            # Deleting the instance's TimeSlot entity will cascade delete its Block entity too.
            entity_slot.delete()

    # =================================================================
    # start
    # =================================================================
    @property
    def start(self):
        """Get/set the start time of the Block, in 24hr clock."""
        return super().start

    @start.setter
    def start(self, new_start: str):
        super(Block, self.__class__).start.fset(self, new_start)

        # If there are synchronized blocks, we must change them too.
        # Beware infinite loops!
        for other in self.synced():
            old = other.start
            if old != super().start:
                other.start = super().start  # Attempting to directly write to the backing field
                # doesn't work.
                # Fortunately, calling the property like this doesn't result in an infinite loop.

    # =================================================================
    # day
    # =================================================================
    @property
    def day(self):
        """Get/set the day of the block, in numeric format (1 for Monday, 7 for Sunday)."""
        return super().day

    @day.setter
    def day(self, new_day):
        super(Block, self.__class__).day.fset(self, new_day)

        # If there are synchronized blocks, change them too.
        # Once again, beware the infinite loop!
        for other in self.synced():
            old = other.day
            if old != super().day:
                other.day = super().day

    # ==================================================================
    # id //ALEX CODE
    # ==================================================================

    @property
    def id(self):
        """Gets the Block id."""
        return self._block_id

    @property
    def time_id(self):
        """Gets the associated Time Slot's id."""
        return super().id

    # =================================================================
    # section
    # =================================================================
    @property
    def section(self):
        """Gets and sets the course Section object which contains this Block."""
        return self.__section

    @section.setter
    def section(self, section: Section):
        if isinstance(section, Section):
            self.__section = section
            self.__set_entity_section(section.id)
        else:
            raise TypeError("<{section}>: invalid section - must be a Section object.")

    @db_session
    def __set_entity_section(self, section_id: int):
        d_section = dbSection.get(id=section_id)
        if d_section is not None:
            d_block = dbBlock[self.id]
            d_block.section_id = d_section

    # =================================================================
    # assign_lab
    # =================================================================
    def assign_lab(self, lab: Lab):
        """Assign a lab to this block."""

        # If the Block doesn't already have a labs dict, create one.
        # if not hasattr(self, '_labs'):
        #     self._labs = {}

        if not isinstance(lab, Lab):
            raise TypeError(f"<{lab}>: invalid lab - must be a Lab object.")

        # TODO: Check if this function allows multiple labs to be assigned at once in the perl
        #  version
        self._labs[lab.id] = lab
        self.__assign_entity_lab(lab.id)

        return self

    @db_session
    def __assign_entity_lab(self, lab_id: int):
        entity_lab = dbLab.get(id=lab_id)
        if entity_lab is not None:
            entity_block = dbBlock[self.id]
            # Add the lab to the entity Block's list of labs. This will automatically add the
            # Block to the lab's list of blocks, too.
            entity_block.labs.add(entity_lab)

    # =================================================================
    # remove_lab
    # =================================================================
    def remove_lab(self, lab: Lab):
        """Removes the specified Lab from this Block.

        Returns the Block object."""

        if not isinstance(lab, Lab):
            raise TypeError(f"<{lab}>: invalid lab - must be a Lab object.")

        # If the labs dict contains an entry for the specified Lab, remove it.
        if lab.id in self._labs.keys():
            self.__remove_entity_lab(lab.id)
            del self._labs[lab.id]

        return self

    @db_session
    def __remove_entity_lab(self, lab_id: int):
        """Breaks the connection between the corresponding database entities for this Block and
        the passed Lab, with deleting either of them. """
        entity_lab = dbLab.get(id=lab_id)
        if entity_lab is not None:
            entity_block = dbBlock[self.id]
            # Set.remove() breaks the connection between the Block and the Lab without actually
            # deleting either record. Only the record in the lookup table seems to be affected.
            # The responsibility of actually deleting the Lab record will be handled elsewhere.
            entity_block.labs.remove(entity_lab)

    # =================================================================
    # remove_all_labs
    # =================================================================
    def remove_all_labs(self):
        """Removes ALL Labs from this Block.
        
        Returns the Block object."""
        for lab in list(self._labs.values()):
            self.remove_lab(lab)

        return self

    # =================================================================
    # labs
    # =================================================================
    def labs(self):
        """Returns a list of the labs assigned to this block."""
        return list(self._labs.values())

    # =================================================================
    # has_lab
    # =================================================================
    def has_lab(self, lab: Lab):
        """Returns true if the Block has the specified Lab."""
        if not lab or not isinstance(lab, Lab):
            return False

        for key in self._labs:
            if self._labs[key].id == lab.id:
                return True

        return False

    # =================================================================
    # assign_teacher
    # =================================================================
    def assign_teacher(self, teacher):
        """Assigns a new teacher to this Block.
        
        Returns the Block object."""
        # Verify that this teacher is, in fact, a Teacher.
        if not isinstance(teacher, Teacher):
            raise TypeError(f"<{teacher}>: invalid teacher - must be a Teacher object.")

        self._teachers[teacher.id] = teacher
        self.__assign_entity_teacher(teacher.id)

        return self

    @db_session
    def __assign_entity_teacher(self, teacher_id: int):
        """Connects this Block's database entity to that of the Teacher with the passed ID."""
        entity_teacher = dbTeacher.get(id=teacher_id)
        if entity_teacher is not None:
            entity_block = dbBlock[self.id]
            entity_block.teachers.add(entity_teacher)

    # =================================================================
    # remove_teacher
    # =================================================================
    def remove_teacher(self, teacher):
        """Removes the specified Teacher from this Block.
        
        Returns the Block object."""
        # Verify that the teacher is, in fact, a Teacher.
        if not isinstance(teacher, Teacher):
            raise TypeError(f"<{teacher}>: invalid teacher - must be a Teacher object.")

        # If the teachers dict contains an entry for this Teacher, remove it.
        if teacher.id in self._teachers.keys():
            del self._teachers[teacher.id]
            self.__remove_entity_teacher(teacher.id)

        return self

    @db_session
    def __remove_entity_teacher(self, teacher_id: int):
        """Breaks the connection between the records for this Block and the passed Teacher in the
        database. """
        entity_teacher = dbTeacher.get(id=teacher_id)
        if entity_teacher is not None:
            entity_block = dbBlock[self.id]
            entity_block.teachers.remove(entity_teacher)

    # =================================================================
    # remove_all_teachers
    # =================================================================
    def remove_all_teachers(self):
        """Removes ALL teachers from this Block.
        
        Returns the Block object."""
        for teacher in list(self._teachers.values()):
            self.remove_teacher(teacher)

        return self

    # =================================================================
    # teachers
    # =================================================================
    def teachers(self):
        """Returns a list of teachers assigned to this Block."""
        return list(self._teachers.values())

    # =================================================================
    # has_teacher
    # =================================================================
    def has_teacher(self, teacher):
        """Returns True if this Block has the specified Teacher."""
        if not teacher or not isinstance(teacher, Teacher):
            return False

        for key in self._teachers:
            if self._teachers[key].id == teacher.id:
                return True
        return False

    # =================================================================
    # teachersObj
    # =================================================================
    def teachersObj(self):
        """Returns a list of teacher objects to this Block."""
        # NOTE: Not entirely sure what this is meant to be doing in the original Perl.
        # ADDENDUM: There are no references to this method anywhere in the code beyond here.
        # May get rid of it.
        return self._teachers

    # =================================================================
    # sync_block
    # =================================================================
    def sync_block(self, block):
        """The new Block object will be synced with this one 
        (i.e., changing the start time of this Block will change the start time of the
        synched block).
        
        Returns the Block object."""
        if not isinstance(block, Block):
            raise TypeError(f"<{block}>: invalid block - must be a Block object.")
        self._sync.append(block)

        return self

    # =================================================================
    # unsync_block
    # =================================================================
    def unsync_block(self, block):
        """Removes syncing of Block from this Block.
        
        Returns this Block object."""

        # This function was not finished or used in the Perl code, so I'm flying blind here.
        if hasattr(self, '_sync') and block in self._sync:
            self._sync.remove(block)

        return self

    # =================================================================
    # synced
    # =================================================================
    def synced(self):
        """Returns an array ref of the Blocks which are synced to this Block."""
        return self._sync

    # =================================================================
    # reset_conflicted
    # =================================================================
    def reset_conflicted(self):
        """Resets conflicted field."""
        self._conflicted = 0

    # =================================================================
    # conflicted
    # =================================================================
    @property
    def conflicted(self):
        """Gets and sets conflicted field."""
        return self._conflicted

    @conflicted.setter
    def conflicted(self, new_conf: int):
        # if not hasattr(self, '_conflicted'):
        #     self._conflicted = 0
        self._conflicted = self.conflicted | new_conf

    # =================================================================
    # is_conflicted
    # =================================================================
    def is_conflicted(self):
        """Returns true if there is a conflict with this Block, false otherwise.

        Returns a number representing the type of conflict with this Block, or 0 if there are no
        conflicts. """
        return self.conflicted != 0

    # =================================================================
    # print_description
    # =================================================================
    def print_description(self):
        """Returns a text string that describes the Block.
        
        Includes information on any Section and Labs related to this Block."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns a text string that describes the Block.
        
        Includes information on any Section and Labs related to this Block."""
        text = ""

        if self.section:
            if self.section.course:
                text += self.section.course.name + " "
            text += f"{self.section.number} "

        text += f"{self.day} {self.start} for {self.duration} hours, in "
        # not intended result, but stops it from crashing
        text += ", ".join(str(l) for l in self.labs())

        return text

    def print_description_2(self):
        """Prints an alternate text string that describes this Block.
        
        Includes information which directly relates to this Block ONLY."""
        text = f"{self.number} : {self.day}, {self.start} {self.duration} hour(s)"
        return text

    # =================================================================
    # conflicts
    # =================================================================
    # def conflicts(self):
    #     """Returns a list of the conflicts related to this Block."""
    #     # NOTE: This function appears to be unfinished. There is no way to actually assign
    #     # anything to Block's -conflicts attributes in the original Perl code.
    #     if not hasattr(self, '_conflicts'):
    #         self._conflicts = []
    #
    #     return self._conflicts

    # ===================================
    # Refresh Number
    # ===================================
    def refresh_number(self):
        """Assigns a number to a Block that doesn't have one."""
        # NOTE: Honestly not sure why this function is necessary.
        number = self.number
        section = self.section

        if number == 0: self.number = section.get_new_number()

    # ===================================
    # List [Tuple]
    # ===================================
    @staticmethod
    def list() -> tuple[Block]:
        """Returns a tuple containing all Block objects."""
        return tuple(Block.__instances.values())

    # ===================================
    # Reset
    # ===================================
    @staticmethod
    def reset():
        """Resets the list of Block objects."""
        for b in Block.list(): b.delete()

    # =================================================================
    # get_day_blocks ($day, $blocks)
    # =================================================================
    @staticmethod
    def get_day_blocks(day: str, blocks: list):
        """Returns an array of all blocks within a specific day.

        Parameter day: str -> three-letter day of the week (mon, tue, etc.)
        Parameter blocks: list -> An array of AssignBlocks."""
        # NOTE: Day was an integer according to the original Perl documentation, but that won't
        # work here because TimeSlot.day returns a string.
        if not blocks or type(blocks[0]) is not Block:
            return []
        day_blocks = filter(lambda x: x.day == day, blocks)
        return list(day_blocks)

    # =================================================================
    # save()
    # =================================================================
    @db_session
    def save(self):
        d_slot = super().save()
        d_block = dbBlock.get(id=self.id)
        if d_block is not None:
            d_block.time_slot_id = d_slot
            for l in self.labs():
                d_lab = dbLab.get(id=l.id)
                if d_lab not in d_block.labs:
                    d_block.labs.add(d_lab)
            for t in self.teachers():
                d_teach = dbTeacher.get(id=t.id)
                if d_teach not in d_block.teachers:
                    d_block.teachers.add(d_teach)
            if self.section:
                d_sect = dbSection.get(id=self.section.id)
                if d_sect:
                    d_block.section = d_sect
            d_block.number = self.number
        return d_block


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
