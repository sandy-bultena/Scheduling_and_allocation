import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))
import pytest

import schedule.Schedule.ConflictCalculations as cc
from schedule.Schedule.Block import Block
from schedule.Schedule.TimeSlot import TimeSlot
from schedule.Schedule.ScheduleEnums import ResourceType, ConflictType


class ParentContainer:
    @property
    def id(self) -> int:
        return 1

    @property
    def title(self) -> str:
        return "whatever"


parent = ParentContainer

ALL_BITS_SET = 255


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    pass


@pytest.fixture(autouse=True)
def before_and_after():
    pass


# ============================================================================
# verify that the is_??_conflict(int) works as expected
# ============================================================================
def test_is_time():
    """verify that 'is_time' returns true or false correctly"""
    assert cc.is_time(ConflictType.TIME.value)
    assert cc.is_time(ALL_BITS_SET)
    assert not cc.is_time(0)
    assert not cc.is_time(ALL_BITS_SET ^ ConflictType.TIME.value)


def test_is_time_lab():
    """verify that 'is_time_lab' returns true or false correctly"""
    assert cc.is_time_lab(ConflictType.TIME_LAB.value)
    assert cc.is_time_lab(ALL_BITS_SET)
    assert not cc.is_time_lab(0)
    assert not cc.is_time_lab(ALL_BITS_SET ^ ConflictType.TIME_LAB.value)


def test_is_time_stream():
    """verify that 'is_time_stream' returns true or false correctly"""
    assert cc.is_time_stream(ConflictType.TIME_STREAM.value)
    assert cc.is_time_stream(ALL_BITS_SET)
    assert not cc.is_time_stream(0)
    assert not cc.is_time_stream(ALL_BITS_SET ^ ConflictType.TIME_STREAM.value)


def test_is_time_teacher():
    """verify that 'is_time_teacher' returns true or false correctly"""
    assert cc.is_time_teacher(ConflictType.TIME_TEACHER.value)
    assert cc.is_time_teacher(ALL_BITS_SET)
    assert not cc.is_time_teacher(0)
    assert not cc.is_time_teacher(ALL_BITS_SET ^ ConflictType.TIME_TEACHER.value)


def test_time_lunch():
    """verify that 'is_time_lunch' returns true or false correctly"""
    assert cc.is_time_lunch(ConflictType.LUNCH.value)
    assert cc.is_time_lunch(ALL_BITS_SET)
    assert not cc.is_time_lunch(0)
    assert not cc.is_time_lunch(ALL_BITS_SET ^ ConflictType.LUNCH.value)


def test_is_minimum_days():
    """verify that 'is_minimum_days' returns true or false correctly"""
    assert cc.is_minimum_days(ConflictType.MINIMUM_DAYS.value)
    assert cc.is_minimum_days(ALL_BITS_SET)
    assert not cc.is_minimum_days(0)
    assert not cc.is_minimum_days(ALL_BITS_SET ^ ConflictType.MINIMUM_DAYS.value)


def test_is_availability():
    """verify that 'is_availability' returns true or false correctly"""
    assert cc.is_availability(ConflictType.AVAILABILITY.value)
    assert cc.is_availability(ALL_BITS_SET)
    assert not cc.is_availability(0)
    assert not cc.is_availability(ALL_BITS_SET ^ ConflictType.AVAILABILITY.value)


# ============================================================================
# most severe
# ============================================================================
severity_order = cc.ORDER_OF_SEVERITY


def test_severity_dependent_on_view():
    """if view can have a conflict specific to its view, then it should be the most severe"""

    most_severe: ConflictType = cc.most_severe(ALL_BITS_SET, ResourceType.lab)
    assert most_severe == ConflictType.TIME_LAB

    most_severe: ConflictType = cc.most_severe(ALL_BITS_SET, ResourceType.stream)
    assert most_severe == ConflictType.TIME_STREAM

    most_severe: ConflictType = cc.most_severe(ALL_BITS_SET, ResourceType.teacher)
    assert most_severe == ConflictType.TIME_TEACHER

    most_severe: ConflictType = cc.most_severe(0, ResourceType.teacher)
    assert most_severe is None

    most_severe: ConflictType = cc.most_severe(0, ResourceType.lab)
    assert most_severe is None

    most_severe: ConflictType = cc.most_severe(0, ResourceType.stream)
    assert most_severe is None

    most_severe: ConflictType = cc.most_severe(ALL_BITS_SET, ResourceType.none)
    assert most_severe != ConflictType.TIME_TEACHER and \
           most_severe != ConflictType.TIME_STREAM and \
           most_severe != ConflictType.TIME_LAB


