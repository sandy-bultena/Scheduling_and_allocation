from Lab import Lab


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
    assert False


def test_remove_unavailable():
    assert False


def test_get_unavailable():
    assert False


def test_unavailable():
    assert False


def test_print_description():
    assert False
