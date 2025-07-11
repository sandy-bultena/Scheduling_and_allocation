from __future__ import annotations
from typing import Optional
from .enums import ResourceType
from .id_generator import IdGenerator

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
    """Describes a teacher."""
    teacher_ids = IdGenerator()

    # -------------------------------------------------------------------
    # constructor
    # --------------------------------------------------------------------
    def __init__(self, firstname: str, lastname: str, department: str = "", release: float = 0, teacher_id: Optional[int] = None):
        """Creates a Teacher object.
        :param firstname:   first name of the teacher
        :param lastname:   last name of the teacher
        :param department:  department that this teacher is associated with
        :param teacher_id: set the teacher id to this value
        """
        self.firstname = firstname
        self.lastname = lastname
        self.department = department
        self.release = release
        self.resource_type = ResourceType.teacher

        self._id = Teacher.teacher_ids.get_new_id(teacher_id)

    # =================================================================
    # unique identifier
    # =================================================================
    @property
    def teacher_id(self) -> int:
        return self._id

    @property
    def number(self) -> str:
        """Returns the unique ID for this Teacher."""
        return str(self._id)

    # =================================================================
    # other
    # =================================================================
    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname}"

    def __repr__(self):
        return str(self)

    def __repl__(self) -> str:
        return str(self)

    def __lt__(self, other: Teacher) -> bool:
        return (self.lastname, self.firstname) < (other.lastname, other.firstname)

    def __eq__(self, other):
        return self.number == other.number

    def __hash__(self):
        return hash(self._id)


# =================================================================
# footer
# =================================================================
__copyright__ = '''

=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns

=head1 COPYRIGHT

Copyright (c) 2016, Jack Burns, Sandy Bultena, Ian Clement. 
Copyright (c) 2025, Sandy Bultena

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut
'''
