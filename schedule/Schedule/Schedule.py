from __future__ import annotations
from .Teacher import Teacher
from .Course import Course
from .Conflict import Conflict
from .Lab import Lab
from .Stream import Stream
from .Section import Section
from .Block import Block
from .LabUnavailableTime import LabUnavailableTime
from .ScheduleEnums import ConflictType, ViewType

from .SectionList import SectionList

from .database import PonyDatabaseConnection as db
from pony.orm import *

""" SYNOPSIS/EXAMPLE:
    from Schedule.Schedule import Schedule

    sched = Schedule.read_DB(my_schedule_id)

    # code here; model classes have been populated

    sched.write_DB()
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

    def __init__(self, id : int, official : bool, scenario_id : int, descr : str = ""):

        """
        Creates an instance of the Schedule class.
        
        - Parameter id -> The ID of the current schedule.
        - Parameter official -> Whether the schedule is "official" (confirmed) or pending
        - Parameter scenario_id -> The idea of the schedule's parent scenario
        - Parameter descr -> A description of the schedule and any unique notes
        """
        self._id = id
        self.official = official
        self.scenario_id = scenario_id
        self.descr = descr
        self.sections = SectionList()
    

    # ========================================================
    # PROPERTIES
    # ========================================================
    @property
    def id(self) -> int:
        return self._id

    # ========================================================
    # METHODS
    # ========================================================

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Static Methods
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

    # --------------------------------------------------------
    # read_DB
    # --------------------------------------------------------
    @staticmethod
    @db_session
    def read_DB(id) -> Schedule:
        sched : db.Schedule = db.Schedule.get(id=id)
        scen = sched.scenario_id.id
        schedule = Schedule(id, sched.official, scen, sched.description)

        # set up all lab unavailable times
        slot : db.LabUnavailableTime
        for slot in select(ts for ts in db.LabUnavailableTime if ts.schedule_id.id == sched.id):
            ts = LabUnavailableTime(slot.day, slot.start, slot.duration, slot.movable, id = slot.id, schedule = schedule)
            l = Schedule._create_lab(slot.lab_id.id)
            l.add_unavailable_slot(ts)
      

        # add release for this schedule to any teachers
        schedule_teacher: db.Schedule_Teacher
        for schedule_teacher in select(t for t in db.Schedule_Teacher if t.schedule_id.id == id):
            Schedule._create_teacher(schedule_teacher.teacher_id.id).release = schedule_teacher.work_release
            

        # create all sections in this schedule
        section: db.Section
        for section in select(s for s in db.Section if s.schedule_id.id == id):
            c = Schedule._create_course(section.course_id.id)
            s = Section(section.number, section.hours, section.name, c, id = section.id)
            schedule.sections.append(s)

            s.num_students = section.num_students
            c.add_section(s)
            # identify teachers and set allocation
            section_teacher: db.Section_Teacher
            for section_teacher in select(t for t in db.Section_Teacher if t.section_id.id == section.id):
                t = Schedule._create_teacher(section_teacher.teacher_id.id)
                s.assign_teacher(t)
                s.set_teacher_allocation(t, section_teacher.allocation)
            # identify section-stream connections and update accordingly
            for section_stream in section.streams:
                st = Schedule._create_stream(section_stream.id)
                s.assign_stream(st)
            # identify, create, and assign blocks
            block: db.Block
            for block in select(b for b in db.Block if b.section_id.id == s.id):
                b = Block(block.day, block.start, block.duration, block.number, movable=block.movable, id=block.id)
                s.add_block(b)

                for l in block.labs: b.assign_lab(Schedule._create_lab(l.id))
                for t in block.teachers: b.assign_teacher(Schedule._create_teacher(t.id))
        
        schedule.calculate_conflicts()
        return schedule

    @db_session
    def write_DB(self):
        """ Save any schedule-level changes to the database """
        # update any schedule changes
        sched : db.Schedule = db.Schedule.get(id=self.id)
        scen : db.Scenario = db.Scenario.get(id=self.scenario_id)

        if not scen: scen = db.Scenario()
        if not sched: sched = db.Schedule(official=self.official, scenario_id=scen)
        sched.official = self.official
        sched.description = self.descr

        # save schedule & scenario to in-memory db
        flush()

        # update all teachers (needs to stay here to update schedule-teacher linking table)
        for t in self.teachers(): t.save(sched)


        # update all lab unavailable times
        for lut in self.lab_unavailable_times(): lut.save()

        # save courses, teachers, streams, and time slots to in-memory db
        flush()

        # update all sections
        se : Section
        for se in self.sections: se.save(sched)
        
        # save labs and sections to in-memory db
        flush()

        # update all blocks
        b : Block
        for b in self.blocks(): b.save()
            
    @staticmethod
    def _create_teacher(id : int) -> Teacher:
        """ Takes a given ID and returns the Teacher model object with given ID.
        If it doesn't exist locally, creates it from the database, and adds to database if not already present. """
        if Teacher.get(id): return Teacher.get(id)
        teacher : db.Teacher = db.Teacher.get(id = id)
        return Teacher(teacher.first_name, teacher.last_name, teacher.dept, id = id) if teacher else Teacher("N/A", "N/A", id = id)
            
    @staticmethod
    def _create_stream(id : int) -> Stream:
        """ Takes a given ID and returns the Stream model object with given ID.
        If it doesn't exist locally, creates it from the database, and adds to database if not already present. """
        if Stream.get(id): return Stream.get(id)
        stream : db.Stream = db.Stream.get(id = id)
        return Stream(stream.number, stream.descr, id = id) if stream else Stream(id = id)
            
    @staticmethod
    def _create_lab(id : int) -> Lab:
        """ Takes a given ID and returns the Lab model object with given ID.
        If it doesn't exist locally, creates it from the database, and adds to database if not already present. """
        if Lab.get(id): return Lab.get(id)
        lab : db.Lab = db.Lab.get(id = id)
        return Lab(lab.number, lab.description, id = id) if lab else Lab(id = id)
            
    @staticmethod
    def _create_course(id : int) -> Course:
        """ Takes a given ID and returns the Course model object with given ID.
        If it doesn't exist locally, creates it from the database, and adds to database if not already present. """
        if Course.get(id): return Course.get(id)
        course : db.Course = db.Course.get(id = id)
        return Course(course.number, course.name, course.semester, course.allocation, id = id) if course else Course(id = id)


    # --------------------------------------------------------
    # teachers
    # --------------------------------------------------------
    def teachers(self) -> tuple[Teacher]:
        """Returns a tuple of all the Teacher objects"""
        teachers : list[Teacher] = []
        s : Section
        for s in self.sections:
            teachers.extend(s.teachers)
            for b in s.blocks:
                teachers.extend(b.teachers())
        
        return tuple(set(teachers))
    
    # --------------------------------------------------------
    # blocks
    # --------------------------------------------------------
    def blocks(self) -> tuple[Block]:
        """ Returns a tuple of all the schedule's Block objects """
        b : list[Block] = []
        s : Section
        for s in self.sections: b.extend(s.blocks)
        return tuple(set(b))

    # --------------------------------------------------------
    # streams
    # --------------------------------------------------------
    def streams(self) -> tuple[Stream]:
        """Returns a tuple of all the Stream objects"""
        streams : list[Stream] = []
        s : Section
        for s in self.sections:
            streams.extend(s.streams)
            
        return tuple(set(streams))

    # --------------------------------------------------------
    # courses
    # --------------------------------------------------------
    def courses(self) -> tuple[Course]:
        """Returns a tuple of all the Course objects"""
        courses : set[Course] = set()
        s : Section
        for s in self.sections:
            courses.add(s.course)
        
        return tuple(courses)
    
    # --------------------------------------------------------
    # labs
    # --------------------------------------------------------
    def labs(self) -> tuple[Lab]:
        """Returns a tuple of all the Lab objects"""
        labs : list[Lab] = []
        s : Section
        for s in self.sections:
            labs.extend(s.labs)
        
        return tuple(set(labs))
    
    def lab_unavailable_times(self) -> tuple[LabUnavailableTime]:
        """ Returns a tuple of all the blocked Lab times in this schedule """
        times : list[LabUnavailableTime] = []
        for l in self.labs(): times.extend(l.unavailable())
        return tuple(times)

    # --------------------------------------------------------
    # conflicts
    # --------------------------------------------------------
    def conflicts(self) -> tuple[Conflict]:
        """Returns a tuple of all the Conflict objects"""
        cons : list[Conflict] = list(Conflict.list())
        correct : set[Conflict] = set()
        
        for c in cons:
            if c.blocks[0].section in self.sections: correct.add(c)
        
        return tuple(correct)

    # --------------------------------------------------------
    # sections_for_teacher
    # --------------------------------------------------------
    def sections_for_teacher(self, teacher : Teacher) -> tuple[Section]:

        """
        Returns a tuple of Sections that the given Teacher teaches
        - Parameter teacher -> The Teacher who's Sections should be found
        """
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        outp = set()
        s : Section
        for s in self.sections:
            if teacher in s.teachers: outp.add(s)
        return tuple(outp)

    # --------------------------------------------------------
    # courses_for_teacher
    # --------------------------------------------------------
    def courses_for_teacher(self, teacher : Teacher) -> tuple[Course]:

        """
        Returns a list of Courses that the given Teacher teaches
        - Parameter teacher -> The Teacher who's Courses should be found
        """
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        outp = set()
        for c in self.courses():
            if c.has_teacher(teacher): outp.add(c)
        return tuple(outp)

    # --------------------------------------------------------
    # allocated_courses_for_teacher
    # --------------------------------------------------------
    def allocated_courses_for_teacher(self, teacher : Teacher) -> tuple[Course]:

        """
        Returns a list of courses that this teacher teaches, which is an allocated type course
        - Parameter teacher -> The Teacher to check
        """
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        return tuple(filter(lambda c : c.needs_allocation, self.courses_for_teacher(teacher)))


    # --------------------------------------------------------
    # blocks_for_teacher
    # --------------------------------------------------------
    def blocks_for_teacher(self, teacher : Teacher) -> tuple[Block]:

        """
        Returns a list of Blocks that the given Teacher teaches
        - Parameter teacher -> The Teacher who's Blocks should be found
        """

        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        outp = set()
        b : Block
        for b in self.blocks():
            if b.has_teacher(teacher): outp.add(b)
        return tuple(outp)

    # --------------------------------------------------------
    # blocks_in_lab
    # --------------------------------------------------------

    def blocks_in_lab(self, lab : Lab) -> tuple[Lab]:

        """
        Returns a list of Blocks using the given Lab
        - Parameter lab -> The Lab that should be found
        """
        if not isinstance(lab, Lab): raise TypeError(f"{lab} must be an object of type Lab")
        outp = set()
        b : Block
        for b in self.blocks():
            if b.has_lab(lab): outp.add(b)
        return tuple(outp)

    # --------------------------------------------------------
    # sections_for_stream
    # --------------------------------------------------------

    def sections_for_stream(self, stream : Stream) -> tuple[Section]:

        """
        Returns a list of Sections assigned to the given Stream
        - Parameter stream -> The Stream that should be found
        """
        if not isinstance(stream, Stream): raise TypeError(f"{stream} must be an object of type Stream")
        outp = set()
        s : Section
        for s in self.sections:
            if s.has_stream(stream): outp.add(s)
        return tuple(outp)

    # --------------------------------------------------------
    # blocks_for_stream
    # --------------------------------------------------------

    def blocks_for_stream(self, stream : Stream) -> tuple[Block]:

        """
        Returns a list of Blocks in the given Stream
        - Parameter stream -> The Stream who's Blocks should be found
        """
        if not isinstance(stream, Stream): raise TypeError(f"{stream} must be an object of type Stream")
        outp = set()
        s : Section
        for s in self.sections_for_stream(stream): outp.update(s.blocks)
        return tuple(outp)

    # NOTE: all_x() methods have been removed, since they're now equivalent to x() methods

    # --------------------------------------------------------
    # remove_course
    # --------------------------------------------------------

    def remove_course(self, course : Course):

        """Removes Course from schedule"""
        if not isinstance(course, Course): raise TypeError(f"{course} must be an object of type Course")
        course.remove()

    # --------------------------------------------------------
    # remove_teacher
    # --------------------------------------------------------

    def remove_teacher(self, teacher : Teacher):

        """Removes Teacher from schedule"""
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        # go through all blocks, and remove teacher from each
        b : Block
        for b in self.blocks(): b.remove_teacher(teacher)
        teacher.remove()

    # --------------------------------------------------------
    # remove_lab
    # --------------------------------------------------------
    def remove_lab(self, lab : Lab):

        """Removes Lab from schedule"""
        if not isinstance(lab, Lab): raise TypeError(f"{lab} must be an object of type Lab")
        # go through all blocks, and remove lab from each
        b : Block
        for b in self.blocks(): b.remove_lab(lab)

    # --------------------------------------------------------
    # remove_stream
    # --------------------------------------------------------
    def remove_stream(self, stream : Stream):

        """Removes Stream from schedule"""
        if not isinstance(stream, Stream): raise TypeError(f"{stream} must be an object of type Stream")
        # go through all sections, and remove stream from each
        s : Section
        for s in self.sections: s.remove_stream(stream)

    # --------------------------------------------------------
    # calculate_conflicts
    # --------------------------------------------------------
    def calculate_conflicts(self):
        """Reviews the schedule, and creates a list of Conflict objects as necessary"""

        def __new_conflict(type: ConflictType, blocks: list[Block]):
            Conflict(type, blocks)
            for b in blocks: b.conflicted = type.value

        # reset all blocks conflicted tags
        for b in self.blocks(): b.reset_conflicted()

        # ---------------------------------------------------------
        # check all block pairs to see if there is a time overlap
        for index, b in enumerate(self.blocks()):
            for bb in self.blocks()[index + 1:]:
                # if the same block, skip (shouldn't happen)
                if b == bb: continue

                # if the blocks overlap in time
                if b.conflicts_time(bb):
                    is_conflict = False
                    # if teachers/labs/streams share these blocks its a real conflict
                    # and must be dealt with
                    if Teacher.share_blocks(b, bb):
                        is_conflict = True
                        b.conflicted = bb.conflicted = ConflictType.TIME_TEACHER.value
                    if Lab.share_blocks(b, bb):
                        is_conflict = True
                        b.conflicted = bb.conflicted = ConflictType.TIME_LAB.value
                    if Stream.share_blocks(b, bb):
                        is_conflict = True
                        b.conflicted = bb.conflicted = ConflictType.TIME_STREAM.value

                    # create a conflict object and mark the blocks as conflicting
                    if is_conflict: __new_conflict(ConflictType.TIME, [b, bb])

        # ---------------------------------------------------------
        # check for lunch break conflicts by teacher
        start_lunch = 11
        end_lunch = 14

        lunch_periods = list(i/2 for i in range(start_lunch * 2, end_lunch * 2))
        for t in Teacher.list():    # no need to use schedule.teachers because it filters using self.blocks_for_teacher anyways
            # filter to only relevant blocks (that can possibly conflict)
            relevant_blocks = list(
                filter(lambda b : b.start_number < end_lunch and b.start_number + b.duration > start_lunch, self.blocks_for_teacher(t)))
            # collect blocks by day
            blocks_by_day : dict[int, list[Block]] = { }
            b : Block

            for b in relevant_blocks:
                if not b.day_number in blocks_by_day: blocks_by_day[b.day_number] = []
                blocks_by_day[b.day_number].append(b)

            for blocks in blocks_by_day.values():
                # don't know how this could occur, but just being careful
                if not blocks: continue

                # check for the existence of a lunch break in any of the :30 periods
                has_lunch = False
                for start in lunch_periods:
                    # is this period free?
                    has_lunch = all(not Schedule._conflict_lunch(b, start) for b in blocks)
                    if has_lunch: break

                # if no lunch, create a conflict obj and mark blocks as conflicted
                if not has_lunch: __new_conflict(ConflictType.LUNCH, blocks)

        # ---------------------------------------------------------
        # check for 4 day schedule or 32 hrs max
        for t in Teacher.list():
            if t.release: continue

            # collect blocks by day

            blocks_by_day : dict[int, list[Block]] = { }
            blocks = self.blocks_for_teacher(t)

            for b in blocks:
                if not b.day_number in blocks_by_day: blocks_by_day[b.day_number] = []
                blocks_by_day[b.day_number].append(b)

            # if < 4 days, create a conflict and mark the blocks as conflicted
            if len(blocks_by_day.keys()) < 4 and blocks: __new_conflict(ConflictType.MINIMUM_DAYS, blocks)

            # if they have more than 32 hours worth of classes
            availability = 0
            for blocks_in_day in blocks_by_day.values():
                day_start = min(map(lambda b: b.start_number, blocks_in_day))
                day_end = max(map(lambda b: b.start_number + b.duration, blocks_in_day))
                if day_end <= day_start: continue
                availability += day_end - day_start - 0.5

            # if over limit, create conflict
            if availability > 32: __new_conflict(ConflictType.AVAILABILITY, blocks)

        # Perl ver. returns self here

    # --------------------------------------------------------
    # _conflict_lunch
    # --------------------------------------------------------
    @staticmethod
    def _conflict_lunch(block: Block, lunch_start):
        lunch_end = lunch_start + .5
        block_end_number = block.start_number + block.duration
        return (
                (block.start_number < lunch_end and lunch_start < block_end_number) or
                (lunch_start < block_end_number and block.start_number < lunch_end)
        )

    # --------------------------------------------------------
    # teacher_stat
    # --------------------------------------------------------

    def teacher_stat(self, teacher : Teacher) -> str:

        """
        Returns text that gives teacher statistics
        Parameter teacher -> The teacher who's statistics will be returned
        """
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
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
                if s.course is c: num_sections += 1
            message += f"-> {c.description} ({num_sections} Section(s))\n"

        return message

    # --------------------------------------------------------
    # teacher_details
    # --------------------------------------------------------

    def teacher_details(self, teacher : Teacher) -> str:

        """
        Prints a schedule for a specific teacher
        Parameter teacher -> The teacher who's schedule to print
        """
        from functools import cmp_to_key
        def __sort_blocks(a: Block, b: Block) -> int:
            if a.number < b.number:
                return 1
            elif a.number > b.number:
                return -1
            elif a.start_number < b.start_number:
                return 1
            elif a.start_number > b.start_number:
                return -1
            else:
                return 0

        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        head = "=" * 50
        text = f"\n\n{head}\n{teacher}\n{head}\n"

        c : Course
        for c in sorted(self.courses_for_teacher(teacher), key = lambda a : a.number.lower()):

            text += f"\n{c.number} {c.name}\n"
            text += "-" * 80

            # sections
            for s in sorted(c.sections(), key=lambda a: a.number):
                if s.has_teacher(teacher):
                    text += f"\n{s}\n\t" + "- " * 25 + "\n"

                    # blocks
                    for b in sorted(s.blocks, key=cmp_to_key(__sort_blocks)):
                        if b.has_teacher(teacher):
                            text += f"\t{b.day} {b.start} {b.duration} hours\n\t\tlabs: "
                            text += ", ".join(str(l) for l in b.labs()) + "\n"
        return text

    # --------------------------------------------------------
    # clear_all_from_course
    # --------------------------------------------------------

    def clear_all_from_course(self, course : Course):

        """
        Removes all teachers, labs, and streams from course
        - Parameter course -> The course to be cleared.
        """
        if not course: return
        if not isinstance(course, Course): raise TypeError(f"{course} must be an object of type Course")
        s : Section
        for s in self.sections: 
            if s.course is course: Schedule.clear_all_from_section(s)

    # --------------------------------------------------------
    # clear_all_from_section
    # --------------------------------------------------------
    @staticmethod
    # can be static because the section is passed in
    def clear_all_from_section(section : Section):

        """
        Removes all teachers, labs, and streams from section
        - Parameter section -> The section to be cleared.
        """
        if not section: return
        if not isinstance(section, Section): raise TypeError(f"{section} must be an object of type Section")
        # done manually in Perl ver
        section.remove_all_teachers()
        section.remove_all_streams()
        labs = Lab.list()  # why does this use the global list of Labs?
        for l in labs: section.remove_lab(l)

    # --------------------------------------------------------
    # clear_all_from_block
    # --------------------------------------------------------
    @staticmethod
    # can be static because the block is passed in
    def clear_all_from_block(block : Block):

        """
        Removes all teachers, labs, and streams from block
        - Parameter block -> The block to be cleared.
        """
        if not block: return
        if not isinstance(block, Block): raise TypeError(f"{block} must be an object of type Block")
        # done manually in Perl ver
        block.remove_all_teachers()
        block.remove_all_labs()

    # --------------------------------------------------------
    # get block info for specified ViewType object
    # --------------------------------------------------------
    def get_blocks_for_obj(self, obj: Teacher | Lab | Stream) -> tuple[Block]:
        """ Returns a tuple of blocks associated with the specified ViewType object"""
        if isinstance(obj, Teacher): return self.blocks_for_teacher(obj)
        if isinstance(obj, Lab): return self.blocks_in_lab(obj)
        if isinstance(obj, Stream): return self.blocks_for_stream(obj)
        return tuple()

    @staticmethod
    def get_view_type_of_object(obj) -> ViewType | None:
        # was originally named: get_scheduable_object_type
        """Returns the type of the ViewType object"""
        for vtype in ViewType:
            if isinstance(obj, vtype.value): return vtype
        return None
