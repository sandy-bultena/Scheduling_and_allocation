from ..Schedule import Schedule
from ..Teacher import Teacher
from ..Stream import Stream
from ..Course import Course
from ..Lab import Lab
from ..Conflict import Conflict
from ..Section import Section
from ..Block import Block

def test_teachers_get():
    """Checks that teachers method returns correct list"""
    t1 = Teacher("Jane", "Doe")
    t2 = Teacher("John", "Doe")
    assert t1 in Schedule.teachers()
    assert t2 in Schedule.teachers()

def test_streams_get():
    """Checks that streams method returns correct list"""
    s1 = Stream()
    s2 = Stream()
    assert s1 in Schedule.streams()
    assert s2 in Schedule.streams()

def test_courses_get():
    """Checks that courses method returns correct list"""
    c1 = Course("1", semester="summer")
    c2 = Course("1", semester="summer")
    assert c1 in Schedule.courses()
    assert c2 in Schedule.courses()

def test_labs_get():
    """Checks that labs method returns correct list"""
    l1 = Lab()
    l2 = Lab()
    assert l1 in Schedule.labs()
    assert l2 in Schedule.labs()

def test_conflicts_get():
    """Checks that conflicts method returns correct list"""
    c1 = Conflict(1, [1])
    c2 = Conflict(1, [1])
    assert c1 in Schedule.conflicts()
    assert c2 in Schedule.conflicts()

def test_get_sections_for_teacher():
    """Checks that sections_for_teacher method returns correct sections"""
    t1 = Teacher("Jane", "Doe")
    
    s1 = Section("1")
    s1.add_block(Block('mon', '13:00', 2, 1))
    s1.assign_teacher(t1)
    
    s2 = Section("2")
    s2.add_block(Block('mon', '13:00', 2, 1))
    s2.assign_teacher(t1)

    s3 = Section("3")
    
    sections = Schedule.sections_for_teacher(t1)
    assert s1 in sections
    assert s2 in sections
    assert s3 not in sections

def test_get_courses_for_teacher():
    """Checks that courses_for_teacher method returns correct courses"""
    t1 = Teacher("Jane", "Doe")

    s1 = Section("1")
    s1.add_block(Block('mon', '13:00', 2, 1))
    c1 = Course(1, semester="summer")
    c1.add_section(s1)
    s1.assign_teacher(t1)

    s2 = Section("2")
    s2.add_block(Block('mon', '13:00', 2, 1))
    c2 = Course(2, semester="summer")
    c2.add_section(s1)
    s2.assign_teacher(t1)

    c3 = Course(3, semester="summer")
    
    courses = Schedule.courses_for_teacher(t1)
    assert c1 in courses
    assert c2 in courses
    assert c3 not in courses

def test_get_allocated_courses_for_teacher():
    """Checks that allocated_courses_for_teacher method returns correct courses"""
    t1 = Teacher("Jane", "Doe")

    s1 = Section("1")
    s1.add_block(Block('mon', '13:00', 2, 1))
    c1 = Course(1, semester="summer")
    c1.add_section(s1)
    s1.assign_teacher(t1)

    s2 = Section("2")
    s2.add_block(Block('mon', '13:00', 2, 1))
    c2 = Course(2, semester="summer")
    c2.add_section(s1)
    c2.needs_allocation = False
    s2.assign_teacher(t1)
    
    courses = Schedule.allocated_courses_for_teacher(t1)
    assert c1 in courses
    assert c2 not in courses

def test_get_blocks_for_teacher():
    """Checks that blocks_for_teacher method returns correct sections"""
    t1 = Teacher("Jane", "Doe")
    
    b1 = Block('mon', '13:00', 2, 1)
    b1.assign_teacher(t1)
    
    b2 = Block('mon', '13:00', 2, 1)
    b2.assign_teacher(t1)

    b3 = Block('mon', '13:00', 2, 1)
    
    blocks = Schedule.blocks_for_teacher(t1)
    assert b1 in blocks
    assert b2 in blocks
    assert b3 not in blocks

def test_get_blocks_in_lab():
    """Checks that blocks_in_lab method returns correct sections"""
    l1 = Lab()
    
    b1 = Block('mon', '13:00', 2, 1)
    b1.assign_lab(l1)
    
    b2 = Block('mon', '13:00', 2, 1)
    b2.assign_lab(l1)

    b3 = Block('mon', '13:00', 2, 1)
    
    blocks = Schedule.blocks_in_lab(l1)
    assert b1 in blocks
    assert b2 in blocks
    assert b3 not in blocks

def test_get_sections_for_stream():
    """Checks that sections_for_stream method returns correct sections"""
    st = Stream()

    s1 = Section("1")
    s1.assign_stream(st)

    s2 = Section("2")
    s2.assign_stream(st)

    s3 = Section("3")
    
    sections = Schedule.sections_for_stream(st)
    assert s1 in sections
    assert s2 in sections
    assert s3 not in sections

