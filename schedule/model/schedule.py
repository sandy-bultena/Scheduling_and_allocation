from __future__ import annotations

from typing import Optional

import schedule.exceptions as errors

from .teacher import Teacher
from .block import Block
from .course import Course
from .lab import Lab
from .stream import Stream
from .section import Section
from .conflicts import (set_block_conflicts, ConflictType, set_lunch_break_conflicts,
                        set_number_of_days_conflict, set_availability_hours_conflict)
from .enums import ResourceType, SemesterType
from .serializor import CSVSerializor as Serializor
DEFAULT_COURSE_HOURS = 3

""" SYNOPSIS/EXAMPLE:
"""


def get_resource_type(obj: Teacher | Lab | Stream) -> ResourceType | None:
    """Returns the resource_type of the ResourceType object"""
    for v_type in ResourceType:
        my_class = eval(f"{v_type.name}")
        if isinstance(obj, my_class):
            return v_type
    return None


class Schedule:
    """ Provides the top level class for all schedule objects. """

    # ------------------------------------------------------------------------
    # Initialize
    # ------------------------------------------------------------------------
    def __init__(self, file: Optional[str] = None):
        """ Creates an instance of the Schedule class. """
        self._teachers: dict[str, Teacher] = dict()
        self._streams: dict[str, Stream] = dict()
        self._labs: dict[str, Lab] = dict()
        self._courses: dict[str, Course] = dict()

        if file is not None:
            self.read_file(file)

    def read_file(self, file):
        """read a csv file containing the schedule info"""
        try:
            Serializor.parse(self, file)
        except Exception as e:
            raise errors.CouldNotReadFileError(f"Could not read {file}, {e}")

    def write_file(self, file):
        """write to a csv file all the info about the schedule"""
        try:
            Serializor.write(self, file)
        except Exception as e:
            raise errors.CouldNotWriteFileError(f"Could not read {file}, {e}")

    # ------------------------------------------------------------------------
    # adding an object to collection
    # ... if the unique identifier already exists, then update existing object,
    #     rather than creating a new one
    # ------------------------------------------------------------------------
    def add_update_course(self, number: str, name: str = "new Course",
                          semester: SemesterType = SemesterType.any, hours:float = DEFAULT_COURSE_HOURS,
                          needs_allocation: bool = True) -> Course:
        """Creates or updates a Course object with the unique identifier 'teacher_id'
        :param number: Unique identifier for the course
        :param name: Name of the course
        :param semester: Which semester is this course in
        :param hours: How many hours per week are allocated for this course
        :param needs_allocation: Will give allocation to any teacher who teaches this course [True]
        """
        original_course: Course = self.get_course_by_number(number)
        if original_course is None:
            course: Course = Course(number, name, semester, hours, needs_allocation)
            self._courses[course.number] = course
            return course
        else:
            original_course.semester = semester
            original_course.name = name
            original_course.needs_allocation = needs_allocation
            return original_course

    def add_update_stream(self, number: str, description: str = "") -> Stream:
        """Creates or updates a Stream object with the unique identifier 'teacher_id'
        :param number: Unique identifier for the stream
        :param description: (optional)
        """
        original_stream = self.get_stream_by_number(number)
        if original_stream is None:
            stream = Stream(number, description)
            self._streams[stream.number] = stream
            return stream
        else:
            original_stream.description = description
            return original_stream

    def add_update_lab(self, number: str, description: str = '') -> Lab:
        """Creates or updates a Lab object with the unique identifier 'teacher_id'
        :param number: Unique identifier for the lab
        :param description: (optional)
        """
        original_lab = self.get_lab_by_number(number)
        if original_lab is None:
            lab: Lab = Lab(number, description)
            self._labs[lab.number] = lab
            return lab
        else:
            original_lab.description = description
            return original_lab

    def add_update_teacher(self, firstname: str, lastname: str, department: str = "", release:float = 0,
                           teacher_id: str = None) -> Teacher:
        """Creates or updates a teacher object with the unique identifier 'teacher_id'
        :param release:
        :param firstname:
        :param lastname:
        :param department: (optional)
        :param teacher_id: (optional) - if not specified, a unique id will be created
        """
        original_teacher = self.get_teacher_by_number(teacher_id) if teacher_id is not None else None
        if original_teacher is None:
            teacher = Teacher(firstname, lastname, department, release=release)
            self._teachers[teacher.number] = teacher
            return teacher
        else:
            original_teacher.firstname = firstname
            original_teacher.lastname = lastname
            original_teacher.department = department
            return original_teacher

    # ------------------------------------------------------------------------
    # returning collections as a tuple (to prevent user from modifying the collection)
    # ------------------------------------------------------------------------
    def courses(self) -> tuple[Course, ...]:
        """sorted list of courses (read only)"""
        return tuple(sorted(self._courses.values()))

    def labs(self) -> tuple[Lab, ...]:
        """sorted list of labs (read only)"""
        return tuple(sorted(self._labs.values()))

    def streams(self) -> tuple[Stream, ...]:
        """sorted list of streams (read only)"""
        return tuple(sorted(self._streams.values()))

    def teachers(self) -> tuple[Teacher, ...]:
        """sorted list of teachers (read only)"""
        return tuple(sorted(self._teachers.values()))

    # ------------------------------------------------------------------------
    # finding object to collection by number, id, etc
    # ------------------------------------------------------------------------

    def get_course_by_number(self, number: str) -> Optional[Course]:
        """Returns the Course which matches this Course number, if it exists."""
        return self._courses.get(number)

    def get_lab_by_number(self, number: str) -> Optional[Lab]:
        """Returns the Lab which matches this Lab number, if it exists."""
        return self._labs.get(number)

    def get_stream_by_number(self, number: str) -> Optional[Stream]:
        """Returns the Stream which matches this Stream number, if it exists."""
        return self._streams.get(number)

    def get_teacher_by_name(self, firstname: str, lastname: str) -> Optional[Teacher]:
        """Returns the Teacher which matches this name, if it exists."""
        found = [t for t in self._teachers.values()
                 if t.firstname.lower() == firstname.lower() and
                 t.lastname.lower() == lastname.lower()]
        return found[0] if found else None

    def get_teacher_by_number(self, teacher_id: str) -> Optional[Teacher]:
        """Returns the teacher which matches this Section number, if it exists."""
        teacher_id = str(teacher_id)
        return self._teachers.get(teacher_id)

    def get_view_type_obj_by_id(self, view_type: ResourceType, obj_id: str) -> Optional[Teacher | Stream | Lab]:
        """Returns the Section which matches this Section number, if it exists."""
        if view_type == ResourceType.teacher:
            return self.get_teacher_by_number(obj_id)
        elif view_type == ResourceType.stream:
            return self.get_stream_by_number(obj_id)
        elif view_type == ResourceType.lab:
            return self.get_lab_by_number(obj_id)
        return None

    # ========================================================================
    # removing objects from the collections
    # - this may require detaching some dependencies
    # ========================================================================

    def remove_course(self, course: Course):
        """Removes Course from the collection of courses"""
        self._courses.pop(course.number, None)

    def remove_teacher(self, teacher: Teacher):
        """Removes Teacher from all scheduled courses and from the collection of teachers"""
        for c in self.courses():
            c.remove_teacher(teacher)
        self._teachers.pop(teacher.number, None)

    def remove_lab(self, lab: Lab):
        """Removes Lab from all blocks where it is used, and removes from collection of labs"""
        for b in self.blocks():
            b.remove_lab(lab)
        self._labs.pop(lab.number, None)

    def remove_stream(self, stream: Stream):
        """Removes Stream from all sections where it is used and removes from collection of streams"""
        for s in self.sections():
            s.remove_stream(stream)
        self._streams.pop(stream.number, None)

    # ========================================================================
    # filtered collections
    # ========================================================================

    def get_teachers_assigned_to_any_course(self) -> tuple[Teacher, ...]:
        """Returns a tuple of all the Teacher objects with assigned courses"""
        teachers: set[Teacher] = set()
        for c in self.courses():
            for s in c.sections():
                teachers.update(set(s.teachers()))
        return tuple(sorted(teachers))

    def get_streams_assigned_to_any_course(self) -> tuple[Stream, ...]:
        """Returns a tuple of all the Stream objects that have been assigned to any section in a course"""
        streams: set[Stream] = set()
        for c in self.courses():
            for s in c.sections():
                streams.update(set(s.streams()))
        return tuple(sorted(streams))

    def get_labs_assigned_to_any_course(self) -> tuple[Lab, ...]:
        """Returns a tuple of all the Lab objects that have been assigned to any block in a course"""
        labs: set[Lab] = set()
        for c in self.courses():
            for s in c.sections():
                labs.update(set(s.labs()))
        return tuple(sorted(labs))

    def get_courses_for_teacher(self, teacher: Teacher) -> tuple[Course, ...]:
        """Get all the courses that has this teacher assigned to it"""
        courses: set[Course] = set([c for c in self.courses() if c.has_teacher(teacher)])
        return tuple(sorted(courses))

    # ========================================================================
    # Course innards
    # ========================================================================
    def sections(self) -> tuple[Section, ...]:
        """ Returns a tuple of all the schedule's Section objects in this Schedule"""
        sections: set[Section] = set()
        for c in self.courses():
            sections.update(set(c.sections()))
        return tuple(sections)

    def blocks(self) -> tuple[Block, ...]:
        """ Returns a tuple of all the schedule's Block objects in this Schedule"""
        blocks: set[Block] = set()
        for s in self.sections():
            blocks.update(set(s.blocks()))
        return tuple(blocks)

    # ========================================================================
    # filtered Course innards
    # ========================================================================
    def get_sections_for_teacher(self, teacher: Teacher) -> tuple[Section, ...]:
        """Returns a tuple of Sections that the given Teacher teaches"""
        sections: set[Section] = set([s for s in self.sections() if teacher in s.teachers()])
        return tuple(sections)

    def get_sections_for_stream(self, stream: Stream) -> tuple[Section, ...]:
        """Returns a tuple of Sections assigned to the given Stream"""
        streams: set[Section] = set([s for s in self.sections() if s.has_stream(stream)])
        return tuple(streams)

    def get_blocks_for_teacher(self, teacher: Teacher) -> tuple[Block, ...]:
        """Returns a tuple of Blocks that the given Teacher teaches"""
        blocks: set[Block] = set([b for b in self.blocks() if b.has_teacher(teacher)])
        return tuple(blocks)

    def get_blocks_in_lab(self, lab: Lab) -> tuple[Block, ...]:
        """Returns a tuple of Blocks using the given Lab"""
        blocks: set[Block] = set([b for b in self.blocks() if b.has_lab(lab)])
        return tuple(blocks)

    def get_blocks_for_stream(self, stream: Stream) -> tuple[Block, ...]:
        """Returns a tuple of blocks in a given stream"""
        blocks: set[Block] = set()
        for s in self.get_sections_for_stream(stream):
            blocks.update(set(s.blocks()))
        return tuple(blocks)

    def get_blocks_for_obj(self, obj: Teacher | Lab | Stream) -> tuple[Block, ...]:
        """ Returns a tuple of blocks associated with the specified ResourceType object"""
        if isinstance(obj, Teacher):
            return self.get_blocks_for_teacher(obj)
        if isinstance(obj, Lab):
            return self.get_blocks_in_lab(obj)
        if isinstance(obj, Stream):
            return self.get_blocks_for_stream(obj)
        return tuple()

    # --------------------------------------------------------
    # teacher_stat
    # --------------------------------------------------------
    def teacher_stat(self, teacher: Teacher) -> str:
        """
        Returns text that gives teacher statistics
        Parameter teacher -> The teacher whose statistics will be returned
        """
        courses = self.get_courses_for_teacher(teacher)
        blocks = self.get_blocks_for_teacher(teacher)
        sections = self.get_sections_for_teacher(teacher)

        week = dict(
            mon=False,
            tue=False,
            wed=False,
            thu=False,
            fri=False,
            sat=False,
            sun=False,
        )

        week_str = dict(
            mon="Monday",
            tue="Tuesday",
            wed="Wednesday",
            thu="Thursday",
            fri="Friday",
            sat="Saturday",
            sun="Sunday"
        )

        hours_of_work = 0

        for b in blocks:
            hours_of_work += b.time_slot.duration

            week[b.time_slot.day] = True

        message = f"""{teacher.firstname} {teacher.lastname}'s Stats.
        
        Days of the week working:
        {" ".join((week_str[k] if v else "") for k, v in week.items())}
        
        Hours of Work: {hours_of_work}
        Courses being taught:
        """

        for c in courses:
            num_sections = 0
            for s in sections:
                if s.course is c:
                    num_sections += 1
            message += f"-> {c.title} ({num_sections} Section(s))\n"

        return message

    # --------------------------------------------------------
    # teacher_details
    # --------------------------------------------------------

    def teacher_details(self, teacher: Teacher) -> str:
        """
        Prints a schedule for a specific teacher
        Parameter teacher -> The teacher whose schedule to print
        """
        head = "=" * 50
        text = f"\n\n{head}\n{teacher}\n{head}\n"

        c: Course
        for c in sorted(self.get_courses_for_teacher(teacher), key=lambda a: a.number.lower()):

            text += f"\n{c.number} {c.name}\n"
            text += "-" * 80

            # sections
            for s in sorted(c.sections(), key=lambda a: a.number):
                if s.has_teacher(teacher):
                    text += f"\n\t{s}\n\t" + "- " * 25 + "\n"

                    # blocks
                    for b in s.blocks():
                        if b.has_teacher(teacher):
                            text += f"\t{b.time_slot} "
                            text += ", ".join(str(lab) for lab in b.labs()) + "\n"
        return text

    # --------------------------------------------------------
    # clear_all_from_course
    # --------------------------------------------------------
    def clear_all_from_course(self, course: Course):
        """
        Removes all teacher_ids, lab_ids, and stream_ids from course
        - Parameter course -> The course to be cleared.
        """
        for section in self.sections():
            if section.course is course:
                section.remove_all_teachers()
                section.remove_all_streams()
                section.remove_all_labs()

    # --------------------------------------------------------
    # Calculate Conflicts
    # --------------------------------------------------------
    def calculate_conflicts(self):
        """Reviews the schedule, and creates a list of Conflict objects as necessary"""

        # reset all blocks conflicted_number tags
        for b in self.blocks():
            b.conflict = ConflictType.NONE

        # set conflicts for each block, as required
        for teacher in self.get_teachers_assigned_to_any_course():
            set_block_conflicts(self.get_blocks_for_teacher(teacher), ConflictType.TIME_TEACHER)
        for stream in self.get_streams_assigned_to_any_course():
            set_block_conflicts(self.get_blocks_for_stream(stream), ConflictType.TIME_STREAM)
        for lab in self.get_labs_assigned_to_any_course():
            set_block_conflicts(self.get_blocks_in_lab(lab), ConflictType.TIME_LAB)

        # ---------------------------------------------------------
        # for each teacher teacher
        # ---------------------------------------------------------
        for teacher in self.get_teachers_assigned_to_any_course():
            set_lunch_break_conflicts(self.get_blocks_for_teacher(teacher))
            set_availability_hours_conflict(self.get_blocks_for_teacher(teacher))
            if not teacher.release:
                set_number_of_days_conflict(self.get_blocks_for_teacher(teacher))
