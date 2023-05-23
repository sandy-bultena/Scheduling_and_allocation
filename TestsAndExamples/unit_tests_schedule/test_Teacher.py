import pytest

import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))

from schedule.Schedule.Teachers import Teacher
import schedule.Schedule.Teachers as Teachers


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    pass


@pytest.fixture(autouse=True)
def before_and_after():
    Teachers.clear_all()


def test_clear_all_removes_all_labs():
    """verify that clear_all works as expected"""
    Teacher("R-101", "Worst place in the world")
    Teacher("R-102", "Second-worst place in the world")
    Teachers.clear_all()
    all_teachers = Teachers.get_all()
    assert len(all_teachers) == 0


def test_id():
    """Verifies that the id property works as intended."""
    teacher = Teacher("Jane", "Doe")
    old_id = teacher.id
    teacher = Teacher("Jane", "Doe")
    assert teacher.id == old_id + 1


def test_id_with_id_given():
    """Verifies that the id property works as intended."""

    existing_id = 12
    teacher1 = Teacher("Jane", "Doe", teacher_id=existing_id)
    assert teacher1.id == existing_id
    teacher2 = Teacher("Jane", "Doe")
    assert teacher2.id == existing_id + 1
    teacher3 = Teacher("Jane", "Doe", teacher_id=existing_id - 5)
    assert teacher3.id == existing_id - 5
    teacher4 = Teacher("Jane", "Doe")
    assert teacher4.id == teacher2.id + 1


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


def test_firstname_setter_with_spaces():
    """Verifies that firstname setter can set a valid first name which has spaces."""
    teach = Teacher("John", "Smith")
    new_f_name = "Bob Blue"
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


def test_lastname_setter_with_spaces():
    """Verifies that the lastname setter can set a valid (non-empty) last name (with spaces) for the Teacher."""
    teach = Teacher("John", "Smith")
    new_l_name = "Forstinger Blue"
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


def test_string_representation():
    """Verifies that the str representation of this object returns a string containing the Teacher's full name."""
    f_name = "John"
    l_name = "Smith"
    teach = Teacher(f_name, l_name)
    assert f"{f_name} {l_name}" in str(teach)


def test_get_bad_id():
    """Verifies that get_by_id() returns None when receiving an invalid ID."""
    Teacher("John", "Smith")
    bad_id = 666
    assert Teachers.get_by_id(bad_id) is None


def test_get_by_name_good():
    """Verifies that the get_by_name() method returns the first Teacher matching the
    passed names. """
    f_name = "John"
    l_name = "Smith"
    Teacher(f_name, "Smythe")
    Teacher("Jane", l_name)
    Teacher("Jane", "Doe")
    teach_4 = Teacher(f_name, l_name)
    Teacher(f_name, "Doe")
    assert Teachers.get_by_name(f_name, l_name) == teach_4


def test_get_by_name_bad():
    """Verifies that get_by_name() returns None if no teacher matching both names is found."""
    f_name = "John"
    l_name = "Smith"
    Teacher(f_name, "Smythe")
    Teacher("Jane", l_name)
    Teacher("Jane", "Doe")
    Teacher("Jim", l_name)
    Teacher(f_name, "Doe")
    assert Teachers.get_by_name(f_name, l_name) is None


def test_get_by_name_missing_name():
    """Verifies that get_by_name() returns None if one of the names is left blank."""
    f_name = "John"
    l_name = "Smith"
    Teacher(f_name, "Smythe")
    Teacher("Jane", l_name)
    Teacher("Jane", "Doe")
    Teacher(f_name, l_name)
    Teacher(f_name, "Doe")
    bad_name = ""
    assert Teachers.get_by_name(f_name, bad_name) is None


def test_remove():
    """Verifies that delete() method can remove a Teacher from the list of teacher instances"""
    Teacher._Teacher__instances = {}
    f_name = "John"
    l_name = "Smith"
    teach_1 = Teacher(f_name, "Smythe")
    Teacher("Jane", l_name)
    Teacher("Jane", "Doe")
    Teacher(f_name, l_name)
    Teacher(f_name, "Doe")
    teach_1.remove()
    teachers = Teachers.get_all()
    assert len(teachers) == 4 and teach_1 not in teachers
