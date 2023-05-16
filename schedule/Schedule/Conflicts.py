from __future__ import annotations

from .ScheduleEnums import ViewType, ConflictType
from .Schedule import Schedule
import Block

""" SYNOPSIS/EXAMPLE:
    from Schedule.Conflict import Conflict

    blocks = [block1, block2, ...]
    new_conflict = Conflict(type = ConflictType.MINIMUM_DAYS, blocks = blocks)
"""

_sorted_conflicts = [ConflictType.TIME, ConflictType.LUNCH, ConflictType.MINIMUM_DAYS, ConflictType.AVAILABILITY]
_instances: list[Conflict] = list()


def add(conflict: Conflict):
    _instances.append(conflict)

# --------------------------------------------------------
# list
# --------------------------------------------------------
@property
def all_conflicts() -> tuple[Conflict]:
    """ Gets all instances of Conflict. Returns a tuple object. """
    return tuple(_instances)


# --------------------------------------------------------
# reset
# --------------------------------------------------------
def clear_conflicts():
    """ Deletes all Conflicts """
    _instances.clear()


# --------------------------------------------------------
# _hash_descriptions
# --------------------------------------------------------
def descriptions() -> dict[ConflictType, str]:
    return ConflictType.descriptions()


# --------------------------------------------------------
# does the conflict number contain the appropriate specified type
# --------------------------------------------------------
def is_time(conflict_number: int) -> int:
    """does the conflict number include a time conflict?"""
    return conflict_number & ConflictType.TIME.value


def is_time_lab(conflict_number: int) -> int:
    """does the conflict number include a time - lab conflict?"""
    return conflict_number & ConflictType.TIME_LAB.value


def is_time_teacher(conflict_number: int):
    """does the conflict number include a time - teacher conflict?"""
    return conflict_number & ConflictType.TIME_TEACHER.value


def is_time_lunch(conflict_number: int) -> int:
    """does the conflict number include a lunch conflict?"""
    return conflict_number & ConflictType.LUNCH.value


def is_minimum_days(conflict_number: int) -> int:
    """does the conflict number include a minimum days conflict?"""
    return conflict_number & ConflictType.MINIMUM_DAYS.value


def is_availability(conflict_number: int) -> int:
    """does the conflict number include a minimum days conflict?"""
    return conflict_number & ConflictType.AVAILABILITY.value


# --------------------------------------------------------
# most_severe
# --------------------------------------------------------
def most_severe(conflict_number: int, view_type: ViewType) -> ConflictType:
    """
    Identify the most severe conflict type in a conflict
    - Parameter conflict_number -> defines the types of conflicts. int
    - Parameter view_type -> defines the user's current view. ViewType (enum)
    """
    severest = None
    sorted_conflicts = _sorted_conflicts.copy()

    # based on the view, get_by_id the string version of the enum ConflictType
    conflict_key = f"time_{view_type.name}".upper()

    # if conflict key is a valid enum for ConflictType, insert this into the sorted conflicts list
    if conflict_key in ConflictType.__members__:
        sorted_conflicts.insert(0, ConflictType[conflict_key])

    # look for the first match where the bit in conflict_number matches all the possible conflict types
    for conflict in sorted_conflicts:
        if conflict_number & conflict.value:
            severest = conflict
            break

    return severest


# --------------------------------------------------------
# get_description_of
# --------------------------------------------------------
def get_description_of(conflict_type: ConflictType) -> str:
    """ Returns the description of the provided conflict type """
    return descriptions()[conflict_type]


