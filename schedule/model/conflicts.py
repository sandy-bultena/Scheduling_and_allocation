"""
Provides classes for managing scheduling conflicts
"""
from __future__ import annotations
import itertools
from enum import Flag
from typing import TYPE_CHECKING
from .enums import ResourceType
from .time_slot import ClockTime

if TYPE_CHECKING:
    from .block import Block


# =============================================================================
# ConflictType Enum
# =============================================================================
class ConflictType(Flag):
    """All types of Conflict types... note it is not an ENUM, but a FLAG
    which allows `or` and `len`, and `__contains__` built in"""
    NONE = 0
    TIME = 1
    LUNCH = 2
    MINIMUM_DAYS = 4
    AVAILABILITY = 8
    TIME_TEACHER = 16
    TIME_LAB = 32
    TIME_STREAM = 64

    @classmethod
    def colours(cls):
        """return a dictionary of colours to go with each conflict type"""
        return {
            cls.TIME: "indianred3",
            cls.LUNCH: "tan4",
            cls.MINIMUM_DAYS: "lightgoldenrod1",
            cls.AVAILABILITY: "mediumvioletred",
            cls.TIME_TEACHER: "red2",
            cls.TIME_LAB: "red2",
            cls.TIME_STREAM: "red2",
        }

    @classmethod
    def descriptions(cls) -> dict[ConflictType, str]:
        """returns a dictionary of descriptions to go with each conflict type"""
        return {
            cls.NONE: "no conflict",
            cls.TIME: "indirect time overlap",
            cls.LUNCH: "no lunch time",
            cls.MINIMUM_DAYS: "too few days",
            cls.TIME_TEACHER: "time overlap",
            cls.TIME_LAB: "time overlap",
            cls.TIME_STREAM: "time overlap",
            cls.AVAILABILITY: "not available",
        }

    def description(self) -> str:
        """ Returns the title of the provided conflict resource_type """
        return ConflictType.descriptions()[self]

    def is_conflicted(self) -> bool:
        """any conflicts?"""
        return len(self) != 0

    def is_time(self) -> bool:
        """does the conflict number include a time conflict?"""
        return ConflictType.TIME in self

    def is_time_lab(self) -> bool:
        """does the conflict number include a time - lab conflict?"""
        return ConflictType.TIME_LAB in self

    def is_time_teacher(self) -> bool:
        """does the conflict number include a time - teacher conflict?"""
        return ConflictType.TIME_TEACHER in self

    def is_time_stream(self) -> bool:
        """does the conflict number include a time - stream conflict?"""
        return ConflictType.TIME_STREAM in self

    def is_time_lunch(self) -> bool:
        """does the conflict number include a lunch conflict?"""
        return ConflictType.LUNCH in self

    def is_minimum_days(self) -> bool:
        """does the conflict number include a minimum days conflict?"""
        return ConflictType.MINIMUM_DAYS in self

    def is_availability(self) -> bool:
        """does the conflict number include a minimum days conflict?"""
        return ConflictType.AVAILABILITY in self

    def most_severe(self, view_type: ResourceType = ResourceType.none) -> ConflictType:
        """
        Identify the most severe conflict resource_type in a list of conflicts defined by
        the conflict number
        :param view_type: -> defines the user's current view. ResourceType (enum)
        """
        severest = None
        sorted_conflicts: list[ConflictType] = ORDER_OF_SEVERITY.copy()

        # based on the view, get_by_id the string version of the enum ConflictType
        if view_type is not None:
            conflict_key: str = f"time_{view_type.name}".upper()

            # if conflict key is a valid enum for ConflictType, insert this into
            # the sorted conflicts list
            if conflict_key in ConflictType.__members__:
                sorted_conflicts.insert(0, ConflictType[conflict_key])

        # look for the first match where the bit in conflict_number matches a possible
        # conflict resource_type
        for conflict in sorted_conflicts:
            if conflict in self:
                severest = conflict
                break

        return severest


# =============================================================================
# Constants
# =============================================================================
LUNCH_START: ClockTime = ClockTime("11:00")
LUNCH_END: ClockTime = ClockTime("14:00")
MAX_HOURS_PER_WEEK = 32.5
ORDER_OF_SEVERITY = [ConflictType.TIME, ConflictType.LUNCH, ConflictType.MINIMUM_DAYS,
                     ConflictType.AVAILABILITY]


