import pytest

from schedule.Model import TimeSlot
from schedule.Model import WeekDay


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    pass


@pytest.fixture(autouse=True)
def before_and_after():
    pass


def test_defaults():
    """Verifies that default values are set_default_fonts_and_colours correctly"""
    slot = TimeSlot()
    assert slot.day == TimeSlot.DEFAULT_DAY
    assert slot.start == TimeSlot.DEFAULT_START
    assert slot.duration == TimeSlot.DEFAULT_DURATION
    assert slot.movable
    assert slot.start_number == 8
    assert slot.day_number == 1


def test_calculate_end_time():
    """Verifies that end time is set_default_fonts_and_colours correctly"""
    slot = TimeSlot(WeekDay.Tuesday, start="13:15", duration=1.5)
    assert slot.day == "tue"
    assert slot.start == "13:15"
    assert slot.duration == 1.5
    assert slot.end == "14:45"


def test_day_setter():
    """verify that day property can take a Weekday enum, or a string"""
    slot = TimeSlot()
    new_day = WeekDay.Friday
    slot.day = new_day

    real_val = 'fri'
    assert slot.day == real_val

    slot.day = 'wed'
    assert slot.day == 'wed'


def test_day_setter_warning():
    """Verifies that the day setter sets to default when an invalid value is passed."""
    slot = TimeSlot()
    bad_day = 14
    assert slot.day == TimeSlot.DEFAULT_DAY


def test_start_setter():
    slot = TimeSlot()
    new_start = "10:00"
    slot.start = new_start
    assert slot.start == new_start


def test_start_setter_warning():
    """Verifies that start setter uses default when presented with an invalid input."""
    slot = TimeSlot()
    bad_start = "foo"
    assert slot.start == TimeSlot.DEFAULT_START


def test_duration_setter():
    """Verifies that TimeSlot's duration setter works."""
    slot = TimeSlot()
    new_dur = 3
    slot.duration = new_dur
    assert slot.duration == new_dur


def test_duration_not_allowed_less_than_zero():
    """cannot have a negative length time slot"""
    slot = TimeSlot("tue", start="13:30", duration=-3)
    assert slot.duration == TimeSlot.DEFAULT_DURATION


def test_duration_not_allowed_greater_than_eight():
    """cannot have a negative length time slot"""
    slot = TimeSlot("tue", start="13:30", duration=8.5)
    assert slot.duration == 8


def test_duration_rounded_up_to_minimum_half_hour():
    """cannot have a negative length time slot"""
    slot = TimeSlot("tue", start="13:30", duration=0.1)
    assert slot.duration == 0.5


def test_duration_rounds_up_to_nearest_half_hour():
    """cannot have a negative length time slot"""
    slot = TimeSlot("tue", start="13:30", duration=1.45)
    assert slot.duration == 1.5
    slot = TimeSlot("tue", start="13:30", duration=1.55)
    assert slot.duration == 2


def test_duration_setter_changes_end():
    """Verifies that changing a TimeSlot's duration will change the value of end()."""
    slot = TimeSlot()
    new_dur = 3
    slot.duration = new_dur
    expected_end = "11:00"
    assert slot.end == expected_end


def test_movable_setter():
    """Verifies that the TimeSlot's movable setter works."""
    slot = TimeSlot()
    slot.movable = False
    assert slot.movable is False


def test_start_number_setter():
    """Verifies that the TimeSlot's start_number changes if start time changes """
    slot = TimeSlot('wed', '13:15')
    assert slot.start_number == 13.25
    slot.start = "12:00"
    assert slot.start_number == 12.0


def test_setting_day_sets_day_number():
    """Verifies that the TimeSlot's day_number changes if day changes """
    slot = TimeSlot('wed', '13:15')
    assert slot.day_number == 3
    slot.day = WeekDay.Thursday
    assert slot.day_number == 4


def test_snap_to_time():
    """Verifies that snap_to_time adjusts the TimeSlot's start property to the nearest half-hour."""
    slot = TimeSlot()
    slot.start = "13:15"
    slot.snap_to_time()
    expected_start = "13:00"
    assert slot.start == expected_start


def test_snap_to_time_bad_value_to_minimum():
    """Verifies that snap_to_time adjusts TimeSlot's start property to the minimum value of 8 if
    start is set_default_fonts_and_colours to something less than 8. """
    slot = TimeSlot()
    slot.start = "5:00"
    slot.snap_to_time()
    expected_start = "8:00"
    assert slot.start == expected_start


def test_snap_to_time_bad_value_to_maximum():
    """Verifies that snap_to_time adjusts TimeSlot's start property to the maximum value of 18
    minus duration if start is set_default_fonts_and_colours to something greater than 18. """
    slot = TimeSlot()
    slot.start = "19:00"
    slot.snap_to_time()
    expected_start = "16:30"
    assert slot.start == expected_start


def test_snap_to_day_with_args():
    """Verifies that TimeSlot's snap_to_day method adjusts its day property to the correct value
    when it is outside a specified date range. """
    slot = TimeSlot()
    slot.day = WeekDay.Friday
    slot.snap_to_day(3, 4)
    expected_day = "thu"
    assert slot.day == expected_day


def test_conflicts_time():
    """Verifies that conflicts_time works as intended."""
    slot1 = TimeSlot()
    slot2 = TimeSlot("mon", "9:00")
    assert slot1.conflicts_time(slot2) is True


def test_conflicts_time_different_days():
    """Verifies that conflicts_time registers no conflict when two TimeSlots are on different
    days. """
    slot1 = TimeSlot()
    slot2 = TimeSlot(WeekDay.Tuesday.value)
    assert slot1.conflicts_time(slot2) is False
