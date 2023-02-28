import sys
from os import path
sys.path.append(path.dirname(path.dirname(__file__)))
import pytest
from unit_tests.db_constants import *
from pony.orm import *
from database.PonyDatabaseConnection import\
    define_database, Schedule as dbSchedule, Scenario as dbScenario, Lab as dbLab, Teacher as dbTeacher, Section_Teacher as dbSecTeach,\
    Course as dbCourse, TimeSlot as dbTimeSlot, Section as dbSection, Stream as dbStream, Block as dbBlock, Schedule_Teacher as dbSchedTeach

from Schedule import Schedule
from Teacher import Teacher
from Stream import Stream
from Course import Course
from Lab import Lab
from Conflict import Conflict
from Section import Section
from Block import Block
from Time_slot import TimeSlot

db : Database
new_db : Database   # only used in write DB test
s : Schedule

@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    global db
    db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    init_scenario_and_schedule()
    yield
    db.drop_all_tables(with_all_data = True)
    db.disconnect()
    db.provider = db.schema = None

@db_session
def init_scenario_and_schedule():
    global s
    sc = dbScenario()
    flush()
    s = dbSchedule(semester="Winter 2023", official=False, scenario_id=sc.id, description="W23")

@pytest.fixture(autouse=True)
def before_and_after():
    db.create_tables()
    Block.reset()
    yield
    db.drop_all_tables(with_all_data=True)

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
    c1 = Course("1")
    c2 = Course("1")
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
    c = Course()
    
    s1 = Section("1", course=c, schedule_id=1)
    s1.add_block(Block('mon', '13:00', 2, 1))
    s1.assign_teacher(t1)
    
    s2 = Section("2", course=c, schedule_id=1)
    s2.add_block(Block('mon', '13:00', 2, 1))
    s2.assign_teacher(t1)

    s3 = Section("3", course=c, schedule_id=1)
    
    sections = Schedule.sections_for_teacher(t1)
    assert s1 in sections
    assert s2 in sections
    assert s3 not in sections

def test_get_courses_for_teacher():
    """Checks that courses_for_teacher method returns correct courses"""
    t1 = Teacher("Jane", "Doe")
    c = Course()

    s1 = Section("1", course=c, schedule_id=1)
    s1.add_block(Block('mon', '13:00', 2, 1))
    c1 = Course(1)
    c1.add_section(s1)
    s1.assign_teacher(t1)

    s2 = Section("2", course=c, schedule_id=1)
    s2.add_block(Block('mon', '13:00', 2, 1))
    c2 = Course(2)
    c2.add_section(s1)
    s2.assign_teacher(t1)

    c3 = Course(3)
    
    courses = Schedule.courses_for_teacher(t1)
    assert c1 in courses
    assert c2 in courses
    assert c3 not in courses

def test_get_allocated_courses_for_teacher():
    """Checks that allocated_courses_for_teacher method returns correct courses"""
    t1 = Teacher("Jane", "Doe")
    c = Course()

    s1 = Section("1", course=c, schedule_id=1)
    s1.add_block(Block('mon', '13:00', 2, 1))
    c1 = Course(1)
    c1.add_section(s1)
    s1.assign_teacher(t1)

    s2 = Section("2", course=c, schedule_id=1)
    s2.add_block(Block('mon', '13:00', 2, 1))
    c2 = Course(2)
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
    c = Course()

    s1 = Section("1", course=c, schedule_id=1)
    s1.assign_stream(st)

    s2 = Section("2", course=c, schedule_id=1)
    s2.assign_stream(st)

    s3 = Section("3", course=c, schedule_id=1)
    
    sections = Schedule.sections_for_stream(st)
    assert s1 in sections
    assert s2 in sections
    assert s3 not in sections

def test_get_blocks_for_stream():
    """Checks that blocks_for_stream method returns correct sections"""
    st = Stream()
    c = Course()

    s1 = Section("1", course=c, schedule_id=1)
    b1 = Block('mon', '13:00', 2, 1)
    s1.add_block(b1)
    s1.assign_stream(st)
    
    s2 = Section("2", course=c, schedule_id=1)
    b2 = Block('mon', '13:00', 2, 1)
    s2.assign_stream(st)
    s2.add_block(b2)

    b3 = Block('mon', '13:00', 2, 1)
    s3 = Section("3", course=c, schedule_id=1)
    s3.add_block(b3)
    
    blocks = Schedule.blocks_for_stream(st)
    assert b1 in blocks
    assert b2 in blocks
    assert b3 not in blocks

