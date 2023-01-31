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
    # read (YAML)
    # --------------------------------------------------------
    @staticmethod
    def read_YAML(file : str):
        schedule = Schedule()
        if os.path.isfile(file):
            try:
                f = open(file, "r")
                # regex substitution replaces - at the beginning of variable names, since they're not allowed in Python
                # remove any lines in a list that are just aliases; classes are now iterators, so collection classes are no longer needed
                raw_yaml = re.sub('!.*$', '', re.sub("^(\s*)-([^- ])", r"\1\2", f.read(), flags=re.MULTILINE), flags=re.MULTILINE)
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
                for i in Block: print(i)
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
    # write (YAML)
    # --------------------------------------------------------
    @staticmethod
    def write_YAML():
        pass

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
            l._Lab__id = lab.get('id', l.id)
            return l

    @staticmethod
    def __create_teacher(teacher : dict) -> Teacher:
        if Teacher.get(teacher.get('id', -1)): return Teacher.get(teacher.get('id', -1))
        else:
            t = Teacher(teacher.get('fname', ''), teacher.get('lname', ''), teacher.get('dept', ''))
            t.release = teacher.get('release', t.release)
            t._Teacher__id = teacher.get('id', t.id)
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
            #c._Course__id = course.get('id', c.id)
            #for k in course.get('sections', {}).keys(): c.assign_section(Schedule.__create_section(course.get('sections', {})[k]))
            return c
        else: return courses[0]

    @staticmethod
    def __create_stream(stream : dict) -> Stream:
        streams = list(filter(lambda i : i.id == stream.get('id', -1), Stream) )
        if len(streams) == 0:
            s = Stream(stream.get('number', 'A'), stream.get('descr', ''))
            s._Stream__id = stream.get('id', s.id)
            return s
        else: return streams[0]

Schedule.read_YAML(r"C:\Users\profw\Desktop\Scheduler\FallSchedule.yaml")