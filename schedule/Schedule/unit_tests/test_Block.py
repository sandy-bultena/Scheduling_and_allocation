import pytest
import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__)))

from Block import Block
from Section import Section
from Lab import Lab
from Teacher import Teacher
from Time_slot import TimeSlot
from pony.orm import *
from database.PonyDatabaseConnection import define_database, Block as dbBlock, \
    TimeSlot as dbTimeSlot, Lab as dbLab, Teacher as dbTeacher, Scenario as dbScenario, \
    Schedule as dbSchedule, Course as dbCourse, Section as dbSection
from unit_tests.db_constants import *
from ScheduleEnums import WeekDay

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
def run_before():
    db.create_tables()
    yield
    db.drop_all_tables(with_all_data=True)
    # db.drop_table(table_name='lab', if_exists=True, with_all_data=True)
    # db.drop_table(table_name='block', if_exists=True, with_all_data=True)
    # db.drop_table(table_name='time_slot', if_exists=True, with_all_data=True)
    # db.drop_table(table_name='section', if_exists=True, with_all_data=True)
    # db.drop_table(table_name='teacher', if_exists=True, with_all_data=True)
    # db.drop_table(table_name='course', if_exists=True, with_all_data=True)
    # The code below prevents us from getting a BindingError when this function is called
    # after the first test. Makes the test suite run really slow, but at least it ensures
    # that all the tests pass. Based on a solution found here:
    # https://github.com/ponyorm/pony/issues/214#issuecomment-787452937
    # self.db.disconnect()
    # self.db.provider = None
    # self.db.schema = None


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
    """Verifies that the delete() method successfully destroys an instance of a Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    block.delete()
    assert block not in Block.list()


def test_delete_gets_underlying_time_slot():
    """Verifies that the delete() method destroys the Block's underlying TimeSlot as well."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    block.delete()
    assert block not in TimeSlot.list()


@db_session
def test_delete_removes_block_from_database():
    """Verifies that the delete() method removes the Block's corresponding record in the
    database. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    block.delete()
    commit()  # necessary to ensure that the Block actually gets deleted in this test.
    d_blocks = select(b for b in dbBlock)
    d_slots = select(t for t in dbTimeSlot)
    assert len(d_blocks) == 0 and len(d_slots) == 0


def test_start_getter():
    """Verifies that the start getter works as intended. Same as TimeSlot.start getter."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    assert block.start == start


def test_start_setter_synced_2_blocks():
    """Verifies that the start setter works as intended, and that it changes the start value of any Blocks synced to
    the Block on which it was called. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block1 = Block(day, start, dur, num)
    block2 = Block("wed", start, dur, 2)
    block1.sync_block(block2)
    block2.sync_block(block1)
    new_start = "10:00"
    block1.start = new_start
    assert block2.start == new_start


def test_start_setter_synced_4_blocks():
    """Same as previous test, but with 4 blocks instead of 2."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block1 = Block(day, start, dur, num)
    block2 = Block("wed", start, dur, 2)
    block3 = Block("thu", start, dur, 3)
    block4 = Block("fri", start, dur, 4)
    block1.sync_block(block2)
    block1.sync_block(block3)
    block1.sync_block(block4)
    block2.sync_block(block1)
    block2.sync_block(block3)
    block2.sync_block(block4)
    block3.sync_block(block1)
    block3.sync_block(block2)
    block3.sync_block(block4)
    block4.sync_block(block1)
    block4.sync_block(block2)
    block4.sync_block(block3)

    new_start = "10:00"
    block1.start = new_start
    assert block2.start == new_start and block3.start == new_start and block4.start == new_start


def test_day_getter():
    """Verifies that the day getter works as intended. Same as in TimeSlot."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block1 = Block(day, start, dur, num)
    assert block1.day == day


def test_day():
    """Verifies that the day setter works as intended, changing the day property of any Block synced to the current
    Block. """
    day = "mon"
    start1 = "8:00"
    start2 = "12:00"
    dur = 2
    num1 = 1
    num2 = 2
    block1 = Block(day, start1, dur, num1)
    block2 = Block(day, start2, dur, num2)
    block1.sync_block(block2)
    block2.sync_block(block1)
    block1.day = "thu"
    assert block2.day == "thu"


def test_id():
    """Verifies that the id property works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    assert block.id == 1


