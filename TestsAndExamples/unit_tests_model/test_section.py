from __future__ import annotations
import re
import pytest

from schedule.model.section import Section
import schedule.model.section as sections_module
from schedule.model import Block, WeekDay, ClockTime
from schedule.model import TimeSlot, ConflictType
from schedule.model import InvalidHoursForSectionError


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    pass


def init_scenario_and_schedule():
    pass


@pytest.fixture(autouse=True)
def before_and_after():
    pass


class Lab:
    def __lt__(self, other: Lab):
        return True


class Stream:
    def __lt__(self, other: Stream):
        return True


class Teacher:
    def __lt__(self, other: Teacher):
        return True


class Course:
    @property
    def title(self):
        return "Course Title"


course = Course()


def test_id():
    """Verifies that the id property works as intended."""
    section = Section(course)
    old_id = section.id
    section = Section(course)
    assert section.id == old_id + 1


def test_id_with_id_given():
    """Verifies that the id property works as intended."""

    existing_id = 12
    section1 = Section(course, section_id=existing_id)
    assert section1.id == existing_id
    section2 = Section(course)
    assert section2.id == existing_id + 1
    section3 = Section(course, section_id=existing_id - 5)
    assert section3.id == existing_id - 5
    section4 = Section(course)
    assert section4.id == section2.id + 1


# region General & Properties
def test_constructor_default_values():
    """Checks that the constructor uses default values"""
    s = Section(course)
    assert isinstance(s.number, str)
    assert s.hours == sections_module.DEFAULT_HOURS
    assert isinstance(s.name, str)


def test_section_created_success():
    """Checks that Section is created correctly"""
    number = "3A"
    hours = 2
    name = "My Section"
    s = Section(course, number, hours, name)
    assert s.name == name
    assert s.hours == hours
    assert s.number == number


def test_set_hours_valid():
    """Checks that valid hours can be set_default_fonts_and_colours"""
    s = Section(course)
    hours = 2
    s.hours = hours
    assert s.hours == hours


def test_set_hours_invalid():
    """Checks that invalid hours can't be set"""
    s = Section(course)
    hours = -10
    with pytest.raises(InvalidHoursForSectionError) as e:
        s.hours = hours
    assert "must be larger than 0" in str(e.value).lower()
    assert s.hours != hours


def test_hours_are_block_hours():
    """Checks if this section has blocks, it returns the number of blocks hours"""
    s = Section(course)
    hours = 22
    s.hours = hours
    block1 = s.add_block(TimeSlot(WeekDay.Monday, ClockTime("9:30"), 3))
    block2 = s.add_block(TimeSlot(WeekDay.Monday, ClockTime("10:30"), 3.5))
    assert s.hours == (block1.time_slot.duration + block2.time_slot.duration)


def test_cannot_override_block_hours():
    """Checks if this section has blocks, even if we change section hours, it is still blocks hours"""
    s = Section(course)
    hours = 22
    s.hours = hours
    block1 = s.add_block(TimeSlot(WeekDay.Monday, ClockTime("9:30"), 3))
    block2 = s.add_block(TimeSlot(WeekDay.Monday, ClockTime("10:30"), 3.5))
    s.hours = hours
    assert s.hours == (block1.time_slot.duration + block2.time_slot.duration)


def test_get_title():
    """Checks that title is retrievable and includes name or number"""
    name = "My Section"
    assert name in Section(course, name=name).title

    number = "3A"
    assert number in Section(course, number=number).title


def test_set_num_students():
    """Checks that num_students can be set_default_fonts_and_colours"""
    s = Section(course)
    num = 20
    s.num_students = num
    assert s.num_students == num


def test_hours_can_be_added():
    """Checks that hours can be added (rather than set_default_fonts_and_colours) if no blocks are set_default_fonts_and_colours"""
    hours = 1
    to_add = 10
    s = Section(course, hours=hours)
    s.add_hours(to_add)
    assert s.hours == hours + to_add


def test_added_hours_ignored_if_blocks():
    """Checks that added hours will be ignored if blocks are set_default_fonts_and_colours"""
    s = Section(course)
    block1 = s.add_block(TimeSlot(WeekDay.Monday, ClockTime("9:30"), 3))
    block2 = s.add_block(TimeSlot(WeekDay.Monday, ClockTime("10:30"), 3.5))
    s.add_hours(20)
    assert s.hours == (block1.time_slot.duration + block2.time_slot.duration)


def test_is_conflicted_detects_conflicts_correctly():
    """Checks that the is_conflicted method correctly picks up conflicted_number blocks"""
    s = Section(course)
    block1 = s.add_block(TimeSlot(WeekDay.Monday, ClockTime("10:30"), 3))
    block1.add_conflict(ConflictType.LUNCH)
    assert s.is_conflicted()


