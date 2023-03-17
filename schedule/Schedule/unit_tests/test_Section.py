import sys
from os import path
import re

sys.path.append(path.dirname(path.dirname(__file__)))
import pytest
from unit_tests.db_constants import *
from database.PonyDatabaseConnection import define_database, Schedule as dbSchedule, Scenario as dbScenario, \
    Section as dbSection
from pony.orm import *

from Section import Section
from Course import Course
from Block import Block
from Lab import Lab
from Teacher import Teacher
from Stream import Stream

db: Database


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    global db
    db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)
    init_scenario_and_schedule()
    yield
    db.drop_all_tables(with_all_data=True)
    db.disconnect()
    db.provider = db.schema = None


@db_session
def init_scenario_and_schedule():
    sc = dbScenario()
    flush()
    s = dbSchedule(semester="Winter 2023", official=False, scenario_id=sc.id)


@pytest.fixture(autouse=True)
def before_and_after():
    db.create_tables()
    Section.reset()
    Block.reset()
    yield
    db.drop_table(table_name='section', if_exists=True, with_all_data=True)
    db.drop_table(table_name='block', if_exists=True, with_all_data=True)
    db.drop_table(table_name='time_slot', if_exists=True, with_all_data=True)


# region General & Properties
def test_constructor_default_values():
    """Checks that the constructor uses default values"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    assert isinstance(s.number, str)
    assert s.hours
    assert isinstance(s.name, str)

def test_create_no_schedule_id():
    """Checks that a section cannot be created without a schedule or section ID"""
    with pytest.raises(ValueError) as e:
        s = Section(course=Course())
    assert "id or schedule_id must be defined" in str(e.value).lower()



def test_section_created_success():
    """Checks that Section is created correctly"""
    number = "3A"
    hours = 2
    name = "My Section"
    c = Course()
    s = Section(number, hours, name, c, schedule_id=1)
    assert s.name == name
    assert s.hours == hours
    assert s.number == number


def test_section_is_added_to_collection():
    """Checks that newly created Section is added to the collection"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    assert s in Section.list()


def test_set_hours_valid():
    """Checks that valid hours can be set"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    hours = 2
    s.hours = hours
    assert s.hours == hours


def test_set_hours_invalid():
    """Checks that invalid hours can't be set"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    hours = "string"
    with pytest.raises(TypeError) as e:
        s.hours = hours
    assert "must be a number" in str(e.value).lower()
    assert s.hours != hours

    hours = -10
    with pytest.raises(TypeError) as e:
        s.hours = hours
    assert "must be larger than 0" in str(e.value).lower()
    assert s.hours != hours


def test_get_title():
    """Checks that title is retrievable and includes name or number"""
    name = "My Section"
    c = Course()
    assert name in Section(name=name, course=c, schedule_id=1).title

    number = "3A"
    assert number in Section(number=number, course=c, schedule_id=1).title


def test_set_course_valid():
    """Checks that valid courses can be set"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    c2 = Course("1")
    s.course = c2
    assert s.course is c2


def test_set_course_invalid():
    """Checks that invalid courses can't be set"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    c2 = 1
    with pytest.raises(TypeError) as e:
        s.course = c2
    assert "invalid course" in str(e.value).lower()


def test_set_num_students():
    """Checks that num_students can be set"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    num = 20
    s.num_students = num
    assert s.num_students == num


def test_hours_can_be_added():
    """Checks that hours can be added (rather than set)"""
    hours = 1
    to_add = 10
    c = Course()
    s = Section(hours=hours, course=c, schedule_id=1)
    s.add_hours(to_add)
    assert s.hours == hours + to_add


@db_session
def test_delete_deletes_all():
    """Checks that the delete method removes the Section and all Blocks from respective lists"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    id = s.id
    b1 = Block('Mon', '13:00', 2, 1)
    b2 = Block('Mon', '13:00', 2, 2)
    b3 = Block('Mon', '13:00', 2, 3)
    s.add_block(b1).add_block(b2).add_block(b3)
    s.delete()
    assert s not in Section.list()
    assert dbSection.get(id=id) is None
    assert b1 not in Block.list()
    assert b2 not in Block.list()
    assert b3 not in Block.list()


