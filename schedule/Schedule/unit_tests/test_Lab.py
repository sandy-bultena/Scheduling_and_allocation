from ..Lab import Lab, LabMeta
from ..Time_slot import TimeSlot
from ..Block import Block


def test_id():
    """Verifies that the ID property automatically increments as Labs are created."""
    # Set Lab's max_id to 0 just to avoid shenanigans with simultaneously running tests.
    Lab._max_id = 0
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
    """Verifies that add_unavailable() creates a TimeSlot object with the passed-in values,
    which is stored in the Lab's _unavailable attribute. """
    # Reset the TimeSlot class's max_id to 0 to avoid KeyErrors when all tests are run
    # simultaneously.
    TimeSlot._max_id = 0
    day = "mon"
    start = "8:30"
    dur = 2.0
    lab = Lab()
    lab.add_unavailable(day, start, dur)
    slot = getattr(lab, '_unavailable')[1]
    assert type(slot) is TimeSlot and slot.day == day \
           and slot.start == start and slot.duration == dur


def test_remove_unavailable_good():
    """Verifies that remove_unavailable() can remove a TimeSlot from Lab based on the received
    TimeSlot ID. """
    day = "mon"
    start = "8:30"
    dur = 2.0
    lab = Lab()
    lab.add_unavailable(day, start, dur)
    slot_id = getattr(TimeSlot, '_max_id')
    lab.remove_unavailable(slot_id)
    assert len(getattr(lab, '_unavailable')) == 0


def test_remove_unavailable_no_crash():
    """Verifies that remove_unavailable will not crash the program when attempting to remove a
    TimeSlot which doesn't exist. """
    day = "mon"
    start = "8:30"
    dur = 2.0
    lab = Lab()
    lab.add_unavailable(day, start, dur)
    bad_id = 9999
    slot_key = getattr(TimeSlot, '_max_id')
    lab.remove_unavailable(bad_id)
    assert len(getattr(lab, '_unavailable')) == 1 \
           and getattr(lab, '_unavailable')[slot_key].start == start


def test_get_unavailable_good():
    """Verifies that get_unavailable() can retrieve a specified TimeSlot from the Lab."""
    day = "mon"
    start = "8:30"
    dur = 2.0
    lab = Lab()
    lab.add_unavailable(day, start, dur)
    slot_id = getattr(TimeSlot, '_max_id')
    slot = lab.get_unavailable(slot_id)
    assert slot.id == slot_id and slot.start == start and slot.day == day and slot.duration == dur


def test_get_unavailable_bad_input():
    """Verifies that get_unavailable returns None when trying to retrieve a nonexistent TimeSlot
    from the Lab. """
    day = "mon"
    start = "8:30"
    dur = 2.0
    lab = Lab()
    lab.add_unavailable(day, start, dur)
    bad_id = 999
    no_slot = lab.get_unavailable(bad_id)
    assert no_slot is None


def test_unavailable():
    """Verifies that unavailable() returns a list of all unavailable TimeSlots for this Lab."""
    day_1 = "mon"
    start_1 = "8:30"
    dur_1 = 2.0
    day_2 = "tue"
    start_2 = "10:00"
    dur_2 = 1.5
    lab = Lab()
    lab.add_unavailable(day_1, start_1, dur_1)
    lab.add_unavailable(day_2, start_2, dur_2)
    slots = lab.unavailable()
    assert len(slots) == 2 and slots[0].day == day_1 and slots[1].day == day_2


def test_unavailable_no_slots():
    """Verifies that unavailable() returns an empty list if no TimeSlots have been assigned to
    this Lab. """
    lab = Lab()
    slots = lab.unavailable()
    assert type(slots) is list and len(slots) == 0


def test_print_description_full():
    """Verifies that print_description() returns a string containing the Lab's number and
    description attributes. """
    num = "R-101"
    desc = "Worst place in the world."
    lab = Lab(num, desc)
    to_string = lab.print_description()
    assert f"{num}: {desc}" in to_string


def test_print_description_short():
    """Verifies that print_description() returns a string containing only the Lab's number if it
    lacks a description attribute. """
    num = "R-101"
    lab = Lab(num)
    desc = lab.print_description()
    assert num in desc


def test_list():
    """Verifies that list() returns a tuple of all extant Lab objects."""
    Lab._Lab__instances = {}
    lab1 = Lab("R-101", "Worst place in the world")
    lab2 = Lab("R-102", "Second-worst place in the world")
    labs = Lab.list()
    assert len(labs) == 2 and lab1 in labs and lab2 in labs


def test_list_empty():
    """Verifies that list() returns an empty tuple if no Labs have been created."""
    Lab._Lab__instances = {}
    labs = Lab.list()
    assert len(labs) == 0


def test_share_blocks_true():
    """Verifies that the static share_blocks() method returns true if two Blocks are sharing the
    same Lab. """
    lab = Lab()
    block_1 = Block("mon", "8:30", 1.5, 1)
    block_2 = Block("wed", "8:30", 1.5, 2)
    block_1.assign_lab(lab)
    block_2.assign_lab(lab)
    assert LabMeta.share_blocks(block_1, block_2) is True


def test_share_blocks_false():
    """Verifies that share_blocks() returns false if two Blocks are not sharing the same Lab."""
    lab = Lab()
    block_1 = Block("mon", "8:30", 1.5, 1)
    block_2 = Block("wed", "8:30", 1.5, 2)
    block_1.assign_lab(lab)
    assert LabMeta.share_blocks(block_1, block_2) is False
