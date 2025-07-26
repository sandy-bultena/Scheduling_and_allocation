import pytest
from schedule.model import enums as enums
from schedule.model import conflicts as con
from schedule.model import Block, TimeSlot, WeekDay, ClockTime
from schedule.model import ResourceType, ConflictType


class ParentContainer:
    @property
    def id(self) -> int:
        return 1

    @property
    def title(self) -> str:
        return "whatever"


parent = ParentContainer

ALL_BITS_SET = ~ConflictType(0)


# ============================================================================
# verify that the is_??_conflict(int) works as expected
# ============================================================================
def test_is_time():
    cc = ConflictType.TIME
    assert cc.is_time()
    cc = ConflictType.TIME | ConflictType.TIME_LAB | ConflictType.NONE | ConflictType.LUNCH
    assert cc.is_conflicted()
    assert cc.is_time()
    cc = cc ^ ConflictType.TIME
    assert not cc.is_time()


def test_is_time_lab():
    cc = ConflictType.TIME_LAB
    assert cc.is_time_lab()
    cc = ConflictType.TIME_LAB | ConflictType.TIME | ConflictType.NONE | ConflictType.LUNCH
    assert cc.is_time_lab()
    cc = cc ^ ConflictType.TIME_LAB
    assert not cc.is_time_lab()


def test_is_time_stream():
    cc = ConflictType.TIME_STREAM
    assert cc.is_time_stream()
    cc = ConflictType.TIME_STREAM | ConflictType.TIME | ConflictType.NONE | ConflictType.LUNCH
    assert cc.is_time_stream()
    cc = cc ^ ConflictType.TIME_STREAM
    assert not cc.is_time_stream()


def test_is_time_teacher():
    cc = ConflictType.TIME_TEACHER
    assert cc.is_time_teacher()
    cc = ConflictType.TIME_TEACHER | ConflictType.TIME | ConflictType.NONE | ConflictType.LUNCH
    assert cc.is_time_teacher()
    cc = cc ^ ConflictType.TIME_TEACHER
    assert not cc.is_time_teacher()


def test_is_time_lunch():
    cc = ConflictType.LUNCH
    assert cc.is_time_lunch()
    cc = ConflictType.TIME | ConflictType.TIME | ConflictType.NONE | ConflictType.LUNCH
    assert cc.is_time_lunch()
    cc = cc ^ ConflictType.LUNCH
    assert not cc.is_time_lunch()


def test_is_minimum_days():
    cc = ConflictType.MINIMUM_DAYS
    assert cc.is_minimum_days()
    cc = ConflictType.TIME | ConflictType.TIME | ConflictType.NONE | ConflictType.MINIMUM_DAYS
    assert cc.is_minimum_days()
    cc = cc ^ ConflictType.MINIMUM_DAYS
    assert not cc.is_minimum_days()


def test_is_availability():
    cc = ConflictType.AVAILABILITY
    assert cc.is_availability()
    cc = ConflictType.TIME | ConflictType.TIME | ConflictType.NONE | ConflictType.AVAILABILITY
    assert cc.is_availability()
    cc = cc ^ ConflictType.AVAILABILITY
    assert not cc.is_availability()


# ============================================================================
# most severe
# ============================================================================
severity_order = enums.ORDER_OF_SEVERITY

def test_severity_dependent_on_view():
    """if view can have a conflict specific to its view, then it should be the most severe"""
    cc = ALL_BITS_SET

    most_severe: ConflictType = cc.most_severe(ResourceType.lab)
    assert most_severe == ConflictType.TIME_LAB

    most_severe: ConflictType = cc.most_severe(ResourceType.stream)
    assert most_severe == ConflictType.TIME_STREAM

    most_severe: ConflictType = cc.most_severe(ResourceType.teacher)
    assert most_severe == ConflictType.TIME_TEACHER

    cc = ConflictType.NONE
    most_severe: ConflictType = cc.most_severe( ResourceType.teacher)
    assert most_severe == ConflictType.NONE

    most_severe: ConflictType = cc.most_severe( ResourceType.lab)
    assert most_severe == ConflictType.NONE

    most_severe: ConflictType = cc.most_severe( ResourceType.stream)
    assert most_severe == ConflictType.NONE

    cc = ALL_BITS_SET
    most_severe: ConflictType = cc.most_severe( ResourceType.none)
    assert most_severe != ConflictType.TIME_TEACHER and \
           most_severe != ConflictType.TIME_STREAM and \
           most_severe != ConflictType.TIME_LAB