# --------------------------------------------------------
# is there a lunch break
# --------------------------------------------------------
def set_lunch_break_conflicts(blocks_for_teacher: tuple[Block, ...]):
    """
    Is there a lunch break for a teacher on each day
    :param blocks_for_teacher:
    :return: A list of conflicts
    """

    # collect blocks by day
    blocks_by_day = itertools.groupby(
        sorted(blocks_for_teacher, key=lambda b: b.time_slot.day), lambda b: b.time_slot.day)

    for _, blocks_group in blocks_by_day:
        blocks: list[Block] = list(blocks_group)
        blocks.sort(key=lambda b: b.time_slot.time_start)

        # verify the 1st and last block
        b1: Block = blocks[0]
        b2: Block = blocks[-1]
        if b1.time_slot.time_start - LUNCH_START > 0.49:
            continue
        if LUNCH_END - b2.time_slot.time_end > 0.49:
            continue

        # look for a 1/2 window in-between blocks
        lunch_time = False
        for b1, b2 in itertools.pairwise(blocks):
            # break between block
            start_break = max(b1.time_slot.time_end, LUNCH_START)
            end_break = min(b2.time_slot.time_start, LUNCH_END)
            if end_break > start_break and end_break - start_break > 0.49:
                lunch_time = True
                break

        # if no lunch on this day, create a conflict obj and mark blocks as conflicted_number
        if not lunch_time:
            _mark_block_conflict(ConflictType.LUNCH, tuple(blocks))


# --------------------------------------------------------
# are blocks overlapping in time/stream/lab/teacher
# --------------------------------------------------------
def set_block_conflicts(blocks_for_week: tuple[Block, ...],
                        conflict_type: ConflictType):
    """
    calculate if any two blocks overlap each other in time, and then
    assign a TIME conflict, and the specified conflict_type to each block that overlap
    :param blocks_for_week: a list of blocks to check for time overlap
    :param conflict_type: what conflict resource_type to set_default_fonts_and_colours it to
    :return: a list of conflicts
    """
    blocks_by_day = itertools.groupby(
        sorted(blocks_for_week, key=lambda a: a.time_slot.day), lambda a: a.time_slot.day)

    for _, blocks in blocks_by_day:
        pairs: itertools.combinations[tuple[Block, Block]] = itertools.combinations(blocks, 2)
        for b1, b2 in pairs:
            if b1.time_slot.conflicts_time(b2.time_slot):
                _mark_block_conflict(ConflictType.TIME, (b1, b2))
                _mark_block_conflict(conflict_type, (b1, b2))


# --------------------------------------------------------
# not enough days per week for a teacher
# --------------------------------------------------------
def set_number_of_days_conflict(blocks_for_teacher: tuple[Block, ...]):
    """ collect blocks by day"""
    blocks_by_day = itertools.groupby(sorted(
        blocks_for_teacher, key=lambda a: a.time_slot.day), lambda a: a.time_slot.day)

    # if < 4 days, create a conflict and mark the blocks as conflicted_number
    if len(tuple(blocks_by_day)) < 4:
        _mark_block_conflict(ConflictType.MINIMUM_DAYS, blocks_for_teacher)


# --------------------------------------------------------
# too many hours for a week availability for a teacher
# --------------------------------------------------------
def set_availability_hours_conflict(blocks_for_teacher: tuple[Block, ...]):
    # collect blocks by day
    blocks_by_day = itertools.groupby(
        sorted(blocks_for_teacher, key=lambda a: a.time_slot.day), lambda a: a.time_slot.day)

    # if they have more than 32 hours worth of classes
    availability = 0
    for _, blocks_iter in blocks_by_day:
        blocks = list(blocks_iter)
        day_start = min(map(lambda b1: b1.time_slot.time_start, blocks))
        day_end = max(map(lambda b1: b1.time_slot.time_end, blocks))
        if day_end.hours <= day_start.hours:
            continue
        availability += day_end.hours - day_start.hours - 0.5

    # if over limit, create conflict
    if availability > MAX_HOURS_PER_WEEK:
        return _mark_block_conflict(ConflictType.AVAILABILITY, tuple(blocks_for_teacher))
    return None


def _mark_block_conflict(conflict_type: ConflictType, conflict_blocks: tuple[Block, ...]):
    for cb in conflict_blocks:
        cb.conflict = cb.conflict | conflict_type


# --------------------------------------------------------
# colors
# --------------------------------------------------------
def colours() -> dict[ConflictType, str]:
    """ Returns the colors used by each conflict resource_type """
    return ConflictType.colours()
