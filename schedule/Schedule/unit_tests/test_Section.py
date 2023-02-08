from ..Section import Section
from ..Course import Course
from ..Block import Block
from ..Lab import Lab
from ..Teacher import Teacher
from ..Stream import Stream
import pytest

@pytest.fixture(autouse=True)
def run_before_and_after():
    Section._max_id = 0
    Section.reset()
    Block.list().clear()

#region General & Properties
def test_constructor_default_values():
    """Checks that the constructor uses default values"""
    s = Section()
    assert isinstance(s.number, str)
    assert s.hours
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

def test_section_is_added_to_collection():
    """Checks that newly created Section is added to the collection"""
    s = Section()
    assert s in Section.list()

def test_set_hours_valid():
    """Checks that valid hours can be set"""
    s = Section()
    hours = 2
    s.hours = hours
    assert s.hours == hours

def test_set_hours_invalid():
    """Checks that invalid hours can't be set"""
    s = Section()
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
    assert name in Section(name=name).title

    number = "3A"
    assert number in Section(number=number).title

def test_set_course_valid():
    """Checks that valid courses can be set"""
    s = Section()
    c = Course("1", semester="winter")
    s.course = c
    assert s.course is c

def test_set_course_invalid():
    """Checks that invalid courses can't be set"""
    s = Section()
    c = 1
    with pytest.raises(TypeError) as e:
        s.course = c
    assert "invalid course" in str(e.value).lower()

def test_set_num_students():
    """Checks that num_students can be set"""
    s = Section()
    num = 20
    s.num_students = num
    assert s.num_students == num

def test_hours_can_be_added():
    """Checks that hours can be added (rather than set)"""
    hours = 1
    to_add = 10
    s = Section(hours = hours)
    s.add_hours(to_add)
    assert s.hours == hours + to_add

def test_delete_deletes_all():
    """Checks that the delete method removes the Section and all Blocks from respective lists"""
    s = Section()
    b1 = Block('Mon', '13:00', 2, 1)
    b2 = Block('Mon', '13:00', 2, 2)
    b3 = Block('Mon', '13:00', 2, 3)
    s.add_block(b1).add_block(b2).add_block(b3)
    s.delete()
    assert s not in Section.list()
    assert b1 not in Block
    assert b2 not in Block
    assert b3 not in Block

def test_is_conflicted_detects_conflicts_correctly():
    """Checks that the is_conflicted method correctly picks up conflicted blocks"""
    s = Section()
    b1 = Block('Mon', '13:00', 2, 1)
    b2 = Block('Mon', '13:00', 2, 2)
    b3 = Block('Mon', '13:00', 2, 3)
    s.add_block(b1).add_block(b2).add_block(b3)
    b1.conflicted = 1
    assert s.is_conflicted()

def test_is_conflicted_detects_ok_correctly():
    """Checks that the is_conflicted method doesn't return false positive"""
    s = Section()
    b1 = Block('Mon', '13:00', 2, 1)
    b2 = Block('Mon', '13:00', 2, 2)
    b3 = Block('Mon', '13:00', 2, 3)
    s.add_block(b1).add_block(b2).add_block(b3)
    assert not s.is_conflicted()

def test_get_new_number_gets_first():
    """Checks that the get_new_number method will get the lowest available block number, regardeless of add order or block id of existing blocks"""
    lowest = 4
    s = Section()
    b1 = Block('Mon', '13:00', 2, 1)
    b2 = Block('Mon', '13:00', 2, 3)
    b3 = Block('Mon', '13:00', 2, 2)
    s.add_block(b1).add_block(b2).add_block(b3)
    assert s.get_new_number() == lowest

def test_get_new_number_no_blocks():
    """Checks that the get_new_number method will return 1 if there are no blocks in the section"""
    assert Section().get_new_number() == 1


#endregion

#region Block
def test_add_block_valid():
    """Checks that a valid block can be added"""
    s = Section()
    b = Block('Mon', '13:00', 2, 1)
    s.add_block(b)
    assert b in s.blocks

def test_add_block_invalid():
    """Checks that an invalid block can't be added"""
    s = Section()
    b = 12
    with pytest.raises(TypeError) as e:
        s.add_block(b)
    assert "invalid block" in str(e.value).lower()

