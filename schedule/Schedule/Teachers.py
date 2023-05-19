from __future__ import annotations
from .exceptions import InvalidTeacherNameError
from typing import *

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

_instances: dict[int, Teacher] = {}


# ============================================================================
# auto id generator
# ============================================================================
def teacher_id_generator(max_id: int = 0):
    the_id = max_id + 1
    while True:
        yield the_id
        the_id = the_id + 1


id_generator: Generator[int, Any, None] = teacher_id_generator()


# ============================================================================
# get_all
# ============================================================================
def get_all() -> tuple[Teacher]:
    """Returns an immutable tuple containing all instances of the Teacher class."""
    return tuple(_instances.values())


# =================================================================
# get_by_id
# =================================================================
def get_by_id(teacher_id: int) -> Teacher | None:
    """Returns the Teacher object matching the specified ID, if it exists."""
    if teacher_id in _instances.keys():
        return _instances[teacher_id]
    return None


# ============================================================================
# reset
# ============================================================================
def clear_all():
    """Reset the local list of labs"""
    _instances.clear()


# =================================================================
# get_by_name
# =================================================================
def get_by_name(first_name: str, last_name: str) -> Teacher | None:
    """Returns the first Teacher found matching the first name and last name, if one exists."""
    if not (first_name and last_name):
        return None
    for teacher in _instances.values():
        if teacher.firstname == first_name and teacher.lastname == last_name:
            return teacher
    return None


class Teacher:
    """Describes a teacher."""

    # -------------------------------------------------------------------
    # constructor
    # --------------------------------------------------------------------
    def __init__(self, firstname: str, lastname: str, dept: str = "", teacher_id: int = None):
        """Creates a Teacher object.
        
        Parameter **firstname:** str -> first name of the teacher.
        Parameter **lastname:** str -> last name of the teacher.
        Parameter **dept:** str -> department that this teacher is associated with (optional)"""
        self.firstname = firstname
        self.lastname = lastname
        self.dept = dept
        self.release = 0

        self.__id = teacher_id if teacher_id else next(id_generator)
        _instances[self.__id] = self

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
            raise InvalidTeacherNameError("First name cannot be an empty string")

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
            raise InvalidTeacherNameError("Last name cannot be an empty string")
        self.__lastname = new_name

    # =================================================================
    # remove lab / delete
    # =================================================================
    def delete(self):
        """Removes this Teacher from Teachers"""

        # Remove the passed Lab object only if it's actually contained in the list of instances.
        if self in _instances.values():
            del _instances[self.__id]

    def remove(self):
        self.delete()

    # =================================================================
    # default string
    # =================================================================
    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname}"

    def __repl__(self) -> str:
        return str(self)


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