def test_is_conflicted_detects_conflicts_correctly():
    """Checks that the is_conflicted method correctly picks up conflicted blocks"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    b1 = Block('Mon', '13:00', 2, 1)
    b2 = Block('Mon', '13:00', 2, 2)
    b3 = Block('Mon', '13:00', 2, 3)
    s.add_block(b1).add_block(b2).add_block(b3)
    b1.conflicted = 1
    assert s.is_conflicted()


def test_is_conflicted_detects_ok_correctly():
    """Checks that the is_conflicted method doesn't return false positive"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    b1 = Block('Mon', '13:00', 2, 1)
    b2 = Block('Mon', '13:00', 2, 2)
    b3 = Block('Mon', '13:00', 2, 3)
    s.add_block(b1).add_block(b2).add_block(b3)
    assert not s.is_conflicted()


def test_get_new_number_gets_first():
    """Checks that the get_new_number method will get the lowest available block number, regardeless of add order or block id of existing blocks"""
    lowest = 4
    c = Course()
    s = Section(course=c, schedule_id=1)
    b1 = Block('Mon', '13:00', 2, 1)
    b2 = Block('Mon', '13:00', 2, 3)
    b3 = Block('Mon', '13:00', 2, 2)
    s.add_block(b1).add_block(b2).add_block(b3)
    assert s.get_new_number() == lowest


def test_get_new_number_no_blocks():
    """Checks that the get_new_number method will return 1 if there are no blocks in the section"""
    assert Section(course=Course(), schedule_id=1).get_new_number() == 1


def test_string_representation_with_valid_name():
    n = "10"
    s = Section(number=n, name="For students taking calculus", schedule_id=1, course=Course())
    assert re.search(f"{n}" + r".*?For students taking calculus", str(s))


def test_string_representation_with_invalid_name():
    n = "10"
    s = Section(number=n, name=f"Section {n}", schedule_id=1, course=Course())
    assert str(s) == f"Section {10}"


def test_string_representation_with_no_name():
    n = "10"
    s = Section(number=n, schedule_id=1, course=Course())
    assert str(s) == f"Section {10}"


@db_session
def test_save():
    c = Course()
    s = Section(course=c, schedule_id=1)
    flush()
    s.name = "Test Section"
    s.hours = 2.0
    s.num_students = 24
    d_sched = s.save(dbSchedule[1])
    assert d_sched.name == s.name and d_sched.hours == s.hours \
           and d_sched.num_students == s.num_students


# endregion

# region Block
def test_add_block_valid():
    """Checks that a valid block can be added"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    b = Block('Mon', '13:00', 2, 1)
    s.add_block(b)
    assert b in s.blocks


def test_add_block_invalid():
    """Checks that an invalid block can't be added"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    b = 12
    with pytest.raises(TypeError) as e:
        s.add_block(b)
    assert "invalid block" in str(e.value).lower()


def test_get_block_by_id_valid():
    """Checks that block can be retrieved by id"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    b = Block('Mon', '13:00', 2, 1)
    id = b.id
    s.add_block(b)
    assert s.get_block_by_id(id) is b


def test_get_block_by_id_invalid():
    """Checks that None is returned when get_block_by_id is passed unfound id"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    assert s.get_block_by_id(-1) is None


def test_get_block_valid():
    """Checks that block can be retrieved by number"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    num = 10
    b = Block('Mon', '13:00', 2, num)
    s.add_block(b)
    assert s.get_block(num) is b


def test_get_block_invalid():
    """Checks that None is returned when get_block is passed unfound number"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    assert s.get_block(-1) is None


