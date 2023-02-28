from Teacher import Teacher
from Course import Course
from Conflict import Conflict
from Lab import Lab
from Stream import Stream
from Section import Section
from Block import Block
from Time_slot import TimeSlot
import os
import re
import yaml # might require pip install pyyaml

import database.PonyDatabaseConnection as db
from pony.orm import *


""" SYNOPSIS/EXAMPLE:
    from Schedule.Schedule import Schedule

    Schedule.read_YAML('my_schedule_file.txt')

    # code here; model classes have been populated

    Schedule.write_YAML('my_new_schedule_file.txt')
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
    def __init__(self, id, semester, official, scenario, descr = ""):
        """ Creates an instance of the Schedule class. """
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
    
    # Read and Write will need to be replaced with DB-relevant methods, see connection syntax below

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Static Methods
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

    # --------------------------------------------------------
    # read_DB
    # --------------------------------------------------------
    @staticmethod
    def read_DB(id):
        sched = db.Schedule.get(id=id)
        scenario = db.Scenario.get(id=sched.scenario_id.id)
        # create Model version of scenario
        schedule = Schedule(id, sched.semester, sched.official, scenario, sched.description)

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
                b = Block(slot.day, slot.start, slot.duration, block.number, id = block.id, time_slot_id = slot.id)
                s.add_block(b)
                for l in block.labs: b.assign_lab(Lab.get(l.id))
                for t in block.teachers: b.assign_teacher(Teacher.get(t.id))
        
        Schedule.calculate_conflicts()
        return schedule
    
    @db_session
    def write_DB(self):
        def save_time_slot(model_time_slot):
            # TimeSlot.save() as written by Evan
            # return entity object at the end
            d_slot = db.TimeSlot.get(id=model_time_slot.id)
            if d_slot is not None:
                d_slot.day = model_time_slot.day
                d_slot.duration = model_time_slot.duration
                d_slot.start = model_time_slot.start
                d_slot.movable = model_time_slot.movable

            return None
        # scenario changes, once that's implemented

        # update any schedule changes
        sched = db.Schedule.get(id=self.id)
        sched.semester = self.semester
        sched.official = self.official
        sched.description = self.descr

        # update all courses
        for c in Course.list():
            cc = db.Course.get(id=c.id)
            cc.name = c.name
            cc.number = c.number
            cc.allocation = c.needs_allocation
        
        # update all teachers
        for t in Teacher.list():
            tt = db.Teacher.get(id=t.id)
            tt.first_name = t.firstname
            tt.last_name = t.lastname
            tt.dept = t.dept
        
        # update all streams
        for st in Stream.list():
            sst = db.Stream.get(id=st.id)
            sst.number = st.number
            sst.descr = st.descr
        
        # update all streams
        for l in Lab.list():
            ll = db.Lab.get(id=l.id)
            ll.number = l.number
            ll.description = l.descr
            for ts in l.unavailable(): ll.unavailable_slots.add(save_time_slot(ts))
        pass
            
    @staticmethod
    def __create_teacher(id : int) -> Teacher:
        """ Takes a given ID and returns the Teacher model object with given ID. If it doesn't exist, creates it from the database. """
        if Teacher.get(id): return Teacher.get(id)
        teacher = db.Teacher.get(id = id)
        return Teacher(teacher.first_name, teacher.last_name, teacher.dept, id = id)
            
    @staticmethod
    def __create_stream(id : int) -> Stream:
        """ Takes a given ID and returns the Stream model object with given ID. If it doesn't exist locally, creates it from the database, and adds to database if not already present. """
        if Stream.get(id): return Stream.get(id)
        stream = db.Stream.get(id = id)
        return Stream(stream.number, stream.descr, id = id)

    #region Read & Write YAML (TEMPORARY)
    # --------------------------------------------------------
    # read_YAML
    # --------------------------------------------------------
    @staticmethod
    def read_YAML(file : str):
        schedule = Schedule()
        if os.path.isfile(file):
            try:
                f = open(file, "r")
                # same as below -_ substitution, but specifically for mangled names (_Class__var)
                raw_yaml = re.sub(r"^(\s*)_[a-zA-Z]*?__", "", f.read())
                # regex substitution replaces - or _ at the beginning of variable names, since the manual casting assumes clean var names
                # take out any tags, since we're bypassing them and initializing classes manually
                    # this is a terrible thing and should NOT be done in a long-term project, absolutely not scalable
                raw_yaml = re.sub(r'!.*$', '', re.sub(r"^(\s*)[_-]([^- ])", r"\1\2", raw_yaml, flags=re.MULTILINE), flags=re.MULTILINE)
                # enclose timestamps in single quotes to avoid sexagesimal conversion (9:00 -> 540 seconds)
                raw_yaml = re.sub(r'(\s)(\d+):(\d+)(\s)', r"\1'\2:\3'\4", raw_yaml)
                max_ids = {}
                (
                    yaml_contents, max_ids['block'], max_ids['course'], max_ids['lab'],
                    max_ids['section'], max_ids['teacher'], max_ids['timeslot'], max_ids['stream'] 
                ) = yaml.safe_load_all(raw_yaml)
                
                # set max IDs so that there's no accidental overlap with automatic calculation & manual overwrite
                Schedule.__set_max_ids(max_ids)

                for c in yaml_contents['conflicts']['list']: Schedule.__create_conflict(c)
                for c in yaml_contents['courses']['list'].values(): Schedule.__create_course(c)
                for l in yaml_contents['labs']['list'].values(): Schedule.__create_lab(l)
                for s in yaml_contents['streams']['list'].values(): Schedule.__create_stream_yaml(s)
                for t in yaml_contents['teachers']['list'].values(): Schedule.__create_teacher_yaml(t)

                # set max IDs again so it now matches with the stored value
                Schedule.__set_max_ids(max_ids)
                return schedule
            except Exception as e:
                print(f"Cannot read from file {file}: {str(e)}")
                # should probably be replaced with tkinter error screen
                return
            finally:
                f.close()
        
        raise f"File {file} does not exist"
        # should probably be replaced with tkinter error screen

    # --------------------------------------------------------
    # write_YAML
    # --------------------------------------------------------
    @staticmethod
    def write_YAML(file : str) -> bool:
        """
        Writes all schedule data to specified YAML file
        - Parameter file -> The file to output to
        """
        if os.path.isfile(file):
            try:
                f = open(file, "w")
                dic = dict(
                    conflicts = dict( list = Conflict.list() ),
                    courses = dict( list = Course.list() ),
                    labs = dict( list = Lab.list() ),
                    streams = dict( list = Stream.list() ),
                    teachers = dict( list = Teacher.list() )
                )
                yam = yaml.dump_all([
                    dic, Block._max_id, Course._max_id, Lab._max_id, Section._max_id,
                    Teacher._max_id, TimeSlot._max_id, Stream._max_id
                    ], explicit_start=True)
                f.write(yam)
                return True
            except Exception as e:
                print(f"Cannot write to file {file}: {str(e)}")
                # should probably be replaced with tkinter error screen
                return False
            finally: f.close()

    # ========================================================
    # BAD METHODS - TEMPORARY FOR YAML FILE
    # break all kinds of conventions but they're temporary
    # DO NOT REPLICATE THIS ANYWHERE ELSE IT'S HARD TO USE AND NOT SCALABLE
    # ========================================================
    
    @staticmethod
    def __create_conflict(conflict : dict) -> Conflict:
        conflicts = list(filter(lambda i : i.id == conflict.get('id', -1), Conflict))
        if len(conflicts) == 0:
            blocks = []
            for b in conflict.get('blocks'): blocks.append(Schedule.__create_block(b))
            c = Conflict(type = conflict.get('type', 1), blocks = blocks)
            
            return c
        else: return conflicts[0]

    @staticmethod
    def __create_block(block : dict) -> Block:
        blocks = list(filter(lambda i : i.id == block.get('id', -1), Block))
        if len(blocks) == 0:
            b = Block(block.get('day', ''), block.get('start', ''), block.get('duration', 0), block.get('number', 0))
            old_id = b.id
            b._Block__id = block.get('id', b.id)
            del Block._Block__instances[old_id]
            Block._Block__instances[b.id] = b
            b.conflicted = block.get('conflicted', b.conflicted)
            # don't set day_number, its calculated based on day
            # don't set start_number, its calculated based on start
            for k in block.get('labs', {}).keys(): b.assign_lab(Schedule.__create_lab(block.get('labs', {})[k]))
            b.movable = block.get('movable', b.movable)
            if block.get('section'): b.section = Schedule.__create_section(block.get('section'))
            for k in block.get('teachers', {}).keys(): b.assign_teacher(Schedule.__create_teacher_yaml(block.get('teachers', {})[k]))
            b._Block__sync = block.get('sync', [])

            return b
        else: return blocks[0]

    @staticmethod
    def __create_section(section : dict) -> Section:
        sections = list(filter(lambda i : i.id == section.get('id', -1), Section) )
        if len(sections) == 0:
            s = Section(section.get('number', ''), section.get('hours', 0), section.get('name', ''))
            if section.get('course'): s.course = Schedule.__create_course(section.get('course'))
            for k in section.get('blocks', {}).keys(): s.add_block(Schedule.__create_block(section.get('blocks', {})[k]))
            old_id = s.id
            s._Section__id = section.get('id', s.id)
            del Section._Section__instances[old_id]
            Section._Section__instances[s.id] = s
            s._allocation = section.get('allocation', s._allocation)
            s.num_students = section.get('num_students', s.num_students)
            for k in section.get('streams', {}).keys(): s.assign_stream(Schedule.__create_stream_yaml(section.get('streams', {})[k]))
            for k in section.get('teachers', {}).keys(): s.assign_teacher(Schedule.__create_teacher_yaml(section.get('teachers', {})[k]))
            return s
        else: return sections[0]

    @staticmethod
    def __create_lab(lab : dict) -> Lab:
        if Lab.get(lab.get('id', -1)): return Lab.get(lab.get('id', -1))
        else:
            l =  Lab(lab.get('number', ''), lab.get('descr', ''))
            old_id = l.id
            l._Lab__id = lab.get('id', l.id)
            del Lab._instances[old_id]
            Lab._instances[l.id] = l
            return l

    @staticmethod
    def __create_teacher_yaml(teacher : dict) -> Teacher:
        if Teacher.get(teacher.get('id', -1)): return Teacher.get(teacher.get('id', -1))
        else:
            t = Teacher(teacher.get('fname', ''), teacher.get('lname', ''), teacher.get('dept', ''))
            t.release = teacher.get('release', t.release)
            old_id = t.id
            t._Teacher__id = teacher.get('id', t.id)
            del Teacher._instances[old_id]
            Teacher._instances[t.id] = t
            return t

    @staticmethod
    def __create_course(course : dict) -> Course:
        if Course.get(course.get('id', -1)): return Course.get(course.get('id', -1))
        else:
            c = Course(number = course.get('number', ''), name = course.get('name', ''), semester = course.get('semester', ''))
            c._allocation = course.get('allocation', c.allocation)
            old_id = c.id
            c._Course__id = course.get('id', c.id)
            del Course._instances[old_id]
            Course._instances[c.id] = c
            for k in course.get('sections', {}).keys(): c.assign_section(Schedule.__create_section(course.get('sections', {})[k]))
            return c
        
    @staticmethod
    def __create_stream_yaml(stream : dict) -> Stream:
        if Stream.get(stream.get('id', -1)): return Stream.get(stream.get('id', -1))
        else:
            s = Stream(stream.get('number', 'A'), stream.get('descr', ''))
            old_id = s.id
            s._Stream__id = stream.get('id', s.id)
            del Stream._Stream__instances[old_id]
            Stream._Stream__instances[s.id] = s
            return s