def test_severity_view_independent():
    """Verity that returned conflict resource_type is the most severe"""

    cc = ConflictType.NONE
    for ct in severity_order:
        cc = ct | cc

    for ct in severity_order:
        most_severe = cc.most_severe(ResourceType.none)
        assert most_severe == ct
        cc = cc ^ ct

    cc = ConflictType.NONE
    most_severe = cc.most_severe(ResourceType.none)
    assert most_severe == ConflictType.NONE


# ============================================================================
# time conflicts
# ============================================================================
def test_block_time_conflicts_is_overlap():
    """Detects a block overlap"""
    block1 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("8:30"), 2))
    block2 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("12:00"), 2))
    block3 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("10:00"), 2))

    con.set_block_conflicts((block1, block2, block3), ConflictType.TIME_LAB)
    assert block1.conflict.is_time_lab()
    assert block3.conflict.is_time_lab()
    assert block1.conflict.is_time()
    assert block3.conflict.is_time()
    assert not block2.conflict.is_conflicted()


def test_block_time_with_overlap_on_different_day():
    """determines no overlap"""
    block1 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("8:30"), 2))
    block2 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("12:00"), 2))
    block3 = Block(parent, TimeSlot(WeekDay.Tuesday,ClockTime( "10:00"), 2))

    con.set_block_conflicts((block1, block2, block3), ConflictType.TIME_LAB)
    assert not block1.conflict.is_conflicted()
    assert not block2.conflict.is_conflicted()
    assert not block3.conflict.is_conflicted()


# ============================================================================
# lunch breaks (need 1/2 hour from 11am until 2pm)
# ============================================================================
def test_lunch_breaks_single_block():
    """Verifies that there is a lunch if a single block"""

    # single block spans entire lunch break
    block1 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("10:30"), 5))
    con.set_lunch_break_conflicts((block1,))
    assert block1.conflict.is_time_lunch()

    # single block that still gives lunch break
    block1 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("11:30"), 5))
    con.set_lunch_break_conflicts((block1,))
    assert not block1.conflict.is_conflicted()


def test_lunch_breaks_two_blocks_with_break_inbetween():
    """two blocks with whole lunch break taken, except for 1/2 in between"""
    block1 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("10:30"), 2))
    block2 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("13:00"), 5))
    block3 = Block(parent, TimeSlot(WeekDay.Tuesday, ClockTime("12:30"), 1.5))
    con.set_lunch_break_conflicts((block1, block2, block3))
    assert not block1.conflict.is_conflicted()
    assert not block2.conflict.is_conflicted()
    assert not block3.conflict.is_conflicted()


def test_lunch_three_blocks_with_no_breaks():
    """three blocks with no breaks"""
    block1 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("10:30"), 2))
    block2 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("13:00"), 5))
    block3 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("12:30"), 1.5))
    con.set_lunch_break_conflicts((block1, block2, block3))
    assert block1.conflict.is_time_lunch()
    assert block2.conflict.is_time_lunch()
    assert block3.conflict.is_time_lunch()


def test_lunch_three_blocks_with_break_at_beginning():
    """three blocks with break at beginning"""
    block1 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("11:30"), 1))
    block2 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("13:00"), 5))
    block3 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("12:30"), 1.5))
    con.set_lunch_break_conflicts((block1, block2, block3))
    assert not block1.conflict.is_conflicted()
    assert not block2.conflict.is_conflicted()
    assert not block3.conflict.is_conflicted()


def test_lunch_three_blocks_with_break_at_end():
    """three blocks with break at end"""
    block1 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("10:30"), 2))
    block2 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("13:00"), 0.5))
    block3 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("12:30"), 1.5))
    con.set_lunch_break_conflicts((block1, block2, block3))
    assert not block1.conflict.is_conflicted()
    assert not block2.conflict.is_conflicted()
    assert not block3.conflict.is_conflicted()


# ============================================================================
# number_of_days
# ============================================================================
def test_number_of_days_too_little():
    block1 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("10:30"), 2))
    block2 = Block(parent, TimeSlot(WeekDay.Tuesday, ClockTime("13:00"), 0.5))
    block3 = Block(parent, TimeSlot(WeekDay.Wednesday, ClockTime("12:30"), 1.5))
    block4 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("12:30"), 1.5))
    con.set_number_of_days_conflict((block1, block2, block3, block4))
    assert block1.conflict.is_minimum_days()
    assert block2.conflict.is_minimum_days()
    assert block3.conflict.is_minimum_days()
    assert block4.conflict.is_minimum_days()


