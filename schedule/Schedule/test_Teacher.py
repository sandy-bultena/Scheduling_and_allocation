import pytest

from Teacher import Teacher


def test_id():
    """"Verifies that Teacher IDs are incremented automatically."""
    teach = Teacher("John", "Smith")
    max_id = getattr(Teacher, '_max_id')
    assert max_id == teach.id


def test_firstname_getter():
    """Verifies that firstname getter works as intended."""
    f_name = "John"
    teach = Teacher(f_name, "Smith")
    assert f_name == teach.firstname


def test_firstname_setter_good():
    """Verifies that firstname setter can set a valid first name."""
    teach = Teacher("John", "Smith")
    new_f_name = "Bob"
    teach.firstname = new_f_name
    assert new_f_name == teach.firstname


def test_firstname_setter_bad():
    """Verifies that firstname setter throws an exception for invalid input (empty strings)."""
    teach = Teacher("John", "Smith")
    bad_name = " "
    with pytest.raises(Exception) as e:
        teach.firstname = bad_name
    assert "first name cannot be an empty string" in str(e.value).lower()


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
