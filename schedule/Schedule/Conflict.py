#!/user/bin/python

# FindBin -> find bin location where script is being run. unclear what it's used for; seemingly unnecessary
# Colour -> custom package for handling colours - needs to be converted. below line is needed import statement
from ..PerlLib.Colour import *

class ConflictMeta(type):
    """
    Metaclass for Conflict, making it iterable
    """
    _conflicts = []
    
    def __iter__(self):
        return iter(getattr(self, '_conflicts', []))

class Conflict(metaclass=ConflictMeta):
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
        Conflict._conflicts.append(self)

    # ========================================================
    # PROPERTIES
    # ========================================================

    # --------------------------------------------------------
    # type
    # --------------------------------------------------------
    @property
    def type(self) -> int:
        """ Gets the conflict's type """
        return self._type

    @type.setter
    def type(self, new_type : int) -> int:
        """ Sets the conflict's type """
        self._type = new_type
        return self.type
    
    # --------------------------------------------------------
    # blocks
    # --------------------------------------------------------
    @property
    def blocks(self) -> list:
        """ Gets the conflict's blocks """
        return self._blocks
    
    @blocks.setter
    def blocks(self, new_blocks) -> list:
        """ Sets the conflict's blocks """
        self._blocks = new_blocks
        return self.blocks

    # ========================================================
    # METHODS
    # ========================================================

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Static Methods
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

    # --------------------------------------------------------
    # colours
    # --------------------------------------------------------
    @staticmethod
    def colours() -> dict[int, str]:
        """ Returns the colours used by each conflict type """
        return Conflict._colours
    
    # --------------------------------------------------------
    # _hash_descriptions
    # --------------------------------------------------------
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
    # list
    # --------------------------------------------------------
    @staticmethod
    def list() -> list:
        """Returns reference to list of Conflict objects"""
        return Conflict._conflicts

    # --------------------------------------------------------
    # most_severe
    # --------------------------------------------------------
    @staticmethod
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
    # get_description
    # --------------------------------------------------------
    @staticmethod
    def get_description(self, type):
        """ Returns the description of the provided conflict type """
        return Conflict._hash_descriptions()[type]


    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Instance Methods
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    
    # --------------------------------------------------------
    # add_block
    # --------------------------------------------------------
    def add_block(self, new_block):
        """
        Adds a new affected block to the conflict.

        Parameter new_block -> the new block to be added.
        """
        self.blocks.append(new_block)
    
    # --------------------------------------------------------
    # delete
    # --------------------------------------------------------
    def delete(self):
        """
        Deletes the conflict from the conflict list
        """
        Conflict._conflicts.remove(self)
        return self