def test_number_of_days_ok():
    block1 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("10:30"), 2))
    block2 = Block(parent, TimeSlot(WeekDay.Tuesday, ClockTime("13:00"), 0.5))
    block3 = Block(parent, TimeSlot(WeekDay.Wednesday, ClockTime("12:30"), 1.5))
    block4 = Block(parent, TimeSlot(WeekDay.Thursday, ClockTime("12:30"), 1.5))
    con.set_number_of_days_conflict((block1, block2, block3, block4))
    assert not block1.conflict.is_conflicted()
    assert not block2.conflict.is_conflicted()
    assert not block3.conflict.is_conflicted()
    assert not block4.conflict.is_conflicted()


# ============================================================================
# allocated hours
# ============================================================================
def test_too_many_hours_per_week():
    block1 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("8:30"), 2))
    block2 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("14:00"), 2))
    block3 = Block(parent, TimeSlot(WeekDay.Tuesday, ClockTime("8:30"), 1.5))
    block4 = Block(parent, TimeSlot(WeekDay.Tuesday, ClockTime("14:00"), 2))
    block5 = Block(parent, TimeSlot(WeekDay.Wednesday, ClockTime("8:30"), 1.5))
    block6 = Block(parent, TimeSlot(WeekDay.Wednesday, ClockTime("17:30"), 1.5))
    block7 = Block(parent, TimeSlot(WeekDay.Thursday, ClockTime("8:30"), 1.5))
    block8 = Block(parent, TimeSlot(WeekDay.Thursday, ClockTime("17:30"), 1.5))
    # verify that we got the right conditions before testing starting and stopping late
    total_hours = ((block2.time_slot.time_end - block1.time_slot.time_start)
                   + (block4.time_slot.time_end - block3.time_slot.time_start)
                   + (block6.time_slot.time_end - block5.time_slot.time_start)
                   + (block8.time_slot.time_end - block7.time_slot.time_start))

    assert total_hours > con.MAX_HOURS_PER_WEEK
    con.set_availability_hours_conflict((block1, block2, block3, block4, block5, block6, block7, block8))
    assert block1.conflict.is_availability()
    assert block2.conflict.is_availability()
    assert block3.conflict.is_availability()
    assert block4.conflict.is_availability()
    assert block5.conflict.is_availability()
    assert block6.conflict.is_availability()
    assert block7.conflict.is_availability()
    assert block8.conflict.is_availability()


def test_ok_many_hours_per_week():
    block1 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("8:30"), 2))
    block2 = Block(parent, TimeSlot(WeekDay.Monday, ClockTime("14:00"), 2))
    block3 = Block(parent, TimeSlot(WeekDay.Tuesday, ClockTime("8:30"), 1.5))
    block4 = Block(parent, TimeSlot(WeekDay.Tuesday, ClockTime("14:00"), 2))
    block5 = Block(parent, TimeSlot(WeekDay.Wednesday, ClockTime("8:30"), 1.5))
    block6 = Block(parent, TimeSlot(WeekDay.Wednesday, ClockTime("17:30"), 1.5))
    block7 = Block(parent, TimeSlot(WeekDay.Thursday, ClockTime("8:30"), 1.5))
    block8 = Block(parent, TimeSlot(WeekDay.Thursday, ClockTime("10:30"), 1.5))

    # verify that we got the right conditions before testing starting and stopping late
    total_hours = ((block2.time_slot.time_end - block1.time_slot.time_start)
                   + (block4.time_slot.time_end - block3.time_slot.time_start)
                   + (block6.time_slot.time_end - block5.time_slot.time_start)
                   + (block8.time_slot.time_end - block7.time_slot.time_start))

    assert total_hours < con.MAX_HOURS_PER_WEEK
    con.set_availability_hours_conflict((block1, block2, block3, block4, block5, block6, block7, block8))
    assert not block1.conflict.is_conflicted()
    assert not block2.conflict.is_conflicted()
    assert not block3.conflict.is_conflicted()
    assert not block4.conflict.is_conflicted()
    assert not block5.conflict.is_conflicted()
    assert not block6.conflict.is_conflicted()
    assert not block7.conflict.is_conflicted()
    assert not block8.conflict.is_conflicted()
