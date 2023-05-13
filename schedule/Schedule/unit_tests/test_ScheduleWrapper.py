import pytest
import sys
from os import path
sys.path.append(path.dirname(path.dirname(__file__)))

from ..ScheduleEnums import ConflictType
from ..LabUnavailableTime import LabUnavailableTime
from ..Block import Block
from ..Lab import Lab
from ..Course import Course
from ..Stream import Stream
from ..Teacher import Teacher
from ..Schedule import Schedule
from ..ScheduleWrapper import ScheduleWrapper, scenarios
from ..database.PonyDatabaseConnection import define_database, Schedule as dbSchedule,\
    Scenario as dbScenario, Lab as dbLab, Teacher as dbTeacher, Course as dbCourse, Stream as dbStream
from pony.orm import *
from .db_constants import *

from .test_Schedule import populate_db as full_populate_db

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
    t3 = dbTeacher(first_name="3Jenna", last_name="3Smith", dept="3Math")
    l1 = dbLab(number="P320", description="Computer Lab 1")
    l2 = dbLab(number="P321", description="Computer Lab 2")
    l3 = dbLab(number="P322", description="Computer Lab 3")
    l3 = dbLab(number="P323", description="Computer Lab 4")

    # return IDs of each created object, in case they need to be identified in tests
    return {
        "c1": c1.id, "c2": c2.id, "c3": c3.id, "c4": c4.id,
        "st1": st1.id, "st2": st2.id, "st3": st3.id, "st4": st4.id,
        "t1": t1.id, "t2": t2.id, "t3": t3.id,
        "l1": l1.id, "l2": l2.id, "l3": l3.id
    }

def test_constructor():
    """Verifies that the constructor correctly populates the top-level model classes"""
    populate_db()
    sw = ScheduleWrapper()

    assert Course.list()
    assert Lab.list()
    assert Teacher.list()
    assert Stream.list()

def test_constructor_doesnt_double_populate():
    """Verifies that the constructor doesn't repopulate the top-level model classes if it's already been populated"""
    populate_db()
    sw = ScheduleWrapper()

    sw2 = ScheduleWrapper()
    assert len(Course.list()) == 4
    assert len(Lab.list()) == 4
    assert len(Teacher.list()) == 4
    assert len(Stream.list()) == 4

def test_load_schedule():
    """Verifies that the load_schedule method correctly loads a schedule"""
    full_populate_db(s.id)
    sw = ScheduleWrapper()
    schedule = sw.load_schedule(s.id, 'winter')

    assert len(schedule._courses()) == 4
    for i, c in enumerate(sorted(schedule._courses(), key=lambda a: a.id)):
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

def test_reset_local():
    """Verifies that reset local correctly wipes the local top-level model lists"""
    populate_db()
    sw = ScheduleWrapper()
    ScheduleWrapper.reset_local()
    assert len(Course.list()) == 0
    assert len(Lab.list()) == 0
    assert len(Teacher.list()) == 0
    assert len(Stream.list()) == 0

def test_read_DB():
    """Verifies that the read DB method correctly loads top-level model data"""
    populate_db()
    ScheduleWrapper.read_DB()

    assert len(Course.list()) == 4
    for i, c in enumerate(Course.list()):
        assert c.semester == i + 1
        assert c.number == f"10{i + 1}-NYA"
        assert c.name == f"Course {i + 1}"
        assert c.needs_allocation != bool(i % 2)

    assert len(Stream.list()) == 4
    for i, s in enumerate(Stream.list()):
        assert s.number == f"3{chr(i + 65)}"
        assert s.descr == f"Stream #{i + 1}"

    assert len(Teacher.list()) == 4
    for i, t in enumerate(Teacher.list()):
        assert t.firstname.startswith(str(i))
        assert t.lastname.startswith(str(i))
        assert t.dept.startswith(str(i))

    assert len(Lab.list()) == 4
    for i, l in enumerate(Lab.list()):
        assert l.number == f"P32{i}"
        assert l.descr == f"Computer Lab {i + 1}"

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
        if PROVIDER == "mysql":
            db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)
        elif PROVIDER == "sqlite":
            db = define_database(provider=PROVIDER, filename=DB_NAME, create_db=CREATE_DB)

def test_write_DB(after_write):
    """
    Verifies that the write DB method correctly saves top-level model data
    NOTE: THIS TEST WILL LIKELY FAIL IF THE ABOVE TEST FAILS
    IF THEY BOTH FAIL, FIX THE ABOVE ONE FIRST
    """
    global db, new_db
    populate_db()
    ScheduleWrapper.read_DB()

    db.disconnect()
    db.provider = db.schema = None

    db_name = DB_NAME + "_wrapper_write_test"
    if PROVIDER == "mysql":
        new_db = define_database(host=HOST, passwd=PASSWD, db=db_name, provider=PROVIDER, user=USERNAME)
    elif PROVIDER == "sqlite":
        new_db = define_database(provider=PROVIDER, filename=db_name + ".sqlite", create_db=CREATE_DB)
    new_db.drop_all_tables(with_all_data=True)
    new_db.create_tables()

    ScheduleWrapper.write_DB()
    ScheduleWrapper.reset_local()
    ScheduleWrapper.read_DB()

    assert len(Course.list()) == 4
    for i, c in enumerate(Course.list()):
        assert c.semester == i + 1
        assert c.number == f"10{i + 1}-NYA"
        assert c.name == f"Course {i + 1}"
        assert c.needs_allocation != bool(i % 2)

    assert len(Stream.list()) == 4
    for i, s in enumerate(Stream.list()):
        assert s.number == f"3{chr(i + 65)}"
        assert s.descr == f"Stream #{i + 1}"

    assert len(Teacher.list()) == 4
    for i, t in enumerate(Teacher.list()):
        assert t.firstname.startswith(str(i))
        assert t.lastname.startswith(str(i))
        assert t.dept.startswith(str(i))

    assert len(Lab.list()) == 4
    for i, l in enumerate(Lab.list()):
        assert l.number == f"P32{i}"
        assert l.descr == f"Computer Lab {i + 1}"

@db_session
def test_scenarios():
    """Verifies that the scenarios method returns all existing scenarios"""
    sc2 = dbScenario()
    sc3 = dbScenario()
    flush()
    
    scen = scenarios()
    assert len(set(scen)) == 3
    schedules = 0
    for s in scen:
        print(s.schedules)
        schedules += len(s.schedules)
    assert schedules == 1