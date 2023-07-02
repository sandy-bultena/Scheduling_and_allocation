from __future__ import annotations

import itertools

from .ScheduleEnums import ViewType, ConflictType
from .Block import Block

""" SYNOPSIS/EXAMPLE:
    from Schedule.Conflict import Conflict

    blocks = [block1, block2, ...]
    new_conflict = Conflict(type = ConflictType.MINIMUM_DAYS, blocks = blocks)
"""

ORDER_OF_SEVERITY = [ConflictType.TIME, ConflictType.LUNCH, ConflictType.MINIMUM_DAYS, ConflictType.AVAILABILITY]

# --------------------------------------------------------
# Properties for lunch times
# --------------------------------------------------------
LUNCH_START: float = 11.0
LUNCH_END: float = 14.0
MAX_HOURS_PER_WEEK = 32.5


# --------------------------------------------------------
# _hash_descriptions
# --------------------------------------------------------
def descriptions() -> dict[ConflictType, str]:
    """returns the description of the conflict"""
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


def is_time_stream(conflict_number: int):
    """does the conflict number include a time - stream conflict?"""
    return conflict_number & ConflictType.TIME_STREAM.value


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
    Identify the most severe conflict type in a list of conflicts defined by the conflict number
    - Parameter conflict_number -> defines the types of conflicts. (each bit represents a conflict type)
    - Parameter view_type -> defines the user's current view. ViewType (enum)
    """
    severest = None
    sorted_conflicts: list[ConflictType] = ORDER_OF_SEVERITY.copy()

    # based on the view, get_by_id the string version of the enum ConflictType
    conflict_key: str = f"time_{view_type.name}".upper()

    # if conflict key is a valid enum for ConflictType, insert this into the sorted conflicts list
    if conflict_key in ConflictType.__members__:
        sorted_conflicts.insert(0, ConflictType[conflict_key])

    # look for the first match where the bit in conflict_number matches a possible conflict type
    for conflict in sorted_conflicts:
        if conflict_number & conflict.value:
            severest = conflict
            break

    return severest


# --------------------------------------------------------
# get_description_of
# --------------------------------------------------------
def get_description_of(conflict_type: ConflictType) -> str:
    """ Returns the title of the provided conflict type """
    return descriptions()[conflict_type]


# --------------------------------------------------------
# is there a lunch break
# --------------------------------------------------------
def lunch_break_conflict(blocks_for_teacher: tuple[Block, ...]) -> list[Conflict]:
    """
    Is there a lunch break for a teacher on each day
    :param blocks_for_teacher:
    :return: A list of conflicts
    """
    conflicts: list[Conflict] = list()

    # collect blocks by day
    blocks_by_day = itertools.groupby(sorted(blocks_for_teacher, key=lambda a: a.day_number), lambda a: a.day_number)
    for _, blocks_group in blocks_by_day:
        blocks: list[Block] = list(blocks_group)
        if not blocks:
            continue

        # sort blocks by order of starting time
        blocks.sort(key=lambda b: b.start_number)

        # verify the 1st and last block
        b1: Block = blocks[0]
        b2: Block = blocks[-1]
        if b1.start_number - LUNCH_START > 0.49:
            continue
        if LUNCH_END - (b2.start_number + b2.duration) > 0.49:
            continue

        # look for a 1/2 window in-between blocks
        lunch_time = False
        for b1, b2 in itertools.pairwise(blocks):
            # break between block
            start_break = max(b1.start_number + b1.duration, LUNCH_START)
            end_break = min(b2.start_number, LUNCH_END)
            if end_break > start_break and end_break - start_break > 0.49:
                lunch_time = True
                break

        # if no lunch on this day, create a conflict obj and mark blocks as conflicted_number
        if not lunch_time:
            conflicts.append(__new_conflict(ConflictType.LUNCH, tuple(blocks)))

    return conflicts


# --------------------------------------------------------
# are blocks overlapping in time/stream/lab/teacher
# --------------------------------------------------------
def block_conflict(blocks_for_week: tuple[Block, ...], conflict_type: ConflictType) -> list[Conflict]:
    """
    calculate if any two blocks overlap each other in time, and then
    assign a TIME conflict, and the specified conflict_type to each block that overlap
    :param blocks_for_week: a list of blocks to check for time overlap
    :param conflict_type: what conflict type to set_default_fonts_and_colours it to
    :return: a list of conflicts
    """
    conflicts: list[Conflict] = list()
    blocks_by_day = itertools.groupby(sorted(blocks_for_week, key=lambda a: a.day_number), lambda a: a.day_number)

    for _, blocks in blocks_by_day:
        pairs: itertools.combinations[tuple[Block, Block]] = itertools.combinations(blocks, 2)
        for b1, b2 in pairs:
            if b1.time_slot.conflicts_time(b2.time_slot):
                conflicts.append(__new_conflict(ConflictType.TIME, (b1, b2)))
                conflicts.append(__new_conflict(conflict_type, (b1, b2)))

    return conflicts


# --------------------------------------------------------
# not enough days per week for a teacher
# --------------------------------------------------------
def number_of_days_conflict(blocks_for_teacher: tuple[Block, ...]) -> Conflict | None:
    # collect blocks by day
    blocks_by_day = itertools.groupby(sorted(blocks_for_teacher, key=lambda a: a.day_number), lambda a: a.day_number)

    # if < 4 days, create a conflict and mark the blocks as conflicted_number
    if len(tuple(blocks_by_day)) < 4:
        return __new_conflict(ConflictType.MINIMUM_DAYS, blocks_for_teacher)
    return None


# --------------------------------------------------------
# too many hours for a week availability for a teacher
# --------------------------------------------------------
def availability_hours_conflict(blocks_for_teacher: tuple[Block, ...]) -> Conflict | None:
    # collect blocks by day
    blocks_by_day = itertools.groupby(sorted(blocks_for_teacher, key=lambda a: a.day_number), lambda a: a.day_number)

    # if they have more than 32 hours worth of classes
    availability = 0
    for _, blocks_iter in blocks_by_day:
        blocks = list(blocks_iter)
        day_start = min(map(lambda b1: b1.start_number, blocks))
        day_end = max(map(lambda b1: b1.start_number + b1.duration, blocks))
        if day_end <= day_start:
            continue
        availability += day_end - day_start - 0.5

    # if over limit, create conflict
    if availability > MAX_HOURS_PER_WEEK:
        return __new_conflict(ConflictType.AVAILABILITY, tuple(blocks_for_teacher))
    return None


def __new_conflict(conflict_type: ConflictType, conflict_blocks: tuple[Block, ...]) -> Conflict:
    for cb in conflict_blocks:
        cb.adjust_conflicted_number(conflict_type.value)
    return Conflict(conflict_type, conflict_blocks)


# --------------------------------------------------------
# colors
# --------------------------------------------------------
def colours() -> dict[ConflictType, str]:
    """ Returns the colors used by each conflict type """
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
    def __init__(self, conflict_type: ConflictType, blocks: tuple[Block, ...]):
        """
        Creates an instance of the Conflict class.
        - Parameter type -> defines the type of conflict.
        - Parameter blocks -> defines the list of blocks involved in the conflict.
        """
        blocks_list = list(blocks)
        self.type = conflict_type
        self.blocks = blocks_list.copy()  # if list is changed, the Conflict won't be

    # --------------------------------------------------------
    # add_block
    # --------------------------------------------------------
    def add_block(self, new_block: Block):
        """
        Adds a new affected blocks to the conflict.
        - Parameter new_block -> the new blocks to be added.
        """
        self.blocks.append(new_block)
