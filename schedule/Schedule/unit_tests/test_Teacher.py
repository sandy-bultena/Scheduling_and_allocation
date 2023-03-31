import pytest

import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__)))

from ..Teacher import Teacher
from ..Block import Block
from ..database.PonyDatabaseConnection import define_database, Teacher as dbTeacher
from pony.orm import *
from .db_constants import *

db: Database


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    global db
    db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)
    yield
    db.drop_all_tables(with_all_data=True)
    db.disconnect()
    db.provider = db.schema = None


@pytest.fixture(autouse=True)
def before_and_after():
    db.create_tables()
    yield
    db.drop_table(table_name='time_slot', if_exists=True, with_all_data=True)
    db.drop_table(table_name='block', if_exists=True, with_all_data=True)
    db.drop_table(table_name='teacher', if_exists=True, with_all_data=True)


@db_session
def test_id():
    """"Verifies that Teacher IDs are incremented automatically."""
    teach = Teacher("John", "Smith")
    max_id = max(t.id for t in dbTeacher)  # this works
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


def test_string_representation():
    """Verifies that the str representation of this object returns a string containing the Teacher's full name."""
    f_name = "John"
    l_name = "Smith"
    teach = Teacher(f_name, l_name)
    assert f"{f_name} {l_name}" in str(teach)


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


def test_get_by_name_good():
    """Verifies that the static get_by_name() method returns the first Teacher matching the
    passed names. """
    Teacher._Teacher__instances = {}
    f_name = "John"
    l_name = "Smith"
    teach_1 = Teacher(f_name, "Smythe")
    teach_2 = Teacher("Jane", l_name)
    teach_3 = Teacher("Jane", "Doe")
    teach_4 = Teacher(f_name, l_name)
    teach_5 = Teacher(f_name, "Doe")
    assert Teacher.get_by_name(f_name, l_name) == teach_4


def test_get_by_name_bad():
    """Verifies that get_by_name() returns None if no teacher matching both names is found."""
    Teacher._Teacher__instances = {}
    f_name = "John"
    l_name = "Smith"
    teach_1 = Teacher(f_name, "Smythe")
    teach_2 = Teacher("Jane", l_name)
    teach_3 = Teacher("Jane", "Doe")
    teach_4 = Teacher("Jim", l_name)
    teach_5 = Teacher(f_name, "Doe")
    assert Teacher.get_by_name(f_name, l_name) is None


def test_get_by_name_missing_name():
    """Verifies that get_by_name() returns None if one of the names is left blank."""
    Teacher._Teacher__instances = {}
    f_name = "John"
    l_name = "Smith"
    teach_1 = Teacher(f_name, "Smythe")
    teach_2 = Teacher("Jane", l_name)
    teach_3 = Teacher("Jane", "Doe")
    teach_4 = Teacher(f_name, l_name)
    teach_5 = Teacher(f_name, "Doe")
    bad_name = ""
    assert Teacher.get_by_name(f_name, bad_name) is None


def test_delete():
    """Verifies that delete() method can remove a Teacher from the dict of instances."""
    Teacher._Teacher__instances = {}
    f_name = "John"
    l_name = "Smith"
    teach_1 = Teacher(f_name, "Smythe")
    teach_2 = Teacher("Jane", l_name)
    teach_3 = Teacher("Jane", "Doe")
    teach_4 = Teacher(f_name, l_name)
    teach_5 = Teacher(f_name, "Doe")
    teach_1.delete()
    teachers = Teacher.list()
    assert len(teachers) == 4 and teach_1 not in teachers


@db_session
def test_delete_updates_database():
    """Verifies that delete() removes the Teacher's corresponding database record."""
    teach = Teacher("John", "Smith")
    teach.delete()
    commit()
    d_teachers = select(t for t in dbTeacher)
    assert len(d_teachers) == 0


@db_session
def test_remove_ignores_database():
    """Verifies that remove() doesn't affect the Teacher's corresponding database record."""
    Teacher.reset()
    teach = Teacher("John", "Smith")
    teach.remove()
    commit()
    d_teachers = select(t for t in dbTeacher)
    teachers = list(d_teachers)
    a_teachers = Teacher.list()
    assert len(teachers) == 1 and teachers[0].first_name == teach.firstname and teachers[0].last_name == teach.lastname and len(a_teachers) == 0


def test_disjoint_true():
    """Verifies that the static disjoint() method returns True if both sets of Teachers nave no
    Teachers in common. """
    f_name = "John"
    l_name = "Smith"
    teach_1 = Teacher(f_name, "Smythe")
    teach_2 = Teacher("Jane", l_name)
    teach_3 = Teacher("Jane", "Doe")
    teach_4 = Teacher(f_name, l_name)
    set_1 = [teach_1, teach_2]
    set_2 = [teach_3, teach_4]
    assert Teacher.disjoint(set_1, set_2) is True


def test_disjoint_false():
    """Verifies that disjoint() returns false if the sets have any common Teachers."""
    f_name = "John"
    l_name = "Smith"
    teach_1 = Teacher(f_name, "Smythe")
    teach_2 = Teacher("Jane", l_name)
    teach_3 = Teacher("Jane", "Doe")
    set_1 = [teach_1, teach_2]
    set_2 = [teach_2, teach_3]
    assert Teacher.disjoint(set_1, set_2) is False


@db_session
def test_save():
    teach = Teacher("John", "Smith")
    flush()
    teach.dept = "Social Studies"
    d_teach = teach.save()
    assert d_teach.dept == teach.dept
