import pytest
import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))
from schedule.Model import Lab
from schedule.Model.time_slot import TimeSlot


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
    lab = Lab(num)
    assert lab.number == num


def test_number_setter():
    """Verifies that the number setter works as intended."""
    lab = Lab("R-202")
    num = "R-101"
    lab.number = num
    assert lab.number == num


def test_descr_getter():
    """Verifies that Lab's descr getter works as intended."""
    room = "R-101"
    descr = "Worst place in the world."
    lab = Lab(room, descr)
    assert lab.description == descr


def test_descr_setter():
    """Verifies that the descr setter works as intended."""
    lab = Lab()
    descr = "Worst place in the world."
    lab.descr = descr
    assert lab.descr == descr


def test_add_unavailable():
    time_slot1 = TimeSlot("wed", "12:30", 3.5, False)
    time_slot2 = TimeSlot("wed", "12:30", 3.5, False)
    lab = Lab()
    lab.add_unavailable_slot(time_slot1)
    lab.add_unavailable_slot(time_slot2)
    assert len(lab.unavailable_slots) == 2


def test_remove_unavailable_good():
    """Verifies that remove_unavailable_slot() can remove a TimeSlot from Lab based on the received
    TimeSlot ID. """
    day = "mon"
    start = "8:30"
    dur = 2.0
    lab = Lab()
    t1 = lab.add_unavailable_slot(TimeSlot(day, start, dur))
    t2 = lab.add_unavailable_slot(TimeSlot(day, start, dur))
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
    lab = Lab()
    lu1 = lab.add_unavailable_slot(TimeSlot(day_1, start_1, dur_1))
    lu2 = lab.add_unavailable_slot(TimeSlot(day_2, start_2, dur_2))
    times = lab.unavailable_slots
    assert len(times) == 2
    assert lu1 in lab.unavailable_slots
    assert lu2 in lab.unavailable_slots


def test_unavailable_no_slots():
    """Verifies that unavailable() returns an empty tuple if no TimeSlots have been assigned to
    this Lab. """
    lab = Lab()
    slots = lab.unavailable_slots
    assert type(slots) is tuple and len(slots) == 0


def test_string_representation_full():
    """Verifies that the string representation returns a string containing the Lab's number and
    title attributes. """
    num = "R-101"
    desc = "Worst place in the world."
    lab = Lab(num, desc)
    to_string = str(lab)
    assert f"{num}: {desc}" in to_string


def test_string_representation_short():
    """Verifies that string representation returns a string containing only the Lab's number if
    it lacks a title attribute. """
    num = "R-101"
    lab = Lab(num)
    desc = str(lab)
    assert num == desc


# ============================================================================
# Collection
# ============================================================================
def test_id():
    """Verifies that the id property works as intended."""
    lab = Lab()
    old_id = lab.id
    lab = Lab()
    assert lab.id == old_id + 1


def test_id_with_id_given():
    """Verifies that the id property works as intended."""
    existing_id = 112
    lab1 = Lab(lab_id=existing_id)
    assert lab1.id == existing_id
    lab2 = Lab()
    assert lab2.id == existing_id + 1
    lab3 = Lab(lab_id=existing_id - 5)
    assert lab3.id == existing_id - 5
    lab4 = Lab()
    assert lab4.id == lab2.id + 1


