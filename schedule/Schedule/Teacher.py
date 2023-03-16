from __future__ import annotations

from database.PonyDatabaseConnection import Teacher as dbTeacher, Schedule_Teacher as dbSchedTeach
from pony.orm import *
import Block
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import Schedule

"""
SYNOPSIS

    from Teacher import Teacher
    mouse    = Teacher(firstname = "Micky", 
                      lastname  = "Mouse",
                      dept      = "Disney"
                      )
    duck    = Teacher(firstname = "Donald", 
                      lastname  = "Duck",
                      dept      = "Mouse"
                      )
    for teacher in Teachers.List():
        print (teacher)
    
    Teacher.remove(duck);

"""


class Teacher:
    __instances : dict[int, Teacher] = {}

    """Describes a teacher."""

    # -------------------------------------------------------------------
    # new
    # --------------------------------------------------------------------

    def __init__(self, firstname: str, lastname: str, dept: str = "", *, id: int = None):
        """Creates a Teacher object.
        
        Parameter **firstname:** str -> first name of the teacher.
        Parameter **lastname:** str -> last name of the teacher.
        Parameter **dept:** str -> department that this teacher is associated with (optional)"""
        self.firstname = firstname
        self.lastname = lastname
        self.dept = dept
        self.release = 0

        self.__id = id if id else Teacher.__create_entity(self)
        Teacher.__instances[self.__id] = self

    @db_session
    @staticmethod
    def __create_entity(instance: Teacher) -> int:
        entity_teacher = dbTeacher(first_name=instance.firstname, last_name=instance.lastname,
                                   dept=instance.dept)
        commit()
        return entity_teacher.get_pk()

    # =================================================================
    # id
    # =================================================================

    @property
    def id(self) -> int:
        """Returns the unique ID for this Teacher."""
        return self.__id

    # =================================================================
    # firstname
    # =================================================================
    @property
    def firstname(self) -> str:
        """Gets and sets the Teacher's name."""
        return self.__firstname

    @firstname.setter
    def firstname(self, new_name: str):
        if not (new_name and not new_name.isspace()):
            raise Exception("First name cannot be an empty string")

        self.__firstname = new_name

    # =================================================================
    # lastname
    # =================================================================
    @property
    def lastname(self) -> str:
        """Gets and sets the Teacher's last name."""
        return self.__lastname

    @lastname.setter
    def lastname(self, new_name: str):
        if not (new_name and not new_name.isspace()):
            raise Exception("Last name cannot be an empty string")
        self.__lastname = new_name

    # =================================================================
    # default string
    # =================================================================
    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname}"

    def __repl__(self) -> str:
        return str(self)

    # =================================================================
    # get all teachers
    # =================================================================
    @staticmethod
    def list() -> tuple[Teacher]:
        """Returns an immutable tuple containing all occurrences of Teachers."""
        return tuple(Teacher.__instances.values())

    # =================================================================
    # share_blocks
    # =================================================================
    @staticmethod
    def share_blocks(block1 : Block.Block, block2 : Block.Block) -> bool:
        """Checks if there are teachers who share these two Blocks."""
        # Count occurrences in both sets to ensure that all values are < 2
        occurrences: dict[int, int] = {}

        # Get all the teachers in the first and second sets.
        for teacher in block1.teachers():
            if teacher.id not in occurrences.keys():
                occurrences[teacher.id] = 0
            occurrences[teacher.id] += 1

        for teacher in block2.teachers():
            if teacher.id not in occurrences.keys():
                occurrences[teacher.id] = 0
            occurrences[teacher.id] += 1

        # A count of 2 means the teachers are in both sets.
        for count in occurrences.values():
            if count >= 2:
                return True

        return False

    # =================================================================
    # get
    # =================================================================
    @staticmethod
    def get(teacher_id: int) -> Teacher | None:
        """Returns the Teacher object matching the passed ID, if it exists."""
        if teacher_id in Teacher.__instances.keys():
            return Teacher.__instances[teacher_id]
        return None

    # =================================================================
    # get_by_name
    # =================================================================
    @staticmethod
    def get_by_name(first_name: str, last_name: str) -> str | None:
        """Returns the first Teacher found matching the first name and last name, if one exists."""
        if not (first_name and last_name):
            return None
        for teacher in Teacher.__instances.values():
            if teacher.firstname == first_name and teacher.lastname == last_name:
                return teacher
        return None

    # =================================================================
    # remove teacher
    # =================================================================
    def remove(self):
        """Removes this Teacher from the Teachers object. Its corresponding database record
        is untouched."""
        if self.id in Teacher.__instances.keys():
            del Teacher.__instances[self.id]

    def delete(self):
        """Removes this Teacher from the Teachers object, along with its corresponding database
        record."""
        # First, remove the Teacher object from the application.
        self.remove()

        # Then delete its corresponding record from the database.
        self.__delete_entity_teacher()

    @db_session
    def __delete_entity_teacher(self):
        """Removes the corresponding Teacher record from the database."""
        d_teacher = dbTeacher.get(id=self.id)
        if d_teacher is not None:
            d_teacher.delete()

    # =================================================================
    # disjoint
    # =================================================================
    @staticmethod
    def disjoint(set_1: list[Teacher], rhs: list[Teacher]) -> bool:
        """Determines if one set of teachers is disjoint with another.

        Returns false if even a single Teacher occurs in both sets, or true otherwise."""
        occurrences = {}

        # Get all the teachers in the current set.
        for teacher in set_1:
            if teacher.id not in occurrences.keys():
                occurrences[teacher.id] = 0
            occurrences[teacher.id] += 1

        # Get all the teachers in the provided set.
        for teacher in rhs:
            if teacher.id not in occurrences.keys():
                occurrences[teacher.id] = 0
            occurrences[teacher.id] += 1

        # A teacher count of 2 means they're in both sets; there is no disjoint.
        for count in occurrences.values():
            if count >= 2:
                return False

        return True

    @db_session
    def save(self, schedule : Schedule.Schedule | None = None) -> dbTeacher:
        """Saves the Teacher object to the database."""
        d_teach : dbTeacher = dbTeacher.get(id=self.id)
        if not d_teach: d_teach = dbTeacher(first_name=self.firstname, last_name=self.lastname)
        d_teach.first_name = self.firstname
        d_teach.last_name = self.lastname
        d_teach.dept = self.dept
        # No need to update the Teacher's schedules/sections/blocks sets; those are handled
        # elsewhere.
        if schedule:
            sched_t = dbSchedTeach.get(teacher_id=d_teach, schedule_id=schedule)
            if not sched_t: sched_t = dbSchedTeach(teacher_id=d_teach, schedule_id=schedule, work_release=self.release)
            sched_t.work_release = self.release
        return d_teach

    # =================================================================
    # reset
    # =================================================================
    @staticmethod
    def reset():
        """Reset the local list of teachers"""
        Teacher.__instances = {}


# =================================================================
# footer
# =================================================================
'''
1;

=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns

Translated to Python by Evan Laverdiere

=head1 COPYRIGHT

Copyright (c) 2016, Jack Burns, Sandy Bultena, Ian Clement. 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut
'''