def test_severity_view_independent():
    """Verity that returned conflict resource_type is the most severe"""

    num = 0
    for ct in severity_order:
        num = ct.value | num

    most_severe = cc.most_severe(num, ResourceType.none)
    assert most_severe == severity_order[0]

    num = num ^ severity_order[0].value
    most_severe = cc.most_severe(num, ResourceType.none)
    assert most_severe == severity_order[1]

    num = num ^ severity_order[-1].value
    most_severe = cc.most_severe(num, ResourceType.none)
    assert most_severe == severity_order[1]

    num = 0
    most_severe = cc.most_severe(num, ResourceType.none)
    assert most_severe is None


# ============================================================================
# time blocks
# ============================================================================
def test_block_time_conflicts_is_overlap():
    """Detects a block overlap"""
    block1 = Block(parent, TimeSlot('mon', "8:30", 2))
    block2 = Block(parent, TimeSlot('mon', "12:00", 2))
    block3 = Block(parent, TimeSlot('mon', "10:00", 2))

    cc.block_conflict((block1, block2, block3), ConflictType.TIME_LAB)
    assert cc.is_time_lab(block1.conflicted_number)
    assert cc.is_time_lab(block3.conflicted_number)
    assert cc.is_time(block1.conflicted_number)
    assert cc.is_time(block3.conflicted_number)
    assert block2.conflicted_number == 0


def test_block_time_with_overlap_on_different_day():
    """determines no overlap"""
    block1 = Block(parent, TimeSlot('mon', "8:30", 2))
    block2 = Block(parent, TimeSlot('mon', "12:00", 2))
    block3 = Block(parent, TimeSlot('tue', "10:00", 2))

    cc.block_conflict((block1, block2, block3), ConflictType.TIME_LAB)
    assert block1.conflicted_number == 0
    assert block2.conflicted_number == 0
    assert block3.conflicted_number == 0


# ============================================================================
# lunch breaks (need 1/2 hour from 11am until 2pm)
# ============================================================================
def test_lunch_breaks_single_block():
    """Verifies that there is a lunch if a single block"""

    # single block spans entire lunch break
    block1 = Block(parent, TimeSlot('mon', "10:30", 5))
    cc.lunch_break_conflict((block1,))
    assert cc.is_time_lunch(block1.conflicted_number)

    # single block that still gives lunch break
    block1 = Block(parent, TimeSlot('mon', "11:30", 5))
    cc.lunch_break_conflict((block1,))
    assert block1.conflicted_number == 0


def test_lunch_breaks_two_blocks_with_break_inbetween():
    """two blocks with whole lunch break taken, except for 1/2 in between"""
    block1 = Block(parent, TimeSlot('mon', "10:30", 2))
    block2 = Block(parent, TimeSlot('mon', "13:00", 5))
    block3 = Block(parent, TimeSlot('tue', "12:30", 1.5))
    cc.lunch_break_conflict((block1, block2, block3))
    assert block1.conflicted_number == 0
    assert block2.conflicted_number == 0
    assert block3.conflicted_number == 0


def test_lunch_three_blocks_with_no_breaks():
    """three blocks with no breaks"""
    block1 = Block(parent, TimeSlot('mon', "10:30", 2))
    block2 = Block(parent, TimeSlot('mon', "13:00", 5))
    block3 = Block(parent, TimeSlot('mon', "12:30", 1.5))
    cc.lunch_break_conflict((block1, block2, block3))
    assert cc.is_time_lunch(block1.conflicted_number)
    assert cc.is_time_lunch(block2.conflicted_number)
    assert cc.is_time_lunch(block3.conflicted_number)


def test_lunch_three_blocks_with_break_at_beginning():
    """three blocks with break at beginning"""
    block1 = Block(parent, TimeSlot('mon', "11:30", 1))
    block2 = Block(parent, TimeSlot('mon', "13:00", 5))
    block3 = Block(parent, TimeSlot('mon', "12:30", 1.5))
    cc.lunch_break_conflict((block1, block2, block3))
    assert block1.conflicted_number == 0
    assert block2.conflicted_number == 0
    assert block3.conflicted_number == 0


def test_lunch_three_blocks_with_break_at_end():
    """three blocks with break at end"""
    block1 = Block(parent, TimeSlot('mon', "10:30", 2))
    block2 = Block(parent, TimeSlot('mon', "13:00", 0.5))
    block3 = Block(parent, TimeSlot('mon', "12:30", 1.5))
    cc.lunch_break_conflict((block1, block2, block3))
    assert block1.conflicted_number == 0
    assert block2.conflicted_number == 0
    assert block3.conflicted_number == 0


