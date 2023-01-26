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
                # replace '!!perl/hash:' with '!' to change tags - not sure why but PyYAML has trouble recognizing 
                # !! tags | ensures support of YAML files set up before Perl > Python conversion
                # regex substitution replaces - at the beginning of variable names, since they're not allowed in Python
                    # (makes casting easier)
                raw_yaml = re.sub("^(\s*)-([^- ])", r"\1\2", f.read().replace(r"!!perl/hash:", "!"), flags=re.MULTILINE)
                (
                    yaml_contents, Block._max_id, Course._max_id, Lab._max_id,
                    Section._max_id, Teacher._max_id, TimeSlot._max_id, Stream._max_id
                ) = yaml.load_all(raw_yaml, Loader=get_loader())

                for i in Conflict: print(i)
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
    def write_YAML():
        pass

def get_loader():
    """ Add constructors to PyYAML loader. """
    loader = yaml.SafeLoader
    loader.add_constructor("!Schedule", lambda l, n : Schedule(**l.construct_mapping(n)))

    # support for YAML files made before Perl > Python conversion
    loader.add_constructor("!Conflicts", generic_collection_constructor)
    loader.add_constructor("!Courses", generic_collection_constructor)
    loader.add_constructor("!Labs", generic_collection_constructor)
    loader.add_constructor("!Streams", generic_collection_constructor)
    loader.add_constructor("!Teachers", generic_collection_constructor)

    # issues with empty lists being passed persist
        # ie a Conflict is passed a list of 0 blocks despite the YAML having 4 listed
    loader.add_constructor("!Conflict", lambda l, n : Conflict(**l.construct_mapping(n)))
    loader.add_constructor("!Block", lambda l, n : Block(**l.construct_mapping(n)))
    loader.add_constructor("!Lab", lambda l, n : Lab(**l.construct_mapping(n)))
    loader.add_constructor("!Section", lambda l, n : Section(**l.construct_mapping(n)))
    loader.add_constructor("!Teacher", lambda l, n : Teacher(**l.construct_mapping(n)))
    loader.add_constructor("!Course", lambda l, n : Course(**l.construct_mapping(n)))
    loader.add_constructor("!Stream", lambda l, n : Stream(**l.construct_mapping(n)))
    return loader

def generic_collection_constructor(l : yaml.SafeLoader, n : yaml.nodes.MappingNode):
    obj = {}
    args = l.construct_mapping(n)
    for a in args.keys():
        obj[a] = args[a]
    return a

Schedule.read_YAML(r"C:\Users\profw\Desktop\Scheduler\FallSchedule.yaml")