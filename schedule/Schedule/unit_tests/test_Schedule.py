import pytest
import sys
from os import path
sys.path.append(path.dirname(path.dirname(__file__)))

from ..ScheduleEnums import ConflictType
from ..LabUnavailableTime import LabUnavailableTime
from ..Block import Block
from ..Section import Section
from ..Conflict import Conflict
from ..Lab import Lab
from ..Course import Course
from ..Stream import Stream
from ..Teacher import Teacher
from ..Schedule import Schedule
from ..ScheduleWrapper import ScheduleWrapper
from ..database.PonyDatabaseConnection import\
    define_database, Schedule as dbSchedule, Scenario as dbScenario, Lab as dbLab, Teacher as dbTeacher, Section_Teacher as dbSecTeach,\
    Course as dbCourse, Section as dbSection, Stream as dbStream, Block as dbBlock, Schedule_Teacher as dbSchedTeach,\
    LabUnavailableTime as dbLUT
from pony.orm import *
from .db_constants import *


db: Database
new_db: Database = None   # only used in write DB test
s: dbSchedule
sc : dbScenario


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    global db
    if PROVIDER == "mysql":
        db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)
    elif PROVIDER == "sqlite":
        db = define_database(provider=PROVIDER, filename=DB_NAME, create_db=CREATE_DB)
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    yield
    db.drop_all_tables(with_all_data=True)
    db.disconnect()
    db.provider = db.schema = None


@db_session
def init_scenario_and_schedule():
    global s
    global sc
    sc = dbScenario(name="Scenario 1", description="First Scenario", semester="W2023", status="Pending")
    flush()
    s = dbSchedule(official=False, scenario_id=sc.id, description="W23")


@pytest.fixture(autouse=True)
def before_and_after():
    db.create_tables()
    init_scenario_and_schedule()
    ScheduleWrapper.reset_local()
    yield
    db.drop_all_tables(with_all_data=True)


def test_teachers_get():
    """Checks that teachers method returns correct list"""
    sched = Schedule(s.id, False, 2, "")
    t1 = Teacher("Jane", "Doe")
    t2 = Teacher("John", "Doe")
    sec1 = Section(course=Course(), schedule_id = sched.id).add_block(Block('mon', '8:00', 3, 3)
                               .assign_teacher(t1))\
                    .add_block(Block('tue', '8:00', 3, 3)
                               .assign_teacher(t2))
    
    sched.sections.append(sec1)

    assert t1 in sched.teachers()
    assert t2 in sched.teachers()


def test_streams_get():
    """Checks that streams method returns correct list"""
    sched = Schedule(s.id, False, 2, "")
    s1 = Stream()
    s2 = Stream()
    sec1 = Section(course=Course(), schedule_id=sched.id).assign_stream(s1, s2)
    
    sched.sections.append(sec1)

    assert s1 in sched.streams()
    assert s2 in sched.streams()


def test_courses_get():
    """Checks that courses method returns correct list"""
    sched = Schedule(s.id, False, 2, "")
    c1 = Course("1")
    c2 = Course("2")
    sec1 = Section(course=c1, schedule_id=sched.id)
    sec2 = Section(course=c2, schedule_id=sched.id)
    sched.sections.extend([sec1, sec2])
    assert c1 in sched.courses()
    assert c2 in sched.courses()


def test_labs_get():
    """Checks that labs method returns correct list"""
    sched = Schedule(s.id, False, 2, "")
    l1 = Lab()
    l2 = Lab()
    sec1 = Section(course=Course(), schedule_id = sched.id).add_block(Block('mon', '8:00', 3, 3)
                               .assign_lab(l1))\
                    .add_block(Block('tue', '8:00', 3, 3)
                               .assign_lab(l2))
    
    sched.sections.append(sec1)

    assert l1 in sched.labs()
    assert l2 in sched.labs()


def test_conflicts_get():
    """Checks that conflicts method returns correct list"""
    sched = Schedule(s.id, False, 2, "")
    b1 = Block('mon', '8:00', 3, 3)
    b2 = Block('tue', '8:00', 3, 3)
    c1 = Conflict(ConflictType.AVAILABILITY, [b1, b2])
    c2 = Conflict(ConflictType.AVAILABILITY, [b1, b2])

    sec1 = Section(course=Course(), schedule_id = sched.id).add_block(b1).add_block(b2)
    
    sched.sections.append(sec1)

    assert c1 in sched.conflicts()
    assert c2 in sched.conflicts()


