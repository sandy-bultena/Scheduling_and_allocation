from Teacher import Teacher


def test_id():
    """"Verifies that Teacher IDs are incremented automatically."""
    teach = Teacher("John", "Smith")
    max_id = getattr(Teacher, '_max_id')
    assert max_id == teach.id


def test_firstname_getter():
    """Verifies that firstname getter works as intended."""
    fname = "John"
    teach = Teacher(fname, "Smith")
    assert fname == teach.firstname


def test_firstname():
    assert False


def test_lastname():
    assert False


def test_lastname():
    assert False


def test_dept():
    assert False


def test_dept():
    assert False


def test_release():
    assert False


def test_release():
    assert False


def test_print_description():
    assert False