def test_course_remove():
    """Checks that courses can be removed"""
    c1 = Course(1)
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
    c = Course()

    l1 = Lab()
    st1 = Stream()
    s1 = Section(course=c, schedule_id=1)
    s1.assign_stream(st1)

    tue_block = Block('tue', "15:00", 1, 50)
    wed_block = Block('wed', "15:00", 1, 51)
    thu_block = Block('thu', "15:00", 1, 52)

    # TIME_TEACHER conflict
    b1 = Block("mon", "13:00", 2, 1)
    b1.assign_teacher(t1)
    b2 = Block("mon", "14:00", 2, 2)
    b2.assign_teacher(t1)
    tue_block.assign_teacher(t1)
    wed_block.assign_teacher(t1)
    thu_block.assign_teacher(t1)
    time_teacher_conflicted = set([b1, b2])

    # TIME_LAB conflict
    b3 = Block("mon", "13:00", 2, 3)
    b3.assign_lab(l1)
    b4 = Block("mon", "14:00", 2, 4)
    b4.assign_lab(l1)
    time_lab_conflicted = set([b3, b4])
    
    # TIME_STREAM conflict
    b5 = Block("mon", "13:00", 2, 5)
    b5.section = s1
    b6 = Block("mon", "14:00", 2, 6)
    b6.section = s1
    time_stream_conflicted = set([b5, b6])

    # LUNCH conflict
    b7 = Block("mon", "10:30", 4, 7)
    b7.assign_teacher(t2)
    tue_block.assign_teacher(t2)
    wed_block.assign_teacher(t2)
    thu_block.assign_teacher(t2)
    lunch_conflicted = set([b7])

    # MINIMUM_DAYS conflict
    b8 = Block("mon", "8:30", 2, 8)
    b8.assign_teacher(t3)
    min_days_conflicted = set([b8])

    # AVAILABILITY conflict
    b9 = Block("mon", "11:30", 8, 9)
    b9.assign_teacher(t4)
    b10 = Block("tue", "11:30", 8, 10)
    b10.assign_teacher(t4)
    b11 = Block("wed", "11:30", 8, 11)
    b11.assign_teacher(t4)
    b12 = Block("thu", "11:30", 8, 12)
    b12.assign_teacher(t4)
    b13 = Block("fri", "11:30", 8, 13)
    b13.assign_teacher(t4)
    availability_conflicted = set([b9, b10, b11, b12, b13])

    Schedule.calculate_conflicts()
    conflict_types = dict()
    conflict_values = dict[int, Conflict]()
    conflict_block_sets = list[list[Block]]()
    for i in Conflict.list():
        if i.type not in conflict_types: conflict_types[i.type] = 0
        conflict_types[i.type] += 1
        conflict_values[i.type] = i
        conflict_block_sets.append(set(i.blocks))

    # check for correct number of instances of each type
    assert conflict_types[Conflict.TIME] == 3   # TIME_TEACHER, TIME_LAB, & TIME_STREAM
    assert conflict_types[Conflict.LUNCH] == 1
    assert conflict_types[Conflict.MINIMUM_DAYS] == 1
    assert conflict_types[Conflict.AVAILABILITY] == 1
    assert len(conflict_block_sets) == 6        # 6 total conflicts
    
    # check that each instance points to the correct blocks for non-TIME conflicts
    assert set(conflict_values[Conflict.LUNCH].blocks) == lunch_conflicted
    assert set(conflict_values[Conflict.MINIMUM_DAYS].blocks) == min_days_conflicted
    assert set(conflict_values[Conflict.AVAILABILITY].blocks) == availability_conflicted

    # check that 3 TIME conflict block lists are included in block lists
    assert time_lab_conflicted in conflict_block_sets
    assert time_stream_conflicted in conflict_block_sets
    assert time_teacher_conflicted in conflict_block_sets

