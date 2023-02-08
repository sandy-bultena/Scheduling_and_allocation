import pytest

from ..Teacher import Teacher
from ..Block import Block


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


def test_lastname_getter():
    """Verifies that the lastname getter works as intended."""
    l_name = "Smith"
    teach = Teacher("John", l_name)
    assert l_name == teach.lastname


def test_lastname_setter_good():
    """Verifies that the lastname setter can set a valid (non-empty) last name for the Teacher."""
    teach = Teacher("John", "Smith")
    new_l_name = "Forstinger"
    teach.lastname = new_l_name
    assert new_l_name == teach.lastname


def test_lastname_setter_bad():
    """Verifies that the lastname setter throws an exception when receiving an invalid input (
    empty strings). """
    teach = Teacher("John", "Smith")
    bad_name = ""
    with pytest.raises(Exception) as e:
        teach.lastname = bad_name
    assert "last name cannot be an empty string" in str(e.value).lower()


def test_dept_getter():
    """Verifies that dept getter works as intended."""
    dept = "Computer Science"
    teach = Teacher("John", "Smith", dept)
    assert dept == teach.dept


def test_dept_setter():
    """Verifies that dept setter can set a new department name."""
    teach = Teacher("John", "Smith")
    dept = "Computer Science"
    teach.dept = dept
    assert dept == teach.dept


def test_release_getter():
    """Verifies that the release getter works as intended, returning a default value of 0."""
    teach = Teacher("John", "Smith")
    assert teach.release == 0


def test_release_setter():
    """Verifies that the release setter can set a new value."""
    teach = Teacher("John", "Smith")
    new_release = 0.5
    teach.release = new_release
    assert new_release == teach.release


def test_print_description():
    """Verifies that print_description() returns a string containing the Teacher's full name."""
    f_name = "John"
    l_name = "Smith"
    teach = Teacher(f_name, l_name)
    assert f"{f_name} {l_name}" in teach.print_description()


def test_share_blocks_true():
    """Verifies that the static share_blocks() method returns true if two blocks are sharing a
    teacher. """
    teach = Teacher("John", "Smith")
    block_1 = Block("mon", "8:30", 1.5, 1)
    block_2 = Block("mon", "10:00", 1.5, 2)
    block_1.assign_teacher(teach)
    block_2.assign_teacher(teach)
    assert Teacher.share_blocks(block_1, block_2) is True


def test_share_blocks_false():
    """Verifies that the static share_blocks() method returns false if two blocks are not sharing
    any Teachers. """
    teach = Teacher("John", "Smith")
    block_1 = Block("mon", "8:30", 1.5, 1)
    block_2 = Block("mon", "10:00", 1.5, 2)
    block_1.assign_teacher(teach)
    assert Teacher.share_blocks(block_1, block_2) is False


def test_get_good_id():
    """Verifies that the static get() method works as intended."""
    Teacher._Teacher__instances = {}
    Teacher._max_id = 0
    teach = Teacher("John", "Smith")
    assert Teacher.get(1) == teach


def test_get_bad_id():
    """Verifies that get() returns None when receiving an invalid ID."""
    Teacher._Teacher__instances = {}
    Teacher._max_id = 0
    teach = Teacher("John", "Smith")
    bad_id = 666
    assert Teacher.get(bad_id) is None
