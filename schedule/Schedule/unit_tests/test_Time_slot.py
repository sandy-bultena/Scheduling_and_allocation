import sys
from os import path
sys.path.append(path.dirname(path.dirname(__file__)))

from Time_slot import TimeSlot



def test_id():
    """Verifies that the ID assigned to a TimeSlot increments automatically."""
    # NOTE: Resetting the TimeSlot max_id to 0 to prevent shenanigans from simultaneously running tests.
    TimeSlot._max_id = 0
    slots = []
    for x in range(5):
        slots.append(TimeSlot())
    last_slot = slots[-1]
    assert last_slot.id == len(slots)


def test_day_getter_default():
    """Verifies that a TimeSlot is created with a default day value of 'mon'."""
    slot = TimeSlot()
    assert slot.day == 'mon'


def test_day_setter():
    slot = TimeSlot()
    new_day = 'Sunday'
    slot.day = new_day

    real_val = 'sun'
    assert slot.day == real_val


def test_start_getter_default():
    """Verifies that a TimeSlot is created with a default start value of '8:00'."""
    slot = TimeSlot()
    assert slot.start == "8:00"


def test_start_setter():
    slot = TimeSlot()
    new_start = "10:00"
    slot.start = new_start
    assert slot.start == new_start


def test_end_default():
    """Verifies that a TimeSlot with default values with have an end of '9:30'."""
    slot = TimeSlot()
    expected_end = "9:30"
    assert slot.end() == expected_end


def test_duration_getter_default():
    """Verifies that a TimeSlot created with default values has a duration of 1.5."""
    slot = TimeSlot()
    expected_dur = 1.5
    assert slot.duration == expected_dur


def test_duration_setter():
    """Verifies that TimeSlot's duration setter works."""
    slot = TimeSlot()
    new_dur = 3
    slot.duration = new_dur
    assert slot.duration == new_dur


def test_duration_setter_changes_end():
    """Verifies that changing a TimeSlot's duration will change the value of end()."""
    slot = TimeSlot()
    new_dur = 3
    slot.duration = new_dur
    expected_end = "11:00"
    assert slot.end() == expected_end


def test_movable_getter_default():
    """Verifies that a TimeSlot with default values is movable."""
    slot = TimeSlot()
    assert slot.movable is True


def test_movable_setter():
    """Verifies that the TimeSlot's movable setter works."""
    slot = TimeSlot()
    slot.movable = False
    assert slot.movable is False


def test_start_number_getter_default():
    """Verifies that the start number for a TimeSlot with default values is 8."""
    slot = TimeSlot()
    expected_start_num = 8
    assert slot.start_number == expected_start_num


def test_start_number_setter():
    """Verifies that the TimeSlot's start_number setter works as intended: that it changes start_number ONLY,
    without affecting start. """
    slot = TimeSlot()
    new_start_num = 12
    slot.start_number = new_start_num
    bad_start = "12:00"
    assert slot.start_number == new_start_num and slot.start != bad_start


def test_day_number_getter_default():
    """Verifies that a TimeSlot with default values will have a day_number of 1."""
    slot = TimeSlot()
    expected_day_num = 1
    assert slot.day_number == expected_day_num


def test_day_number_setter():
    """Verifies that the TimeSlot's day_number setter works as intended: that it changes day_number ONLY,
    without affecting day. """
    slot = TimeSlot()
    new_day_num = 7
    slot.day_number = new_day_num
    bad_day = "fri"
    assert slot.day_number == new_day_num and slot.day != bad_day


def test_snap_to_time():
    """Verifies that snap_to_time adjusts the TimeSlot's start property to the nearest half-hour."""
    slot = TimeSlot()
    slot.start = "13:15"
    slot.snap_to_time()
    expected_start = "13:00"
    assert slot.start == expected_start


def test__snap_to_time_bad_value_to_minimum():
    """Verifies that snap_to_time adjusts TimeSlot's start property to the minimum value of 8 if start is set to
    something less than 8. """
    slot = TimeSlot()
    slot.start = "5:00"
    slot.snap_to_time()
    expected_start = "8:00"
    assert slot.start == expected_start


def test_snap_to_time_bad_value_to_maximum():
    """Verifies that snap_to_time adjusts TimeSlot's start property to the maximum value of 18 minus duration if
    start is set to something greater than 18. """
    slot = TimeSlot()
    slot.start = "19:00"
    slot.snap_to_time()
    expected_start = "16:30"
    assert slot.start == expected_start


def test_snap_to_day_with_args():
    """Verifies that TimeSlot's snap_to_day method adjusts its day property to the correct value when it is outside a
    specified date range."""
    slot = TimeSlot()
    slot.day = "sun"
    slot.snap_to_day(3, 4)
    expected_day = "thu"
    assert slot.day == expected_day


def test_conflicts_time():
    """Verifies that conflicts_time works as intended."""
    slot1 = TimeSlot()
    slot2 = TimeSlot("monday", "9:00")
    assert slot1.conflicts_time(slot2) is True


def test_conflicts_time_different_days():
    """Verifies that conflicts_time registers no conflict when two TimeSlots are on different days."""
    slot1 = TimeSlot()
    slot2 = TimeSlot("Tuesday")
    assert slot1.conflicts_time(slot2) is False


def test_list():
    """Verifies that the static list() method returns a tuple containing all extant TimeSlot objects."""
    TimeSlot._TimeSlot__instances = []
    slot1 = TimeSlot()
    slot2 = TimeSlot("Tuesday")
    slots = TimeSlot.list()
    assert len(slots) == 2 and slot1 in slots and slot2 in slots


def test_list_no_slots():
    """Verifies that the static list() method returns an empty tuple if no TimeSlots have been created yet."""
    TimeSlot._TimeSlot__instances = []
    slots = TimeSlot.list()
    assert len(slots) == 0
