from __future__ import annotations
from typing import Generator, TYPE_CHECKING

from ._model_exceptions import InvalidSectionNumberForCourseError
from . import _id_generator_code as id_gen
from .enums import SemesterType
from .section import Section

if TYPE_CHECKING:
    from .block import Block
    from .teacher import Teacher
    from .stream import Stream
    from .lab import Lab

DEFAULT_HOURS: float = 1.5

'''SYNOPSIS

    from Schedule.Course import Course
    from Schedule.Block import Block
    from Schedule.Section import Section
    from DaysOfWeek import WeekDays

    blocks = Block(day = WeekDay.Wednesday, start = "9:30", duration = 1.5)
    section = Section(number = 1, hours = 6)
    course = Course(name = "Basket Weaving", number="420-ABC-DEF")
    
    course.add_section(section)
    section.add_block(blocks)

    print("Course consists of the following sections: ")
    for s in course.sections():
        # print info about section
'''

_course_id_generator: Generator[int, int, None] = id_gen.get_id_generator()


class Course:
    """Describes a distinct course."""

    # -------------------------------------------------------------------
    # new
    # --------------------------------------------------------------------
    def __init__(self, number: str = "", name: str = "New Course",
                 semester: (SemesterType | int) = SemesterType.any, needs_allocation: bool = True,
                 course_id: int = None):
        """Creates and returns a course object.

        Parameter **number**: str -> The alphanumeric course number.

        Parameter **name**: str -> the name of the course."""

        self.number: str = number
        self.name: str = name
        self.needs_allocation: bool = needs_allocation
        self._sections: set[Section] = set()
        self.semester: int = SemesterType.validate(semester)

        self.__id = id_gen.set_id(_course_id_generator, course_id)

    # =================================================================
    # id
    # =================================================================
    @property
    def id(self) -> int:
        """Returns the unique ID for this Course object."""
        return self.__id

    # =================================================================
    # title
    # =================================================================
    @property
    def title(self) -> str:
        """Returns text string that describes this Block."""
        return f"{self.number}: {self.name}"

    # =================================================================
    # add_section
    # =================================================================
    def add_section(self, number: str = "", hours: float = DEFAULT_HOURS, name: str = "",
                    section_id: int = None) -> Section:
        """Assign a Section to this Course."""

        # -------------------------------------------------------
        # Section numbers must be unique for this Course.
        # -------------------------------------------------------
        if number in (s.number for s in self.sections):
            raise InvalidSectionNumberForCourseError(
                f"<{number}>: section number is not unique for this Course.")

        # ----------------------------------------------------------
        # save section for this course, save course for this section
        # ----------------------------------------------------------
        section = Section(self, number, hours, name, section_id)
        self._sections.add(section)

        return section

    # =================================================================
    # get_section_by_number
    # =================================================================
    def get_section_by_number(self, number: str) -> Section | None:
        """Gets the Section from this Course that has the passed section number, if it exists.
        Otherwise, returns None. """
        found = [section for section in self.sections if section.number == number]
        return found[0] if found else None

    # =================================================================
    # get_section_by_id
    # =================================================================
    def get_section_by_id(self, sect_id: int) -> Section | None:
        """Gets the Section from this Course that matches the passed section ID, if it exists.
        Returns the Section if found, or None otherwise."""
        found = [section for section in self.sections if section.id == sect_id]
        return found[0] if found else None

    # =================================================================
    # get_sections_by_name
    # =================================================================
    def get_sections_by_name(self, name: str) -> tuple[Section, ...]:
        """Gets the Section from this Course that has the passed section name, if it exists.
        Returns a list containing the Section if found, or an empty list otherwise."""
        found = [section for section in self.sections if section.name == name]
        return tuple(found)

    # =================================================================
    # remove_section
    # =================================================================
    def remove_section(self, section: Section) -> Course:
        """Removes the passed Section from this Course, if it exists.
        Returns the modified Course object."""
        self._sections.discard(section)
        return self

    # =================================================================
    # sections
    # =================================================================
    @property
    def sections(self) -> tuple[Section, ...]:
        """Returns a list of all the Sections assigned to this Course."""
        return tuple(sorted(self._sections))

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
    def get_sections_for_teacher(self, teacher: Teacher) -> tuple[Section, ...]:
        """Returns a list of the Sections assigned to this course, with this Teacher."""
        sections = []

        for section in self.sections:
            if teacher in section.teachers:
                sections.append(section)

        return tuple(sorted(set(sections)))

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
    def blocks(self) -> tuple[Block, ...]:
        """Returns a tuple of the Blocks assigned to this Course."""
        blocks = []

        for section in self.sections:
            blocks.extend(section.blocks)

        return tuple(sorted(set(blocks)))

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
            for b in sorted(s.blocks, key=lambda x: x.day_number or x.start_number):
                text += f"{b.day} {b.start}, {b.duration} hours\n"
                text += "\tlab_ids: " + ", ".join([str(lab) for lab in b.labs]) + "\n"
                text += "\tteacher_ids: "
                text += ", ".join([str(t) for t in b.teachers])
                text += "\n"

        return text

    def __repr__(self) -> str:
        return self.title

    # =================================================================
    # teacher_ids
    # =================================================================
    @property
    def teachers(self) -> tuple[Teacher, ...]:
        """Returns a list of the Teachers assigned to all Sections of this Course."""

        teachers: list[Teacher] = list()
        for section in self.sections:
            teachers.extend(section.teachers)
        return tuple(sorted(set(teachers)))

    # =================================================================
    # has teacher
    # =================================================================

    def has_teacher(self, teacher: Teacher) -> bool:
        """Returns true if the passed Teacher is assigned to this Course."""
        return teacher in self.teachers

    # =================================================================
    # stream
    # =================================================================
    @property
    def streams(self) -> tuple[Stream, ...]:
        """Returns a list of Streams assigned to all Sections of this Course."""

        streams: list[Stream] = list()
        for section in self.sections:
            streams.extend(section.streams)
        return tuple(sorted(set(streams)))

    # =================================================================
    # has_stream_with_id
    # =================================================================
    def has_stream(self, stream: Stream) -> bool:
        """Returns true if this Course has the specified Stream."""
        return stream in self.streams

    # =================================================================
    # assign_teacher_by_id
    # =================================================================
    def add_teacher(self, teacher: Teacher) -> Course:
        """Assigns a Teacher to all Sections of this Course."""

        for section in self.sections:
            section.add_teacher(teacher)
        return self

    # =================================================================
    # add_lab
    # =================================================================
    # =================================================================
    # stream
    # =================================================================
    @property
    def labs(self) -> tuple[Lab, ...]:
        """Returns a list of Labs assigned to all Sections of this Course."""

        lab_list: list[Lab] = []

        for section in self.sections:
            for block in section.blocks:
                lab_list.extend(block.labs)
        return tuple(sorted(set(lab_list)))

    def add_lab(self, lab: Lab) -> Course:
        """Assigns a Lab to all Sections of this Course."""

        for section in self.sections:
            section.add_lab(lab)
        return self

    # =================================================================
    # assign_stream_by_id
    # =================================================================
    def add_stream(self, stream: Stream) -> Course:
        """Assigns a Stream to all Sections of this Course."""
        if stream:
            for section in self.sections:
                section.add_stream(stream)

        return self

    # =================================================================
    # remove_teacher
    # =================================================================
    def remove_teacher(self, teacher: Teacher) -> Course:
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
    # remove_stream_by_id
    # =================================================================
    def remove_stream(self, stream: Stream) -> Course:
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
        while self.get_section_by_number(str(number)):
            number += 1
        return number

    # ------------------------------------------------------------------------
    # for sorting
    # ------------------------------------------------------------------------
    def __lt__(self, other):
        return self.number < other.number


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
