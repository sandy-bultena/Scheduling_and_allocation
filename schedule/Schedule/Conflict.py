from ..PerlLib import Colour
# kind of a hack-y way to import Colour, but forces PerlLib to be recognized as a valid import source
# if the top line stops working again, use this
"""import sys
try:
    from ..PerlLib import Colour
    print("W")
except ImportError or ModuleNotFoundError:
        sys.path.insert(0, "\\".join(sys.path[0].split("\\")[:-1]) + "\\PerlLib")
        import Colour
        print("L")
"""
class ConflictMeta(type):
    """ Metaclass for Conflict, making it iterable """
    _conflicts = []
    
    def __iter__(self):
        return iter(getattr(self, '_conflicts', []))

class Conflict(metaclass=ConflictMeta):
    """
    Represents a scheduling conflict.
    - Constant Attributes -> TIME, LUNCH, MINIMUM_DAYS, AVAILABILITY, TIME_TEACHER, TIME_LAB, TIME_STREAM
    
    Constant Attributes represent the possible types of conflicts

    ------

    Instances of this class are automatically saved to a list, which can be iterated over by iterating over the class itself.
    - To remove references to a Conflict object, call the .delete() method on the object
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

    _colours[TIME] = Colour.lighten(_colours[TIME_TEACHER], 30)

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, type : int, blocks : list):
        """
        Creates an instance of the Conflict class.
        - Parameter type -> defines the type of conflict.
        - Parameter blocks -> defines the list of blocks involved in the conflict.
        """
        if not type or not blocks: raise TypeError("Bad inputs")
        
        self.type = type
        self.blocks = blocks.copy() # if list is changed, the Conflict won't be
        Conflict._conflicts.append(self)

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
    def most_severe(conflict_number : int, view_type : str):
        """
        Identify the most severe conflict type in a conflict
        - Parameter conflict_number -> defines the types of conflicts. Integer
        - Parameter view_type -> defines the user's current view. String
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
    def get_description(type):
        """ Returns the description of the provided conflict type """
        return Conflict._hash_descriptions()[type]
    
    # --------------------------------------------------------
    # reset | new to Python version
    # --------------------------------------------------------
    @staticmethod
    def reset():
        """ Resets the list of conflicts """
        Conflict._conflicts.clear()


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
        Conflict._conflicts.remove(self)
        return self