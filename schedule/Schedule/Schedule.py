from __future__ import annotations
from .Teachers import Teacher, Teachers
from .Courses import Course, Courses
import ConflictCalculations
from .Labs import Lab, Labs
from .Streams import Stream, Streams
from .Sections import Section
from .Block import Block
from .ScheduleEnums import ViewType, ConflictType

from typing import Optional

""" SYNOPSIS/EXAMPLE:
    from Schedule.Schedule import Schedule

    schedule = Schedule.read_DB(my_schedule_id)

    # code here; model classes have been populated

    schedule.write_DB()
"""


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
        
        - File -> the schedule YAML file
        """
        self.teachers = Teachers()
        self.streams = Streams()
        self.labs = Labs()
        self.courses = Courses()

        # TODO: If file, then read data from file

    # --------------------------------------------------------
    # teacher_ids
    # --------------------------------------------------------
    @property
    def assigned_teachers(self) -> tuple[Teacher, ...]:
        """Returns a tuple of all the Teacher objects with assigned courses"""
        teachers: set[Teacher] = set()
        for s in self.sections:
            teachers.update(set(s.teachers))
        return tuple(teachers)

    # --------------------------------------------------------
    # stream_ids
    # --------------------------------------------------------
    @property
    def assigned_streams(self) -> tuple[Stream, ...]:
        """Returns a tuple of all the Stream objects that have been assigned in this Schedule"""
        streams: set[Stream] = set()
        for s in self.sections:
            streams.update(set(s.streams))
        return tuple(streams)

    # --------------------------------------------------------
    # lab_ids
    # --------------------------------------------------------
    @property
    def assigned_labs(self) -> tuple[Lab, ...]:
        """Returns a tuple of all the Lab objects that have been assigned in this Schedule"""
        labs: set[Lab] = set()
        for s in self.sections:
            labs.update(set(s.labs))
        return tuple(labs)

    # --------------------------------------------------------
    # blocks
    # --------------------------------------------------------
    @property
    def blocks(self) -> tuple[Block, ...]:
        """ Returns a tuple of all the schedule's Block objects in this Schedule"""
        blocks: set[Block] = set()
        for s in self.sections:
            blocks.update(set(s.blocks))
        return tuple(blocks)

    # --------------------------------------------------------
    # sections
    # --------------------------------------------------------
    @property
    def sections(self) -> tuple[Section, ...]:
        """ Returns a tuple of all the schedule's Section objects in this Schedule"""
        sections: set[Section] = set()
        for c in self.courses:
            sections.update(set(c.sections))
        return tuple(sections)

    # --------------------------------------------------------
    # sections_for_teacher
    # --------------------------------------------------------
    def sections_for_teacher(self, teacher: Teacher) -> tuple[Section, ...]:
        """
        Returns a tuple of Sections that the given Teacher teaches
        - Parameter teacher -> The Teacher whose Sections should be found
        """
        sections: set[Section] = set([s for s in self.sections if teacher in s.teachers])
        return tuple(sections)

    # --------------------------------------------------------
    # courses_for_teacher
    # --------------------------------------------------------
    def courses_for_teacher(self, teacher: Teacher) -> tuple[Course, ...]:
        """
        :param teacher: the Teacher whose courses should be found
        :return: a tuple of courses where that teacher teaches
        """
        courses: [Course] = set([c for c in self.courses if c.has_teacher(teacher)])
        return tuple(courses)

    # --------------------------------------------------------
    # allocated_courses_for_teacher
    # --------------------------------------------------------
    def allocated_courses_for_teacher(self, teacher: Teacher) -> tuple[Course]:
        """
        Get tuple of courses that are allocated, where the teacher is teaching
        :param teacher:
        :return: tuple of Courses
        """
        return tuple([c for c in self.courses_for_teacher(teacher) if c.needs_allocation])

    # --------------------------------------------------------
    # blocks_for_teacher
    # --------------------------------------------------------
    def blocks_for_teacher(self, teacher: Teacher) -> tuple[Block]:
        """
        Returns a list of Blocks that the given Teacher teaches
        :param teacher:
        :return: tuple of Blocks objects
        """
        blocks: [Block] = set([b for b in self.blocks if b.has_teacher(teacher)])
        return tuple(blocks)

    # --------------------------------------------------------
    # blocks_in_lab
    # --------------------------------------------------------
    def blocks_in_lab(self, lab: Lab) -> tuple[Block]:
        """
        Returns a list of Blocks using the given Lab
        :param lab:
        :return: a tuple of blocks objects
        """
        blocks: [Block] = set([b for b in self.blocks if b.has_lab(lab)])
        return tuple(blocks)

    # --------------------------------------------------------
    # sections_for_stream
    # --------------------------------------------------------

    def sections_for_stream(self, stream: Stream) -> tuple[Section]:
        """
        Returns a list of Sections assigned to the given Stream
        :param stream: The Stream that should be found
        :return: a tuple of section objects
        """
        streams: [Section] = set([s for s in self.sections if s.has_stream(stream)])
        return tuple(streams)

    # --------------------------------------------------------
    # blocks_for_stream
    # --------------------------------------------------------

    def blocks_for_stream(self, stream: Stream) -> tuple[Block]:
        """
        :param stream: The Stream whose Blocks should be found
        :return: Returns a list of Blocks in the given Stream
        """
        blocks: set[Block] = set()
        for s in self.sections_for_stream(stream):
            blocks.union(set(s.blocks))
        return tuple(blocks)

    # --------------------------------------------------------
    # remove_course
    # --------------------------------------------------------
    def remove_course(self, course: Course):
        """Removes Course from schedule"""
        self.courses.remove(course)

    # --------------------------------------------------------
    # remove_teacher_by_id
    # --------------------------------------------------------
    def remove_teacher(self, teacher: Teacher):
        """Removes Teacher from all scheduled courses and from available teachers list"""
        # go through all blocks, and remove teacher from each
        for b in self.blocks:
            b.remove_teacher(teacher)
        for s in self.sections:
            s.remove_teacher(teacher)
        self.teachers.remove(teacher)

    # --------------------------------------------------------
    # remove_lab_by_id
    # --------------------------------------------------------
    def remove_lab(self, lab: Lab):
        """Removes Lab from schedule"""
        for b in self.blocks:
            b.remove_lab(lab)
        self.labs.remove(lab)

    # --------------------------------------------------------
    # remove_stream_by_id
    # --------------------------------------------------------
    def remove_stream(self, stream: Stream):
        """Removes Stream from schedule"""
        for s in self.sections:
            s.remove_stream(stream)
        self.streams.remove(stream)

    # --------------------------------------------------------
    # teacher_stat
    # --------------------------------------------------------
    def teacher_stat(self, teacher: Teacher) -> str:
        """
        Returns text that gives teacher statistics
        Parameter teacher -> The teacher whose statistics will be returned
        """
        courses = self.courses_for_teacher(teacher)
        blocks = self.blocks_for_teacher(teacher)
        sections = self.sections_for_teacher(teacher)

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
        from functools import cmp_to_key

        head = "=" * 50
        text = f"\n\n{head}\n{teacher}\n{head}\n"

        c: Course
        for c in sorted(self.courses_for_teacher(teacher), key=lambda a: a.number.lower()):

            text += f"\n{c.number} {c.name}\n"
            text += "-" * 80

            # sections
            for s in sorted(c.sections, key=lambda a: a.number):
                if s.has_teacher(teacher):
                    text += f"\n{s}\n\t" + "- " * 25 + "\n"

                    # blocks
                    for b in sorted(s.blocks, key=cmp_to_key(self.__sort_blocks)):
                        if b.has_teacher(teacher):
                            text += f"\t{b.day} {b.start} {b.duration} hours\n\t\tlab_ids: "
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
    # get_by_id blocks info for specified ViewType object
    # --------------------------------------------------------
    def get_blocks_for_obj(self, obj: Teacher | Lab | Stream) -> tuple[Block]:
        """ Returns a tuple of blocks associated with the specified ViewType object"""
        if isinstance(obj, Teacher):
            return self.blocks_for_teacher(obj)
        if isinstance(obj, Lab):
            return self.blocks_in_lab(obj)
        if isinstance(obj, Stream):
            return self.blocks_for_stream(obj)
        return tuple()

    @staticmethod
    def get_view_type_of_object(obj: Teacher | Lab | Stream) -> ViewType | None:
        """Returns the type of the ViewType object"""
        for vtype in ViewType:
            my_class = eval(f"{vtype.name}")
            if isinstance(obj, my_class):
                return vtype
        return None

    def calculate_conflicts(self):
        """Reviews the schedule, and creates a list of Conflict objects as necessary"""

        # reset all blocks conflicted_number tags
        for b in self.blocks:
            b.reset_conflicted()

        # ---------------------------------------------------------
        # check all blocks pairs to see if there is a time overlap
        # ---------------------------------------------------------
        # check if these blocks have a conflict
        for teacher in self.assigned_teachers:
            ConflictCalculations.block_conflict(self.blocks_for_teacher(teacher), ConflictType.TIME_TEACHER)
        for stream in self.assigned_streams:
            ConflictCalculations.block_conflict(self.blocks_for_stream(stream), ConflictType.TIME_STREAM)
        for lab in self.assigned_labs:
            ConflictCalculations.block_conflict(self.blocks_in_lab(lab), ConflictType.TIME_LAB)


        # ---------------------------------------------------------
        # for each teacher teacher
        # ---------------------------------------------------------
        for teacher in self.assigned_teachers:

            # lunch break
            relevant_blocks = tuple(list(b for b in self.blocks_for_teacher(teacher)
                                         if b.start_number < ConflictCalculations.LUNCH_END
                                         and b.start_number + b.duration > ConflictCalculations.LUNCH_START))

            ConflictCalculations.lunch_break_conflict(relevant_blocks)

            # check for 4 day schedule
            if not teacher.release:
                ConflictCalculations.number_of_days_conflict(self.blocks_for_teacher(teacher))

            # too many availability hours
            ConflictCalculations.availability_hours_conflict(self.blocks_for_teacher(teacher))

    @staticmethod
    def __sort_blocks(a: Block, b: Block) -> int:
        if a.day_number < b.day_number:
            return 1
        elif a.day_number > b.day_number:
            return -1
        elif a.start_number < b.start_number:
            return 1
        elif a.start_number > b.start_number:
            return -1
        else:
            return 0