def test_is_conflicted_detects_ok_correctly():
    """Checks that the is_conflicted method doesn't return false positive"""
    s = Section(course)
    s.add_block(TimeSlot('Mon', '13:00', 2))
    s.add_block(TimeSlot('Mon', '13:00', 2))
    s.add_block(TimeSlot('Mon', '13:00', 2))
    assert not s.is_conflicted()


def test_string_representation_with_valid_name():
    n = "10"
    s = Section(course, number=n, name="For students taking calculus")
    assert re.search(f"{n}" + r".*?For students taking calculus", str(s))


def test_string_representation_with_invalid_name():
    n = "10"
    s = Section(course, number=n, name=f"Section {n}")
    assert str(s) == f"Section {10}"


def test_string_representation_with_no_name():
    n = "10"
    s = Section(course, number=n)
    assert str(s) == f"Section {10}"


# endregion

# region Block
def test_add_block_valid():
    """Checks that a valid blocks can be added"""
    s = Section(course)
    b = s.add_block(TimeSlot(WeekDay.Monday, ClockTime('13:00'), 2))
    assert b in s.blocks()


def test_get_block_by_id_valid():
    """Checks that blocks can be retrieved by id"""
    s = Section(course)
    b1 = s.add_block(TimeSlot('Mon', '13:00', 2))
    b1_id = b1.id
    s.add_block(TimeSlot('tue', "12:00", 5))
    assert s.get_block_by_id(b1_id) == b1


def test_get_block_by_id_invalid():
    """Checks that None is returned when get_block_by_id is passed a non-blocks id"""
    s = Section(course)
    assert s.get_block_by_id(-1) is None


def test_remove_block_valid():
    """Checks that when passed a valid blocks, it will be removed"""
    s = Section(course)
    b1 = s.add_block(TimeSlot('Mon', '13:00', 2))
    b2 = s.add_block(TimeSlot('Mon', '13:00', 2))
    s.remove_block(b1)
    assert b1 not in s.blocks()
    assert b2 in s.blocks()


# endregion

# region Lab

def test_assign_lab_valid():
    """Checks that a valid lab can be added, if there is a block"""
    s = Section(course)
    s.add_block(TimeSlot(WeekDay.Monday, ClockTime('13:00'), 2))
    lab = Lab()
    s.add_lab(lab)
    assert lab in s.labs()


def test_remove_lab_valid():
    """Checks that when passed a valid lab, it will be removed & deleted"""
    s = Section(course)
    s.add_block(TimeSlot(WeekDay.Monday, ClockTime('13:00'), 2))
    lab = Lab()
    s.add_lab(lab)
    s.remove_lab(lab)
    assert lab not in s.labs()


def test_remove_lab_not_there():
    """Checks that when passed not-included lab, it will still be 'removed' """
    s = Section(course)
    s.add_block(TimeSlot(WeekDay.Monday, ClockTime('13:00'), 2))
    lab = Lab()
    s.remove_lab(lab)
    assert lab not in s.labs()


# endregion

# region Teacher

def test_assign_teacher_valid():
    """Checks that a valid teacher can be added"""
    s = Section(course)
    s.hours = 15
    t = Teacher()
    s.add_teacher(t)
    assert t in s.teachers()


def test_get_teacher_allocation_valid():
    """Checks that get_teacher_allocation returns the correct allocation hours"""
    s = Section(course)
    t = Teacher()
    hours = 12
    s.add_teacher(t)
    s.set_teacher_allocation(t, hours)
    assert s.get_teacher_allocation(t) == hours


def test_assign_teacher_valid_allocation_hours_default_to_section_hours():
    """Checks that a valid teacher can be added, and that the teacher allocation hours is set_default_fonts_and_colours to section hours"""
    s = Section(course)
    s.hours = 15
    t = Teacher()
    s.add_teacher(t)
    assert s.get_teacher_allocation(t) == s.hours
    t2 = Teacher()
    s.add_teacher(t2)
    assert s.get_teacher_allocation(t2) == s.hours


def test_section_allocation_hours_total_of_teacher_hours():
    """Checks that a valid teacher can be added, and that the teacher allocation hours is set_default_fonts_and_colours to section hours"""
    s = Section(course)
    s.hours = 15
    t = Teacher()
    s.add_teacher(t)
    assert s.get_teacher_allocation(t) == s.hours
    t2 = Teacher()
    s.add_teacher(t2)
    assert s.get_teacher_allocation(t2) == s.hours
    assert s.allocated_hours() == s.get_teacher_allocation(t) + s.get_teacher_allocation(t2)


def test_set_teacher_allocation_valid():
    """Checks that valid hours can be set_default_fonts_and_colours to valid teacher"""
    s = Section(course)
    t = Teacher()
    s.hours = 15
    hours = 12
    s.add_teacher(t)
    s.set_teacher_allocation(t, hours)
    assert s.get_teacher_allocation(t) == hours


