import pytest

import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))

from schedule.Schedule.Teachers import Teachers


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    pass


@pytest.fixture(autouse=True)
def before_and_after():
    pass


# ============================================================================
# Stream
# ============================================================================
def test_dept_getter():
    teachers = Teachers()
    teacher = teachers.add("Jane", "Doe", "CompSci")
    assert teacher.department == "CompSci"


def test_dept_setter():
    teachers = Teachers()
    teacher = teachers.add("Jane", "Doe", "CompSci")
    teacher.department = "Mathematics"
    assert teacher.department == "Mathematics"


def test_firstname_getter():
    teachers = Teachers()
    teacher = teachers.add("Jane", "Doe", "CompSci")
    assert teacher.firstname == "Jane"


def test_lastname_getter():
    teachers = Teachers()
    teacher = teachers.add("Jane", "Doe", "CompSci")
    assert teacher.lastname == "Doe"


def test_release_setter_getter():
    teachers = Teachers()
    teacher = teachers.add("Jane", "Doe", "CompSci")
    teacher.release = 11.3
    assert teacher.release == 11.3


def test_string_representation_short():
    teachers = Teachers()
    teacher = teachers.add("Jane", "Doe", "CompSci")
    assert str(teacher) == f"{teacher.firstname} {teacher.lastname}"


def test_firstname_setter_good():
    """Verifies that firstname setter can set a valid first name."""
    teachers = Teachers()
    teach = teachers.add("John", "Smith")
    new_f_name = "Bob"
    teach.firstname = new_f_name
    assert new_f_name == teach.firstname


def test_firstname_setter_with_spaces():
    """Verifies that firstname setter can set a valid first name which has spaces."""
    teachers = Teachers()
    teach = teachers.add("John", "Smith")
    new_f_name = "Bob Blue"
    teach.firstname = new_f_name
    assert new_f_name == teach.firstname


def test_firstname_setter_bad():
    """Verifies that firstname setter doesn't change for invalid input (empty strings)."""
    teachers = Teachers()
    teach = teachers.add("John", "Smith")
    bad_name = " "
    teach.bad_name = bad_name
    assert teach.firstname == "John"


def test_lastname_setter_good():
    """Verifies that the lastname setter can set a valid (non-empty) last name for the Teacher."""
    teachers = Teachers()
    teach = teachers.add("John", "Smith")
    new_l_name = "Forstinger"
    teach.lastname = new_l_name
    assert new_l_name == teach.lastname


def test_lastname_setter_with_spaces():
    """Verifies that the lastname setter can set a valid (non-empty) last name (with spaces) for the Teacher."""
    teachers = Teachers()
    teach = teachers.add("John", "Smith")
    new_l_name = "Forstinger Blue"
    teach.lastname = new_l_name
    assert new_l_name == teach.lastname


def test_lastname_setter_bad():
    """Verifies that the lastname setter doesn't change if invalid input (
    empty strings). """
    teachers = Teachers()
    teach = teachers.add("John", "Smith")
    bad_name = " "
    teach.lastname = bad_name
    assert teach.lastname == "Smith"


# ============================================================================
# Collection
# ============================================================================
def test_id():
    """Verifies that the id property works as intended."""
    teachers = Teachers()
    teacher = teachers.add("Jane", "Doe")
    old_id = teacher.id
    teacher = teachers.add("Jane", "Doe")
    assert teacher.id == old_id + 1


def test_id_with_id_given():
    """Verifies that the id property works as intended."""
    existing_id = 112
    teachers = Teachers()
    teacher1 = teachers.add("Jane", "Doe", teacher_id=existing_id)
    assert teacher1.id == existing_id
    teacher1 = teachers.add("Jane", "Doe", teacher_id=existing_id - 5)
    assert teacher1.id == existing_id - 5
    teacher2 = teachers.add("Jane", "Doe")
    assert teacher2.id == existing_id + 1
    teacher3 = teachers.add("Jane", "Doe")
    assert teacher3.id == existing_id + 2
    teacher4 = teachers.add("Jane", "Doe")
    assert teacher4.id == existing_id + 3


def test_clear_removes_all_labs():
    """verify that clear works as expected"""
    teachers = Teachers()
    teachers.add("Jane", "Doe")
    teachers.add("Jane", "Doe")
    teachers.clear()
    all_teachers = teachers.get_all()
    assert len(all_teachers) == 0


def test_get_all():
    """Verifies that get_all() returns a tuple of all extant Lab objects."""
    teachers = Teachers()
    teacher1 = teachers.add("R-101", "Worst place in the world")
    teacher2 = teachers.add("R-102", "Second-worst place in the world")
    all_teachers = teachers.get_all()
    assert len(all_teachers) == 2 and teacher1 in all_teachers and teacher2 in all_teachers


def test_get_all_is_empty():
    """Verifies that get_all() returns an empty tuple if no Labs have been created."""
    teachers = Teachers()
    all_teachers = teachers.get_all()
    assert len(all_teachers) == 0


def test_remove():
    """Verifies that the remove() method works as intended."""
    teachers = Teachers()
    teacher1 = teachers.add("Jane", "Doe")
    teachers.add("Jane", "Doe")
    teachers.remove(teacher1)
    all_teachers = teachers.get_all()
    assert len(all_teachers) == 1 and teacher1 not in all_teachers


def test_get_by_id_good():
    """Verifies that get_by_id() returns the first Lab matches the id."""
    teachers = Teachers()
    teacher1 = teachers.add("Jane", "Doe", teacher_id=11)
    teacher2 = teachers.add("Jane", "Doe", teacher_id=14)
    assert teachers.get_by_id(teacher1.id) == teacher1
    assert teacher1.id == 11
    assert teachers.get_by_id(teacher2.id) == teacher2
    assert teacher2.id == 14


def test_get_by_id_not_valid():
    teachers = Teachers()
    teachers.add("Jane", "Doe", teacher_id=11)
    teachers.add("Jane", "Doe", teacher_id=14)
    assert teachers.get_by_id(666) is None


def test_get_by_id_on_empty_list():
    teachers = Teachers()
    assert teachers.get_by_id(666) is None


def test_get_by_name_good():
    """Verifies that the get_by_name() method returns the first Teacher matching the
    passed names. """
    teachers = Teachers()
    f_name = "John"
    l_name = "Smith"
    teachers.add(f_name, "Smythe")
    teachers.add("Jane", l_name)
    teachers.add("Jane", "Doe")
    teach_4 = teachers.add(f_name, l_name)
    teachers.add(f_name, "Doe")
    assert teachers.get_by_name(f_name, l_name) == teach_4


def test_get_by_name_bad():
    """Verifies that get_by_name() returns None if no teacher matching both names is found."""
    teachers = Teachers()
    f_name = "John"
    l_name = "Smith"
    teachers.add(f_name, "Smythe")
    teachers.add("Jane", l_name)
    teachers.add("Jane", "Doe")
    teachers.add(f_name, "Doe")
    assert teachers.get_by_name(f_name, l_name) is None


def test_get_by_name_missing_name():
    """Verifies that get_by_name() returns None if one of the names is left blank."""
    teachers = Teachers()
    f_name = "John"
    l_name = "Smith"
    teachers.add(f_name, "Smythe")
    teachers.add("Jane", l_name)
    teachers.add("Jane", "Doe")
    teachers.add(f_name, l_name)
    teachers.add(f_name, "Doe")
    bad_name = ""
    assert teachers.get_by_name(f_name, bad_name) is None