def test_get_block_by_id_valid():
    """Checks that block can be retrieved by id"""
    s = Section()
    b = Block('Mon', '13:00', 2, 1)
    id = b.id
    s.add_block(b)
    assert s.get_block_by_id(id) is b

def test_get_block_by_id_invalid():
    """Checks that None is returned when get_block_by_id is passed unfound id"""
    s = Section()
    assert s.get_block_by_id(-1) is None

def test_get_block_valid():
    """Checks that block can be retrieved by number"""
    s = Section()
    num = 10
    b = Block('Mon', '13:00', 2, num)
    s.add_block(b)
    assert s.get_block(num) is b

def test_get_block_invalid():
    """Checks that None is returned when get_block is passed unfound number"""
    s = Section()
    assert s.get_block(-1) is None

def test_remove_block_valid():
    """Checks that when passed a valid block, it will be removed & deleted"""
    s = Section()
    b = Block('Mon', '13:00', 2, 1)
    s.add_block(b)
    s.remove_block(b)
    assert b not in s.blocks
    assert b not in Block.list()        # make sure block.delete is called

def test_remove_block_invalid():
    """Checks that error is thrown when remove_block is passed non-Block object"""
    s = Section()
    with pytest.raises(TypeError) as e:
        s.remove_block(1)
    assert "invalid block" in str(e.value).lower()

def test_remove_block_not_there():
    """Checks that when passed not-included block, it will still be deleted"""
    b = Block('Mon', '13:00', 2, 1)
    Section().remove_block(b)
    assert b not in Block.list()

def test_hours_auto_calc_when_blocks_are_present():
    """Checks that if the section has blocks, hours will be auto-calculated"""
    s = Section()
    dur = 2
    b1 = Block('Mon', '13:00', dur, 1)
    b2 = Block('Mon', '13:00', dur, 2)
    s.add_block(b1).add_block(b2)
    s.hours = dur
    assert s.hours == (dur * 2)

#endregion

#region Lab

def test_assign_lab_valid():
    """Checks that a valid lab can be added"""
    s = Section()
    b = Block('Mon', '13:00', 2, 1)
    l = Lab()
    s.add_block(b)
    s.assign_lab(l)
    assert l in s.labs

# don't check for invalid, since verification is done in Block.assign_lab

def test_remove_lab_valid():
    """Checks that when passed a valid lab, it will be removed & deleted"""
    s = Section()
    b = Block('Mon', '13:00', 2, 1)
    l = Lab()
    s.add_block(b)
    s.assign_lab(l)
    s.remove_lab(l)
    assert l not in s.labs

# don't check for invalid, since verification is done in Block.remove_lab

def test_remove_lab_not_there():
    """Checks that when passed not-included lab, it will still be 'removed' """
    s = Section()
    b = Block('Mon', '13:00', 2, 1)
    l = Lab()
    s.add_block(b)
    s.remove_lab(l)
    assert l not in s.labs

#endregion

#region Teacher

def test_assign_teacher_valid():
    """Checks that a valid teacher can be added"""
    s = Section()
    t = Teacher("Jane", "Doe")
    s.assign_teacher(t)
    assert t in s.teachers
    assert s.allocated_hours == s.hours

def test_assign_teacher_invalid():
    """Checks that an invalid teacher can't be added"""
    s = Section()
    with pytest.raises(TypeError) as e:
        s.assign_teacher(12)
    assert "invalid teacher" in str(e.value).lower()

def test_set_teacher_allocation_valid():
    """Checks that valid hours can be set to valid teacher"""
    s = Section()
    t = Teacher("Jane", "Doe")
    hours = 12
    s.assign_teacher(t)
    s.set_teacher_allocation(t, hours)
    assert s._allocation[t.id] == hours

def test_set_teacher_allocation_new_teacher():
    """Checks that valid hours can be set to new teacher teacher"""
    s = Section()
    t = Teacher("Jane", "Doe")
    hours = 12
    s.set_teacher_allocation(t, hours)
    assert s._allocation[t.id] == hours
    assert s.has_teacher(t)

def test_set_teacher_allocation_zero_hours():
    """Checks that assigning 0 hours to teacher will remove that teacher"""
    s = Section()
    t = Teacher("Jane", "Doe")
    s.assign_teacher(t)
    s.set_teacher_allocation(t, 0)
    assert t.id not in s._allocation
    assert not s.has_teacher(t)

