from __future__ import annotations
import re
from warnings import warn
# directly importing modules to avoid circular dependencies
import Stream
import Teacher
import Lab
import Section

from database.PonyDatabaseConnection import Course as dbCourse, Section as dbSection
from pony.orm import *
from ScheduleEnums import SemesterType

'''SYNOPSIS

    from Schedule.Course import Course
    from Schedule.Block import Block
    from Schedule.Section import Section
    from DaysOfWeek import WeekDays

    block = Block(day = WeekDay.Wednesday, start = "9:30", duration = 1.5)
    section = Section(number = 1, hours = 6)
    course = Course(name = "Basket Weaving", number="420-ABC-DEF")
    
    course.add_section(section)
    section.add_block(block)

    print("Course consists of the following sections: ")
    for s in course.sections():
        # print info about section
'''


class Course:
    """Describes a distinct course."""
    __instances = {}

    # -------------------------------------------------------------------
    # new
    # --------------------------------------------------------------------
    def __init__(self, number: str = "", name: str = "New Course",
                 semester: SemesterType = SemesterType.any, needs_allocation: bool = True,
                 *, id: int = None):
        """Creates and returns a course object.

        Parameter **number**: str -> The alphanumeric course number.

        Parameter **name**: str -> the name of the course."""

        self.number: str = str(number)
        self.name: str = str(name)
        self.needs_allocation: bool = needs_allocation
        self._sections: dict[int, Section.Section] = {}
        self.semester: int = SemesterType.validate(semester)

        self.__id = id if id else Course.__create_entity(self)
        Course.__instances[self.__id] = self

    @db_session
    @staticmethod
    def __create_entity(instance: Course):
        entity_course = dbCourse(name=instance.name, number=instance.number,
                                 allocation=instance.needs_allocation, semester=instance.semester)
        commit()
        return entity_course.get_pk()

    # =================================================================
    # id
    # =================================================================
    @property
    def id(self):
        """Returns the unique ID for this Course object."""
        return self.__id

    # =================================================================
    # name
    # =================================================================
    @property
    def name(self):
        """Gets or sets the Course name."""
        return self.__name

    @name.setter
    def name(self, new_name: str):
        self.__name = new_name

    # =================================================================
    # description - replaces print_description_2
    # =================================================================
    @property
    def description(self):
        """Returns text string that describes this Block."""
        return f"{self.number}: {self.name}"

    # =================================================================
    # number
    # =================================================================
    @property
    def number(self):
        """Gets and sets the Course number."""
        return self.__number

    @number.setter
    def number(self, new_num: str):
        self.__number = new_num

    # =================================================================
    # add_ section
    # =================================================================
    def add_section(self, *sections):
        """Assign one or more Sections to this Course.

        Returns the modified Course object."""
        # In Perl, this function is structured in a way that allows it to take multiple sections
        # and add them all to the Course, one at a time. However, it is never actually used that
        # way. I am preserving the original structure just in case.
        for section in sections:
            # Verify that this is actually a Section object.
            if not isinstance(section, Section.Section):
                raise TypeError(f"<{section}>: invalid section - must be a Section object.")

            # -------------------------------------------------------
            # Section numbers must be unique for this Course.
            # -------------------------------------------------------
            if section.number in (sec.number for sec in self._sections.values()):
                raise Exception(
                    f"<{section.number}>: section number is not unique for this Course.")

            # ----------------------------------------------------------
            # save section for this course, save course for this section
            # ----------------------------------------------------------
            self._sections[section.number] = section
            section.course = self
            self.__add_entity_section(section.id)

        return self

    @db_session
    def __add_entity_section(self, sect_id: int):
        d_sect = dbSection.get(id=sect_id)
        if d_sect is not None:
            d_course = dbCourse[self.id]
            d_course.sections.add(d_sect)

    # =================================================================
    # get_section
    # =================================================================
    def get_section(self, number):
        """Gets the Section from this Course that has the passed section number, if it exists.
        Otherwise, returns None. """
        if number in self._sections.keys():
            return self._sections[number]
        return None

    # =================================================================
    # get_section_by_id
    # =================================================================
    def get_section_by_id(self, sect_id):
        """Gets the Section from this Course that matches the passed section ID, if it exists.

        Returns the Section if found, or None otherwise."""
        found = [section for section in self.sections() if section.id == sect_id]
        return found[0] if found else None

    # =================================================================
    # get_section_by_name
    # =================================================================
    def get_section_by_name(self, name: str) -> list:
        """Gets the Section from this Course that has the passed section name, if it exists.

        Returns a list containing the Section if found, or an empty list otherwise."""
        # NOTE: This method is coded to return an array in the Perl code. However, the one place
        # where this function is being called--AssignToResource.pm--only cares about the first
        # element of the returned array. I'm keeping the structure as-is, but this will probably
        # need revision.
        if name:
            sections = [s for s in self.sections() if s.name == name]
            return sections
        return []

    # =================================================================
    # remove_section
    # =================================================================
    def remove_section(self, section):
        """Removes the passed Section from this Course, if it exists.

        Returns the modified Course object."""
        # Verify that the section is indeed a Section object.
        if not isinstance(section, Section.Section):
            raise TypeError(f"<{section}>: invalid section - must be a Section object")

        if section.number in getattr(self, '_sections', {}):
            del self._sections[section.number]
            self.__remove_entity_section(section.id)
            section.delete()

        return self

    @db_session
    def __remove_entity_section(self, section_id: int):
        d_sect = dbSection.get(id=section_id)
        if d_sect is not None:
            d_course = dbCourse[self.id]
            d_course.sections.remove(d_sect)

    # =================================================================
    # delete
    # =================================================================
    def remove(self):
        """Removes this object from the application, without deleting its corresponding
        database record."""
        # Remove each of its associated sections.
        for section in self.sections():
            self.remove_section(section)
        if Course.__instances[self.id]:
            del Course.__instances[self.id]

    def delete(self):
        """Delete this object (and all its dependants), including its corresponding database record.

        Returns None."""
        self.remove()
        self.__delete_entity()

    @db_session
    def __delete_entity(self):
        """Removes this Course's corresponding entry from the database."""
        d_course = dbCourse.get(id=self.id)
        if d_course is not None:
            d_course.delete()

    # =================================================================
    # sections
    # =================================================================
    def sections(self) -> tuple[Section.Section]:
        """Returns a list of all the Sections assigned to this Course."""
        return tuple(self._sections.values())

    # =================================================================
    # number of sections
    # =================================================================
    def number_of_sections(self):
        """Returns the number of Sections assigned to this Course."""
        sections = self.sections()
        return len(sections)

    # =================================================================
    # sections for teacher
    # =================================================================
    def sections_for_teacher(self, teacher: Teacher.Teacher):
        """Returns a list of the Sections assigned to this course, with this Teacher."""
        sections = []

        for section in self.sections():
            for teacher_id in section.teachers:
                if teacher.id == teacher_id.id:
                    sections.append(section)

        return sections

    # =================================================================
    # max_section_number
    # =================================================================
    def max_section_number(self):
        """Returns the maximum Section number from the Sections assigned to this Course."""
        sections = sorted(self.sections(), key=lambda s: s.number)
        return sections[-1].number if len(sections) > 0 else 0

    # =================================================================
    # blocks
    # =================================================================
    def blocks(self):
        """Returns a list of the Blocks assigned to this Course."""
        blocks = []

        for section in self.sections():
            blocks.append(section.blocks)

        return blocks

    # =================================================================
    # section
    # =================================================================
    def section(self, section_number) -> Section.Section:
        """Returns the Section associated with this Section number."""
        if section_number in self._sections.keys():
            return self._sections[section_number]

    # =================================================================
    # string representation of the object
    # =================================================================
    def __str__(self):
        """Returns a text string that describes the Course, its Sections, its Blocks,
        its Teachers, and its Labs. """
        text = ''

        # Header
        text += "\n\n"
        text += '=' * 50 + "\n"
        text += f"{self.number} {self.name}\n"
        text += '=' * 50 + "\n"

        # Sections
        for s in sorted(self.sections(), key=lambda x: x.number):
            text += f"\n{s}\n"
            text += "-" * 50 + "\n"

            # Blocks
            blocks = list(s.blocks)
            for b in sorted(blocks, key=lambda x: x.day_number or x.start_number):
                text += f"{b.day} {b.start}, {b.duration} hours\n"
                text += "\tlabs: " + ", ".join([str(lab) for lab in b.labs()]) + "\n"
                text += "\tteachers: "
                text += ", ".join([str(t) for t in b.teachers()])
                text += "\n"

        return text

    def __repr__(self) -> str:
        return self.description

    # =================================================================
    # teachers
    # =================================================================
    def teachers(self):
        """Returns a list of the Teachers assigned to all Sections of this Course."""
        teachers = {}

        for section in self.sections():
            for teacher in section.teachers:
                teachers[teacher] = teacher

        return list(teachers.values())

    # =================================================================
    # has teacher
    # =================================================================
    def has_teacher(self, teacher: Teacher.Teacher):
        """Returns true if the passed Teacher is assigned to this Course."""
        if not teacher or not isinstance(teacher, Teacher.Teacher):
            return False
        return teacher.id in (adult.id for adult in self.teachers())

    # =================================================================
    # streams
    # =================================================================
    def streams(self):
        """Returns a list of Streams assigned to all Sections of this Course."""
        streams = {}

        for section in self.sections():
            for stream in section.streams:
                streams[stream] = stream

        return list(streams.values())

    # =================================================================
    # has_stream
    # =================================================================
    def has_stream(self, stream):
        """Returns true if this Course has the specified Stream."""
        if not stream:
            return False

        return stream.id in (s.id for s in self.streams())

    # =================================================================
    # assign_teacher
    # =================================================================
    def assign_teacher(self, teacher: Teacher.Teacher):
        """Assigns a Teacher to all Sections of this Course.

        Returns the modified Course object."""
        if teacher:
            for section in self.sections():
                section.assign_teacher(teacher)

        return self

    # =================================================================
    # assign_lab
    # =================================================================
    def assign_lab(self, lab: Lab.Lab):
        """Assigns a Lab to all Sections of this Course.

        Returns the modified Course object."""
        if lab:
            for section in self.sections():
                section.assign_lab(lab)

        return self

    # =================================================================
    # assign_stream
    # =================================================================
    def assign_stream(self, stream: Stream.Stream):
        """Assigns a Stream to all Sections of this Course.

        Returns the modified Course object."""
        if stream:
            for section in self.sections():
                section.assign_stream(stream)

        return self

    # =================================================================
    # remove_teacher
    # =================================================================
    def remove_teacher(self, teacher: Teacher.Teacher):
        """Removes the passed Teacher from all Blocks in this Course.

        Returns the modified Course object."""
        for section in self.sections():
            section.remove_teacher(teacher)

        return self

    # =================================================================
    # remove_all_teachers
    # =================================================================
    def remove_all_teachers(self):
        """Removes all Teachers from all Blocks in this Course.

        Returns the modified Course object."""
        for teacher in self.teachers():
            self.remove_teacher(teacher)

        return self

    # =================================================================
    # remove_stream
    # =================================================================
    def remove_stream(self, stream: Stream.Stream):
        """Removes the specified Stream from this Course.

        Returns the modified Course object."""
        for section in self.sections():
            section.remove_stream(stream)

        return self

    # =================================================================
    # remove_all_streams
    # =================================================================
    def remove_all_streams(self):
        """Removes all Streams from all Sections of this Course.

        Returns the modified Course object."""
        for stream in self.streams():
            self.remove_stream(stream)

        return self

    # =======================================
    # Get unused section number (Alex Code)
    # =======================================
    def get_new_number(self, number: int) -> int:
        """Returns the first unused Section Number."""
        while self.get_section(str(number)):
            number += 1
        return number

    # =======================================
    # list
    # =======================================

    @staticmethod
    def list() -> tuple[Course]:
        """Returns a list of all Course objects."""
        return tuple(Course.__instances.values())

    # =================================================================
    # get
    # =================================================================
    @staticmethod
    def get(c_id: int) -> Course | None:
        """Returns the Course object with the matching ID."""
        return Course.__instances.get(c_id)

    # =================================================================
    # get_by_number
    # =================================================================
    @staticmethod
    def get_by_number(number) -> Course | None:
        """Return the Course which matches this Course number, if it exists."""
        if not number: return

        for course in Course.__instances.values():
            if course.number == number: return course

        return None

    # =================================================================
    # courses list for allocation
    # =================================================================
    @staticmethod
    def allocation_list() -> list[Course]:
        """Returns a sorted list of the Courses that need allocation."""
        courses = list(filter(lambda x: x.needs_allocation, Course.list()))
        courses = sorted(courses, key=lambda c: c.number)
        return courses

    @db_session
    def save(self):
        cc = dbCourse.get(id=self.id)
        if not cc: cc = dbCourse(name=self.name, semester=self.semester)
        cc.name = self.name
        cc.number = self.number
        cc.allocation = self.needs_allocation
        cc.semester = self.semester
        return cc

    # =================================================================
    # reset
    # =================================================================
    @staticmethod
    def reset():
        """Reset the local list of courses"""
        Course.__instances = {}


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
