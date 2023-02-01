from Block import Block


def test_number_getter():
    """Verifies that the number property works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    assert block.number == str(num)


def test_number():
    assert False


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
