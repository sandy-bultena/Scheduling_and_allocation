import sys
from os import path
import re

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))
import pytest
import schedule.Schedule.Sections as Sections
from schedule.Schedule.Sections import Section
from schedule.Schedule.Block import Block
from schedule.Schedule.Labs import Lab
from schedule.Schedule.Teachers import Teacher
from schedule.Schedule.Streams import Stream
from schedule.Schedule.exceptions import InvalidHoursForSectionError
import schedule.Schedule.IDGeneratorCode as id_gen


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    pass


def init_scenario_and_schedule():
    pass


@pytest.fixture(autouse=True)
def before_and_after():
    Sections._all_sections.clear()
    Sections._block_id_to_section_id.clear()


def test_id():
    """Verifies that the id property works as intended."""
    section = Section()
    old_id = section.id
    section = Section()
    assert section.id == old_id + 1


def test_id_with_id_given():
    """Verifies that the id property works as intended."""
    Sections._section_id_generator = id_gen.get_id_generator()

    existing_id = 12
    section1 = Section(section_id=existing_id)
    assert section1.id == existing_id
    section2 = Section()
    assert section2.id == existing_id + 1
    section3 = Section(section_id=existing_id - 5)
    assert section3.id == existing_id - 5
    section4 = Section()
    assert section4.id == section2.id + 1


# region General & Properties
def test_constructor_default_values():
    """Checks that the constructor uses default values"""
    s = Section()
    assert isinstance(s.number, str)
    assert s.hours == Sections.DEFAULT_HOURS
    assert isinstance(s.name, str)


def test_section_created_success():
    """Checks that Section is created correctly"""
    number = "3A"
    hours = 2
    name = "My Section"
    s = Section(number, hours, name)
    assert s.name == name
    assert s.hours == hours
    assert s.number == number


def test_set_hours_valid():
    """Checks that valid hours can be set"""
    s = Section()
    hours = 2
    s.hours = hours
    assert s.hours == hours


def test_set_hours_invalid():
    """Checks that invalid hours can't be set"""
    s = Section()
    hours = -10
    with pytest.raises(InvalidHoursForSectionError) as e:
        s.hours = hours
    assert "must be larger than 0" in str(e.value).lower()
    assert s.hours != hours


def test_hours_are_block_hours():
    """Checks if this section has blocks, it returns the number of blocks hours"""
    s = Section()
    hours = 22
    s.hours = hours
    block1: Block = Block("mon", "9:30", 3)
    block2: Block = Block("mon", "10:30", 3.5)
    s.add_block(block1)
    s.add_block(block2)
    assert s.hours == (block1.duration + block2.duration)


def test_cannot_override_block_hours():
    """Checks if this section has blocks, even if we change section hours, it is still blocks hours"""
    s = Section()
    hours = 22
    s.hours = hours
    block1: Block = Block("mon", "9:30", 3)
    block2: Block = Block("mon", "10:30", 3.5)
    s.add_block(block1)
    s.add_block(block2)
    s.hours = hours
    assert s.hours == (block1.duration + block2.duration)


def test_get_title():
    """Checks that title is retrievable and includes name or number"""
    name = "My Section"
    assert name in Section(name=name).title

    number = "3A"
    assert number in Section(number=number).title


def test_set_num_students():
    """Checks that num_students can be set"""
    s = Section()
    num = 20
    s.num_students = num
    assert s.num_students == num


def test_hours_can_be_added():
    """Checks that hours can be added (rather than set) if no blocks are set"""
    hours = 1
    to_add = 10
    s = Section(hours=hours)
    s.add_hours(to_add)
    assert s.hours == hours + to_add


def test_added_hours_ignored_if_blocks():
    """Checks that added hours will be ignored if blocks are set"""
    s = Section()
    block1: Block = Block("mon", "9:30", 3)
    block2: Block = Block("mon", "10:30", 3.5)
    s.add_block(block1)
    s.add_block(block2)
    s.add_hours(20)
    assert s.hours == (block1.duration + block2.duration)