def test_get_sections_for_teacher():
    """Checks that sections_for_teacher method returns correct sections"""
    t1 = Teacher("Jane", "Doe")
    c = Course()

    s1 = Section("1", course=c, schedule_id=s.id)
    s1.add_block(Block('mon', '13:00', 2, 1))
    s1.assign_teacher(t1)

    s2 = Section("2", course=c, schedule_id=s.id)
    s2.add_block(Block('mon', '13:00', 2, 1))
    s2.assign_teacher(t1)

    s3 = Section("3", course=c, schedule_id=s.id)

    sched = Schedule(s.id, False, 2, "")
    sched.sections.extend([s1, s2, s3])

    sections = sched.sections_for_teacher(t1)
    assert s1 in sections
    assert s2 in sections
    assert s3 not in sections


def test_get_courses_for_teacher():
    """Checks that courses_for_teacher method returns correct courses"""
    t1 = Teacher("Jane", "Doe")
    c = Course(0)

    s1 = Section("1", course=c, schedule_id=s.id)
    s1.add_block(Block('mon', '13:00', 2, 1))
    c1 = Course(1).add_section(s1.assign_teacher(t1))

    s2 = Section("2", course=c, schedule_id=s.id)
    s2.add_block(Block('mon', '13:00', 2, 1))
    c2 = Course(2).add_section(s2)
    s2.assign_teacher(t1)

    c3 = Course(3)

    sched = Schedule(s.id, False, 2, "")
    sched.sections.extend([s1, s2])

    courses = sched.courses_for_teacher(t1)
    assert c1 in courses
    assert c2 in courses
    assert c3 not in courses


def test_get_allocated_courses_for_teacher():
    """Checks that allocated_courses_for_teacher method returns correct courses"""
    t1 = Teacher("Jane", "Doe")
    c = Course()

    s1 = Section("1", course=c, schedule_id=s.id)
    s1.add_block(Block('mon', '13:00', 2, 1))
    c1 = Course(1).add_section(s1.assign_teacher(t1))

    s2 = Section("2", course=c, schedule_id=s.id)
    s2.add_block(Block('mon', '13:00', 2, 1))
    c2 = Course(2)
    c2.add_section(s2)
    c2.needs_allocation = False
    s2.assign_teacher(t1)

    sched = Schedule(s.id, False, 2, "")
    sched.sections.extend([s1, s2])

    courses = sched.allocated_courses_for_teacher(t1)
    assert c1 in courses
    assert c2 not in courses


def test_get_blocks_for_teacher():
    """Checks that blocks_for_teacher method returns correct sections"""
    sched = Schedule(s.id, False, 2, "")
    t1 = Teacher("Jane", "Doe")

    b1 = Block('mon', '13:00', 2, 1)
    b1.assign_teacher(t1)
    s1 = Section(course=Course(), schedule_id=sched.id).add_block(b1)

    b2 = Block('mon', '13:00', 2, 1)
    b2.assign_teacher(t1)
    s2 = Section(course=Course(), schedule_id=sched.id).add_block(b2)

    b3 = Block('mon', '13:00', 2, 1)
    s3 = Section(course=Course(), schedule_id=sched.id).add_block(b3)

    sched.sections.extend([s1, s2, s3])

    blocks = sched.blocks_for_teacher(t1)
    assert b1 in blocks
    assert b2 in blocks
    assert b3 not in blocks


def test_get_blocks_in_lab():
    """Checks that blocks_in_lab method returns correct sections"""
    l1 = Lab()
    sched = Schedule(s.id, False, 2, "")

    b1 = Block('mon', '13:00', 2, 1)
    b1.assign_lab(l1)
    s1 = Section(course=Course(), schedule_id=sched.id).add_block(b1)

    b2 = Block('mon', '13:00', 2, 1)
    b2.assign_lab(l1)
    s2 = Section(course=Course(), schedule_id=sched.id).add_block(b2)

    b3 = Block('mon', '13:00', 2, 1)
    s3 = Section(course=Course(), schedule_id=sched.id).add_block(b3)

    sched.sections.extend([s1, s2, s3])

    blocks = sched.blocks_in_lab(l1)
    assert b1 in blocks
    assert b2 in blocks
    assert b3 not in blocks


