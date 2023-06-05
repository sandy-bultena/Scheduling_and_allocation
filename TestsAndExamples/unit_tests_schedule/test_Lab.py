import pytest
import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))
from schedule.Schedule.Labs import Labs
from schedule.Schedule.LabUnavailableTime import LabUnavailableTime


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    pass


@pytest.fixture(autouse=True)
def before_and_after():
    pass


# ============================================================================
# Lab
# ============================================================================
def test_number_getter():
    """Verifies that number getter works as intended."""
    num = "R-101"
    labs = Labs()
    lab = labs.add(num)
    assert lab.number == num


def test_number_setter():
    """Verifies that the number setter works as intended."""
    labs = Labs()
    lab = labs.add("R-202")
    num = "R-101"
    lab.number = num
    assert lab.number == num


def test_descr_getter():
    """Verifies that Lab's descr getter works as intended."""
    labs = Labs()
    room = "R-101"
    descr = "Worst place in the world."
    lab = labs.add(room, descr)
    assert lab.description == descr


def test_descr_setter():
    """Verifies that the descr setter works as intended."""
    labs = Labs()
    lab = labs.add()
    descr = "Worst place in the world."
    lab.descr = descr
    assert lab.descr == descr


def test_add_unavailable():
    labs = Labs()
    time_slot1 = LabUnavailableTime("wed", "12:30", 3.5, False)
    time_slot2 = LabUnavailableTime("wed", "12:30", 3.5, False)
    lab = labs.add()
    lab.add_unavailable_slot(time_slot1)
    lab.add_unavailable_slot(time_slot2)
    assert len(lab.unavailable_slots) == 2


def test_remove_unavailable_good():
    """Verifies that remove_unavailable_slot() can remove a TimeSlot from Lab based on the received
    TimeSlot ID. """
    day = "mon"
    start = "8:30"
    dur = 2.0
    labs = Labs()
    lab = labs.add()
    t1 = lab.add_unavailable_slot(LabUnavailableTime(day, start, dur))
    t2 = lab.add_unavailable_slot(LabUnavailableTime(day, start, dur))
    lab.remove_unavailable_slot(t1)
    assert len(lab.unavailable_slots) == 1
    assert lab.unavailable_slots[0] == t2


def test_unavailable():
    """Verifies that unavailable() returns a list of all unavailable TimeSlots for this Lab."""
    day_1 = "mon"
    start_1 = "8:30"
    dur_1 = 2.0
    day_2 = "tue"
    start_2 = "10:00"
    dur_2 = 1.5
    labs = Labs()
    lab = labs.add()
    lu1 = lab.add_unavailable_slot(LabUnavailableTime(day_1, start_1, dur_1))
    lu2 = lab.add_unavailable_slot(LabUnavailableTime(day_2, start_2, dur_2))
    times = lab.unavailable_slots
    assert len(times) == 2
    assert lu1 in lab.unavailable_slots
    assert lu2 in lab.unavailable_slots


def test_unavailable_no_slots():
    """Verifies that unavailable() returns an empty tuple if no TimeSlots have been assigned to
    this Lab. """
    labs = Labs()
    lab = labs.add()
    slots = lab.unavailable_slots
    assert type(slots) is tuple and len(slots) == 0


def test_string_representation_full():
    """Verifies that the string representation returns a string containing the Lab's number and
    title attributes. """
    num = "R-101"
    desc = "Worst place in the world."
    labs = Labs()
    lab = labs.add(num, desc)
    to_string = str(lab)
    assert f"{num}: {desc}" in to_string


def test_string_representation_short():
    """Verifies that string representation returns a string containing only the Lab's number if
    it lacks a title attribute. """
    num = "R-101"
    labs = Labs()
    lab = labs.add(num)
    desc = str(lab)
    assert num == desc


# ============================================================================
# Collection
# ============================================================================
def test_id():
    """Verifies that the id property works as intended."""
    labs = Labs()
    lab = labs.add()
    old_id = lab.id
    lab = labs.add()
    assert lab.id == old_id + 1


def test_id_with_id_given():
    """Verifies that the id property works as intended."""
    existing_id = 112
    labs = Labs()
    lab1 = labs.add(lab_id=existing_id)
    assert lab1.id == existing_id
    lab2 = labs.add()
    assert lab2.id == existing_id + 1
    lab3 = labs.add(lab_id=existing_id - 5)
    assert lab3.id == existing_id - 5
    lab4 = labs.add()
    assert lab4.id == lab2.id + 1


def test_clear_all_removes_all_labs():
    """verify that clear_all works as expected"""
    labs = Labs()
    labs.add("R-101", "Worst place in the world")
    labs.add("R-102", "Second-worst place in the world")
    labs.clear()
    all_labs = labs.get_all()
    assert len(all_labs) == 0


def test_get_all():
    """Verifies that list() returns a tuple of all extant Lab objects."""
    labs = Labs()
    lab1 = labs.add("R-101", "Worst place in the world")
    lab2 = labs.add("R-102", "Second-worst place in the world")
    all_labs = labs.get_all()
    assert len(all_labs) == 2 and lab1 in all_labs and lab2 in all_labs


def test_get_all_is_empty_empty():
    """Verifies that list() returns an empty tuple if no Labs have been created."""
    labs = Labs()
    all_labs = labs.get_all()
    assert len(all_labs) == 0


def test_remove():
    """Verifies that the static remove() method works as intended."""
    labs = Labs()
    lab1 = labs.add("R-101", "Worst place in the world")
    labs.add("R-102", "Second-worst place in the world")
    labs.remove(lab1)
    all_labs = labs.get_all()
    assert len(all_labs) == 1 and lab1 not in all_labs


def test_get_by_number_good():
    """Verifies that get_by_number() returns the first Lab matching the passed room number."""
    labs = Labs()
    room = "R-101"
    lab1 = labs.add("R-101", "Worst place in the world")
    labs.add("R-102", "Second-worst place in the world")
    assert labs.get_by_number(room) == lab1


def test_get_by_number_not_valid():
    labs = Labs()
    labs.add("R-101", "Worst place in the world")
    labs.add("R-102", "Second-worst place in the world")
    bad_room = "foo"
    assert labs.get_by_number(bad_room) is None


def test_get_by_number_on_empty_list():
    labs = Labs()
    bad_room = "foo"
    assert labs.get_by_number(bad_room) is None


def test_get_by_id_good():
    """Verifies that get_by_id() returns the first Lab matches the id."""
    labs = Labs()
    lab1 = labs.add("R-101", "Worst place in the world", lab_id=11)
    lab2 = labs.add("R-102", "Second-worst place in the world", lab_id=14)
    assert labs.get_by_id(lab1.id) == lab1
    assert lab1.id == 11
    assert labs.get_by_id(lab2.id) == lab2
    assert lab2.id == 14


def test_get_by_id_not_valid():
    labs = Labs()
    labs.add("R-101", "Worst place in the world", lab_id=11)
    labs.add("R-102", "Second-worst place in the world", lab_id=14)
    assert labs.get_by_id(666) is None


def test_get_by_id_on_empty_list():
    labs = Labs()
    bad_id = 666
    assert labs.get_by_id(bad_id) is None