def test_is_conflicted_detects_conflicts_correctly():
    """Checks that the is_conflicted method correctly picks up conflicted_number blocks"""
    s = Section()
    b1 = Block('Mon', '13:00', 2)
    b2 = Block('Mon', '13:00', 2)
    b3 = Block('Mon', '13:00', 2)
    s.add_block(b1).add_block(b2).add_block(b3)
    b1.conflicted_number = 1
    assert s.is_conflicted()


def test_is_conflicted_detects_ok_correctly():
    """Checks that the is_conflicted method doesn't return false positive"""
    s = Section()
    b1 = Block('Mon', '13:00', 2)
    b2 = Block('Mon', '13:00', 2)
    b3 = Block('Mon', '13:00', 2)
    s.add_block(b1).add_block(b2).add_block(b3)
    assert not s.is_conflicted()


def test_string_representation_with_valid_name():
    n = "10"
    s = Section(number=n, name="For students taking calculus")
    assert re.search(f"{n}" + r".*?For students taking calculus", str(s))


def test_string_representation_with_invalid_name():
    n = "10"
    s = Section(number=n, name=f"Section {n}")
    assert str(s) == f"Section {10}"


def test_string_representation_with_no_name():
    n = "10"
    s = Section(number=n)
    assert str(s) == f"Section {10}"


# endregion

# region Block
def test_add_block_valid():
    """Checks that a valid blocks can be added"""
    s = Section()
    b = Block('Mon', '13:00', 2)
    s.add_block(b)
    assert b in s.blocks


def test_get_block_by_id_valid():
    """Checks that blocks can be retrieved by id"""
    s = Section()
    b1 = Block('Mon', '13:00', 2)
    b1_id = b1.id
    Block('tue', "12:00", 5)
    s.add_block(b1)
    assert s.get_block_by_id(b1_id) is b1


def test_get_block_by_id_invalid():
    """Checks that None is returned when get_block_by_id is passed a non-blocks id"""
    s = Section()
    assert s.get_block_by_id(-1) is None


def test_remove_block_valid():
    """Checks that when passed a valid blocks, it will be removed"""
    s = Section()
    b = Block('Mon', '13:00', 2)
    s.add_block(b)
    s.remove_block(b)
    assert b not in s.blocks


def find_section_for_given_block():
    """Given a blocks, return the section that pertains to that blocks"""
    s1 = Section()
    s2 = Section()
    b1 = Block("mon", "12:00", 1.5)
    b2 = Block("tue", "12:00", 1.5)
    b3 = Block("wed", "20:00", 1.5)
    b4 = Block("thu", "12:00", 1.5)
    b5 = Block("fri", "12:00", 1.5)
    s1.add_block(b1).add_block(b2)
    s2.add_block(b3).add_block(b4)
    assert Sections.get_section_with_this_block(b1) == s1
    assert Sections.get_section_with_this_block(b2) == s1
    assert Sections.get_section_with_this_block(b3) == s2
    assert Sections.get_section_with_this_block(b4) == s2
    assert Sections.get_section_with_this_block(b5) is None


def find_section_for_given_block_after_deletion_returns_none():
    """Given a blocks, that has been removed, will not return a section"""
    s1 = Section()
    s2 = Section()
    b1 = Block("mon", "12:00", 1.5)
    b2 = Block("tue", "12:00", 1.5)
    b3 = Block("wed", "20:00", 1.5)
    b4 = Block("thu", "12:00", 1.5)
    b5 = Block("fri", "12:00", 1.5)
    s1.add_block(b1).add_block(b2)
    s2.add_block(b3).add_block(b4)
    s1.remove_block(b1)
    assert Sections.get_section_with_this_block(b1) is None
    assert Sections.get_section_with_this_block(b2) == s1
    assert Sections.get_section_with_this_block(b3) == s2
    assert Sections.get_section_with_this_block(b4) == s2
    assert Sections.get_section_with_this_block(b5) is None


# endregion

# region Lab

