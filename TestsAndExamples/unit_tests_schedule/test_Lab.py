import pytest
import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))
import schedule.Schedule.Labs as labs
from schedule.Schedule.Labs import Lab
from schedule.Schedule.LabUnavailableTime import LabUnavailableTime
import schedule.Schedule.IDGeneratorCode as id_gen


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    pass


@pytest.fixture(autouse=True)
def before_and_after():
    labs.clear_all()


def test_id():
    """Verifies that the id property works as intended."""
    lab = Lab()
    old_id = lab.id
    lab = Lab()
    assert lab.id == old_id + 1


def test_id_with_id_given():
    """Verifies that the id property works as intended."""
    labs._lab_id_generator = id_gen.get_id_generator()

    existing_id = 12
    lab1 = Lab(lab_id=existing_id)
    assert lab1.id == existing_id
    lab2 = Lab()
    assert lab2.id == existing_id + 1
    lab3 = Lab(lab_id=existing_id - 5)
    assert lab3.id == existing_id - 5
    lab4 = Lab()
    assert lab4.id == lab2.id + 1


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
    assert lab.descr == descr


def test_descr_setter():
    """Verifies that the descr setter works as intended."""
    lab = Lab()
    descr = "Worst place in the world."
    lab.descr = descr
    assert lab.descr == descr


def test_add_unavailable():
    """Verifies that add_unavailable_time() creates a TimeSlot object with the passed-in values,
    which is stored in the Lab's _unavailable attribute. """
    day = "mon"
    start = "8:30"
    dur = 2.0
    lab = Lab()
    lab.add_unavailable_time(day, start, dur)
    assert len(lab.unavailable_slots) == 1
    time = lab.unavailable_slots[0]
    assert type(time) is LabUnavailableTime and time.day == day \
           and time.start == start and time.duration == dur


def test_remove_unavailable_good():
    """Verifies that remove_unavailable_slot() can remove a TimeSlot from Lab based on the received
    TimeSlot ID. """
    day = "mon"
    start = "8:30"
    dur = 2.0
    lab = Lab()
    lab.add_unavailable_time(day, start, dur)
    lab.add_unavailable_time(day, start, dur)
    slot = lab.unavailable_slots[0]
    lab.remove_unavailable_slot(slot)
    assert len(lab.unavailable_slots) == 1


def test_unavailable():
    """Verifies that unavailable() returns a list of all unavailable TimeSlots for this Lab."""
    day_1 = "mon"
    start_1 = "8:30"
    dur_1 = 2.0
    day_2 = "tue"
    start_2 = "10:00"
    dur_2 = 1.5
    lab = Lab()
    lu1 = lab.add_unavailable_time(day_1, start_1, dur_1)
    lu2 = lab.add_unavailable_time(day_2, start_2, dur_2)
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


def test_clear_all_removes_all_labs():
    """verify that clear_all works as expected"""
    Lab("R-101", "Worst place in the world")
    Lab("R-102", "Second-worst place in the world")
    labs.clear_all()
    all_labs = labs.get_all()
    assert len(all_labs) == 0


def test_string_representation_full():
    """Verifies that the string representation returns a string containing the Lab's number and
    description attributes. """
    num = "R-101"
    desc = "Worst place in the world."
    lab = Lab(num, desc)
    to_string = str(lab)
    assert f"{num}: {desc}" in to_string


def test_string_representation_short():
    """Verifies that string representation returns a string containing only the Lab's number if
    it lacks a description attribute. """
    num = "R-101"
    lab = Lab(num)
    desc = str(lab)
    assert num == desc


def test_list():
    """Verifies that list() returns a tuple of all extant Lab objects."""
    labs.clear_all()
    lab1 = Lab("R-101", "Worst place in the world")
    lab2 = Lab("R-102", "Second-worst place in the world")
    all_labs = labs.get_all()
    assert len(all_labs) == 2 and lab1 in all_labs and lab2 in all_labs


def test_list_empty():
    """Verifies that list() returns an empty tuple if no Labs have been created."""
    labs.clear_all()
    all_labs = labs.get_all()
    assert len(all_labs) == 0


def test_remove():
    """Verifies that the static remove() method works as intended."""
    labs.clear_all()
    lab1 = Lab("R-101", "Worst place in the world")
    Lab("R-102", "Second-worst place in the world")
    lab1.delete()
    all_labs = labs.get_all()
    assert len(all_labs) == 1 and lab1 not in all_labs


def test_get_by_number_good():
    """Verifies that get_by_number() returns the first Lab matching the passed room number."""
    labs.clear_all()
    room = "R-101"
    lab1 = Lab("R-101", "Worst place in the world")
    Lab("R-102", "Second-worst place in the world")
    assert labs.get_by_number(room) == lab1


def test_get_by_number_not_valid():
    labs.clear_all()
    Lab("R-101", "Worst place in the world")
    Lab("R-102", "Second-worst place in the world")
    bad_room = "foo"
    assert labs.get_by_number(bad_room) is None


def test_get_by_number_on_empty_list():
    labs.clear_all()
    bad_room = "foo"
    assert labs.get_by_number(bad_room) is None