#endregion

    # --------------------------------------------------------
    # __set_max_ids - Sets the max IDs of each class to specified values or 0. Unsure if it'll be useful for DB, but just in case listed separately from YAML methods
    # --------------------------------------------------------
    @staticmethod
    def __set_max_ids(max_ids : dict):
        Block._max_id = max_ids.get("block", 0)
        Course._max_id = max_ids.get("course", 0)
        Lab._max_id = max_ids.get("lab", 0)
        Section._max_id = max_ids.get("section", 0)
        Teacher._max_id = max_ids.get("teacher", 0)
        TimeSlot._max_id = max_ids.get("timeslot", 0)
        Stream._max_id = max_ids.get("stream", 0)

    # --------------------------------------------------------
    # teachers
    # --------------------------------------------------------
    @staticmethod
    def teachers() -> list[Teacher]:
        """Returns the list of Teachers"""
        return Teacher.list()

    # --------------------------------------------------------
    # streams
    # --------------------------------------------------------
    @staticmethod
    def streams() -> tuple[Stream]:
        """Returns the list of Streams"""
        return Stream.list()

    # --------------------------------------------------------
    # courses
    # --------------------------------------------------------
    @staticmethod
    def courses() -> list[Course]:
        """Returns the list of Courses"""
        return Course.list()

    # --------------------------------------------------------
    # labs
    # --------------------------------------------------------
    @staticmethod
    def labs() -> list[Lab]:
        """Returns the list of Labs"""
        return Lab.list()

    # --------------------------------------------------------
    # conflicts
    # --------------------------------------------------------
    @staticmethod
    def conflicts() -> list[Conflict]:
        """Returns the list of Conflicts"""
        return Conflict.list()

    # --------------------------------------------------------
    # sections_for_teacher
    # --------------------------------------------------------
    @staticmethod
    def sections_for_teacher(teacher : Teacher) -> list[Section]:
        """
        Returns a list of Sections that the given Teacher teaches
        - Parameter teacher -> The Teacher who's Sections should be found
        """
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        outp = set()
        for s in Section.list():
            if teacher in s.teachers: outp.add(s)
        return list(outp)

    # --------------------------------------------------------
    # courses_for_teacher
    # --------------------------------------------------------
    @staticmethod
    def courses_for_teacher(teacher : Teacher) -> list[Course]:
        """
        Returns a list of Courses that the given Teacher teaches
        - Parameter teacher -> The Teacher who's Courses should be found
        """
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        outp = set()
        for c in Course.list():
            if c.has_teacher(teacher): outp.add(c)
        return list(outp)

    # --------------------------------------------------------
    # allocated_courses_for_teacher
    # --------------------------------------------------------
    @staticmethod
    def allocated_courses_for_teacher(teacher : Teacher) -> list[Course]:
        """
        Returns a list of courses that this teacher teaches, which is an allocated type course
        - Parameter teacher -> The Teacher to check
        """
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        return list(filter(lambda c : c.needs_allocation, Schedule.courses_for_teacher(teacher)))

    # --------------------------------------------------------
    # blocks_for_teacher
    # --------------------------------------------------------
    @staticmethod
    def blocks_for_teacher(teacher : Teacher) -> list[Block]:
        """
        Returns a list of Blocks that the given Teacher teaches
        - Parameter teacher -> The Teacher who's Blocks should be found
        """
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        outp = set()
        for b in Block.list():
            if b.has_teacher(teacher): outp.add(b)
        return list(outp)

    # --------------------------------------------------------
    # blocks_in_lab
    # --------------------------------------------------------
    @staticmethod
    def blocks_in_lab(lab : Lab) -> list[Lab]:
        """
        Returns a list of Blocks using the given Lab
        - Parameter lab -> The Lab that should be found
        """
        if not isinstance(lab, Lab): raise TypeError(f"{lab} must be an object of type Lab")
        outp = set()
        for b in Block.list():
            if b.has_lab(lab): outp.add(b)
        return list(outp)

    # --------------------------------------------------------
    # sections_for_stream
    # --------------------------------------------------------
    @staticmethod
    def sections_for_stream(stream : Stream) -> list[Section]:
        """
        Returns a list of Sections assigned to the given Stream
        - Parameter stream -> The Stream that should be found
        """
        if not isinstance(stream, Stream): raise TypeError(f"{stream} must be an object of type Stream")
        outp = set()
        for s in Section.list():
            if s.has_stream(stream): outp.add(s)
        return list(outp)

    # --------------------------------------------------------
    # blocks_for_stream
    # --------------------------------------------------------
    @staticmethod
    def blocks_for_stream(stream : Stream) -> list[Block]:
        """
        Returns a list of Blocks in the given Stream
        - Parameter stream -> The Stream who's Blocks should be found
        """
        if not isinstance(stream, Stream): raise TypeError(f"{stream} must be an object of type Stream")
        outp = set()
        for s in Schedule.sections_for_stream(stream): outp.update(s.blocks)
        return list(outp)

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
        def __new_conflict(type, blocks):
            Conflict(type, blocks)
            for b in blocks: b.conflicted = type
        # create list of all blocks -> no longer needed
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
                    if (Teacher.share_blocks(b, bb)):
                        is_conflict = True
                        b.conflicted = bb.conflicted = Conflict.TIME_TEACHER
                    if (Lab.share_blocks(b, bb)):
                        is_conflict = True
                        b.conflicted = bb.conflicted = Conflict.TIME_LAB
                    if (Stream.share_blocks(b, bb)):
                        is_conflict = True
                        b.conflicted = bb.conflicted = Conflict.TIME_STREAM
                    
                    # create a conflict object and mark the blocks as conflicting
                    if is_conflict: __new_conflict(Conflict.TIME, [b, bb])

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
                # don't know how this could occur, in Python or Perl
                if not blocks: continue

                # check for the existence of a lunch break in any of the :30 periods
                has_lunch = False
                for start in lunch_periods:
                    # is this period free?
                    has_lunch = all(not Schedule._conflict_lunch(b, start) for b in blocks)
                    if has_lunch: break
                
                # if no lunch, create a conflict obj and mark blocks as conflicted
                if not has_lunch: __new_conflict(Conflict.LUNCH, blocks)

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
            if len(blocks_by_day.keys()) < 4 and blocks: __new_conflict(Conflict.MINIMUM_DAYS, blocks)
            
            # if they have more than 32 hours worth of classes
            availability = 0
            for blocks_in_day in blocks_by_day.values():
                day_start = min(map(lambda b: b.start_number, blocks_in_day))
                day_end = max(map(lambda b: b.start_number + b.duration, blocks_in_day))
                if day_end <= day_start: continue
                availability += day_end - day_start - 0.5
            
            # if over limit, create conflict
            if availability > 32: __new_conflict(Conflict.AVAILABILITY, blocks)
        
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
            Monday = False,
            Tuesday = False,
            Wednesday = False,
            Thursday = False,
            Friday = False,
            Saturday = False,
            Sunday = False
        )
        hours_of_work = 0

        for b in blocks:
            hours_of_work += b.duration
            match b.day.lower():
                case 'mon': week['Monday'] = True
                case 'tue': week['Tuesday'] = True
                case 'wed': week['Wednesday'] = True
                case 'thu': week['Thursday'] = True
                case 'fri': week['Friday'] = True
                case 'sat': week['Saturday'] = True
                case 'sun': week['Sunday'] = True
        
        message = f"""{teacher.firstname} {teacher.lastname}'s Stats.
        
        Days of the week working:
        {"Monday " if week['Monday'] else ''}{"Tuesday " if week['Tuesday'] else ''}{"Wednesday " if week['Wednesday'] else ''}{"Thursday " if week['Thursday'] else ''}{"Friday " if week['Friday'] else ''}{"Saturday " if week['Saturday'] else ''}{"Sunday " if week['Sunday'] else ''}
        
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