def test_remove_block_valid():
    """Checks that when passed a valid block, it will be removed & deleted"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    b = Block('Mon', '13:00', 2, 1)
    s.add_block(b)
    s.remove_block(b)
    assert b not in s.blocks
    assert b not in Block.list()  # make sure block.delete is called


def test_remove_block_invalid():
    """Checks that error is thrown when remove_block is passed non-Block object"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    with pytest.raises(TypeError) as e:
        s.remove_block(1)
    assert "invalid block" in str(e.value).lower()


def test_remove_block_not_there():
    """Checks that when passed not-included block, it will still be deleted"""
    b = Block('Mon', '13:00', 2, 1)
    c = Course()
    Section(course=c, schedule_id=1).remove_block(b)
    assert b not in Block.list()


def test_hours_auto_calc_when_blocks_are_present():
    """Checks that if the section has blocks, hours will be auto-calculated"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    dur = 2
    b1 = Block('Mon', '13:00', dur, 1)
    b2 = Block('Mon', '13:00', dur, 2)
    s.add_block(b1).add_block(b2)
    s.hours = dur
    assert s.hours == (dur * 2)


# endregion

# region Lab

def test_assign_lab_valid():
    """Checks that a valid lab can be added"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    b = Block('Mon', '13:00', 2, 1)
    l = Lab()
    s.add_block(b)
    s.assign_lab(l)
    assert l in s.labs


# don't check for invalid, since verification is done in Block.assign_lab

def test_remove_lab_valid():
    """Checks that when passed a valid lab, it will be removed & deleted"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    b = Block('Mon', '13:00', 2, 1)
    l = Lab()
    s.add_block(b)
    s.assign_lab(l)
    s.remove_lab(l)
    assert l not in s.labs


# don't check for invalid, since verification is done in Block.remove_lab

def test_remove_lab_not_there():
    """Checks that when passed not-included lab, it will still be 'removed' """
    c = Course()
    s = Section(course=c, schedule_id=1)
    b = Block('Mon', '13:00', 2, 1)
    l = Lab()
    s.add_block(b)
    s.remove_lab(l)
    assert l not in s.labs


# endregion

# region Teacher

def test_assign_teacher_valid():
    """Checks that a valid teacher can be added"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    t = Teacher("Jane", "Doe")
    s.assign_teacher(t)
    assert t in s.teachers
    assert s.allocated_hours == s.hours


def test_assign_teacher_invalid():
    """Checks that an invalid teacher can't be added"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    with pytest.raises(TypeError) as e:
        s.assign_teacher(12)
    assert "invalid teacher" in str(e.value).lower()


def test_set_teacher_allocation_valid():
    """Checks that valid hours can be set to valid teacher"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    t = Teacher("Jane", "Doe")
    hours = 12
    s.assign_teacher(t)
    s.set_teacher_allocation(t, hours)
    assert s._allocation[t.id] == hours


def test_set_teacher_allocation_new_teacher():
    """Checks that valid hours can be set to new teacher teacher"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    t = Teacher("Jane", "Doe")
    hours = 12
    s.set_teacher_allocation(t, hours)
    assert s._allocation[t.id] == hours
    assert s.has_teacher(t)


def test_set_teacher_allocation_zero_hours():
    """Checks that assigning 0 hours to teacher will remove that teacher"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    t = Teacher("Jane", "Doe")
    s.assign_teacher(t)
    s.set_teacher_allocation(t, 0)
    assert t.id not in s._allocation
    assert not s.has_teacher(t)


def test_get_teacher_allocation_valid():
    """Checks that get_teacher_allocation returns the correct allocation hours"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    t = Teacher("Jane", "Doe")
    hours = 12
    s.assign_teacher(t)
    s.set_teacher_allocation(t, hours)
    assert s.get_teacher_allocation(t) == hours


def test_get_teacher_allocation_not_teaching():
    """Checks that get_teacher_allocation returns the correct allocation hours"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    t = Teacher("Jane", "Doe")
    assert s.get_teacher_allocation(t) == 0


