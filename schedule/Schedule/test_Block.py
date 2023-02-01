import pytest

from Block import Block
from Section import Section
from Lab import Lab


def test_number_getter():
    """Verifies that the number property works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    assert block.number == num


def test_number_setter_good():
    """Verifies that the number setter can set an appropriate value."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    new_num = 4
    block.number = new_num
    assert block.number == new_num


def test_number_setter_bad():
    """Verifies that the number setter throws an exception when receiving bad input."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    bad_num = "foo"
    with pytest.raises(Exception) as e:
        block.number = bad_num
    assert "must be an integer and cannot be null" in str(e.value).lower()


# def test_delete():
#     """Verifies that the delete() method successfully destroys an instance of a Block."""
#     day = "mon"
#     start = "8:30"
#     dur = 2
#     num = 1
#     block = Block(day, start, dur, num)
#     block.delete()
#     assert block is None


def test_start_getter():
    """Verifies that the start getter works as intended. Same as TimeSlot.start getter."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    assert block.start == start


def test_start_setter_synced_2_blocks():
    """Verifies that the start setter works as intended, and that it changes the start value of any Blocks synced to
    the Block on which it was called. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block1 = Block(day, start, dur, num)
    block2 = Block("wed", start, dur, 2)
    block1.sync_block(block2)
    block2.sync_block(block1)
    new_start = "10:00"
    block1.start = new_start
    assert block2.start == new_start


def test_start_setter_synced_4_blocks():
    """Same as previous test, but with 4 blocks instead of 2."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block1 = Block(day, start, dur, num)
    block2 = Block("wed", start, dur, 2)
    block3 = Block("thu", start, dur, 3)
    block4 = Block("sat", start, dur, 4)
    block1.sync_block(block2)
    block1.sync_block(block3)
    block1.sync_block(block4)
    block2.sync_block(block1)
    block2.sync_block(block3)
    block2.sync_block(block4)
    block3.sync_block(block1)
    block3.sync_block(block2)
    block3.sync_block(block4)
    block4.sync_block(block1)
    block4.sync_block(block2)
    block4.sync_block(block3)

    new_start = "10:00"
    block1.start = new_start
    assert block2.start == new_start and block3.start == new_start and block4.start == new_start


def test_day_getter():
    """Verifies that the day getter works as intended. Same as in TimeSlot."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block1 = Block(day, start, dur, num)
    assert block1.day == day


def test_day():
    """Verifies that the day setter works as intended, changing the day property of any Block synced to the current
    Block. """
    day = "mon"
    start1 = "8:00"
    start2 = "12:00"
    dur = 2
    num1 = 1
    num2 = 2
    block1 = Block(day, start1, dur, num1)
    block2 = Block(day, start2, dur, num2)
    block1.sync_block(block2)
    block2.sync_block(block1)
    block1.day = "thu"
    assert block2.day == "thu"


def test_id():
    assert False


def test_section_getter():
    """Verifies that the section getter works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    """Since sections are not assigned to Blocks at initialization, the value of section will be None."""
    assert block.section is None


def test_section_setter_good():
    """Verifies that the section setter can set a valid section."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    sect = Section()
    block.section = sect
    assert block.section == sect


def test_section_setter_bad():
    """Verifies that the section setter throws a TypeError when receiving a value that isn't a Section."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    bad_sect = {
        "foo": "foo",
        "bar": "bar"
    }
    with pytest.raises(TypeError) as e:
        block.section = bad_sect
    assert "invalid section" in str(e.value).lower()


def test_assign_lab_good():
    """Verifies that the assign_lab method can assign a valid Lab object to the Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    lab = Lab()
    block.assign_lab(lab)
    assert getattr(block, '_labs', {})[lab.id] == lab


def test_assign_lab_bad():
    """Verifies that assign_lab will reject an input that isn't a Lab object."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    bad_lab = "baz"
    with pytest.raises(TypeError) as e:
        block.assign_lab(bad_lab)
    assert "invalid lab" in str(e.value).lower()


def test_remove_lab():
    assert False


def test_remove_all_labs():
    assert False


def test_labs():
    assert False


def test_has_lab():
    assert False


def test_assign_teacher():
    assert False


def test_remove_teacher():
    assert False


def test_remove_all_teachers():
    assert False


def test_teachers():
    assert False


def test_has_teacher():
    assert False


def test_teachers_obj():
    assert False


def test_sync_block():
    assert False


def test_unsync_block():
    assert False


def test_synced():
    assert False


def test_reset_conflicted():
    assert False


def test_conflicted():
    assert False


def test_conflicted():
    assert False


def test_is_conflicted():
    assert False


def test_print_description():
    assert False


def test_print_description_2():
    assert False


def test_conflicts():
    assert False


def test_refresh_number():
    assert False