def test_section_getter():
    """Verifies that the section getter works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    """Since sections are not assigned to Blocks at initialization, the value of section will 
    be None. """
    assert block.section is None


def test_section_setter_good():
    """Verifies that the section setter can set a valid section."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    sect = Section(id=1)
    block.section = sect
    assert block.section == sect


def test_section_setter_bad():
    """Verifies that the section setter throws a TypeError when receiving a value that isn't
    a Section. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    bad_sect = {
        "foo": "foo",
        "bar": "bar"
    }
    with pytest.raises(TypeError) as e:
        block.section = bad_sect
    assert "invalid section" in str(e.value).lower()


@db_session
def test_section_setter_updates_database():
    """Verifies that the section setter updates the database when it receives a Section
    containing a valid Schedule ID. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)

    d_scenario = dbScenario(name="Test")
    flush()
    d_schedule = dbSchedule(semester="fall", official=False, scenario_id=d_scenario.id)
    flush()
    d_course = dbCourse(name="Test")
    flush()
    sect = Section(course=d_course, schedule_id=d_schedule.id)
    commit()
    block.section = sect
    commit()
    d_block = dbBlock[block.id]
    d_sect = dbSection[sect.id]
    # Note that section_id is NOT an integer; it's an object reference to a Section entity.
    assert d_block.section_id == d_sect


def test_assign_lab_good():
    """Verifies that the assign_lab method can assign a valid Lab object to the Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    lab = Lab()
    block.assign_lab(lab)
    assert getattr(block, '_labs', {})[lab.id] == lab


def test_assign_lab_bad():
    """Verifies that assign_lab() will reject an input that isn't a Lab object."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    bad_lab = "baz"
    with pytest.raises(TypeError) as e:
        block.assign_lab(bad_lab)
    assert "invalid lab" in str(e.value).lower()


@db_session
def test_assign_lab_updates_database():
    """Verifies that _assign_lab() connects the Block's corresponding database entity to that of
    the passed Lab. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    lab = Lab()
    block.assign_lab(lab)
    commit()
    d_block = dbBlock[1]
    d_lab = dbLab[1]
    assert len(d_block.labs) == 1 and len(d_lab.blocks) == 1 and d_lab in d_block.labs \
           and d_block in d_lab.blocks


def test_remove_lab_good():
    """Verifies that remove_lab() can successfully remove a valid Lab object from this Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    lab = Lab()
    block.assign_lab(lab)
    block.remove_lab(lab)
    assert lab not in getattr(block, '_labs').values()


def test_remove_lab_bad():
    """Verifies that remove_lab() throws an exception if asked to remove something that isn't
    a Lab from this Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    lab = Lab()
    block.assign_lab(lab)
    bad_lab = "tesla"
    with pytest.raises(TypeError) as e:
        block.remove_lab(bad_lab)
    assert "invalid lab" in str(e.value).lower()


def test_remove_lab_no_crash():
    """Verifies that remove_lab won't crash the program if the Block doesn't contain
    the specified valid Lab. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    lab = Lab()
    block.assign_lab(lab)
    other_lab = Lab("R-101", "dummy")
    block.remove_lab(other_lab)
    assert lab in getattr(block, "_labs").values()


@db_session
def test_remove_lab_affects_database():
    """Verifies that remove_lab() breaks the connection between an entity Block and an entity
    Lab, without destroying their records in the database. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    lab = Lab()
    block.assign_lab(lab)
    block.remove_lab(lab)
    commit()
    d_block = dbBlock[block.id]
    d_lab = dbLab[lab.id]
    assert d_block not in d_lab.blocks and d_lab not in d_block.labs


def test_remove_all_labs():
    """Verifies that remove_all_labs works as intended, removing all Labs from the current
    Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    this_lab = Lab("R-100", "the second-worst place in the world")
    other_lab = Lab("R-101", "the worst place in the world")
    block.assign_lab(this_lab)
    block.assign_lab(other_lab)
    block.remove_all_labs()
    assert len(getattr(block, '_labs')) == 0


def test_labs():
    """Verifies that labs() returns a list of all Lab objects assigned to this Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    this_lab = Lab("R-100", "the second-worst place in the world")
    other_lab = Lab("R-101", "the worst place in the world")
    block.assign_lab(this_lab)
    block.assign_lab(other_lab)
    labs = block.labs()
    assert len(labs) == 2 and labs[0] == this_lab and labs[1] == other_lab


def test_labs_empty():
    """Verifies that labs() returns an empty list if called while no Labs are assigned to the
    Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    labs = block.labs()
    assert len(labs) == 0


