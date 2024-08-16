from __future__ import annotations
from typing import Optional,  TYPE_CHECKING
import schedule.exceptions as errors

from .teacher import Teacher
from .course import Course
from .lab import Lab
from .stream import Stream
from .section import Section
from ._conflict_calculations import *
from .enums import ResourceType, SemesterType
from .serializor import CSVSerializor as Serializor


""" SYNOPSIS/EXAMPLE:
    from Schedule.Schedule import Schedule

    schedule = Schedule.read_DB(my_schedule_id)

    # code here; model classes have been populated

    schedule.write_DB()
"""


def _by_number(collection, number):
    found = [obj for obj in collection.values() if obj.number == number]
    return found[0] if found else None


def get_view_type_of_object(obj: Teacher | Lab | Stream) -> ResourceType | None:
    """Returns the resource_type of the ResourceType object"""
    for vtype in ResourceType:
        my_class = eval(f"{vtype.name}")
        if isinstance(obj, my_class):
            return vtype
    return None


class Schedule:
    """
    Provides the top level class for all schedule objects.

    The data that creates the schedule can be saved to or read from a MySQL database.

    This class provides links to all the other classes that are used to create and/or modify course schedules.
    """

    # ========================================================
    # CONSTRUCTOR
    # ========================================================

    def __init__(self, file: Optional[str] = None):
        """
        Creates an instance of the Schedule class.
        """
        self._teachers: dict[int, Teacher] = dict()
        self._streams: dict[int, Stream] = dict()
        self._labs: dict[int, Lab] = dict()
        self._courses: dict[int, Course] = dict()

        # If file argument not none, then read data from file
        if file is not None:
            self.read_file(file)

    def read_file(self, file):
        try:
            Serializor.parse(self, file)
        except Exception as e:
            raise errors.CouldNotReadFileError(f"Could not read {file}, {e}")

    def write_file(self, file):
        try:
            Serializor.write(self, file)
        except Exception as e:
            raise errors.CouldNotWriteFileError(f"Could not read {file}, {e}")

    # ========================================================================
    # adding object to collection
    # ========================================================================
    def add_course(self, number: str = "", name: str = "new Course",
                   semester: (SemesterType | int) = SemesterType.any, needs_allocation: bool = True,
                   course_id: int = None) -> Course:
        """Creates and saves a new Course object."""
        course: Course = Course(number, name, semester, needs_allocation, course_id)
        self._courses[course.id] = course
        return course

    def add_stream(self, number: str = "A", description: str = "", *, stream_id: int = None) -> Stream:
        """Creates and saves a new Stream object."""
        stream = Stream(number, description, stream_id=stream_id)
        self._streams[stream.id] = stream
        return stream

    def add_lab(self, number: str = "P100", description: str = '', *, lab_id: int = None) -> Lab:
        """Creates and saves a new Lab object."""
        lab: Lab = Lab(number, description, lab_id=lab_id)
        self._labs[lab.id] = lab
        return lab

    def add_teacher(self, firstname: str, lastname: str, department: str = "", teacher_id: int = None) -> Teacher:
        teacher = Teacher(firstname, lastname, department, teacher_id=teacher_id)
        self._teachers[teacher.id] = teacher
        return teacher

    # ========================================================================
    # returning collections as a tuple
    # ========================================================================
    @property
    def courses(self) -> tuple[Course, ...]:
        """sorted list of courses (read only)"""
        return tuple(sorted(self._courses.values()))

    @property
    def labs(self) -> tuple[Lab, ...]:
        """sorted list of labs (read only)"""
        return tuple(sorted(self._labs.values()))

    @property
    def streams(self) -> tuple[Stream, ...]:
        """sorted list of streams (read only)"""
        return tuple(sorted(self._streams.values()))

    @property
    def teachers(self) -> tuple[Teacher, ...]:
        """sorted list of teachers (read only)"""
        return tuple(sorted(self._teachers.values()))

    # ========================================================================
    # finding object to collection by number, id, etc
    # ========================================================================

    def get_course_by_number(self, number: str) -> Course | None:
        """Returns the Course which matches this Course number, if it exists."""
        return _by_number(self._courses, number)

    def get_lab_by_number(self, number: str) -> Lab | None:
        """Returns the Lab which matches this Lab number, if it exists."""
        return _by_number(self._labs, number)

    def get_stream_by_number(self, number: str) -> Stream | None:
        """Returns the Stream which matches this Stream number, if it exists."""
        return _by_number(self._streams, number)

    def get_teacher_by_name(self, firstname: str, lastname: str) -> Teacher | None:
        """Returns the Teacher which matches this name, if it exists."""
        for t in self._teachers.values():
            if t.firstname.lower() == firstname.lower():
                if t.lastname.lower() == lastname.lower():
                    print(t)
        found = [t for t in self._teachers.values() if t.firstname.lower() == firstname.lower() and
                 t.lastname.lower() == lastname.lower()]
        return found[0] if found else None

    def get_course_by_id(self, course_id: int) -> Course | None:
        """Returns the Course which matches this id, if it exists."""
        return self._courses.get(course_id)

    def get_lab_by_id(self, lab_id: int) -> Lab | None:
        """Returns the Lab which matches this id, if it exists."""
        return self._labs.get(lab_id)

    def get_stream_by_id(self, stream_id: int) -> Stream | None:
        """Returns the Stream which matches this id, if it exists."""
        return self._streams.get(stream_id)

    def get_teacher_by_id(self, teacher_id: int) -> Teacher | None:
        """Returns the Section which matches this Section number, if it exists."""
        return self._teachers.get(teacher_id)

    def get_view_type_obj_by_id(self, view_type: ResourceType, obj_id: int) -> Optional[Teacher | Stream | Lab]:
        """Returns the Section which matches this Section number, if it exists."""
        if view_type == ResourceType.teacher:
            return self._teachers.get(obj_id)
        elif view_type == ResourceType.stream:
            return self._streams.get(obj_id)
        elif view_type == ResourceType.lab:
            return self._labs.get(obj_id)
        return None

    # ========================================================================
    # removing objects from the collections
    # - this may require detaching some dependencies
    # ========================================================================

    def remove_course(self, course: Course):
        """Removes Course from the collection of courses"""
        if course.id in self._courses:
            _ = self._courses.pop(course.id)

    def remove_teacher(self, teacher: Teacher):
        """Removes Teacher from all scheduled courses and from the collection of teachers"""
        for c in self.courses:
            c.remove_teacher(teacher)
        if teacher.id in self._teachers:
            _ = self._teachers.pop(teacher.id)

    def remove_lab(self, lab: Lab):
        """Removes Lab from all blocks where it is used, and removes from collection of labs"""
        for b in self.blocks:
            b.remove_lab(lab)
        if lab.id in self._labs:
            _ = self._labs.pop(lab.id)

    def remove_stream(self, stream: Stream):
        """Removes Stream from all sections where it is used and removes from collection of streams"""
        for s in self.sections:
            s.remove_stream(stream)
        if stream.id in self._streams:
            _ = self._streams.pop(stream.id)

    # ========================================================================
    # filtered collections
    # ========================================================================

    @property
    def get_teachers_assigned_to_any_course(self) -> tuple[Teacher, ...]:
        """Returns a tuple of all the Teacher objects with assigned courses"""
        teachers: set[Teacher] = set()
        for c in self.courses:
            for s in c.sections:
                teachers.update(set(s.teachers))
        return tuple(sorted(teachers))

    @property
    def get_streams_assigned_to_any_course(self) -> tuple[Stream, ...]:
        """Returns a tuple of all the Stream objects that have been assigned to any section in a course"""
        streams: set[Stream] = set()
        for c in self.courses:
            for s in c.sections:
                streams.update(set(s.streams))
        return tuple(sorted(streams))

    @property
    def get_labs_assigned_to_any_course(self) -> tuple[Lab, ...]:
        """Returns a tuple of all the Lab objects that have been assigned to any block in a course"""
        labs: set[Lab] = set()
        for c in self.courses:
            for s in c.sections:
                labs.update(set(s.labs))
        return tuple(sorted(labs))

    def get_courses_for_teacher(self, teacher: Teacher) -> tuple[Course, ...]:
        """Get all the courses that has this teacher assigned to it"""
        courses: [Course] = set([c for c in self.courses if c.has_teacher(teacher)])
        return tuple(sorted(courses))

    # ========================================================================
    # Course innards
    # ========================================================================
    @property
    def sections(self) -> tuple[Section, ...]:
        """ Returns a tuple of all the schedule's Section objects in this Schedule"""
        sections: set[Section] = set()
        for c in self.courses:
            sections.update(set(c.sections))
        return tuple(sections)

    @property
    def blocks(self) -> tuple[Block, ...]:
        """ Returns a tuple of all the schedule's Block objects in this Schedule"""
        blocks: set[Block] = set()
        for s in self.sections:
            blocks.update(set(s.blocks))
        return tuple(blocks)

    # ========================================================================
    # filtered Course innards
    # ========================================================================
    def get_sections_for_teacher(self, teacher: Teacher) -> tuple[Section, ...]:
        """Returns a tuple of Sections that the given Teacher teaches"""
        sections: set[Section] = set([s for s in self.sections if teacher in s.teachers])
        return tuple(sections)

    def get_sections_for_stream(self, stream: Stream) -> tuple[Section, ...]:
        """Returns a tuple of Sections assigned to the given Stream"""
        streams: [Section] = set([s for s in self.sections if s.has_stream(stream)])
        return tuple(streams)

    def get_blocks_for_teacher(self, teacher: Teacher) -> tuple[Block, ...]:
        """Returns a tuple of Blocks that the given Teacher teaches"""
        blocks: [Block] = set([b for b in self.blocks if b.has_teacher(teacher)])
        return tuple(blocks)

    def get_blocks_in_lab(self, lab: Lab) -> tuple[Block, ...]:
        """Returns a tuple of Blocks using the given Lab"""
        blocks: [Block] = set([b for b in self.blocks if b.has_lab(lab)])
        return tuple(blocks)

    def get_blocks_for_stream(self, stream: Stream) -> tuple[Block, ...]:
        """Returns a tuple of blocks in a given stream"""
        blocks: set[Block] = set()
        for s in self.get_sections_for_stream(stream):
            blocks.update(set(s.blocks))
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
            hours_of_work += b.duration

            week[b.day] = True

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
            for s in sorted(c.sections, key=lambda a: a.number):
                if s.has_teacher(teacher):
                    text += f"\n\t{s}\n\t" + "- " * 25 + "\n"

                    # blocks
                    for b in s.blocks:
                        if b.has_teacher(teacher):
                            text += f"\t{b.day} {b.start} {b.duration} hours\n\t\tlabs: "
                            text += ", ".join(str(lab) for lab in b.labs) + "\n"
        return text

    # --------------------------------------------------------
    # clear_all_from_course
    # --------------------------------------------------------
    def clear_all_from_course(self, course: Course):
        """
        Removes all teacher_ids, lab_ids, and stream_ids from course
        - Parameter course -> The course to be cleared.
        """
        for section in self.sections:
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
        for b in self.blocks:
            b.reset_conflicted()

        # ---------------------------------------------------------
        # check all blocks pairs to see if there is a time overlap
        # ---------------------------------------------------------
        # check if these blocks have a conflict
        for teacher in self.get_teachers_assigned_to_any_course:
            block_conflict(self.get_blocks_for_teacher(teacher), ConflictType.TIME_TEACHER)
        for stream in self.get_streams_assigned_to_any_course:
            block_conflict(self.get_blocks_for_stream(stream), ConflictType.TIME_STREAM)
        for lab in self.get_labs_assigned_to_any_course:
            block_conflict(self.get_blocks_in_lab(lab), ConflictType.TIME_LAB)

        # ---------------------------------------------------------
        # for each teacher teacher
        # ---------------------------------------------------------
        for teacher in self.get_teachers_assigned_to_any_course:

            # lunch break
            relevant_blocks = tuple(list(b for b in self.get_blocks_for_teacher(teacher)
                                         if b.start_number < LUNCH_END
                                         and b.start_number + b.duration > LUNCH_START))

            lunch_break_conflict(relevant_blocks)

            # check for 4 day schedule
            if not teacher.release:
                number_of_days_conflict(self.get_blocks_for_teacher(teacher))

            # too many availability hours
            availability_hours_conflict(self.get_blocks_for_teacher(teacher))