def test_assign_lab_valid():
    """Checks that a valid lab can be added"""
    s = Section()
    b = Block('Mon', '13:00', 2)
    l = Lab()
    s.add_block(b)
    s.add_lab(l)
    assert l in s.lab_ids


def test_remove_lab_valid():
    """Checks that when passed a valid lab, it will be removed & deleted"""
    s = Section()
    b = Block('Mon', '13:00', 2)
    l = Lab()
    s.add_block(b)
    s.add_lab(l)
    s.remove_lab(l)
    assert l not in s.lab_ids


def test_remove_lab_not_there():
    """Checks that when passed not-included lab, it will still be 'removed' """
    s = Section()
    b = Block('Mon', '13:00', 2)
    l = Lab()
    s.add_block(b)
    s.remove_lab(l)
    assert l not in s.lab_ids


# endregion

# region Teacher

def test_assign_teacher_valid():
    """Checks that a valid teacher can be added"""
    s = Section()
    s.hours = 15
    t = Teacher("Jane", "Doe")
    s.add_teacher(t)
    assert t in s.teacher_ids


def test_get_teacher_allocation_valid():
    """Checks that get_teacher_allocation returns the correct allocation hours"""
    s = Section()
    t = Teacher("Jane", "Doe")
    hours = 12
    s.add_teacher(t)
    s.set_teacher_allocation(t, hours)
    assert s.get_teacher_allocation(t) == hours


def test_assign_teacher_valid_allocation_hours_default_to_section_hours():
    """Checks that a valid teacher can be added, and that the teacher allocation hours is set to section hours"""
    s = Section()
    s.hours = 15
    t = Teacher("Jane", "Doe")
    s.add_teacher(t)
    assert s.get_teacher_allocation(t) == s.hours
    t2 = Teacher("Bob", "Doe")
    s.add_teacher(t2)
    assert s.get_teacher_allocation(t2) == s.hours


def test_section_allocation_hours_total_of_teacher_hours():
    """Checks that a valid teacher can be added, and that the teacher allocation hours is set to section hours"""
    s = Section()
    s.hours = 15
    t = Teacher("Jane", "Doe")
    s.add_teacher(t)
    assert s.get_teacher_allocation(t) == s.hours
    t2 = Teacher("Bob", "Doe")
    s.add_teacher(t2)
    assert s.get_teacher_allocation(t2) == s.hours
    assert s.allocated_hours == s.get_teacher_allocation(t) + s.get_teacher_allocation(t2)


def test_set_teacher_allocation_valid():
    """Checks that valid hours can be set to valid teacher"""
    s = Section()
    t = Teacher("Jane", "Doe")
    s.hours = 15
    hours = 12
    s.add_teacher(t)
    s.set_teacher_allocation(t, hours)
    assert s.get_teacher_allocation(t) == hours


def test_section_allocation_hours_total_of_teacher_hours_after_setting_teacher_allocation():
    """Checks that a valid teacher can be added, and that the teacher allocation hours is set to section hours"""
    s = Section()
    s.hours = 15
    t = Teacher("Jane", "Doe")
    s.add_teacher(t)
    t2 = Teacher("Bob", "Doe")
    s.add_teacher(t2)
    s.set_teacher_allocation(t, 4)
    s.set_teacher_allocation(t2, 5)
    assert s.allocated_hours == s.get_teacher_allocation(t) + s.get_teacher_allocation(t2)


def test_set_teacher_allocation_new_teacher():
    """Checks that valid hours can be set to new teacher"""
    s = Section()
    t = Teacher("Jane", "Doe")
    hours = 12
    s.set_teacher_allocation(t, hours)
    assert s.has_teacher(t)
    assert s.get_teacher_allocation(t) == hours


def test_set_teacher_allocation_zero_hours():
    """Checks that assigning 0 hours to teacher will remove that teacher"""
    s = Section()
    hours = 5
    t = Teacher("Jane", "Doe")
    t2 = Teacher("Jane", "Doe")
    s.add_teacher(t)
    s.add_teacher(t2)
    s.set_teacher_allocation(t, 0)
    s.set_teacher_allocation(t2, hours)
    assert not s.has_teacher(t)
    assert s.has_teacher(t2)
    assert s.allocated_hours == s.get_teacher_allocation(t2)