def test_has_lab_good():
    """Verifies that has_lab() returns true when the specified Lab is assigned to this Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    lab = Lab()
    block.assign_lab(lab)
    assert block.has_lab(lab)


def test_has_lab_false():
    """"Verifies that has_lab() returns false when the Lab isn't assigned to this Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    lab = Lab()
    assert block.has_lab(lab) is False


def test_has_lab_bad_input():
    """Verifies that has_lab() returns false when checking for something that isn't a Lab."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    lab = Lab()
    block.assign_lab(lab)
    bad_lab = "nonce"
    assert block.has_lab(bad_lab) is False


def test_assign_teacher_good():
    """Verifies that the assign_teacher() method works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    teach = Teacher("John", "Smith")
    block.assign_teacher(teach)
    assert getattr(block, '_teachers')[teach.id] == teach


def test_assign_teacher_bad():
    """Verifies that assign_teacher() throws an exception for bad input."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    bad_teach = "foo"
    with pytest.raises(TypeError) as e:
        block.assign_teacher(bad_teach)
    assert "invalid teacher" in str(e.value).lower()


@db_session
def test_assign_teacher_updates_database():
    """Verifies that assign_teacher() connects this Block's corresponding entity to the Teacher's
    corresponding entity."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    teach = Teacher("John", "Smith")
    block.assign_teacher(teach)
    commit()
    d_block = dbBlock[block.id]
    d_teach = dbTeacher[teach.id]
    assert d_teach in d_block.teachers and d_block in d_teach.blocks


def test_remove_teacher_good():
    """Verifies that remove_teacher() works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    teach = Teacher("John", "Smith")
    block.assign_teacher(teach)
    block.remove_teacher(teach)
    assert len(getattr(block, '_teachers')) == 0


def test_remove_teacher_bad():
    """Verifies that remove_teacher() throws an exception when trying to remove something
    that isn't a Teacher object. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    teach = Teacher("John", "Smith")
    block.assign_teacher(teach)
    bad_teach = "foo"
    with pytest.raises(TypeError) as e:
        block.remove_teacher(bad_teach)
    assert "invalid teacher" in str(e.value).lower()


def test_remove_teacher_no_crash():
    """Verifies that remove_teacher() doesn't crash the program when attempting to remove a
    Teacher that isn't assigned to this Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    teach = Teacher("John", "Smith")
    block.assign_teacher(teach)
    other_teach = Teacher("Jane", "Doe")
    block.remove_teacher(other_teach)
    assert len(getattr(block, '_teachers')) == 1 and getattr(block, '_teachers')[
        teach.id] == teach


@db_session
def test_remove_teacher_updates_database():
    """Verifies that remove_teacher() breaks the connection between the records for this Block
    and the Teacher in the database, without deleting said records. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    teach = Teacher("John", "Smith")
    block.assign_teacher(teach)
    block.remove_teacher(teach)
    commit()
    d_block = dbBlock[block.id]
    d_teach = dbTeacher[teach.id]
    assert d_block not in d_teach.blocks and d_teach not in d_block.teachers


def test_remove_all_teachers():
    """Verifies that remove_all_teachers() works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    teach = Teacher("John", "Smith")
    other_teach = Teacher("Jane", "Doe")
    block.assign_teacher(teach)
    block.assign_teacher(other_teach)
    block.remove_all_teachers()
    assert len(getattr(block, '_teachers')) == 0


def test_remove_all_teachers_no_crash():
    """Verifies that remove_all_teachers() won't crash the program when no teachers have been
    assigned yet. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    block.remove_all_teachers()
    assert len(getattr(block, '_teachers')) == 0


def test_teachers():
    """Verifies that teachers() returns a list of all the Teachers assigned to this Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    teach = Teacher("John", "Smith")
    other_teach = Teacher("Jane", "Doe")
    block.assign_teacher(teach)
    block.assign_teacher(other_teach)
    teachers = block.teachers()
    assert len(teachers) == 2 and teach in teachers and other_teach in teachers


def test_teachers_empty_list():
    """Verifies that teachers() will return an empty list if no Teachers are assigned to this
    Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    teachers = block.teachers()
    assert len(teachers) == 0