def test_get_blocks_for_stream():
    """Checks that blocks_for_stream method returns correct sections"""
    st = Stream()

    s1 = Section("1")
    b1 = Block('mon', '13:00', 2, 1)
    s1.add_block(b1)
    s1.assign_stream(st)
    
    s2 = Section("2")
    b2 = Block('mon', '13:00', 2, 1)
    s2.assign_stream(st)
    s2.add_block(b2)

    b3 = Block('mon', '13:00', 2, 1)
    s3 = Section("3")
    s3.add_block(b3)
    
    blocks = Schedule.blocks_for_stream(st)
    assert b1 in blocks
    assert b2 in blocks
    assert b3 not in blocks

def test_course_remove():
    """Checks that courses can be removed"""
    c1 = Course(1, semester="summer")
    Schedule.remove_course(c1)
    assert c1 not in Course.list()

def test_teacher_remove():
    """Checks that teachers can be removed"""
    t1 = Teacher("Jane", "Doe")
    Schedule.remove_teacher(t1)
    assert t1 not in Teacher.list()

def test_lab_remove():
    """Checks that labs can be removed"""
    l1 = Lab()
    Schedule.remove_lab(l1)
    assert l1 not in Lab.list()

def test_stream_remove():
    """Checks that streams can be removed"""
    s1 = Stream()
    Schedule.remove_stream(s1)
    assert s1 not in Stream.list()

def test_calculate_conflicts():
    t1 = Teacher("Jane", "Doe")
    t2 = Teacher("John", "Doe")
    t3 = Teacher("Joe", "Doe")
    t4 = Teacher("J", "D")

    l1 = Lab()
    st1 = Stream()
    s1 = Section()
    s1.assign_stream(st1)

    tue_block = Block('tue', "15:00", 1, 1)
    wed_block = Block('wed', "15:00", 1, 1)
    thu_block = Block('thu', "15:00", 1, 1)

    # TIME_TEACHER conflict
    b1 = Block("mon", "13:00", 2, 1)
    b1.assign_teacher(t1)
    b2 = Block("mon", "14:00", 2, 1)
    b2.assign_teacher(t1)
    tue_block.assign_teacher(t1)
    wed_block.assign_teacher(t1)
    thu_block.assign_teacher(t1)
    time_teacher_conflicted = [b1, b2]

    # TIME_LAB conflict
    b3 = Block("mon", "13:00", 2, 1)
    b3.assign_lab(l1)
    b4 = Block("mon", "14:00", 2, 1)
    b4.assign_lab(l1)
    time_lab_conflicted = [b3, b4]
    
    # TIME_STREAM conflict
    b5 = Block("mon", "13:00", 2, 1)
    b5.section = s1
    b6 = Block("mon", "14:00", 2, 1)
    b6.section = s1
    time_stream_conflicted = [b5, b6]

    # LUNCH conflict
    b7 = Block("mon", "10:30", 2, 1)
    b7.assign_teacher(t2)
    b8 = Block("mon", "12:30", 2, 1)
    b8.assign_teacher(t2)
    tue_block.assign_teacher(t2)
    wed_block.assign_teacher(t2)
    thu_block.assign_teacher(t2)
    lunch_conflicted = [b7, b8]

    # MINIMUM_DAYS conflict
    b7 = Block("mon", "8:30", 2, 1)
    b7.assign_teacher(t3)
    min_days_conflicted = [b7]

    # AVAILABILITY conflict
    b9 = Block("mon", "12:00", 6, 1)
    b9.assign_teacher(t4)
    b10 = Block("tue", "12:00", 6, 1)
    b10.assign_teacher(t4)
    b11 = Block("wed", "12:00", 6, 1)
    b11.assign_teacher(t4)
    b12 = Block("thu", "12:00", 6, 1)
    b12.assign_teacher(t4)
    b13 = Block("fri", "12:00", 6, 1)
    b13.assign_teacher(t4)
    availability_conflicted = [b9, b10, b11, b12, b13]

    Schedule.calculate_conflicts()
    conflict_types = dict()
    conflict_values = dict[int, Conflict]()
    conflict_block_sets = list[list[Block]]
    for i in Conflict:
        if i.type not in conflict_types: conflict_types[i.type] = 0
        conflict_types[i.type] += 1
        conflict_values[i.type] = i
        conflict_block_sets.append(i.blocks)
    
    # check for correct number of instances of each type
    assert conflict_types[Conflict.TIME] == 3   # TIME_TEACHER, TIME_LAB, & TIME_STREAM
    assert conflict_types[Conflict.LUNCH] == 1
    assert conflict_types[Conflict.MINIMUM_DAYS] == 1
    assert conflict_types[Conflict.AVAILABILITY] == 1
    assert len(conflict_block_sets) == 6
    
    # check that each instance points to the correct blocks for non-TIME conflicts
    assert conflict_values[Conflict.LUNCH].blocks == lunch_conflicted
    assert conflict_values[Conflict.MINIMUM_DAYS].blocks == min_days_conflicted
    assert conflict_values[Conflict.AVAILABILITY].blocks == availability_conflicted

    # check that 3 TIME conflict block lists are included in block lists
    assert time_lab_conflicted in conflict_block_sets
    assert time_stream_conflicted in conflict_block_sets
    assert time_teacher_conflicted in conflict_block_sets