def test_get_sections_for_stream():
    """Checks that sections_for_stream method returns correct sections"""
    st = Stream()
    c = Course()

    s1 = Section("1", course=c, schedule_id=s.id)
    s1.assign_stream(st)

    s2 = Section("2", course=c, schedule_id=s.id)
    s2.assign_stream(st)

    s3 = Section("3", course=c, schedule_id=s.id)

    sched = Schedule(s.id, False, 2, "")
    sched.sections.extend([s1, s2, s3])

    sections = sched.sections_for_stream(st)
    assert s1 in sections
    assert s2 in sections
    assert s3 not in sections


def test_get_blocks_for_stream():
    """Checks that blocks_for_stream method returns correct sections"""
    st = Stream()
    c = Course()

    s1 = Section("1", course=c, schedule_id=s.id)
    b1 = Block('mon', '13:00', 2, 1)
    s1.add_block(b1)
    s1.assign_stream(st)

    s2 = Section("2", course=c, schedule_id=s.id)
    b2 = Block('mon', '13:00', 2, 1)
    s2.assign_stream(st)
    s2.add_block(b2)

    b3 = Block('mon', '13:00', 2, 1)
    s3 = Section("3", course=c, schedule_id=s.id)
    s3.add_block(b3)

    sched = Schedule(s.id, False, 2, "")
    sched.sections.extend([s1, s2, s3])

    blocks = sched.blocks_for_stream(st)
    assert b1 in blocks
    assert b2 in blocks
    assert b3 not in blocks


def test_course_remove():
    """Checks that courses can be removed"""
    c1 = Course(1)
    sched = Schedule(s.id, False, 2, "")
    sched.sections.append(Section("1", course=c1, schedule_id=s.id))
    sched.remove_course(c1)
    assert c1 not in sched.courses()


def test_teacher_remove():
    """Checks that teachers can be removed"""
    t1 = Teacher("Jane", "Doe")
    sched = Schedule(s.id, False, 2, "")
    sched.sections.append(
        Section("1", course=Course(), schedule_id=s.id)
        .add_block(Block("mon", '8:00', 3, 3)
                   .assign_teacher(t1))
    )

    sched.remove_teacher(t1)
    assert t1 not in sched.teachers()


def test_lab_remove():
    """Checks that labs can be removed"""
    l1 = Lab()
    sched = Schedule(s.id, False, 2, "")
    sched.sections.append(
        Section("1", course=Course(), schedule_id=s.id)
        .add_block(Block("mon", '8:00', 3, 3)
                   .assign_lab(l1))
    )
    sched.remove_lab(l1)
    assert l1 not in sched.labs()


def test_stream_remove():
    """Checks that streams can be removed"""
    s1 = Stream()
    sched = Schedule(s.id, False, 2, "")
    sched.sections.append(
        Section("1", course=Course(), schedule_id=s.id)
            .assign_stream(s1)
    )
    sched.remove_stream(s1)
    assert s1 not in sched.streams()