def test_has_teacher_valid():
    """Checks has_teacher returns True if teacher is included"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    t = Teacher("Jane", "Doe")
    s.assign_teacher(t)
    assert s.has_teacher(t)


def test_has_teacher_not_found():
    """Checks has_teacher returns False if teacher is not included"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    t = Teacher("Jane", "Doe")
    assert not s.has_teacher(t)


def test_has_teacher_invalid():
    """Checks has_teacher returns False if non-Teacher is given"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    with pytest.raises(TypeError) as e:
        s.has_teacher(12)
    assert "invalid teacher" in str(e.value).lower()


def test_remove_teacher_valid():
    """Checks that when passed a valid teacher, it will be removed & allocation will be deleted"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    t = Teacher("Jane", "Doe")
    s.assign_teacher(t)
    s.remove_teacher(t)
    assert t not in s.teachers
    assert t.id not in s._allocation


def test_remove_teacher_invalid():
    """Checks that error is thrown when remove_teacher is passed non-Teacher object"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    with pytest.raises(TypeError) as e:
        s.remove_teacher(1)
    assert "invalid teacher" in str(e.value).lower()


def test_remove_teacher_not_there():
    """Checks that when passed not-included teacher, it will still be 'removed' """
    c = Course()
    s = Section(course=c, schedule_id=1)
    t = Teacher("Jane", "Doe")
    s.remove_teacher(t)
    assert t not in s.teachers
    assert t.id not in s._allocation


def test_remove_all_deletes_all_teachers():
    """Checks that remove_all_teachers will correctly delete them all"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    s.assign_teacher(Teacher("Jane", "Doe"))
    s.assign_teacher(Teacher("John", "Doe"))
    s.assign_teacher(Teacher("1", "2"))
    s.remove_all_teachers()
    assert not s.teachers
    assert not s._allocation


# endregion

# region Stream

def test_assign_stream_valid():
    """Checks that a valid stream can be added"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    st = Stream()
    s.assign_stream(st)
    assert st in s.streams


def test_assign_stream_invalid():
    """Checks that an invalid stream can't be added"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    with pytest.raises(TypeError) as e:
        s.assign_stream(12)
    assert "invalid stream" in str(e.value).lower()


def test_has_stream_valid():
    """Checks has_stream returns True if stream is included"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    st = Stream()
    s.assign_stream(st)
    assert s.has_stream(st)


def test_has_stream_not_found():
    """Checks has_stream returns False if stream is not included"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    st = Stream()
    assert not s.has_stream(st)


def test_has_stream_invalid():
    """Checks has_stream returns False if non-Stream is given"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    with pytest.raises(TypeError) as e:
        s.has_stream(12)
    assert "invalid stream" in str(e.value).lower()


def test_remove_stream_valid():
    """Checks that when passed a valid stream, it will be removed & allocation will be deleted"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    st = Stream()
    s.assign_stream(st)
    s.remove_stream(st)
    assert st not in s.streams


def test_remove_stream_invalid():
    """Checks that error is thrown when remove_stream is passed non-Stream object"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    with pytest.raises(TypeError) as e:
        s.remove_stream(1)
    assert "invalid stream" in str(e.value).lower()


def test_remove_stream_not_there():
    """Checks that when passed not-included stream, it will still be 'removed' """
    c = Course()
    s = Section(course=c, schedule_id=1)
    st = Stream()
    s.remove_stream(st)
    assert s not in s.streams


def test_remove_all_deletes_all_streams():
    """Checks that remove_all_streams will correctly delete them all"""
    c = Course()
    s = Section(course=c, schedule_id=1)
    s.assign_stream(Stream())
    s.assign_stream(Stream())
    s.assign_stream(Stream())
    s.remove_all_streams()
    assert not s.streams

# endregion