# ============================================================================
# number_of_days
# ============================================================================
def test_number_of_days_too_little():
    block1 = Block(parent, TimeSlot('mon', "10:30", 2))
    block2 = Block(parent, TimeSlot('tue', "13:00", 0.5))
    block3 = Block(parent, TimeSlot('wed', "12:30", 1.5))
    block4 = Block(parent, TimeSlot('mon', "12:30", 1.5))
    cc.number_of_days_conflict((block1, block2, block3, block4))
    assert cc.is_minimum_days(block1.conflicted_number)
    assert cc.is_minimum_days(block2.conflicted_number)
    assert cc.is_minimum_days(block3.conflicted_number)
    assert cc.is_minimum_days(block4.conflicted_number)


def test_number_of_days_ok():
    block1 = Block(parent, TimeSlot('mon', "10:30", 2))
    block2 = Block(parent, TimeSlot('tue', "13:00", 0.5))
    block3 = Block(parent, TimeSlot('wed', "12:30", 1.5))
    block4 = Block(parent, TimeSlot('thu', "12:30", 1.5))
    cc.number_of_days_conflict((block1, block2, block3, block4))
    assert block1.conflicted_number == 0
    assert block2.conflicted_number == 0
    assert block3.conflicted_number == 0
    assert block4.conflicted_number == 0


# ============================================================================
# allocated hours
# ============================================================================
def test_too_many_hours_per_week():
    block1 = Block(parent, TimeSlot('mon', "8:30", 2))
    block2 = Block(parent, TimeSlot('mon', "14:00", 2))
    block3 = Block(parent, TimeSlot('tue', "8:30", 1.5))
    block4 = Block(parent, TimeSlot('tue', "14:00", 2))
    block5 = Block(parent, TimeSlot('wed', "8:30", 1.5))
    block6 = Block(parent, TimeSlot('wed', "17:30", 1.5))
    block7 = Block(parent, TimeSlot('thu', "8:30", 1.5))
    block8 = Block(parent, TimeSlot('thu', "17:30", 1.5))
    total_hours = (block2.start_number + block2.duration - block1.start_number
                   + block4.start_number + block4.duration - block3.start_number
                   + block6.start_number + block6.duration - block5.start_number
                   + block8.start_number + block8.duration - block7.start_number)

    assert total_hours > cc.MAX_HOURS_PER_WEEK
    cc.availability_hours_conflict((block1, block2, block3, block4, block5, block6, block7, block8))
    assert cc.is_availability(block1.conflicted_number)
    assert cc.is_availability(block2.conflicted_number)
    assert cc.is_availability(block3.conflicted_number)
    assert cc.is_availability(block4.conflicted_number)
    assert cc.is_availability(block5.conflicted_number)
    assert cc.is_availability(block6.conflicted_number)
    assert cc.is_availability(block7.conflicted_number)
    assert cc.is_availability(block8.conflicted_number)


def test_ok_many_hours_per_week():
    block1 = Block(parent, TimeSlot('mon', "8:30", 2))
    block2 = Block(parent, TimeSlot('mon', "14:00", 2))
    block3 = Block(parent, TimeSlot('tue', "8:30", 1.5))
    block4 = Block(parent, TimeSlot('tue', "14:00", 2))
    block5 = Block(parent, TimeSlot('wed', "8:30", 1.5))
    block6 = Block(parent, TimeSlot('wed', "17:30", 1.5))
    block7 = Block(parent, TimeSlot('thu', "8:30", 1.5))
    block8 = Block(parent, TimeSlot('thu', "10:30", 1.5))
    total_hours = (block2.start_number + block2.duration - block1.start_number
                   + block4.start_number + block4.duration - block3.start_number
                   + block6.start_number + block6.duration - block5.start_number
                   + block8.start_number + block8.duration - block7.start_number)

    assert total_hours < cc.MAX_HOURS_PER_WEEK
    cc.availability_hours_conflict((block1, block2, block3, block4, block5, block6, block7, block8))
    assert block1.conflicted_number == 0
    assert block2.conflicted_number == 0
    assert block3.conflicted_number == 0
    assert block4.conflicted_number == 0
    assert block5.conflicted_number == 0
    assert block6.conflicted_number == 0
    assert block7.conflicted_number == 0
    assert block8.conflicted_number == 0
