import pytest

from Block import Block


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


def test_day():
    assert False


def test_day():
    assert False


def test_id():
    assert False


def test_section():
    assert False


def test_section():
    assert False


def test_assign_lab():
    assert False


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
