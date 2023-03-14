from Teacher import Teacher
from Course import Course
from Conflict import Conflict
from Lab import Lab
from Stream import Stream
from Section import Section
from Block import Block
from Time_slot import TimeSlot
from ScheduleEnums import ConflictType, ViewType
import os
import re

import database.PonyDatabaseConnection as db
from pony.orm import *

""" SYNOPSIS/EXAMPLE:
    from Schedule.Schedule import Schedule

    sched = Schedule.read_DB(my_schedule_id)

    # code here; model classes have been populated

    sched.write_YAML()
"""

class Schedule:
    """
    Provides the top level class for all schedule objects.

    The data that creates the schedule can be saved to an external file, or read in from an external file.

    This class provides links to all the other classes that are used to create and/or modify course schedules.
    """

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, id : int, semester : str, official : bool, scenario : dict, descr : str = ""):
        """
        Creates an instance of the Schedule class.
        
        - Parameter id -> The ID of the current schedule.
        - Parameter semester -> The semester the schedule applies to. Ideally formatted "Season Year" (i.e. "Winter 2023")
        - Parameter official -> Whether the schedule is "official" (confirmed) or pending
        - Parameter scenario -> A dict defining the schedule's scenario. Includes name, description, year, and id
        - Parameter descr -> A description of the schedule and any unique notes
        """
        self._id = id
        self.semester = semester
        self.official = official
        self.scenario = scenario
        self.descr = descr
    
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
    # reset_local
    # --------------------------------------------------------
    @staticmethod
    def reset_local():
        """ Reset the local model data """
        Block.reset()
        Course.reset()
        Lab.reset()
        Section.reset()
        Stream.reset()
        Teacher.reset()
        TimeSlot.reset()
        Conflict.reset()

    # --------------------------------------------------------
    # read_DB
    # --------------------------------------------------------
    @staticmethod
    @db_session
    def read_DB(id):
        # wipe all existing model data
        Schedule.reset_local()

        sched = db.Schedule.get(id=id)
        scenario = db.Scenario.get(id=sched.scenario_id.id)
        # placeholder dict
        scen = {
            "name": scenario.name,
            "description": scenario.description,
            "year": scenario.year,
            "id": scenario.id
        }
        schedule = Schedule(id, sched.semester, sched.official, scen, sched.description)

        # create all courses
        for course in select(c for c in db.Course):
            c = Course(course.number, course.name, id=course.id)
            c.needs_allocation = course.allocation
        
        # create all labs
        for lab in select(l for l in db.Lab):
            l1 = Lab(lab.number, lab.description, id=lab.id)
            # set up unavailable times
            for slot in select(ts for ts in db.TimeSlot if ts.unavailable_lab_id.id == lab.id):
                ts = TimeSlot(slot.day, slot.start, slot.duration, slot.movable, id = slot.id)
                l1.add_unavailable_slot(ts)

        # create all teachers
        for teacher in select(t for t in db.Teacher): Schedule.__create_teacher(teacher.id)
        
        # add release for this schedule to any teachers
        for schedule_teacher in select(t for t in db.Schedule_Teacher if t.schedule_id.id == id):
            Schedule.__create_teacher(schedule_teacher.teacher_id.id).release = schedule_teacher.work_release
        
        # create all streams
        for stream in select(s for s in db.Stream): Schedule.__create_stream(stream.id)
            
        # create all sections in this schedule
        for section in select(s for s in db.Section if s.schedule_id.id == id):
            s = Section(section.number, section.hours, section.name, Course.get(section.course_id.id), id = section.id)
            s.num_students = section.num_students
            Course.get(section.course_id.id).add_section(s)
            # identify teachers and set allocation
            for section_teacher in select(t for t in db.Section_Teacher if t.section_id.id == section.id):
                t = Schedule.__create_teacher(section_teacher.teacher_id.id)
                s.assign_teacher(t)
                s.set_teacher_allocation(t, section_teacher.allocation)
            # identify section-stream connections and update accordingly
            for section_stream in section.streams:
                st = Schedule.__create_stream(section_stream.id)
                s.assign_stream(st)
            # identify, create, and assign blocks
            for block in select(b for b in db.Block if b.section_id.id == s.id):
                slot = db.TimeSlot.get(id = block.time_slot_id.id)
                b = Block(slot.day, slot.start, slot.duration, block.number, movable = slot.movable, id = block.id, time_slot_id = slot.id)
                s.add_block(b)
                for l in block.labs: b.assign_lab(Lab.get(l.id))
                for t in block.teachers: b.assign_teacher(Teacher.get(t.id))
        
        Schedule.calculate_conflicts()
        return schedule
    
    @db_session
    def write_DB(self):
        # update any schedule changes
        sched = db.Schedule.get(id=self.id)
        scen = db.Scenario.get(id=self.scenario.get("id", 1))   # assumes Scenario 1 if id isn't stored
        if not scen: scen = db.Scenario()

        if not sched: sched = db.Schedule(semester=self.semester, official=self.official, scenario_id=scen)
        sched.semester = self.semester
        sched.official = self.official
        sched.description = self.descr

        # save schedule & scenario to in-memory db
        flush()

        # update all courses
        for c in Course.list(): c.save()
        
        # update all teachers
        for t in Teacher.list(): t.save(sched)
        
        # update all streams
        for st in Stream.list(): st.save()

        # update all time slots
        for t in TimeSlot.list(): t.save()

        # save courses, teachers, streams, and time slots to in-memory db
        flush()
        
        # update all labs
        for l in Lab.list(): l.save()

        # update all sections
        for se in Section.list(): se.save(sched)
        
        # save labs and sections to in-memory db
        flush()

        # update all blocks
        for b in Block.list(): b.save()
            
    @staticmethod
    def __create_teacher(id : int) -> Teacher:
        """ Takes a given ID and returns the Teacher model object with given ID. If it doesn't exist, creates it from the database. """
        if Teacher.get(id): return Teacher.get(id)
        teacher = db.Teacher.get(id = id)
        return Teacher(teacher.first_name, teacher.last_name, teacher.dept, id = id)
            
    @staticmethod
    def __create_stream(id : int) -> Stream:
        """ Takes a given ID and returns the Stream model object with given ID.
        If it doesn't exist locally, creates it from the database, and adds to database if not already present. """
        if Stream.get(id): return Stream.get(id)
        stream = db.Stream.get(id = id)
        return Stream(stream.number, stream.descr, id = id)

    # --------------------------------------------------------
    # teachers
    # --------------------------------------------------------
    @staticmethod
    def teachers() -> tuple[Teacher]:
        """Returns a tuple of all the Teacher objects"""
        return Teacher.list()

    # --------------------------------------------------------
    # streams
    # --------------------------------------------------------
    @staticmethod
    def streams() -> tuple[Stream]:
        """Returns a tuple of all the Stream objects"""
        return Stream.list()

    # --------------------------------------------------------
    # courses
    # --------------------------------------------------------
    @staticmethod
    def courses() -> tuple[Course]:
        """Returns a tuple of all the Course objects"""
        return Course.list()

    # --------------------------------------------------------
    # labs
    # --------------------------------------------------------
    @staticmethod
    def labs() -> tuple[Lab]:
        """Returns a tuple of all the Lab objects"""
        return tuple(Lab.list())

    # --------------------------------------------------------
    # conflicts
    # --------------------------------------------------------
    @staticmethod
    def conflicts() -> tuple[Conflict]:
        """Returns the a tuple of all the Conflict objects"""
        return tuple(Conflict.list())

    # --------------------------------------------------------
    # sections_for_teacher
    # --------------------------------------------------------
    @staticmethod
    def sections_for_teacher(teacher : Teacher) -> tuple[Section]:
        """
        Returns a tuple of Sections that the given Teacher teaches
        - Parameter teacher -> The Teacher who's Sections should be found
        """
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        outp = set()
        # TODO: Comparing to perl code, this only works if courses,
        #       which may previously exist, but then are removed from the schedule, also remove
        #       the sections, labs, blocks, etc from their lists,
        #       ... if that is taken care of, then this code is ok, (it looks like it is, but we have to be sure)
        #       ... otherwise, you have to verify that the section, lab, block, etc belongs to a course
        #           that belongs to this schedule.
        #       ...
        #       ... Example, we may have a scenario that has complementary xyz in that schedule,
        #           and it is removed, and replaced with course abc.  Sections lists should be
        #           updated accordingly
        #       questions: Do you have a test for dropping a course, and validating that
        #           the lists of teachers, blocks, labs, etc are updated?
        for s in Section.list():
            if teacher in s.teachers: outp.add(s)
        return tuple(outp)

    # --------------------------------------------------------
    # courses_for_teacher
    # --------------------------------------------------------
    @staticmethod
    def courses_for_teacher(teacher : Teacher) -> tuple[Course]:
        """
        Returns a list of Courses that the given Teacher teaches
        - Parameter teacher -> The Teacher who's Courses should be found
        """
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        outp = set()
        for c in Course.list():
            if c.has_teacher(teacher): outp.add(c)
        return tuple(outp)

    # --------------------------------------------------------
    # allocated_courses_for_teacher
    # --------------------------------------------------------
    @staticmethod
    def allocated_courses_for_teacher(teacher : Teacher) -> tuple[Course]:
        """
        Returns a list of courses that this teacher teaches, which is an allocated type course
        - Parameter teacher -> The Teacher to check
        """
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        return tuple(filter(lambda c : c.needs_allocation, Schedule.courses_for_teacher(teacher)))

    # --------------------------------------------------------
    # blocks_for_teacher
    # --------------------------------------------------------
    @staticmethod
    def blocks_for_teacher(teacher : Teacher) -> tuple[Block]:
        """
        Returns a list of Blocks that the given Teacher teaches
        - Parameter teacher -> The Teacher who's Blocks should be found
        """
        # TODO: see above comments for sections_for_teachers

        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        outp = set()
        for b in Block.list():
            if b.has_teacher(teacher): outp.add(b)
        return tuple(outp)

    # --------------------------------------------------------
    # blocks_in_lab
    # --------------------------------------------------------
    @staticmethod
    def blocks_in_lab(lab : Lab) -> tuple[Lab]:
        """
        Returns a list of Blocks using the given Lab
        - Parameter lab -> The Lab that should be found
        """
        # TODO: see above comments for sections_for_teachers
        if not isinstance(lab, Lab): raise TypeError(f"{lab} must be an object of type Lab")
        outp = set()
        for b in Block.list():
            if b.has_lab(lab): outp.add(b)
        return tuple(outp)

    # --------------------------------------------------------
    # sections_for_stream
    # --------------------------------------------------------
    @staticmethod
    def sections_for_stream(stream : Stream) -> tuple[Section]:
        """
        Returns a list of Sections assigned to the given Stream
        - Parameter stream -> The Stream that should be found
        """
        # TODO: see above comments for sections_for_teachers
        if not isinstance(stream, Stream): raise TypeError(f"{stream} must be an object of type Stream")
        outp = set()
        for s in Section.list():
            if s.has_stream(stream): outp.add(s)
        return tuple(outp)

    # --------------------------------------------------------
    # blocks_for_stream
    # --------------------------------------------------------
    @staticmethod
    def blocks_for_stream(stream : Stream) -> tuple[Block]:
        """
        Returns a list of Blocks in the given Stream
        - Parameter stream -> The Stream who's Blocks should be found
        """
        if not isinstance(stream, Stream): raise TypeError(f"{stream} must be an object of type Stream")
        outp = set()
        for s in Schedule.sections_for_stream(stream): outp.update(s.blocks)
        return tuple(outp)

    # NOTE: all_x() methods have been removed, since they're now equivalent to x() methods

    # --------------------------------------------------------
    # remove_course
    # --------------------------------------------------------
    @staticmethod
    def remove_course(course : Course):
        """Removes Course from schedule"""
        if not isinstance(course, Course): raise TypeError(f"{course} must be an object of type Course")
        course.delete()

    # --------------------------------------------------------
    # remove_teacher
    # --------------------------------------------------------
    @staticmethod
    def remove_teacher(teacher : Teacher):
        """Removes Teacher from schedule"""
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        # go through all blocks, and remove teacher from each
        for b in Block.list(): b.remove_teacher(teacher)
        Teacher.delete(teacher)

    # --------------------------------------------------------
    # remove_lab
    # --------------------------------------------------------
    @staticmethod
    def remove_lab(lab : Lab):
        """Removes Lab from schedule"""
        if not isinstance(lab, Lab): raise TypeError(f"{lab} must be an object of type Lab")
        # go through all blocks, and remove lab from each
        for b in Block.list(): b.remove_lab(lab)
        Lab.delete(lab)

    # --------------------------------------------------------
    # remove_stream
    # --------------------------------------------------------
    @staticmethod
    def remove_stream(stream : Stream):
        """Removes Stream from schedule"""
        if not isinstance(stream, Stream): raise TypeError(f"{stream} must be an object of type Stream")
        # go through all sections, and remove stream from each
        for s in Section.list(): s.remove_stream(stream)
        stream.delete()

    # --------------------------------------------------------
    # calculate_conflicts
    # --------------------------------------------------------
    @staticmethod
    def calculate_conflicts():
        """Reviews the schedule, and creates a list of Conflict objects as necessary"""
        def __new_conflict(type:ConflictType, blocks):
            Conflict(type, blocks)
            for b in blocks: b.conflicted = type.value

        # reset the conflict list
        Conflict.reset()

        # reset all blocks conflicted tags
        for b in Block.list(): b.reset_conflicted()

        # ---------------------------------------------------------
        # check all block pairs to see if there is a time overlap
        for index, b in enumerate(Block.list()):
            for bb in Block.list()[index + 1:]:
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
        lunch_periods = list(i/2 for i in range(start_lunch*2, end_lunch*2))
        for t in Teacher.list():
            # filter to only relevant blocks (that can possibly conflict)
            relevant_blocks = list(
                filter(lambda b : b.start_number < end_lunch and b.start_number + b.duration > start_lunch, Schedule.blocks_for_teacher(t)))
            # collect blocks by day
            blocks_by_day = { }
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
            blocks_by_day = { }
            blocks = Schedule.blocks_for_teacher(t)
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
    def _conflict_lunch(block : Block, lunch_start):
        lunch_end = lunch_start + .5
        block_end_number = block.start_number + block.duration
        return (
            (block.start_number < lunch_end and lunch_start < block_end_number) or
            (lunch_start < block_end_number and block.start_number < lunch_end)
        )

    # --------------------------------------------------------
    # teacher_stat
    # --------------------------------------------------------
    @staticmethod
    def teacher_stat(teacher : Teacher) -> str:
        """
        Returns text that gives teacher statistics
        Parameter teacher -> The teacher who's statistics will be returned
        """
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        courses = Schedule.courses_for_teacher(teacher)
        blocks = Schedule.blocks_for_teacher(teacher)
        sections = Schedule.sections_for_teacher(teacher)

        week = dict(
            mon = False,
            tue = False,
            wed = False,
            thu = False,
            fri = False,
            sat = False,
            sun = False,
        )

        week_str = dict(
            mon = "Monday",
            tue = "Tuesday",
            wed = "Wednesday",
            thu = "Thursday",
            fri = "Friday",
            sat = "Saturday",
            sun = "Sunday"
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
            message += f"-> {c.print_description2()} ({num_sections} Section(s))\n"
        
        return message

    # --------------------------------------------------------
    # teacher_details
    # --------------------------------------------------------
    @staticmethod
    def teacher_details(teacher : Teacher) -> str:
        """
        Prints a schedule for a specific teacher
        Parameter teacher -> The teacher who's schedule to print
        """
        from functools import cmp_to_key
        def __sort_blocks(a, b):
            if a.number < b.number: return 1
            elif a.number > b.number: return -1
            elif a.start_number < b.start_number: return 1
            elif a.start_number > b.start_number: return -1
            else: return 0

        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        head = "="*50
        text = f"\n\n{head}\n{teacher}\n{head}\n"
        for c in sorted(Schedule.courses_for_teacher(teacher), key=lambda a : a.number.lower()):
            text += f"\n{c.number} {c.name}\n"
            text += "-"*80

            # sections
            for s in sorted(c.sections(), key = lambda a : a.number):
                if s.has_teacher(teacher):
                    text += f"\n{s}\n\t" + "- "*25 + "\n"

                    # blocks
                    for b in sorted(s.blocks, key=cmp_to_key(__sort_blocks)):
                        if b.has_teacher(teacher):
                            text += f"\t{b.day} {b.start} {b.duration} hours\n\t\tlabs: "
                            text += ", ".join(str(l) for l in b.labs()) + "\n"
        return text

    # --------------------------------------------------------
    # clear_all_from_course
    # --------------------------------------------------------
    @staticmethod
    def clear_all_from_course(course : Course):
        """
        Removes all teachers, labs, and streams from course
        - Parameter course -> The course to be cleared.
        """
        if not course: return
        if not isinstance(course, Course): raise TypeError(f"{course} must be an object of type Course")
        for s in course.sections(): Schedule.clear_all_from_section(s)

    # --------------------------------------------------------
    # clear_all_from_section
    # --------------------------------------------------------
    @staticmethod
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
        labs = Lab.list()   # why does this use the global list of Labs?
        for l in labs: section.remove_lab(l)

    # --------------------------------------------------------
    # clear_all_from_block
    # --------------------------------------------------------
    @staticmethod
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
    # get block infor for specified ViewType object
    # --------------------------------------------------------
    def get_blocks_for_obj(self, obj) -> tuple[Block]:
        """ Returns a tuple of blocks associated with the specified ViewType object"""
        if isinstance(obj,Teacher): return self.blocks_for_teacher(obj)
        if isinstance(obj,Lab): return self.blocks_for_lab(obj)
        if isinstance(obj,Stream): return self.blocks_for_stream(obj)
        return tuple()

    @staticmethod
    def get_view_type_of_object(obj)->ViewType:
        # was originally named: get_scheduable_object_type
        """Returns the type of the ViewType object"""
        for vtype in ViewType:
            if isinstance(obj,vtype.value): return vtype
        return None

