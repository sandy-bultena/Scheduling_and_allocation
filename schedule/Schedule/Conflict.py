#!/user/bin/python

# FindBin -> find bin location where script is being run. unclear what it's used for; seemingly unnecessary
# Colour -> custom package for handling colours - needs to be converted. below line is needed import statement
#from ..PerlLib.Colour import *

class Conflict:
    """
    Represents a scheduling conflict.

    Constant Attributes -> TIME, LUNCH, MINIMUM_DAYS, AVAILABILITY, TIME_TEACHER, TIME_LAB, TIME_STREAM
    Constant Attributes represent the possible types of conflicts    
    """

    TIME = 1
    LUNCH = 2
    MINIMUM_DAYS = 4
    AVAILABILITY = 8
    TIME_TEACHER = 16
    TIME_LAB = 32
    TIME_STREAM = 64

    _sorted_conflicts = [TIME, LUNCH, MINIMUM_DAYS, AVAILABILITY]
    _colours = {
        TIME_TEACHER : "red2",
        TIME_LAB : "red2",
        TIME_STREAM  : "red2",
        LUNCH        : "tan4",
        MINIMUM_DAYS : "lightgoldenrod1",
        AVAILABILITY : "mediumvioletred"
    }

    _colours[TIME] = _colours[TIME_TEACHER]
    # replace with below code when PerlLib/Colour.py has been completed
    #_colours[TIME] = Colour(_colours[TIME_TEACHER]).lighten(30)

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, type : int, blocks : list):
        """
        Creates an instance of the Conflict class.

        Parameter type -> defines the type of conflict. Integer.

        Parameter blocks -> defines the list of blocks involved in the conflict. List of Block objects.
        """
        if not type or not blocks: raise "Bad inputs"
        
        self.type = type
        self.blocks = blocks

    # ========================================================
    # PROPERTIES
    # ========================================================
    
    # --------------------------------------------------------
    # static properties (colours, hash_descriptions)
    # --------------------------------------------------------
    @property
    @staticmethod
    def colours() -> list: return Conflict._colours

    @property
    @staticmethod
    def _hash_descriptions() -> dict: return {
        Conflict.TIME : "indirect time overlap",
        Conflict.LUNCH : "no lunch time",
        Conflict.MINIMUM_DAYS : "too few days",
        Conflict.TIME_TEACHER : "time overlap",
        Conflict.TIME_LAB : "time overlap",
        Conflict.TIME_STREAM  : "time overlap",
        Conflict.AVAILABILITY : "not available"
    }

    # --------------------------------------------------------
    # type
    # --------------------------------------------------------
    @property
    def type(self) -> int:
        """ Gets the conflict's type """
        return self.type

    @property
    def type(self, new_type : int) -> int:
        """ Sets the conflict's type """
        self.type = new_type
        return self.type
    
    # --------------------------------------------------------
    # blocks
    # --------------------------------------------------------
    @property
    def blocks(self) -> list:
        """ Gets the conflict's blocks """
        return self.blocks
    
    @property
    def blocks(self, new_blocks) -> list:
        """ Sets the conflict's blocks """
        self.blocks = new_blocks
        return self.blocks

    # ========================================================
    # METHODS
    # ========================================================

    # --------------------------------------------------------
    # get_description
    # --------------------------------------------------------
    def get_description(self, type): return Conflict._hash_descriptions[type]
    
    # --------------------------------------------------------
    # type checking methods
    # --------------------------------------------------------
    def is_time(self, type): return type & Conflict.TIME
    def is_time_lab(self, type): return type & Conflict.TIME_LAB
    def is_time_teacher(self, type): return type & Conflict.TIME_TEACHER
    def is_time_stream(self, type): return type & Conflict.TIME_STREAM
    def is_lunch(self, type): return type & Conflict.LUNCH
    def is_minimum_days(self, type): return type & Conflict.MINIMUM_DAYS
    def is_availability(self, type): return type & Conflict.AVAILABILITY

    # --------------------------------------------------------
    # most_severe
    # --------------------------------------------------------
    def most_severe(self, conflict_number : int, view_type : str):
        """
        Identify the most severe conflict type in a conflict

        Parameter conflict_number -> defines the types of conflicts. Integer

        Parameter view_type -> defines the user's current view. String
        """
        severest = 0
        sorted_conflicts = Conflict._sorted_conflicts.copy()
        match view_type.lower():
            case "lab":
                sorted_conflicts.insert(0, Conflict.TIME_LAB)
            case "stream":
                sorted_conflicts.insert(0, Conflict.TIME_STREAM)
            case "teacher":
                sorted_conflicts.insert(0, Conflict.TIME_TEACHER)
        
        for conflict in sorted_conflicts:
            if conflict_number & conflict:
                severest = conflict
                break
        
        return severest
    
    # --------------------------------------------------------
    # add_block
    # --------------------------------------------------------
    def add_block(self, new_block):
        """
        Adds a new affected block to the conflict.

        Parameter new_block -> the new block to be added.
        """
        self.blocks.append(new_block)