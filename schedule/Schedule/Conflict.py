from __future__ import annotations
import sys
from os import path
from ScheduleEnums import ViewType, ConflictType
sys.path.append(path.dirname(path.dirname(__file__)))
# NOTE: using an enum will impact ViewBase.py when it is coded

# TODO:  Evaluate if we even need to keep a list of conflict objects, since the conflict numbers
#        are stored with the blocks.
#        - maybe conflict list is holdover from previous design
#        - this can be validated as the gui is implemented

""" SYNOPSIS/EXAMPLE:
    from Schedule.Conflict import Conflict

    blocks = [block1, block2, ...]
    new_conflict = Conflict(type = Conflict.MINIMUM_DAYS, blocks = blocks)
"""

class Conflict:
    """
    Represents a scheduling conflict.
    - Constant Attributes -> TIME, LUNCH, MINIMUM_DAYS, AVAILABILITY, TIME_TEACHER, TIME_LAB, TIME_STREAM
    
    Constant Attributes represent the possible types of conflicts

    ------

    Instances of this class are automatically saved to a list, which can be iterated over by iterating over the class itself.
    - To remove references to a Conflict object, call the .delete() method on the object
    """


    _sorted_conflicts = [ConflictType.TIME, ConflictType.LUNCH, ConflictType.MINIMUM_DAYS, ConflictType.AVAILABILITY]
    __instances = list()

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, type: ConflictType, blocks: list):
        """
        Creates an instance of the Conflict class.
        - Parameter type -> defines the type of conflict.
        - Parameter blocks -> defines the list of blocks involved in the conflict.
        """
        if type is None or not blocks: raise TypeError("Bad inputs")

        self.type = type
        self.blocks = blocks.copy()  # if list is changed, the Conflict won't be
        Conflict.__instances.append(self)

    # ========================================================
    # ITERATING RELATED (STATIC)
    # ========================================================
    # --------------------------------------------------------
    # list
    # --------------------------------------------------------
    @staticmethod
    def list() -> tuple[Conflict]:
        """ Gets all instances of Conflict. Returns a tuple object. """
        return tuple(Conflict.__instances)

    # --------------------------------------------------------
    # reset
    # --------------------------------------------------------
    @staticmethod
    def reset():
        """ Deletes all Conflicts """
        for c in Conflict.list(): c.delete()

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
    def colours() -> dict[ConflictType, str]:
        """ Returns the colours used by each conflict type """
        return ConflictType.colours()

    # --------------------------------------------------------
    # _hash_descriptions
    # --------------------------------------------------------
    @staticmethod
    def _hash_descriptions() -> dict[ConflictType,str]:
        return ConflictType.descriptions()

    # --------------------------------------------------------
    # does the confict number contain the appropriate the specified type
    # --------------------------------------------------------
    @staticmethod
    def is_time(conflict_number:int):
        """does the conflict number include a time conflict?"""
        return conflict_number & ConflictType.TIME.value


    @staticmethod
    def is_time_lab(conflict_number: int):
        """does the conflict number include a time - lab conflict?"""
        return conflict_number & ConflictType.TIME_LAB.value

    @staticmethod
    def is_time_teacher(conflict_number: int):
        """does the conflict number include a time - teacher conflict?"""
        return conflict_number & ConflictType.TIME_TEACHER.value


    @staticmethod
    def is_time_lunch(conflict_number: int):
        """does the conflict number include a lunch conflict?"""
        return conflict_number & ConflictType.LUNCH.value

    @staticmethod
    def is_minimum_days(conflict_number: int):
        """does the conflict number include a minimum days conflict?"""
        return conflict_number & ConflictType.MINIMUM_DAYS.value

    @staticmethod
    def is_availability(conflict_number: int):
        """does the conflict number include a minimum days conflict?"""
        return conflict_number & ConflictType.AVAILABILITY.value


    # --------------------------------------------------------
    # most_severe
    # --------------------------------------------------------
    @staticmethod
    def most_severe(conflict_number: int, view_type: ViewType) -> ConflictType:
        """
        Identify the most severe conflict type in a conflict
        - Parameter conflict_number -> defines the types of conflicts. integer
        - Parameter view_type -> defines the user's current view. ViewType (enum)
        """
        severest = None
        sorted_conflicts = Conflict._sorted_conflicts.copy()
        match view_type:
            case ViewType.lab:
                sorted_conflicts.insert(0, ConflictType.TIME_LAB)
            case ViewType.stream:
                sorted_conflicts.insert(0, ConflictType.TIME_STREAM)
            case ViewType.teacher:
                sorted_conflicts.insert(0, ConflictType.TIME_TEACHER)

        for conflict in sorted_conflicts:
            if conflict_number & conflict.value:
                severest = conflict
                break

        return severest

    # --------------------------------------------------------
    # get_description
    # --------------------------------------------------------
    @staticmethod
    def get_description(type):
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
        - Parameter new_block -> the new block to be added.
        """
        self.blocks.append(new_block)

    # --------------------------------------------------------
    # delete
    # --------------------------------------------------------
    def delete(self):
        """ Deletes the conflict from the conflict list """
        Conflict.__instances.remove(self)