def test_calculate_conflicts():
    sched = Schedule(s.id, False, 2, "")
    c = Course()

    # TIME_TEACHER conflict
    s1 = Section('1', course=c, schedule_id=s.id).add_block(
        b1 := Block("mon", "13:00", 2, 1),
        b2 := Block("mon", "14:00", 2, 2),
        Block('tue', "15:00", 1, 50),
        Block('wed', "15:00", 1, 51),
        Block('thu', "15:00", 1, 52)
        ).assign_teacher(Teacher("Jane", "Doe"))
    time_teacher_conflicted = set([b1, b2])

    # TIME_LAB conflict
    s2 = Section('2', course=c, schedule_id=s.id).add_block(
        b3 := Block("mon", "13:00", 2, 3),
        b4 := Block("mon", "14:00", 2, 4)
        ).assign_lab(Lab())
    time_lab_conflicted = set([b3, b4])

    # TIME_STREAM conflict
    s3 = Section('3', course=c, schedule_id=s.id).add_block(
        b5 := Block("mon", "13:00", 2, 5),
        b6 := Block("mon", "14:00", 2, 6)
        ).assign_stream(Stream())
    time_stream_conflicted = set([b5, b6])

    # LUNCH conflict
    s4 = Section('4', course=c, schedule_id=s.id).add_block(
        b7 := Block("mon", "10:30", 4, 7),
        Block('tue', "15:00", 1, 53),
        Block('wed', "15:00", 1, 54),
        Block('thu', "15:00", 1, 55)
        ).assign_teacher(Teacher("John", "Doe"))
    lunch_conflicted = set([b7])

    # MINIMUM_DAYS conflict
    s5 = Section('5', course=c, schedule_id=s.id).add_block(
        b8 := Block("mon", "8:30", 2, 8)
        ).assign_teacher(Teacher("Joe", "Doe"))
    min_days_conflicted = set([b8])

    # AVAILABILITY conflict
    s6 = Section('6', course=c, schedule_id=s.id).add_block(
        b9 := Block("mon", "11:30", 8, 9),
        b10 := Block("tue", "11:30", 8, 10),
        b11 := Block("wed", "11:30", 8, 11),
        b12 := Block("thu", "11:30", 8, 12),
        b13 := Block("fri", "11:30", 8, 13)
        ).assign_teacher(Teacher("J", "D"))
    availability_conflicted = set([b9, b10, b11, b12, b13])

    sched.sections.extend([s1, s2, s3, s4, s5, s6])
    sched.calculate_conflicts()
    conflict_types = dict()
    conflict_values = dict[int, Conflict]()
    conflict_block_sets = list[list[Block]]()
    for i in sched.conflicts():
        print(i.type)
        print(i.blocks)
        if i.type not in conflict_types: conflict_types[i.type] = 0
        conflict_types[i.type] += 1
        conflict_values[i.type] = i
        conflict_block_sets.append(set(i.blocks))

    # check for correct number of instances of each type
    # TIME_TEACHER, TIME_LAB, & TIME_STREAM
    assert conflict_types[ConflictType.TIME] == 3
    assert conflict_types[ConflictType.LUNCH] == 1
    assert conflict_types[ConflictType.MINIMUM_DAYS] == 1
    assert conflict_types[ConflictType.AVAILABILITY] == 1
    assert len(conflict_block_sets) == 6        # 6 total conflicts

    # check that each instance points to the correct blocks for non-TIME conflicts
    assert set(conflict_values[ConflictType.LUNCH].blocks) == lunch_conflicted
    assert set(conflict_values[ConflictType.MINIMUM_DAYS].blocks) == min_days_conflicted
    assert set(conflict_values[ConflictType.AVAILABILITY].blocks) == availability_conflicted

    # check that 3 TIME conflict block lists are included in block lists
    assert time_lab_conflicted in conflict_block_sets
    assert time_stream_conflicted in conflict_block_sets
    assert time_teacher_conflicted in conflict_block_sets