def test_has_teacher_true():
    """Verifies that has_teacher() returns true when the specified Teacher has been assigned
    to this Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    teach = Teacher("John", "Smith")
    block.assign_teacher(teach)
    assert block.has_teacher(teach)


def test_has_teach_false():
    """Verifies that has_teacher returns false when the specified Teacher isn't assigned to
    this Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    teach = Teacher("John", "Smith")
    block.assign_teacher(teach)
    other_teach = Teacher("Jane", "Doe")
    assert block.has_teacher(other_teach) is False


def test_has_teach_bad_input():
    """Verifies that has_teacher() returns false when passed something that isn't a Teacher
    object. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    teach = Teacher("John", "Smith")
    block.assign_teacher(teach)
    bad_teach = "foo"
    assert block.has_teacher(bad_teach) is False


def test_teachers_obj():
    """Verifies that teachersObj() returns a dict of teachers."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    teach = Teacher("John", "Smith")
    other_teach = Teacher("Jane", "Doe")
    block.assign_teacher(teach)
    block.assign_teacher(other_teach)
    teachers = block.teachersObj()
    assert type(teachers) is dict


def test_sync_block_good():
    """Verifies that sync_block() synchronizes a passed Block with this Block."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block1 = Block(day, start, dur, num)
    block2 = Block("tue", start, dur, 2)
    block1.sync_block(block2)
    assert len(getattr(block1, '_sync')) == 1 and block2 in getattr(block1, '_sync')


def test_sync_block_bad():
    """Verifies that sync_block() throws an exception when receiving something that isn't a
    Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    bad_block = "foo"
    with pytest.raises(TypeError) as e:
        block.sync_block(bad_block)
    assert "invalid block" in str(e.value).lower()


def test_unsync_block_good():
    """Verifies that unsync_block() works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block1 = Block(day, start, dur, num)
    block2 = Block("tue", start, dur, 2)
    block1.sync_block(block2)
    block1.unsync_block(block2)
    assert len(getattr(block1, '_sync')) == 0


def test_unsync_block_no_crash_bad_input():
    """Verifies that unsync_block will not crash the program when receiving bad input."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block1 = Block(day, start, dur, num)
    block2 = Block("tue", start, dur, 2)
    block1.sync_block(block2)
    block1.unsync_block("foo")
    assert len(getattr(block1, '_sync')) == 1 and block2 in getattr(block1, '_sync')


def test_synced():
    """Verifies that synced() returns a list of all the Blocks that are synced with this
    Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block1 = Block(day, start, dur, num)
    block2 = Block("tue", start, dur, 2)
    block1.sync_block(block2)
    blocks = block1.synced()
    assert len(blocks) == 1 and block2 in blocks


def test_synced_empty_list():
    """Verifies that synced() returns an empty list if called when no Blocks are synced with
    this Block. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block1 = Block(day, start, dur, num)
    blocks = block1.synced()
    assert len(blocks) == 0


def test_reset_conflicted():
    """Verifies that reset_conflicted works as intended, setting the value of conflicted to
    False. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block1 = Block(day, start, dur, num)
    block1.reset_conflicted()
    assert getattr(block1, '_conflicted') is 0


def test_conflicted_getter():
    """Verifies that the conflicted getter works as intended, returning a default value of
    False. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block1 = Block(day, start, dur, num)
    assert block1.conflicted is 0


def test_conflicted_setter_good():
    """Verifies that the conflicted setter works as intended."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block1 = Block(day, start, dur, num)
    block1.conflicted = 1
    assert block1.conflicted is 1


# def test_conflicted_setter_bad():
# """Verifies that the conflicted setter converts invalid input to a boolean value."""
# day = "mon"
# start = "8:30"
# dur = 2
# num = 1
# block1 = Block(day, start, dur, num)
# block1.conflicted = "yes"
# assert block1.conflicted is True

def test_is_conflicted():
    """Verifies that is_conflicted() returns the value of the conflicted property."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block1 = Block(day, start, dur, num)
    block1.conflicted = True
    assert block1.is_conflicted() is True


