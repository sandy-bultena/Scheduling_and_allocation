from __future__ import annotations
from typing import *
import schedule.Schedule.IDGeneratorCode as id_gen

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

_teacher_id_generator: Generator[int, int, None] = id_gen.get_id_generator()


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: _Teachers - should never be instantiated directly!
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Teacher:
    """Describes a teacher."""

    # -------------------------------------------------------------------
    # constructor
    # --------------------------------------------------------------------
    def __init__(self, firstname: str, lastname: str, department: str = "", teacher_id: int = None):
        """Creates a Teacher object.
        
        Parameter **firstname:** str -> first name of the teacher.
        Parameter **lastname:** str -> last name of the teacher.
        Parameter **dept:** str -> department that this teacher is associated with (optional)"""
        self.firstname = firstname
        self.lastname = lastname
        self.department = department
        self.release = 0

        self.__id = id_gen.set_id(_teacher_id_generator, teacher_id)

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
        if new_name and not new_name.isspace():
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
        if new_name and not new_name.isspace():
            self.__lastname = new_name

    # =================================================================
    # default string
    # =================================================================
    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname}"

    def __repl__(self) -> str:
        return str(self)

    # ------------------------------------------------------------------------
    # for sorting
    # ------------------------------------------------------------------------
    def __lt__(self, other: Teacher) -> bool:
        if self.lastname != other.lastname:
            return self.lastname < other.lastname
        return self.firstname < other.firstname


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
