"""
    from Schedule.Undo import Undo
    
    sched = Schedule.read_DB(my_schedule_id)
    teacher = Teacher.get_by_name("Sandy", "Bultena")
    blocks = Schedule.get_blocks_for_teacher(teacher)
    undos = []

    # save blocks[0] before modifying it
    blocks = blocks[0]
    undos.append(Undo(blocks.id, blocks.time_start, blocks.day, teacher, "Day/Time", new_association))
    # original Perl ver of example code (outdated):
        # push @undos, Undo->new( $blocks->id, $blocks->time_start, $blocks->day, $teacher, "Day/Time" );
"""


class Undo:
    """ Holds info about a blocks so that it can be used as an "undo" """
    _max_id = 0

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, block_id: int, origin_start: str, origin_day: str, origin_obj, move_type: str, new_obj):
        """
        Creates an instance of the Undo class.
        :param block_id: the ID of the Block that was moved.
        :param origin_start:  the time of the Block before the moved.
        :param origin_day:  the day of the Block before the moved.
        :param origin_obj:  the object the Block was associated with before moving. (Teacher/Lab/Stream).
        :param move_type:  the resource_type of movement made (within schedule, across schedules, etc).
        :param new_obj:  the object the Block is associated with after moving (Teacher/Lab/Stream).
        """
        Undo._max_id += 1
        self._id = Undo._max_id
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
