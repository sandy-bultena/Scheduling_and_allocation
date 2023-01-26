class Undo:
    """ Holds info about a block so that it can be used as an "undo" """
    __max_id = 0

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, block_id : int, origin_start : str, origin_day : str, origin_obj, move_type : str, new_obj):
        """
        Creates an instance of the Undo class.
        - Parameter block_id -> defines the ID of the Block that was moved.
        - Parameter origin_start -> defines the time of the Block before the moved.
        - Parameter origin_day -> defines the day of the Block before the moved.
        - Parameter origin_obj -> defines the object the Block was associated with before moving. (Teacher/Lab/Stream).
        - Paremeter move_type -> defines the type of movement made (within schedule, across schedules, etc).
        - Parameter new_obj -> defines the object the Block is associated with after moving (Teacher/Lab/Stream).
        """
        Undo.__max_id += 1
        self._id = Undo.__max_id
        self.block_id = block_id
        self.origin_start = origin_start
        self.origin_day = origin_day
        self.origin_obj = origin_obj
        self.move_type = move_type
        self.new_obj = new_obj
    
    # ========================================================
    # PROPERTIES
    # ========================================================
    
    # --------------------------------------------------------
    # id
    # --------------------------------------------------------
    @property
    def id(self) -> int:
        """ Gets the unique id for this Undo object. """
        return self._id
    