def test_teacher_stats():
    """Checks that the teacher_stats method gives all and only relevant and accurate information"""
    t1 = Teacher("Jane", "Doe")
    c = Course()

    tue_block = Block('tue', "15:00", 1, 50)
    wed_block = Block('wed', "15:00", 1, 51)
    thu_block = Block('thu', "15:00", 1, 52)

    s1 = Section("S1", course=c, schedule_id=1)
    s2 = Section("S2", course=c, schedule_id=1)
    s1.add_block(tue_block)
    s2.add_block(wed_block)
    s2.add_block(thu_block)

    c1 = Course("C1", "Course #1")
    Course("C2", "Course #2")
    c1.add_section(s1)
    c1.add_section(s2)

    c1.assign_teacher(t1)
    c1.assign_teacher(t1)

    stats = Schedule.teacher_stat(t1)
    
    assert "Jane Doe's Stats" in stats

    assert "Tuesday" in stats
    assert "Wednesday" in stats
    assert "Thursday" in stats
    assert "Monday" not in stats
    assert "Friday" not in stats
    
    assert "Hours of Work: 3" in stats  # 3.0
    assert "Course #1" in stats
    assert "Course #2" not in stats
    assert "2 Section(s)" in stats

def test_teacher_details():
    """Checks that the teacher_details method gives all and only relevant and accurate information"""
    t1 = Teacher("Jane", "Doe")
    c = Course()

    l1 = Lab("P327")
    l2 = Lab("P326")
    l3 = Lab("P325")

    tue_block = Block('tue', "12:00", 2.5, 50)
    tue_block.assign_lab(l1)
    tue_block.assign_lab(l2)
    wed_block = Block('wed', "8:30", 3, 51)
    wed_block.assign_lab(l2)
    thu_block = Block('thu', "14:00", 1, 52)
    thu_block.assign_lab(l3)

    s1 = Section("S1", course=c, schedule_id=1)
    s2 = Section("S2", course=c, schedule_id=1)
    s1.add_block(tue_block)
    s2.add_block(wed_block)
    s2.add_block(thu_block)

    c1 = Course("C1", "Course #1")
    Course("C2", "Course #2")
    c1.add_section(s1)
    c1.add_section(s2)

    c1.assign_teacher(t1)
    c1.assign_teacher(t1)

    dets = Schedule.teacher_details(t1)
    
    assert "Jane Doe" in dets

    assert "Course #1" in dets
    assert "Course #2" not in dets
    assert "Section S1" in dets
    assert "Section S2" in dets

    assert tue_block.day in dets
    assert tue_block.start in dets
    assert str(tue_block.duration) in dets
    assert wed_block.day in dets
    assert wed_block.start in dets
    assert str(wed_block.duration) in dets
    assert thu_block.day in dets
    assert thu_block.start in dets
    assert str(thu_block.duration) in dets

    assert str(l1) in dets
    assert str(l2) in dets
    assert str(l3) in dets
    assert f"{l1}, {l2}" in dets

def test_clear_Course():
    """Checks that the clear_all_from_course method correctly clears course"""
    t1 = Teacher("Jane", "Doe")
    c = Course()

    tue_block = Block('tue', "15:00", 1, 50)
    wed_block = Block('wed', "15:00", 1, 51)
    thu_block = Block('thu', "15:00", 1, 52)

    tue_block.assign_lab(Lab())
    wed_block.assign_lab(Lab())
    thu_block.assign_lab(Lab())

    s1 = Section("S1", course=c, schedule_id=1)
    s2 = Section("S2", course=c, schedule_id=1)
    s1.add_block(tue_block)
    s2.add_block(wed_block)
    s2.add_block(thu_block)

    s1.assign_stream(Stream())
    s2.assign_stream(Stream())

    c1 = Course("C1", "Course #1")
    c1.add_section(s1)
    c1.add_section(s2)

    c1.assign_teacher(t1)
    c1.assign_teacher(t1)

    Schedule.clear_all_from_course(c1)

    assert len(c1.sections()) == 2
    assert len(s1.blocks) == 1
    assert len(s2.blocks) == 2
    assert not s1.teachers
    assert not s2.teachers
    assert not s1.streams
    assert not s2.streams
    assert not s1.labs
    assert not s2.labs

def test_clear_section():
    """Checks that the clear_all_from_section method correctly clears section"""
    c = Course()
    s1 = Section("S1", course=c, schedule_id=1)
    
    tue_block = Block('tue', "15:00", 1, 50)
    tue_block.assign_lab(Lab())
    s1.add_block(tue_block)
    s1.add_block(Block('wed', "15:00", 1, 51))
    s1.add_block(Block('thu', "15:00", 1, 52))

    s1.assign_stream(Stream())

    s1.assign_teacher(Teacher("Jane", "Doe"))

    Schedule.clear_all_from_section(s1)

    assert len(s1.blocks) == 3
    assert not s1.teachers
    assert not s1.streams
    assert not s1.labs