def calculate_conflicts(schedule: Schedule):
    """Reviews the schedule, and creates a list of Conflict objects as necessary"""

    def __new_conflict(conflict_type: ConflictType, conflict_blocks: tuple[Block.Block]):
        Conflict(conflict_type, conflict_blocks)
        for cb in blocks:
            cb.conflicted_number = conflict_type.value

    # reset all blocks conflicted_number tags
    for b in schedule.blocks:
        b.reset_conflicted()

    # ---------------------------------------------------------
    # check all block pairs to see if there is a time overlap
    for index, b in enumerate(schedule.blocks):
        for bb in schedule.blocks[index + 1:]:
            # if the same block, skip (shouldn't happen)
            if b == bb:
                continue

            # if the blocks overlap in time
            if b.conflicts_time(bb):
                is_conflict = False
                # if teachers/labs/streams share these blocks it is a real conflict
                # and must be dealt with
                if set(b.teachers).intersection(set(bb.teachers)):
                    is_conflict = True
                    b.conflicted_number = bb.conflicted_number = ConflictType.TIME_TEACHER.value
                if set(b.labs).intersection(set(bb.labs)) :
                    is_conflict = True
                    b.conflicted_number = bb.conflicted_number = ConflictType.TIME_LAB.value
                if set(b.streams).intersection(set(bb.teachers)):
                    is_conflict = True
                    b.conflicted_number = bb.conflicted_number = ConflictType.TIME_STREAM.value

                # create a conflict object and mark the blocks as conflicting
                if is_conflict:
                    __new_conflict(ConflictType.TIME, (b, bb))

    # ---------------------------------------------------------
    # check for lunch break conflicts by teacher
    start_lunch = 11
    end_lunch = 14

    lunch_periods = list(i / 2 for i in range(start_lunch * 2, end_lunch * 2))
    for t in schedule.assigned_teachers:
        # filter to only relevant blocks (that can possibly conflict)
        relevant_blocks = list(
            filter(lambda b1: b1.start_number < end_lunch and b1.start_number + b1.duration > start_lunch,
                   schedule.blocks_for_teacher(t)))
        # collect blocks by day
        blocks_by_day: dict[int, list[Block.Block]] = {}

        for b in relevant_blocks:
            if b.day_number not in blocks_by_day:
                blocks_by_day[b.day_number] = []
            blocks_by_day[b.day_number].append(b)

        for blocks in blocks_by_day.values():
            # don't know how this could occur, but just being careful
            if not blocks:
                continue

            # check for the existence of a lunch break in any of the :30 periods
            has_lunch = False
            for start in lunch_periods:
                # is this period free?
                has_lunch = all(not _conflict_lunch(b, start) for b in blocks)
                if has_lunch:
                    break

            # if no lunch, create a conflict obj and mark blocks as conflicted_number
            if not has_lunch:
                __new_conflict(ConflictType.LUNCH, tuple(blocks))

    # ---------------------------------------------------------
    # check for 4 day schedule or 32 hrs max
    for t in schedule.assigned_teachers:
        if t.release:
            continue

        # collect blocks by day

        blocks_by_day: dict[int, list[Block.Block]] = {}
        blocks = schedule.blocks_for_teacher(t)

        for b in blocks:
            if b.day_number not in blocks_by_day:
                blocks_by_day[b.day_number] = []
            blocks_by_day[b.day_number].append(b)

        # if < 4 days, create a conflict and mark the blocks as conflicted_number
        if len(blocks_by_day.keys()) < 4 and blocks:
            __new_conflict(ConflictType.MINIMUM_DAYS, blocks)

        # if they have more than 32 hours worth of classes
        availability = 0
        for blocks_in_day in blocks_by_day.values():
            day_start = min(map(lambda b1: b1.start_number, blocks_in_day))
            day_end = max(map(lambda b1: b1.start_number + b.duration, blocks_in_day))
            if day_end <= day_start:
                continue
            availability += day_end - day_start - 0.5

        # if over limit, create conflict
        if availability > 32:
            __new_conflict(ConflictType.AVAILABILITY, blocks)


# --------------------------------------------------------
# _conflict_lunch
# --------------------------------------------------------
def _conflict_lunch(block: Block.Block, lunch_start):
    lunch_end = lunch_start + .5
    block_end_number = block.start_number + block.duration
    return (
            (block.start_number < lunch_end and lunch_start < block_end_number) or
            (lunch_start < block_end_number and block.start_number < lunch_end)
    )


# --------------------------------------------------------
# colours
# --------------------------------------------------------
def colours() -> dict[ConflictType, str]:
    """ Returns the colours used by each conflict type """
    return ConflictType.colours()


class Conflict:
    """
    Represents a scheduling conflict.
    - Constant Attributes -> TIME, LUNCH, MINIMUM_DAYS, AVAILABILITY, TIME_TEACHER, TIME_LAB, TIME_STREAM
    
    Constant Attributes represent the possible types of conflicts

    ------

    Instances of this class are automatically saved to a list, which can be iterated over by
      iterating over the class itself.
    - To remove references to a Conflict object, call the .delete() method on the object
    """

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, conflict_type: ConflictType, blocks: tuple[Block.Block]):
        """
        Creates an instance of the Conflict class.
        - Parameter type -> defines the type of conflict.
        - Parameter blocks -> defines the list of blocks involved in the conflict.
        """
        if isinstance(blocks, tuple) or isinstance(blocks, set):
            blocks = list(blocks)

        self.type = conflict_type
        self.blocks = blocks.copy()  # if list is changed, the Conflict won't be
        _instances.append(self)

    # --------------------------------------------------------
    # calculate_conflicts
    # --------------------------------------------------------

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Instance Methods
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

    # --------------------------------------------------------
    # add_block
    # --------------------------------------------------------
    def add_block(self, new_block: Block.Block):
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
        _instances.remove(self)