def test_section_allocation_hours_total_of_teacher_hours_after_setting_teacher_allocation():
    """Checks that a valid teacher can be added, and that the teacher allocation hours is set_default_fonts_and_colours to section hours"""
    s = Section(course)
    s.hours = 15
    t = Teacher()
    s.add_teacher(t)
    t2 = Teacher()
    s.add_teacher(t2)
    s.set_teacher_allocation(t, 4)
    s.set_teacher_allocation(t2, 5)
    assert s.allocated_hours() == s.get_teacher_allocation(t) + s.get_teacher_allocation(t2)


def test_set_teacher_allocation_new_teacher():
    """Checks that valid hours can be set_default_fonts_and_colours to new teacher"""
    s = Section(course)
    t = Teacher()
    hours = 12
    s.set_teacher_allocation(t, hours)
    assert s.has_teacher(t)
    assert s.get_teacher_allocation(t) == hours


def test_set_teacher_allocation_zero_hours():
    """Checks that assigning 0 hours to teacher will remove that teacher"""
    s = Section(course)
    hours = 5
    t = Teacher()
    t2 = Teacher()
    s.add_teacher(t)
    s.add_teacher(t2)
    s.set_teacher_allocation(t, 0)
    s.set_teacher_allocation(t2, hours)
    assert not s.has_teacher(t)
    assert s.has_teacher(t2)
    assert s.allocated_hours() == s.get_teacher_allocation(t2)


def test_get_teacher_allocation_not_teaching():
    """Checks that get_teacher_allocation returns the correct allocation hours"""
    s = Section(course)
    t = Teacher()
    assert s.get_teacher_allocation(t) == 0


def test_has_teacher_valid():
    """Checks has_teacher_with_id returns True if teacher is included"""
    s = Section(course)
    t = Teacher()
    s.add_teacher(t)
    assert s.has_teacher(t)


def test_has_teacher_not_found():
    """Checks has_teacher_with_id returns False if teacher is not included"""
    s = Section(course)
    t = Teacher()
    assert not s.has_teacher(t)


def test_remove_teacher_valid():
    """Checks that when passed a valid teacher, it will be removed & allocation will be deleted"""
    s = Section(course)
    hours = 5
    t = Teacher()
    t2 = Teacher()
    s.add_teacher(t)
    s.add_teacher(t2)
    s.remove_teacher(t)
    s.set_teacher_allocation(t2, hours)
    assert not s.has_teacher(t)
    assert s.has_teacher(t2)
    assert s.allocated_hours() == s.get_teacher_allocation(t2)


def test_remove_all_deletes_all_teachers():
    """Checks that remove_all_teachers will correctly delete them all"""
    s = Section(course)
    s.add_teacher(Teacher())
    s.add_teacher(Teacher())
    s.add_teacher(Teacher())
    s.remove_all_teachers()
    assert len( s.teachers()) == 0
    assert s.allocated_hours() == 0


def test_teachers_in_blocks_in_teachers_property():
    s = Section(course)
    b1: Block = s.add_block(TimeSlot(WeekDay.Monday, ClockTime("13:00"), 1.5))
    b2: Block = s.add_block(TimeSlot(WeekDay.Monday, ClockTime("13:00"), 1.5))
    t1 = Teacher()
    t2 = Teacher()
    t3 = Teacher()
    s.add_teacher(t3)
    s.add_teacher(t1)
    s.add_teacher(t2)

    assert len(s.teachers()) == 3
    assert t1 in s.teachers()
    assert t2 in s.teachers()
    assert t3 in s.teachers()
    assert t1 in b1.teachers()
    assert t3 in b1.teachers()
    assert t2 in b2.teachers()
    assert t3 in b2.teachers()
    assert len(b1.teachers()) == 3
    assert len(b2.teachers()) == 3


# endregion

# region Stream

def test_assign_stream_valid():
    """Checks that a valid stream can be added"""
    s = Section(course)
    st = Stream()
    s.add_stream(st)
    assert st in s.streams()


def test_has_stream_valid():
    """Checks has_stream_with_id returns True if stream is included"""
    s = Section(course)
    st = Stream()
    s.add_stream(st)
    assert s.has_stream(st)


def test_has_stream_not_found():
    """Checks has_stream_with_id returns False if stream is not included"""
    s = Section(course)
    st = Stream()
    assert not s.has_stream(st)


def test_remove_stream_valid():
    """Checks that when passed a valid stream"""
    s = Section(course)
    st = Stream()
    s.add_stream(st)
    s.remove_stream(st)
    assert st not in s.streams()


def test_remove_stream_not_there():
    """Checks that when passed not-included stream, it will still be 'removed' """
    s = Section(course)
    st = Stream()
    s.remove_stream(st)
    assert s not in s.streams()


def test_remove_all_deletes_all_streams():
    """Checks that remove_all_streams will correctly delete them all"""
    s = Section(course)
    s.add_stream(Stream())
    s.add_stream(Stream())
    s.add_stream(Stream())
    s.remove_all_streams()
    assert not s.streams()

# endregion