def test_teacher_stats():
    """Checks that the teacher_stats method gives all and only relevant and accurate information"""
    sched = Schedule(s.id, False, 2, "")
    t1 = Teacher("Jane", "Doe")
    c = Course()

    tue_block = Block('tue', "15:00", 1, 50)
    wed_block = Block('wed', "15:00", 1, 51)
    thu_block = Block('thu', "15:00", 1, 52)

    s1 = Section("S1", course=c, schedule_id=s.id)
    s2 = Section("S2", course=c, schedule_id=s.id)
    s1.add_block(tue_block)
    s2.add_block(wed_block)
    s2.add_block(thu_block)

    c1 = Course("C1", "Course #1")
    Course("C2", "Course #2")
    c1.add_section(s1, s2)

    c1.assign_teacher(t1)
    c1.assign_teacher(t1)

    sched.sections.extend([s1, s2])
    stats = sched.teacher_stat(t1)

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
    sched = Schedule(s.id, False, 2, "")
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

    s1 = Section("S1", course=c, schedule_id=s.id)
    s2 = Section("S2", course=c, schedule_id=s.id)
    s1.add_block(tue_block)
    s2.add_block(wed_block)
    s2.add_block(thu_block)

    c1 = Course("C1", "Course #1")
    Course("C2", "Course #2")
    c1.add_section(s1, s2)

    c1.assign_teacher(t1)
    c1.assign_teacher(t1)

    sched.sections.extend([s1, s2])
    dets = sched.teacher_details(t1)

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
    sched = Schedule(s.id, False, 2, "")
    t1 = Teacher("Jane", "Doe")
    c = Course()

    tue_block = Block('tue', "15:00", 1, 50).assign_lab(Lab())
    wed_block = Block('wed', "15:00", 1, 51).assign_lab(Lab())
    thu_block = Block('thu', "15:00", 1, 52).assign_lab(Lab())

    s1 = Section("S1", course=c, schedule_id=s.id)\
        .add_block(tue_block)\
        .assign_stream(Stream())
    s2 = Section("S2", course=c, schedule_id=s.id)\
        .add_block(wed_block, thu_block)\
        .assign_stream(Stream())

    c1 = Course("C1", "Course #1").add_section(s1, s2)\
        .assign_teacher(t1).assign_teacher(t1)

    sched.sections.extend([s1, s2])
    sched.clear_all_from_course(c1)

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
    s1 = Section("S1", course=c, schedule_id=s.id)

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
def populate_db(sid: int = None):
    """Populates the DB with dummy data"""
    if not sid: sid = s.id
    c1 = dbCourse(name="Course 1", number="101-NYA", semester=1, allocation=True)
    c2 = dbCourse(name="Course 2", number="102-NYA", semester=2, allocation=False)
    c3 = dbCourse(name="Course 3", number="103-NYA", semester=3, allocation=True)
    c4 = dbCourse(name="Course 4", number="104-NYA", semester=4, allocation=False)
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

    lut1 = dbLUT(day="mon", duration=1, start="8:00", lab_id=l1.id, schedule_id=sid)
    se1 = dbSection(course_id=c1.id, schedule_id=sid, name="Section 1", number="SE1", num_students=10)
    se2 = dbSection(course_id=c2.id, schedule_id=sid, name="Section 2", number="SE2", num_students=20)
    se3 = dbSection(course_id=c3.id, schedule_id=sid, name="Section 3", number="SE3", num_students=30)
    se4 = dbSection(course_id=c4.id, schedule_id=sid, name="Section 4", number="SE4", num_students=40)
    se1.streams.add(st1)
    se2.streams.add(st2)
    se3.streams.add(st3)
    se4.streams.add(st4)
    dbSchedTeach(teacher_id=t1.id, schedule_id=sid, work_release=3)
    dbSchedTeach(teacher_id=t2.id, schedule_id=sid, work_release=4)
    dbSchedTeach(teacher_id=t3.id, schedule_id=sid, work_release=5)
    flush()

    dbSecTeach(teacher_id=t1.id, section_id=se1.id, allocation=3)
    dbSecTeach(teacher_id=t2.id, section_id=se2.id, allocation=4)
    dbSecTeach(teacher_id=t3.id, section_id=se3.id, allocation=5)
    b1 = dbBlock(section_id=se1.id, day="tue", duration=2, start="9:00", number=1)
    b2 = dbBlock(section_id=se2.id, day="wed", duration=3, start="10:00", number=2)
    b3 = dbBlock(section_id=se4.id, day="wed", duration=2, start="11:00", number=3)
    b1.teachers.add(t1)
    b2.teachers.add(t2)
    b3.teachers.add(t2)
    b1.labs.add(l1)
    b2.labs.add(l2)
    b3.labs.add(l3)
    flush()

    # return IDs of each created object, in case they need to be identified in tests
    return {
        "c1": c1.id, "c2": c2.id, "c3": c3.id, "c4": c4.id,
        "st1": st1.id, "st2": st2.id, "st3": st3.id, "st4": st4.id,
        "t1": t1.id, "t2": t2.id, "t3": t3.id,
        "l1": l1.id, "l2": l2.id, "l3": l3.id, "lut1": lut1.id,
        "se1": se1.id, "se2": se2.id, "se3": se3.id, "se4": se4.id,
        "b1": b1.id, "b2": b2.id, "b3": b3.id,
    }


def test_read_db():
    """Checks that the read_DB method correctly reads the database and creates required model objects & conflict"""
    populate_db()
    ScheduleWrapper.reset_local()

    schedule = Schedule.read_DB(1)

    assert len(schedule.courses()) == 4
    for i, c in enumerate(sorted(schedule.courses(), key=lambda a: a.id)):
        assert len(c.sections()) == 1
        assert c.semester == i + 1

    assert len(schedule.streams()) == 4

    assert len(schedule.teachers()) == 3
    for t in schedule.teachers():
        assert t.release

    assert len(schedule.lab_unavailable_times()) == 1
    lut = LabUnavailableTime.get(1)
    assert lut.day and lut.start and lut.duration
    assert len(schedule.labs()) == 3
    assert Lab.get(1).get_unavailable(1)

    assert len(schedule.sections) == 4
    for se in schedule.sections:
        assert len(se.teachers) == 1
        assert len(se.streams) == 1

    assert len(schedule.blocks()) == 3
    for b in schedule.blocks():
        assert len(b.teachers()) == 1
        assert len(b.labs()) == 1
        assert b.day and b.start and b.duration
    
    assert len(schedule.conflicts()) == 1
    assert schedule.conflicts()[0].type == ConflictType.TIME
    assert Block.get(2).conflicted
    assert Block.get(3).conflicted

    assert schedule
    assert schedule.id == s.id
    assert schedule.official == s.official
    assert schedule.scenario_id == 1 # CHECK HARDCODED VALUE; model Schedule holds a # while entity Schedule holds an object
    assert schedule.descr == s.description


