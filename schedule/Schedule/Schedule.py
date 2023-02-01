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


class Schedule:
    """
    Provides the top level class for all schedule objects.

    The data that creates the schedule can be saved to an external file, or read in from an external file.

    This class provides links to all the other classes that are used to create and/or modify course schedules.
    """

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, **kwargs):
        """ Creates an instance of the Schedule class. """
        # Reset max ids (NOTE: Conflict has no max id)
        Stream._max_id = 0
        Teacher._max_id = 0
        Course._max_id = 0
        Lab._max_id = 0
        Block._max_id = 0
        TimeSlot._max_id = 0
        Section._max_id = 0

    # ========================================================
    # METHODS
    # ========================================================
    
    # Read and Write will need to be replaced with DB-relevant methods, see connection syntax below
    """
    # pip install mysql-connector-python

    import mysql.connector

    db = mysql.connector.connect(
        host = server_ip,
        username = username,
        password = password
    )

    cursor = db.cursor()

    # connect to DB, create tables, etc
    cursor.execute("command")
    """

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Static Methods
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

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
                raw_yaml = re.sub("^(\s*)_[a-zA-Z]*?__", "", f.read())
                # regex substitution replaces - or _ at the beginning of variable names, since the manual casting assumes clean var names
                # take out any tags, since we're bypassing them and initializing classes manually
                    # this is a terrible thing and should NOT be done in a long-term project, absolutely not scalable
                raw_yaml = re.sub('!.*$', '', re.sub("^(\s*)[_-]([^- ])", r"\1\2", raw_yaml, flags=re.MULTILINE), flags=re.MULTILINE)
                # enclose timestamps in single quotes to avoid sexagesimal conversion (9:00 -> 540 seconds)
                raw_yaml = re.sub('(\s)(\d+):(\d+)(\s)', r"\1'\2:\3'\4", raw_yaml)
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
                for s in yaml_contents['streams']['list'].values(): Schedule.__create_stream(s)
                for t in yaml_contents['teachers']['list'].values(): Schedule.__create_teacher(t)

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
                    courses = dict( list = Course._instances ),
                    labs = dict( list = Lab._instances ),
                    streams = dict( list = Stream._instances ),
                    teachers = dict( list = Teacher._instances )
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
    # ========================================================
    @staticmethod
    def __set_max_ids(max_ids : dict):
        Block._max_id = max_ids.get("block", 0)
        Course._max_id = max_ids.get("course", 0)
        Lab._max_id = max_ids.get("lab", 0)
        Section._max_id = max_ids.get("section", 0)
        Teacher._max_id = max_ids.get("teacher", 0)
        TimeSlot._max_id = max_ids.get("timeslot", 0)
        Stream._max_id = max_ids.get("stream", 0)
    
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
            b._block_id = block.get('id', b.id)
            b.conflicted = block.get('conflicted', b.conflicted)
            # don't set day_number, its calculated based on day
            # don't set start_number, its calculated based on start
            for k in block.get('labs', {}).keys(): b.assign_lab(Schedule.__create_lab(block.get('labs', {})[k]))
            b.movable = block.get('movable', b.movable)
            if block.get('section'): b.section = Schedule.__create_section(block.get('section'))
            for k in block.get('teachers', {}).keys(): b.assign_teacher(Schedule.__create_teacher(block.get('teachers', {})[k]))
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
            s._Section__id = section.get('id', s.id)
            s._allocation = section.get('allocation', s._allocation)
            s.num_students = section.get('num_students', s.num_students)
            for k in section.get('streams', {}).keys(): s.assign_stream(Schedule.__create_stream(section.get('streams', {})[k]))
            for k in section.get('teachers', {}).keys(): s.assign_teacher(Schedule.__create_teacher(section.get('teachers', {})[k]))
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
    def __create_teacher(teacher : dict) -> Teacher:
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
        # uncomment those lines if Course is implemented w/ a list in metaclass
        #courses = list(filter(lambda i : i.id == course.get('id', -1), Course))
        #if len(courses) == 0:

        # uncomment these lines if Course is implemented w/ a dict in metaclass (& delete bottom else)
        #if Course.get(course.get('id', -1)): return Course.get(course.get('id', -1))
        #else:
        if True:
            c = Course(number = course.get('number', ''), name = course.get('name', ''), semester = course.get('semester', ''))
            # uncomment following 3 lines when Course is implemented
            #c._allocation = course.get('allocation', c.allocation)
            #old_id = c.id
            #c._Course__id = course.get('id', c.id)
            #del Course._instances[old_id]
            #Course._instances[c.id] = c
            #for k in course.get('sections', {}).keys(): c.assign_section(Schedule.__create_section(course.get('sections', {})[k]))
            return c
        else: return courses[0]

    @staticmethod
    def __create_stream(stream : dict) -> Stream:
        if Stream.get(stream.get('id', -1)): return Stream.get(stream.get('id', -1))
        else:
            s = Stream(stream.get('number', 'A'), stream.get('descr', ''))
            old_id = s.id
            s._Stream__id = stream.get('id', s.id)
            del Stream._instances[old_id]
            Stream._instances[s.id] = s
            return s

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
    def streams() -> list[Stream]:
        """Returns the list of Streams"""
        return Stream.list()

    # --------------------------------------------------------
    # courses
    # --------------------------------------------------------
    @staticmethod
    def courses() -> list[Course]:
        """Returns the list of Courses"""
        return list() # uncomment following line & delete this when Course is done
        #return Course.list()

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
        outp = []
        for s in Section:
            if teacher in s.teachers: outp.add(s)
        return outp

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
        outp = []
        for c in Course:
            if c.has_teacher(teacher): outp.add(c)
        return outp

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
        outp = []
        for b in Block:
            if b.has_teacher(teacher): outp.add(b)
        return outp

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
        outp = []
        for b in Block:
            if b.has_lab(lab): outp.add(b)
        return outp

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
        outp = []
        for s in Section:
            if s.has_stream(stream): outp.add(s)
        return outp

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
        outp = []
        for s in Schedule.sections_for_stream(stream): outp.extend(s)
        return outp

    # NOTE: all_x() methods have been removed, since they're now equivalent to x() methods

    # --------------------------------------------------------
    # remove_course
    # --------------------------------------------------------
    @staticmethod
    def remove_course(course : Course):
        """Removes Course from schedule"""
        if not isinstance(course, Course): raise TypeError(f"{course} must be an object of type Course")
        # uncomment when Course is implemented
        #course.delete()

    # --------------------------------------------------------
    # remove_teacher
    # --------------------------------------------------------
    @staticmethod
    def remove_teacher(teacher : Teacher):
        """Removes Teacher from schedule"""
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        # potentially loop over Blocks and remove Teacher from all
        Teacher.remove(teacher)

    # --------------------------------------------------------
    # remove_lab
    # --------------------------------------------------------
    @staticmethod
    def remove_lab(lab : Lab):
        """Removes Lab from schedule"""
        if not isinstance(lab, Lab): raise TypeError(f"{lab} must be an object of type Lab")
        # potentially loop over Blocks and remove Lab from all
        Lab.remove(lab)

    # --------------------------------------------------------
    # calculate_conflicts
    # --------------------------------------------------------
    @staticmethod
    def calculate_conflicts() -> list[Conflict]:
        """Reviews the schedule, and creates a list of Conflict objects as necessary"""
        # create list of all blocks -> no longer needed
        # reset the conflict list
        Conflict.reset()
        # reset all blocks conflicted tags
        for b in Block: b.reset_conflicted()

        # ---------------------------------------------------------
        # check all block pairs to see if there is a time overlap
        for index, b in enumerate(Block.list()):
            for bb in Block[index + 1:]:
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
                    if is_conflict: Schedule.__new_conflict(Conflict.TIME, blocks)

        # ---------------------------------------------------------
        # check for lunch break conflicts by teacher
        start_lunch = 11
        end_lunch = 14
        lunch_periods = (i + .5 for i in range(start_lunch, end_lunch -1))
        for t in Teacher:
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
                if not has_lunch: Schedule.__new_conflict(Conflict.LUNCH, blocks)

        # ---------------------------------------------------------
        # check for 4 day schedule or 32 hrs max
        for t in Teacher:
            if t.release: continue

            # collect blocks by day
            blocks_by_day = { }
            blocks = Schedule.blocks_for_teacher(t)
            for b in blocks:
                if not b.day_number in blocks_by_day: blocks_by_day[b.day_number] = []
                blocks_by_day[b.day_number].append(b)

            # if < 4 days, create a conflict and mark the blocks as conflicted
            if len(blocks_by_day.keys()) < 4: Schedule.__new_conflict(Conflict.MINIMUM_DAYS, blocks)
            
            availability = 0
            for day in blocks_by_day.keys():
                day_start = min(map(lambda b: b.start_number, blocks_by_day[day]))
                day_end = max(map(lambda b: b.start_number + b.duration, blocks_by_day[day]))
                if day_end <= day_start: continue
                availability += day_end - day_start - 0.5
            
            # if over limit, create conflict
            if availability > 32: Schedule.__new_conflict(Conflict.AVAILABILITY, blocks)
        
        # Perl ver. returns self here

    # --------------------------------------------------------
    # __new_conflict - new to Python ver
    # --------------------------------------------------------
    @staticmethod
    def __new_conflict(type, blocks):
        Conflict(type, blocks)
        for b in blocks: b.conflicted = type

    # --------------------------------------------------------
    # _calculate_conflicts
    # --------------------------------------------------------
    # NOTE: Perl ver. was defined | sub _conflictLunch($$) | - confirm what $$ means
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
                case 'monday': week['Monday'] = True
                case 'tuesday': week['Tuesday'] = True
                case 'wednesday': week['Wednesday'] = True
                case 'thursday': week['Thursday'] = True
                case 'friday': week['Friday'] = True
                case 'saturday': week['Saturday'] = True
                case 'sunday': week['Sunday'] = True
        
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
            message += f"-> {c.print_description2} ({num_sections} Section(s))\n"
        
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
        if not isinstance(teacher, Teacher): raise TypeError(f"{teacher} must be an object of type Teacher")
        head = "="*50
        text = f"\n\n{head}\n{teacher}\n{head}\n"
        # NOTE: INCOMPLETE


# NOTE: As Course isn't yet implemented, the output YAML will be different from the input
# Course objects default to { name = "C" } as a placeholder, so many teachers, labs, and streams
# won't appear in normal output and will only appear in the respective list sections
# this shouldn't affect functionality (outside of Course not being saved)

# NOTE: The sample FallSchedule.yaml given by Aref has an error in it;
# Teacher max_id is written as 16, despite there being teachers with IDs up to 29
# this causes bugs with teachers being overwritten by each other and should be manually fixed in the YAML file
# if more teachers are added in the Perl version, the old ones with higher IDs would be overwritten