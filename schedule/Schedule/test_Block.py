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

def test_delete():
    assert False


def test_start():
    assert False


def test_start():
    assert False


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