def test_string_representation():
    """Verifies that string_representation returns a description containing info about the Block,
    its assigned Labs, and its Section. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    sect = Section("42", 2, "Section 42", id=1)
    lab1 = Lab("R-101", "Worst place in the world")
    lab2 = Lab("R-102", "Second-worst place in the world")
    block.section = sect
    block.assign_lab(lab1)
    block.assign_lab(lab2)
    desc = str(block)
    assert str(sect.number) in desc and day in desc and start in desc and lab1.number in desc \
           and lab2.number in desc


def test_string_representation_no_section():
    """Verifies that string representation returns information about just the Block if it has no
    assigned Section. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    lab1 = Lab("R-101", "Worst place in the world")
    lab2 = Lab("R-102", "Second-worst place in the world")
    block.assign_lab(lab1)
    block.assign_lab(lab2)
    desc = str(block)
    assert day in desc \
           and start in desc and lab1.number in desc and lab1.descr in desc \
           and lab2.number in desc and lab2.descr in desc


def test_description():
    """Verifies that short_description() works as intended: returning information about just
    the Block itself. """
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    block = Block(day, start, dur, num)
    desc = block.description
    assert f"{num} : {day}, {start} {dur:.1f} hour(s)" in desc


# def test_conflicts():
# """Verifies that conflicts() returns an empty list when no Conflicts are
# assigned to this Block."""
# day = "mon"
# start = "8:30"
# dur = 2
# num = 1
# block = Block(day, start, dur, num)
# conflicts = block.conflicts()
# assert len(conflicts) == 0

def test_refresh_number():
    """Verifies that refresh_number gives the Block a new number if its number is 0."""
    day = "mon"
    start = "8:30"
    dur = 2
    num = 0
    block = Block(day, start, dur, num)
    sect = Section("42", id=1)
    sect.add_block(block)
    block.refresh_number()
    assert block.number == 1


def test_list():
    """Verifies that list() returns a tuple containing all extant Blocks."""
    Block._Block__instances = {}
    block_1 = Block("mon", "8:00", 1.5, 1)
    block_2 = Block("mon", "8:00", 1.5, 2)
    blocks = Block.list()
    assert len(blocks) == 2 and block_1 in blocks and block_2 in blocks


def test_list_empty():
    """Verifies that list() returns an empty tuple if there are no Blocks."""
    Block._Block__instances = {}
    blocks = Block.list()
    assert len(blocks) == 0


def test_get_day_blocks():
    """Verifies that get_day_blocks() returns a list of all Blocks occurring on a specific
    day of the week. """
    day = WeekDay.Monday
    block_1 = Block("mon", "8:00", 1.5, 1)
    block_2 = Block("mon", "8:00", 1.5, 2)
    block_3 = Block("tue", "8:00", 1.5, 2)
    block_4 = Block("wed", "8:00", 1.5, 2)
    unfiltered_blocks = [block_1, block_2, block_3, block_4]
    monday_blocks = Block.get_day_blocks(day, unfiltered_blocks)
    assert len(monday_blocks) == 2 and block_1 in monday_blocks and block_2 in monday_blocks


def test_get_day_blocks_bad_input():
    """Verifies that get_day_blocks() won't crash the program if passed a list containing
    non-Block objects. """
    day = WeekDay.Monday
    block_1 = Block("mon", "8:00", 1.5, 1)
    block_2 = Block("mon", "8:00", 1.5, 2)
    block_3 = Block("tue", "8:00", 1.5, 2)
    block_4 = Block("wed", "8:00", 1.5, 2)
    bad_blocks = ["foo", "bar", "baz"]
    monday_blocks = Block.get_day_blocks(day, bad_blocks)
    assert len(monday_blocks) == 0


def test_get_day_blocks_empty_list():
    """Verifies that get_day_blocks() returns an empty list if no Blocks match the passed
    day. """
    block_1 = Block("mon", "8:00", 1.5, 1)
    block_2 = Block("mon", "8:00", 1.5, 2)
    block_3 = Block("tue", "8:00", 1.5, 2)
    block_4 = Block("wed", "8:00", 1.5, 2)
    unfiltered_blocks = [block_1, block_2, block_3, block_4]
    bad_day = WeekDay.Friday
    friday_blocks = Block.get_day_blocks(bad_day, unfiltered_blocks)
    assert len(friday_blocks) == 0


@db_session
def test_save_simple():
    """Verifies that save() works as intended."""
    block = Block("mon", "10:00", 2.5, 1)
    flush()
    block.day = "tue"
    block.start = "9:30"
    block.duration = 3.0
    d_block = block.save()
    d_slot = d_block.time_slot_id
    assert d_block.id == block.id and d_slot.day == block.day \
        and d_slot.start == block.start \
        and d_slot.duration == block.duration

