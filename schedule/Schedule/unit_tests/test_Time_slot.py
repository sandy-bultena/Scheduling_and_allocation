import sys
from os import path


sys.path.append(path.dirname(path.dirname(__file__)))
import pytest
from .db_constants import *

from .. import Block    # avoids circular import
from ..Time_slot import TimeSlot
from ..ScheduleEnums import WeekDay
from ..database.PonyDatabaseConnection import define_database
from pony.orm import *

db: Database


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    global db
    db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)
    yield
    db.drop_all_tables(with_all_data=True)
    db.disconnect()
    db.provider = db.schema = None


@pytest.fixture(autouse=True)
def before_and_after():
    db.create_tables()
    yield
    #db.drop_table(table_name='time_slot', if_exists=True, with_all_data=True)

def test_defaults():
    """Verifies that default values are set correctly"""
    slot = TimeSlot()
    assert slot.day == "mon"
    assert slot.start == "8:00"
    assert slot.end() == "9:30"
    assert slot.duration == 1.5
    assert slot.movable
    assert slot.start_number == 8
    assert slot.day_number == 1

def test_day_setter():
    slot = TimeSlot()
    new_day = WeekDay.Friday.value
    slot.day = new_day

    real_val = 'fri'
    assert slot.day == real_val


def test_day_setter_warning():
    """Verifies that the day setter raises an error when an invalid value is passed."""
    slot = TimeSlot()
    bad_day = 14
    with pytest.warns(UserWarning, match="invalid day specified"):
        slot.day = bad_day


def test_start_setter():
    slot = TimeSlot()
    new_start = "10:00"
    slot.start = new_start
    assert slot.start == new_start


def test_start_setter_warning():
    """Verifies that start setter raises a warning when presented with an invalid input."""
    slot = TimeSlot()
    bad_start = "foo"
    with pytest.warns(UserWarning, match="invalid start time"):
        slot.start = bad_start


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


def test_movable_setter():
    """Verifies that the TimeSlot's movable setter works."""
    slot = TimeSlot()
    slot.movable = False
    assert slot.movable is False


def test_start_number_setter():
    """Verifies that the TimeSlot's start_number setter works as intended: that it changes
    start_number ONLY, without affecting start. """
    slot = TimeSlot()
    new_start_num = 12
    slot.start_number = new_start_num
    bad_start = "12:00"
    assert slot.start_number == new_start_num and slot.start != bad_start


def test_snap_to_time():
    """Verifies that snap_to_time adjusts the TimeSlot's start property to the nearest half-hour."""
    slot = TimeSlot()
    slot.start = "13:15"
    slot.snap_to_time()
    expected_start = "13:00"
    assert slot.start == expected_start


def test_snap_to_time_bad_value_to_minimum():
    """Verifies that snap_to_time adjusts TimeSlot's start property to the minimum value of 8 if
    start is set to something less than 8. """
    slot = TimeSlot()
    slot.start = "5:00"
    slot.snap_to_time()
    expected_start = "8:00"
    assert slot.start == expected_start


def test_snap_to_time_bad_value_to_maximum():
    """Verifies that snap_to_time adjusts TimeSlot's start property to the maximum value of 18
    minus duration if start is set to something greater than 18. """
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