def test_get_teacher_allocation_valid():
    """Checks that get_teacher_allocation returns the correct allocation hours"""
    s = Section()
    t = Teacher("Jane", "Doe")
    hours = 12
    s.assign_teacher(t)
    s.set_teacher_allocation(t, hours)
    assert s.get_teacher_allocation(t) == hours

def test_get_teacher_allocation_not_teaching():
    """Checks that get_teacher_allocation returns the correct allocation hours"""
    s = Section()
    t = Teacher("Jane", "Doe")
    assert s.get_teacher_allocation(t) == 0

def test_has_teacher_valid():
    """Checks has_teacher returns True if teacher is included"""
    s = Section()
    t = Teacher("Jane", "Doe")
    s.assign_teacher(t)
    assert s.has_teacher(t)

def test_has_teacher_not_found():
    """Checks has_teacher returns False if teacher is not included"""
    s = Section()
    t = Teacher("Jane", "Doe")
    assert not s.has_teacher(t)

def test_has_teacher_invalid():
    """Checks has_teacher returns False if non-Teacher is given"""
    s = Section()
    with pytest.raises(TypeError) as e:
        s.has_teacher(12)
    assert "invalid teacher" in str(e.value).lower()

def test_remove_teacher_valid():
    """Checks that when passed a valid teacher, it will be removed & allocation will be deleted"""
    s = Section()
    t = Teacher("Jane", "Doe")
    s.assign_teacher(t)
    s.remove_teacher(t)
    assert t not in s.teachers
    assert t.id not in s._allocation

def test_remove_teacher_invalid():
    """Checks that error is thrown when remove_teacher is passed non-Teacher object"""
    s = Section()
    with pytest.raises(TypeError) as e:
        s.remove_teacher(1)
    assert "invalid teacher" in str(e.value).lower()

def test_remove_teacher_not_there():
    """Checks that when passed not-included teacher, it will still be 'removed' """
    s = Section()
    t = Teacher("Jane", "Doe")
    s.remove_teacher(t)
    assert t not in s.teachers
    assert t.id not in s._allocation

def test_remove_all_deletes_all_teachers():
    """Checks that remove_all_teachers will correctly delete them all"""
    s = Section()
    s.assign_teacher(Teacher("Jane", "Doe"))
    s.assign_teacher(Teacher("John", "Doe"))
    s.assign_teacher(Teacher("1", "2"))
    s.remove_all_teachers()
    assert not s.teachers
    assert not s._allocation

#endregion

#region Stream

def test_assign_stream_valid():
    """Checks that a valid stream can be added"""
    s = Section()
    st = Stream()
    s.assign_stream(st)
    assert st in s.streams

def test_assign_stream_invalid():
    """Checks that an invalid stream can't be added"""
    s = Section()
    with pytest.raises(TypeError) as e:
        s.assign_stream(12)
    assert "invalid stream" in str(e.value).lower()

def test_has_stream_valid():
    """Checks has_stream returns True if stream is included"""
    s = Section()
    st = Stream()
    s.assign_stream(st)
    assert s.has_stream(st)

def test_has_stream_not_found():
    """Checks has_stream returns False if stream is not included"""
    s = Section()
    st = Stream()
    assert not s.has_stream(st)

def test_has_stream_invalid():
    """Checks has_stream returns False if non-Stream is given"""
    s = Section()
    with pytest.raises(TypeError) as e:
        s.has_stream(12)
    assert "invalid stream" in str(e.value).lower()

def test_remove_stream_valid():
    """Checks that when passed a valid stream, it will be removed & allocation will be deleted"""
    s = Section()
    st = Stream()
    s.assign_stream(st)
    s.remove_stream(st)
    assert st not in s.streams

def test_remove_stream_invalid():
    """Checks that error is thrown when remove_stream is passed non-Stream object"""
    s = Section()
    with pytest.raises(TypeError) as e:
        s.remove_stream(1)
    assert "invalid stream" in str(e.value).lower()

def test_remove_stream_not_there():
    """Checks that when passed not-included stream, it will still be 'removed' """
    s = Section()
    st = Stream()
    s.remove_stream(st)
    assert s not in s.streams

def test_remove_all_deletes_all_streams():
    """Checks that remove_all_streams will correctly delete them all"""
    s = Section()
    s.assign_stream(Stream())
    s.assign_stream(Stream())
    s.assign_stream(Stream())
    s.remove_all_streams()
    assert not s.streams

#endregion