def test_clear_block():
    """Checks that the clear_all_from_block method correctly clears block"""    
    b1 = Block('tue', "15:00", 1, 50)
    b1.assign_lab(Lab())
    b1.assign_teacher(Teacher("Jane", "Doe"))

    Schedule.clear_all_from_block(b1)

    assert not b1.teachers()
    assert not b1.labs()

@db_session
def populate_db(sid : int = None):
    """Populates the DB with dummy data"""
    if not sid: sid = s.id
    c1 = dbCourse(name="Course 1", number="101-NYA", allocation=True)
    c2 = dbCourse(name="Course 2", number="102-NYA", allocation=False)
    c3 = dbCourse(name="Course 3", number="103-NYA", allocation=True)
    c4 = dbCourse(name="Course 4", number="104-NYA", allocation=False)
    st1 = dbStream(number="3A", descr="Stream #1")
    st2 = dbStream(number="3B", descr="Stream #2")
    st3 = dbStream(number="3C", descr="Stream #3")
    st4 = dbStream(number="3D", descr="Stream #4")
    t1 = dbTeacher(first_name="0Jane", last_name="0Doe", dept="0Computer Science")
    t2 = dbTeacher(first_name="1John", last_name="1Doe", dept="1English")
    t3 = dbTeacher(first_name="2Joe", last_name="2Smith", dept="2Science")
    l1 = dbLab(number="P320", description="Computer Lab 1")
    l2 = dbLab(number="P321", description="Computer Lab 2")
    l3 = dbLab(number="P322", description="Computer Lab 3")
    flush()

    ts1 = dbTimeSlot(day="mon", duration=1, start="8:00", unavailable_lab_id=l1.id)
    ts2 = dbTimeSlot(day="tue", duration=2, start="8:00", movable = False)
    ts3 = dbTimeSlot(day="wed", duration=3, start="9:00")
    ts4 = dbTimeSlot(day="wed", duration=3, start="10:00")
    se1 = dbSection(course_id=c1.id, schedule_id=sid, name="Section 1", number="SE1", num_students=10)
    se2 = dbSection(course_id=c2.id, schedule_id=sid, name="Section 2", number="SE2", num_students=20)
    se3 = dbSection(course_id=c3.id, schedule_id=sid, name="Section 3", number="SE3", num_students=30)
    se4 = dbSection(course_id=c4.id, schedule_id=sid, name="Section 4", number="SE4", num_students=40)
    se1.streams.add(st1)
    se2.streams.add(st2)
    se3.streams.add(st3)
    se4.streams.add(st4)
    sc_te1 = dbSchedTeach(teacher_id=t1.id, schedule_id=sid, work_release=3)
    sc_te2 = dbSchedTeach(teacher_id=t2.id, schedule_id=sid, work_release=4)
    sc_te3 = dbSchedTeach(teacher_id=t3.id, schedule_id=sid, work_release=5)
    flush()

    se_te1 = dbSecTeach(teacher_id=t1.id, section_id=se1.id, allocation=3)
    se_te2 = dbSecTeach(teacher_id=t2.id, section_id=se2.id, allocation=4)
    se_te3 = dbSecTeach(teacher_id=t3.id, section_id=se3.id, allocation=5)
    b1 = dbBlock(section_id=se1.id, time_slot_id=ts2.id, number=1)
    b2 = dbBlock(section_id=se2.id, time_slot_id=ts3.id, number=2)
    b3 = dbBlock(section_id=se4.id, time_slot_id=ts4.id, number=3)
    b1.teachers.add(t1)
    b2.teachers.add(t2)
    b3.teachers.add(t2)
    b1.labs.add(l1)
    b2.labs.add(l2)
    b3.labs.add(l3)
    flush()

    return {
        "c1": c1.id, "c2": c2.id, "c3": c3.id, "c4": c4.id,
        "st1": st1.id, "st2": st2.id, "st3": st3.id, "st4": st4.id,
        "t1": t1.id, "t2": t2.id, "t3": t3.id,
        "l1": l1.id, "l2": l2.id, "l3": l3.id,
        "ts1": ts1.id, "ts2": ts2.id, "ts3": ts3.id, "ts4": ts4.id,
        "se1": se1.id, "se2": se2.id, "se3": se3.id, "se4": se4.id,
        "b1": b1.id, "b2": b2.id, "b3": b3.id,
    }