@pytest.fixture
def after_write():
    # reconnects to the original DB. run after test_write_db
    global new_db
    global db
    yield
    if new_db:  # if the test fails before setting new_db, don't bother running this
        # drop all tables to be safe
        new_db.drop_all_tables(with_all_data=True)
        new_db.disconnect()
        new_db.provider = new_db.schema = None
        db = define_database(host=HOST, passwd=PASSWD,
                             db=DB_NAME, provider=PROVIDER, user=USERNAME)


def test_write_db(after_write):
    """
    Checks that the write_DB method correctly writes to the database
    NOTE: THIS TEST WILL LIKELY FAIL IF THE ABOVE TEST FAILS
    IF THEY BOTH FAIL, FIX THE ABOVE ONE FIRST
    """
    global db
    global new_db
    ids = populate_db()
    ScheduleWrapper.reset_local()
    schedule = Schedule.read_DB(1)

    # disconnect from existing database
    db.disconnect()
    db.provider = db.schema = None

    # create a new test DB
    db_name = DB_NAME + "_write_test"
    new_db = define_database(host=HOST, passwd=PASSWD,
                             db=db_name, provider=PROVIDER, user=USERNAME)
    # ensure that there's no existing data
    new_db.drop_all_tables(with_all_data=True)
    new_db.create_tables()

    # write to the new DB
    schedule.write_DB()
    
    ScheduleWrapper.reset_local()
    # to avoid having to query the DB here, rely on read_DB again
    # if read_DB breaks, this test will fail
    new_schedule = Schedule.read_DB(1)

    # confirm schedule data was transferred correctly
    assert new_schedule
    assert new_schedule.id == schedule.id
    assert new_schedule.descr == schedule.descr
    assert new_schedule.official == schedule.official
    assert new_schedule.scenario_id == schedule.scenario_id

    # confirm correct number of courses and data was transferred correctly
    assert len(schedule.courses()) == 4
    for i, c in enumerate(sorted(schedule.courses(), key=lambda a: a.id)):
        assert len(c.sections()) == 1
        assert c.name == f"Course {i+1}"
        assert c.number == f"10{i+1}-NYA"
        assert c.needs_allocation == (0 == i % 2)
        assert c.semester == i + 1

    # confirm correct number of streams and data was transferred correctly
    assert len(schedule.streams()) == 4
    for i, st in enumerate(sorted(schedule.streams(), key=lambda a: a.id)):
        assert st.number == f"3{chr(i + 65)}"
        assert st.descr == f"Stream #{i + 1}"

    # confirm correct number of teachers and data was transferred correctly
    assert len(schedule.teachers()) == 3
    for i, t in enumerate(sorted(schedule.teachers(), key=lambda a: a.id)):
        assert t.release == i + 3
        assert t.firstname.startswith(str(i))
        assert t.lastname.startswith(str(i))
        assert t.dept.startswith(str(i))

    # confirm correct number of labs and data was transferred correctly
    assert len(schedule.labs()) == 3
    assert Lab.get(1).get_unavailable(ids.get("lut1"))
    for i, l in enumerate(sorted(schedule.labs(), key=lambda a: a.id)):
        assert l.number == f"P32{i}"
        assert l.descr == f"Computer Lab {i+1}"

    # confirm correct number of sections and data was transferred correctly
    assert len(schedule.sections) == 4
    for i, se in enumerate(schedule.sections):
        assert len(se.teachers) == 1
        assert len(se.streams) == 1
        assert se.course.id == i+1
        assert se.name == f"Section {i+1}"
        assert se.number == f"SE{i+1}"
        assert se.num_students == (i+1)*10

    # confirm correct number of blocks and data was transferred correctly
    assert len(schedule.blocks()) == 3
    for i, b in enumerate(sorted(schedule.blocks(), key=lambda a: a.id)):
        assert len(b.teachers()) == 1
        assert len(b.labs()) == 1
        assert b.number == i+1
        assert b.start == f"{i+9}:00"
        assert b.duration == (i % 2)+2
    assert Block.get(1).day == "tue"
    assert Block.get(2).day == "wed"
    assert Block.get(2).movable
