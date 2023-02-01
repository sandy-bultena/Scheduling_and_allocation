from Lab import Lab
from Time_slot import TimeSlot


def test_id():
    """Verifies that the ID property automatically increments as Labs are created."""
    lab = Lab()
    assert lab.id == 1  # The first Lab created will always have an ID of 1.


def test_id_multiple_labs():
    """Verifies that the last Lab created will have the highest ID."""
    lab1 = Lab("R-101", "Worst place in the world")
    lab2 = Lab("R-102", "Second-worst place in the world")
    assert lab2.id == getattr(lab2, '_max_id')


def test_number_getter():
    """Verifies that number getter works as intended."""
    num = "R-101"
    lab = Lab(num)
    assert lab.number == num


def test_number_setter():
    """Verifies that the number setter works as intended."""
    lab = Lab()
    num = "R-101"
    lab.number = num
    assert lab.number != "100" and lab.number == num


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
    """Verifies that add_unavailable() creates a TimeSlot object with the passed-in values, which is stored in the
    Lab's _unavailable attribute. """
    day = "mon"
    start = "8:30"
    dur = 2.0
    lab = Lab()
    lab.add_unavailable(day, start, dur)
    slot = getattr(lab, '_unavailable')[1]
    assert type(slot) is TimeSlot and slot.day == day and slot.start == start and slot.duration == dur


def test_remove_unavailable_good():
    """Verifies that remove_unavailable() can remove a TimeSlot from Lab based on the received TimeSlot ID."""
    day = "mon"
    start = "8:30"
    dur = 2.0
    lab = Lab()
    lab.add_unavailable(day, start, dur)
    slot_id = getattr(TimeSlot, '_max_id')
    lab.remove_unavailable(slot_id)
    assert len(getattr(lab, '_unavailable')) == 0


def test_remove_unavailable_no_crash():
    """Verifies that remove_unavailable will not crash the program when attempting to remove a TimeSlot which doesn't
    exist. """
    day = "mon"
    start = "8:30"
    dur = 2.0
    lab = Lab()
    lab.add_unavailable(day, start, dur)
    bad_id = 9999
    lab.remove_unavailable(bad_id)
    assert len(getattr(lab, '_unavailable')) == 1 and getattr(lab, '_unavailable')[1].start == start


def test_get_unavailable():
    assert False


def test_unavailable():
    assert False


def test_print_description():
    assert False
