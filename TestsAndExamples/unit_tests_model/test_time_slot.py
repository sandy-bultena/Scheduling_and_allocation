import pytest
from schedule.Model import ScheduleTime, ClockTime
from schedule.Model import TimeSlot
from schedule.Model import WeekDay
from schedule.Model import time_slot as ts


def test_defaults():
    slot = TimeSlot()
    assert slot.day == ts.DEFAULT_DAY
    assert slot.time_start == ts.DEFAULT_START
    assert slot.duration == ts.DEFAULT_DURATION
    assert slot.movable


def test_calculate_end_time():
    slot = TimeSlot(WeekDay.Tuesday, start=ClockTime("13:15"), duration=1.5)
    assert slot.day == WeekDay.Tuesday
    assert slot.time_start == ClockTime("13:15")
    assert slot.duration == 1.5
    assert slot.time_end == ClockTime("14:45")


def test_equality():
    slot1 = TimeSlot(WeekDay.Tuesday, start=ClockTime("13:15"), duration=1.5)
    slot2 = TimeSlot(WeekDay.Tuesday, start=ClockTime("13:15"), duration=1.5)
    assert slot1 == slot2


def test_hashable():
    slot1 = TimeSlot(WeekDay.Tuesday, start=ClockTime("13:15"), duration=1.5)
    slot2 = TimeSlot(WeekDay.Tuesday, start=ClockTime("13:15"), duration=1.5)
    s = {slot1, slot2}
    assert len(s) == 1


def test_sortable():
    slot1 = TimeSlot(WeekDay.Tuesday, start=ClockTime("13:15"), duration=1.5)
    slot2 = TimeSlot(WeekDay.Monday, start=ClockTime("13:15"), duration=1.5)
    s = [slot1, slot2]
    s.sort()
    assert s[0] == slot2
    assert s[1] == slot1


def test_duration_not_allowed_less_than_zero():
    slot = TimeSlot(WeekDay.Tuesday, start=ClockTime("13:15"), duration=-3)
    assert abs(slot.duration - ts.MINUTE_BLOCK_SIZE / 60) < 0.001


def test_duration_not_allowed_greater_than_eight():
    slot = TimeSlot(WeekDay.Tuesday, start=ClockTime("13:30"), duration=ts.MAXIMUM_DURATION + .5)
    assert slot.duration == ts.MAXIMUM_DURATION


def test_duration_rounded_up_to_minimum_half_hour():
    slot = TimeSlot(WeekDay.Tuesday, ClockTime("13:30"), duration=0.1)
    assert slot.duration == ts.MINIMUM_DURATION


def test_duration_setter_changes_end():
    slot = TimeSlot(WeekDay.Tuesday, ClockTime("13:30"), duration=1)
    assert slot.time_end == ClockTime("14:30")
    slot.duration = 3
    assert slot.time_end == ClockTime("16:30")


def test_no_snapping_required():
    slot = TimeSlot(start=ClockTime("13:00"))
    assert not slot.snap_to_time()


def test_snap_to_time():
    slot = TimeSlot(start=ClockTime("13:15"))
    assert slot.snap_to_time()
    expected_start = ClockTime("13:00")
    assert slot.time_start.hours == expected_start.hours


def test_snap_to_time_adjust_duration():
    slot = TimeSlot(duration=1.2, start=ClockTime("13:00"))
    assert slot.snap_to_time()
    assert slot.duration == 1


def test_snap_to_time_bad_value_to_minimum():
    slot = TimeSlot(start=ClockTime("5:00"))
    slot.snap_to_time()
    expected_start = "8:00"
    print()
    print(slot)
    assert slot.time_start == ClockTime(expected_start)


def test_snap_to_time_bad_value_to_maximum():
    slot = TimeSlot(start=ClockTime("19:00"))
    slot.snap_to_time()
    assert slot.time_start.hours + slot.duration <= ts.MAX_END_TIME


def test_snap_to_day_with_args():
    """Verifies that TimeSlot's snap_to_day method adjusts its day property to the correct value
    when it is outside a specified date range. """
    slot = TimeSlot()
    slot.day = WeekDay.Friday
    assert slot.snap_to_day(slot.day.value, WeekDay.Tuesday, WeekDay.Wednesday)
    assert slot.day == WeekDay.Wednesday


def test_snap_to_day_with_fractional_day():
    slot = TimeSlot()
    slot.day = WeekDay.Friday
    assert slot.snap_to_day(2.3)
    assert slot.day == WeekDay.Tuesday


def test_snap_to_day_returns_false_no_change():
    slot = TimeSlot()
    slot.day = WeekDay.Tuesday
    assert not slot.snap_to_day(2)
    assert slot.day == WeekDay.Tuesday


def test_conflicts_time1():
    """Verifies that conflicts_time works as intended."""
    slot1 = TimeSlot(WeekDay.Monday, ClockTime("8:00"), 1.5)
    slot2 = TimeSlot(WeekDay.Monday, ClockTime("9:00"), 1)
    assert slot1.conflicts_time(slot2)


def test_conflicts_time2():
    """Verifies that conflicts_time works as intended."""
    slot1 = TimeSlot(WeekDay.Monday, ClockTime("8:00"), 1)
    slot2 = TimeSlot(WeekDay.Monday, ClockTime("9:00"), 1)
    assert not slot1.conflicts_time(slot2)


def test_conflicts_time3():
    """Verifies that conflicts_time works as intended."""
    slot1 = TimeSlot(WeekDay.Monday, ClockTime("9:30"), 1)
    slot2 = TimeSlot(WeekDay.Monday, ClockTime("9:00"), 1)
    assert slot1.conflicts_time(slot2)


def test_conflicts_time4():
    """Verifies that conflicts_time works as intended."""
    slot1 = TimeSlot(WeekDay.Monday, ClockTime("9:30"), 1)
    slot2 = TimeSlot(WeekDay.Monday, ClockTime("10:30"), 1)
    assert not slot1.conflicts_time(slot2)


def test_conflicts_time_different_days():
    """Verifies that conflicts_time registers no conflict when two TimeSlots are on different
    days. """
    slot1 = TimeSlot(WeekDay.Tuesday, ClockTime("9:30"), 1)
    slot2 = TimeSlot(WeekDay.Monday, ClockTime("9:00"), 1)
    assert slot1.conflicts_time(slot2) is False