def test_read_db():
    """Checks that the read_DB method correctly reads the database and creates required model objects & conflict"""
    populate_db()

    schedule = Schedule.read_DB(1)

    assert len(TimeSlot.list()) == 4
    
    assert len(Course.list()) == 4
    for c in Course.list(): assert len(c.sections()) == 1
    assert len(Stream.list()) == 4
    assert len(Teacher.list()) == 3
    for t in Teacher.list(): assert t.release
    assert len(Lab.list()) == 3
    assert Lab.get(1).get_unavailable(1)

    assert len(Section.list()) == 4
    for se in Section.list():
        assert len(se.teachers) == 1
        assert len(se.streams) == 1

    assert len(Block.list()) == 3
    for b in Block.list():
        assert len(b.teachers()) == 1
        assert len(b.labs()) == 1
    
    for c in Conflict.list(): print(c.type)
    assert len(Conflict.list()) == 1
    assert Conflict.list()[0].type == Conflict.TIME
    assert Block.list()[1].conflicted
    assert Block.list()[2].conflicted

    assert schedule
    assert schedule.id == s.id

@pytest.fixture
def after_write():
    # reconnects to the original DB. run after test_write_db
    global new_db
    global db
    yield
    #new_db.drop_all_tables(with_all_data=True)  # drop all tables to be safe
    new_db.disconnect()
    new_db.provider = new_db.schema = None
    db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)

def test_write_db(after_write):
    """
    Checks that the write_DB method correctly writes to the database
    NOTE: THIS TEST WILL LIKELY FAIL IF THE ABOVE TEST FAILS
    IF THEY BOTH FAIL, FIX THE ABOVE ONE FIRST
    """
    global db
    global new_db
    ids = populate_db()
    schedule = Schedule.read_DB(1)

    # disconnect from existing database
    db.disconnect()
    db.provider = db.schema = None

    # create a new test DB
    db_name = DB_NAME + "_write_test"
    new_db = define_database(host=HOST, passwd=PASSWD, db=db_name, provider=PROVIDER, user=USERNAME)
    # ensure that there's no existing data
    new_db.drop_all_tables(with_all_data=True)
    new_db.create_tables()

    # write to the new DB
    schedule.write_DB()

    # to avoid having to query the DB here, rely on read_DB again
    # if read_DB breaks, this test will fail
    new_schedule = Schedule.read_DB(1)

    # confirm schedule data was transferred correctly
    assert new_schedule
    assert new_schedule.id == schedule.id
    assert new_schedule.descr == schedule.descr
    assert new_schedule.official == schedule.official
    assert new_schedule.semester == schedule.semester
    assert new_schedule.scenario == schedule.scenario

    # confirm correct number of courses and data was transferred correctly
    assert len(Course.list()) == 4
    for i, c in enumerate(Course.list()):
        assert len(c.sections()) == 1
        assert c.name == f"Course {i+1}"
        assert c.number == f"10{i+1}-NYA"
        assert c.needs_allocation == (0 == i%2)

    # confirm correct number of streams and data was transferred correctly
    assert len(Stream.list()) == 4
    for i, st in enumerate(Stream.list()):
        assert st.number == f"3{chr(i + 65)}"
        assert st.descr == f"Stream #{i + 1}"

    # confirm correct number of teachers and data was transferred correctly
    assert len(Teacher.list()) == 3
    for i, t in enumerate(Teacher.list()):
        assert t.release == i + 3
        assert t.firstname.startswith(str(i))
        assert t.lastname.startswith(str(i))
        assert t.dept.startswith(str(i))

    # confirm correct number of labs and data was transferred correctly
    assert len(Lab.list()) == 3
    assert Lab.get(1).get_unavailable(ids.get("ts1"))
    for i, l in enumerate(Lab.list()):
        assert l.number == f"P32{i}"
        assert l.descr == f"Computer Lab {i+1}"

    # confirm correct number of sections and data was transferred correctly
    assert len(Section.list()) == 4
    for i, se in enumerate(Section.list()):
        assert len(se.teachers) == 1
        assert len(se.streams) == 1
        assert se.course.id == i+1
        assert se.name == f"Section {i+1}"
        assert se.number == f"SE{i+1}"
        assert se.num_students == (i+1)*10

    # confirm correct number of blocks and data was transferred correctly
    assert len(Block.list()) == 3
    for i, b in enumerate(Block.list()):
        assert len(b.teachers()) == 1
        assert len(b.labs()) == 1
        assert b.number == i+1
        
        # time slot values
        assert b.duration == max(i+1, 3)
        assert b.start == f"{i+9}:00"
    assert not Block.list()[0].movable