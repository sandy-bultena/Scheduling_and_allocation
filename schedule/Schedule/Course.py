from __future__ import annotations
# directly importing modules to avoid circular dependencies
from . import Streams
from . import Teachers
from . import Labs
from . import Section
from . import Block
from .exceptions import InvalidSectionNumberForCourseError

from .ScheduleEnums import SemesterType

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


def course_id_generator(max_id: int = 0):
    the_id = max_id + 1
    while True:
        yield the_id
        the_id = the_id + 1


class Course:
    """Describes a distinct course."""

    __instances: dict[int, Course] = {}
    course_id = course_id_generator()

    # -------------------------------------------------------------------
    # new
    # --------------------------------------------------------------------
    def __init__(self, number: str = "", name: str = "New Course",
                 semester: (SemesterType | int) = SemesterType.any, needs_allocation: bool = True,
                 course_id: int = None):
        """Creates and returns a course object.

        Parameter **number**: str -> The alphanumeric course number.

        Parameter **name**: str -> the name of the course."""

        self.number: str = str(number)
        self.name: str = str(name)
        self.needs_allocation: bool = needs_allocation
        self.__sections: dict[str, Section.Section] = {}
        self.semester: int = SemesterType.validate(semester)

        self.__id = course_id if course_id else next(Course.course_id, 1)
        Course.__instances[self.__id] = self

    # =================================================================
    # id
    # =================================================================
    @property
    def id(self) -> int:
        """Returns the unique ID for this Course object."""
        return self.__id

    # =================================================================
    # description
    # =================================================================
    @property
    def description(self) -> str:
        """Returns text string that describes this Block."""
        return f"{self.number}: {self.name}"

    # =================================================================
    # add_section
    # =================================================================
    def add_section(self, section: Section.Section) -> Course:
        """Assign a Section to this Course."""

        # If this section is already on the Course, skip it
        if section.number in self.__sections and section.id == self.__sections[section.number].id:
            return self

        # -------------------------------------------------------
        # Section numbers must be unique for this Course.
        # -------------------------------------------------------
        if section.number in self.__sections:
            raise InvalidSectionNumberForCourseError(
                f"<{section.number}>: section number is not unique for this Course.")

        # ----------------------------------------------------------
        # save section for this course, save course for this section
        # ----------------------------------------------------------
        self.__sections[section.number] = section
        section.course = self

        return self

    # =================================================================
    # get_section
    # =================================================================
    def get_section(self, number: str) -> Section.Section | None:
        """Gets the Section from this Course that has the passed section number, if it exists.
        Otherwise, returns None. """
        if number in self.__sections.keys():
            return self.__sections[number]
        return None

    # =================================================================
    # get_section_by_id
    # =================================================================
    def get_section_by_id(self, sect_id: int) -> Section.Section | None:
        """Gets the Section from this Course that matches the passed section ID, if it exists.

        Returns the Section if found, or None otherwise."""
        found = [section for section in self.sections if section.id == sect_id]
        return found[0] if found else None

    # =================================================================
    # get_section_by_name
    # =================================================================
    def get_section_by_name(self, name: str) -> tuple[Section.Section]:
        """Gets the Section from this Course that has the passed section name, if it exists.

        Returns a list containing the Section if found, or an empty list otherwise."""
        if name:
            sections = [s for s in self.sections if s.name == name]
            return tuple(sections)
        return tuple()

    # =================================================================
    # remove_section
    # =================================================================
    def remove_section(self, section: Section.Section) -> Course:
        """Removes the passed Section from this Course, if it exists.

        Returns the modified Course object."""

        if section.number in self.__sections:
            del self.__sections[section.number]

        return self

    # =================================================================
    # delete
    # =================================================================
    def remove(self):
        """Removes this object from the application"""
        # Remove each of its associated sections.
        for section in self.sections:
            self.remove_section(section)
        if Course.__instances[self.id]:
            del Course.__instances[self.id]

    def delete(self):
        """Delete this object (and all its dependants)."""
        self.remove()

    # =================================================================
    # sections
    # =================================================================
    @property
    def sections(self) -> tuple[Section.Section]:
        """Returns a list of all the Sections assigned to this Course."""
        return tuple(self.__sections.values())

    # =================================================================
    # number of sections
    # =================================================================
    @property
    def number_of_sections(self) -> int:
        """Returns the number of Sections assigned to this Course."""
        return len(self.sections)

    # =================================================================
    # sections for teacher
    # =================================================================
    def sections_for_teacher(self, teacher: Teacher.Teacher) -> tuple[Section.Section]:
        """Returns a list of the Sections assigned to this course, with this Teacher."""
        sections = []

        for section in self.sections:
            for teacher_id in section.teachers:
                if teacher.id == teacher_id.id:
                    sections.append(section)

        return tuple(sections)

    # =================================================================
    # max_section_number
    # =================================================================
    @property
    def max_section_number(self) -> int:
        """Returns the maximum Section number from the Sections assigned to this Course."""
        sections = sorted(self.sections, key=lambda s: s.number)
        return sections[-1].number if len(sections) > 0 else 0

    # =================================================================
    # blocks
    # =================================================================
    @property
    def blocks(self) -> tuple[Block.Block]:
        """Returns a tuple of the Blocks assigned to this Course."""
        blocks = []

        for section in self.sections:
            blocks.extend(section.blocks)

        return tuple(blocks)

    # =================================================================
    # section
    # =================================================================
    def section(self, section_number: str) -> Section.Section | None:
        """Returns the Section associated with this Section number."""
        if section_number in self.__sections.keys():
            return self.__sections[section_number]
        return None

    # =================================================================
    # string representation of the object
    # =================================================================
    def __str__(self) -> str:
        """Returns a text string that describes the Course, its Sections, its Blocks,
        its Teachers, and its Labs. """
        text = ''

        # Header
        text += "\n\n"
        text += '=' * 50 + "\n"
        text += f"{self.number} {self.name}\n"
        text += '=' * 50 + "\n"

        # Sections
        for s in sorted(self.sections, key=lambda x: x.number):
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
    @property
    def teachers(self) -> tuple[Teacher.Teacher]:
        """Returns a list of the Teachers assigned to all Sections of this Course."""

        teachers: set[Teacher.Teacher] = set()
        for section in self.sections:
            teachers.union(section.teachers)
        return tuple(teachers)

    # =================================================================
    # has teacher
    # =================================================================

    def has_teacher(self, teacher: Teacher.Teacher) -> bool:
        """Returns true if the passed Teacher is assigned to this Course."""
        return teacher.id in (x.id for x in self.teachers)

    # =================================================================
    # streams
    # =================================================================
    @property
    def streams(self) -> tuple[Stream.Stream]:
        """Returns a list of Streams assigned to all Sections of this Course."""

        streams: set[Stream.Stream] = set()
        for section in self.sections:
            streams.union(section.streams)
        return tuple(streams)

    # =================================================================
    # has_stream
    # =================================================================
    def has_stream(self, stream: Stream.Stream) -> bool:
        """Returns true if this Course has the specified Stream."""
        return stream.id in (s.id for s in self.streams)

    # =================================================================
    # assign_teacher
    # =================================================================
    def assign_teacher(self, teacher: Teacher.Teacher) -> Course:
        """Assigns a Teacher to all Sections of this Course."""

        for section in self.sections:
            section.assign_teacher(teacher)
        return self

    # =================================================================
    # assign_lab
    # =================================================================
    def assign_lab(self, lab: Lab.Lab) -> Course:
        """Assigns a Lab to all Sections of this Course."""

        for section in self.sections:
            section.assign_lab(lab)
        return self

    # =================================================================
    # assign_stream
    # =================================================================
    def assign_stream(self, stream: Stream.Stream) -> Course:
        """Assigns a Stream to all Sections of this Course."""
        if stream:
            for section in self.sections:
                section.assign_stream(stream)

        return self

    # =================================================================
    # remove_teacher
    # =================================================================
    def remove_teacher(self, teacher: Teacher.Teacher) -> Course:
        """Removes the passed Teacher from all Sections/Blocks in this Course."""
        for section in self.sections:
            section.remove_teacher(teacher)

        return self

    # =================================================================
    # remove_all_teachers
    # =================================================================
    def remove_all_teachers(self) -> Course:
        """Removes all Teachers from all Sections/Blocks in this Course."""
        for teacher in self.teachers:
            self.remove_teacher(teacher)
        return self

    # =================================================================
    # remove_stream
    # =================================================================
    def remove_stream(self, stream: Stream.Stream) -> Course:
        """Removes the specified Stream from this Course."""
        for section in self.sections:
            section.remove_stream(stream)
        return self

    # =================================================================
    # remove_all_streams
    # =================================================================
    def remove_all_streams(self) -> Course:
        """Removes all Streams from all Sections of this Course."""
        for stream in self.streams:
            self.remove_stream(stream)
        return self

    # =================================================================
    # Get unused section number
    # =================================================================
    def get_new_number(self, number: int) -> int:
        """Returns the first unused Section Number."""
        while self.get_section(str(number)):
            number += 1
        return number

    # =================================================================
    # list
    # =================================================================
    @staticmethod
    def list() -> tuple[Course]:
        """Returns a list of all Course objects."""
        return tuple(Course.__instances.values())

    # =================================================================
    # get_by_id
    # =================================================================
    @staticmethod
    def get(c_id: int) -> Course | None:
        """Returns the Course object with the matching ID."""
        return Course.__instances.get(c_id)

    # =================================================================
    # get_by_number
    # =================================================================
    @staticmethod
    def get_by_number(number: str) -> Course | None:
        """Return the first Course which matches this Course number, if it exists."""
        courses: list[Course] = [course for course in Course.__instances.values() if course.number == number]
        return courses[0] if len(courses) != 0 else None

    # =================================================================
    # courses list for allocation
    # =================================================================
    @staticmethod
    def allocation_list() -> tuple[Course]:
        """Returns a sorted list of the Courses that need allocation."""
        courses = [course for course in Course.__instances.values() if course.needs_allocation]
        courses = sorted(courses, key=lambda c: c.number)
        return tuple(courses)

    # =================================================================
    # reset
    # =================================================================
    @staticmethod
    def reset():
        """Reset the local list of courses"""
        Course.__instances = dict()


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