def test_get_teacher_allocation_not_teaching():
    """Checks that get_teacher_allocation returns the correct allocation hours"""
    s = Section()
    t = Teacher("Jane", "Doe")
    assert s.get_teacher_allocation(t) == 0


def test_has_teacher_valid():
    """Checks has_teacher_with_id returns True if teacher is included"""
    s = Section()
    t = Teacher("Jane", "Doe")
    s.add_teacher(t)
    assert s.has_teacher(t)


def test_has_teacher_not_found():
    """Checks has_teacher_with_id returns False if teacher is not included"""
    s = Section()
    t = Teacher("Jane", "Doe")
    assert not s.has_teacher(t)


def test_remove_teacher_valid():
    """Checks that when passed a valid teacher, it will be removed & allocation will be deleted"""
    s = Section()
    hours = 5
    t = Teacher("Jane", "Doe")
    t2 = Teacher("Jane", "Doe")
    s.add_teacher(t)
    s.add_teacher(t2)
    s.remove_teacher(t)
    s.set_teacher_allocation(t2, hours)
    assert not s.has_teacher(t)
    assert s.has_teacher(t2)
    assert s.allocated_hours == s.get_teacher_allocation(t2)


def test_remove_all_deletes_all_teachers():
    """Checks that remove_all_teachers will correctly delete them all"""
    s = Section()
    s.add_teacher(Teacher("Jane", "Doe"))
    s.add_teacher(Teacher("John", "Doe"))
    s.add_teacher(Teacher("1", "2"))
    s.remove_all_teachers()
    assert not s.teacher_ids
    assert s.allocated_hours == 0


def test_teachers_in_blocks_in_teachers_property():
    s = Section()
    b1: Block = Block("mon", "13:00", 1.5)
    b2: Block = Block("mon", "13:00", 1.5)
    t1 = Teacher("Jane", "doe")
    t2 = Teacher("John", "Smith")
    t3 = Teacher("John", "Doe")
    b1.assign_teacher_by_id(t1)
    b2.assign_teacher_by_id(t2)
    s.add_block(b1).add_block(b2)
    s.add_teacher(t3)

    assert len(s.teacher_ids) == 3
    assert t1 in s.teacher_ids
    assert t2 in s.teacher_ids
    assert t3 in s.teacher_ids
    assert t1 in b1.teacher_ids
    assert t3 in b1.teacher_ids
    assert t2 in b2.teacher_ids
    assert t3 in b2.teacher_ids
    assert len(b1.teacher_ids) == 2
    assert len(b2.teacher_ids) == 2

test_teachers_in_blocks_in_teachers_property()
# endregion

# region Stream

def test_assign_stream_valid():
    """Checks that a valid stream can be added"""
    s = Section()
    st = Stream()
    s.add_stream(st)
    assert st in s.streams


def test_has_stream_valid():
    """Checks has_stream_with_id returns True if stream is included"""
    s = Section()
    st = Stream()
    s.add_stream(st)
    assert s.has_stream(st)


def test_has_stream_not_found():
    """Checks has_stream_with_id returns False if stream is not included"""
    s = Section()
    st = Stream()
    assert not s.has_stream(st)


def test_remove_stream_valid():
    """Checks that when passed a valid stream"""
    s = Section()
    st = Stream()
    s.add_stream(st)
    s.remove_stream(st)
    assert st not in s.streams


def test_remove_stream_not_there():
    """Checks that when passed not-included stream, it will still be 'removed' """
    s = Section()
    st = Stream()
    s.remove_stream(st)
    assert s not in s.streams


def test_remove_all_deletes_all_streams():
    """Checks that remove_all_streams will correctly delete them all"""
    s = Section()
    s.add_stream(Stream())
    s.add_stream(Stream())
    s.add_stream(Stream())
    s.remove_all_streams()
    assert not s.streams

# endregion
