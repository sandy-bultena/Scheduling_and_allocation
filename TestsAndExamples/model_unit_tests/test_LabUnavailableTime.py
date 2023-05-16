import pytest
import sys
from os import path
from pony.orm import *

sys.path.append(path.dirname(path.dirname(__file__)))

from schedule.Schedule.Schedule import Schedule
from ..ScheduleWrapper import ScheduleWrapper
from schedule.Schedule.LabUnavailableTime import LabUnavailableTime
from ..database.PonyDatabaseConnection import define_database, Scenario as dbScenario, \
    Schedule as dbSchedule, LabUnavailableTime as dbUnavailableTime
from .db_constants import *

db: Database
s: dbSchedule


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    global db
    if PROVIDER == "mysql":
        db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)
    elif PROVIDER == "sqlite":
        db = define_database(provider=PROVIDER, filename=DB_NAME, create_db=CREATE_DB)
    yield
    db.drop_all_tables(with_all_data=True)
    db.disconnect()
    db.provider = db.schema = None


@db_session
def init_scenario_and_schedule():
    global s
    sc = dbScenario()
    flush()
    s = dbSchedule(official=False, scenario_id=sc.id, description="W23")


@pytest.fixture(autouse=True)
def run_before():
    db.create_tables()
    init_scenario_and_schedule()
    ScheduleWrapper.reset_local()
    yield
    db.drop_all_tables(with_all_data=True)


@db_session
def test_constructor_no_db():
    """Verifies that the initializer can create a LabUnavailableTime object with
    no corresponding database record."""
    sched = Schedule.read_DB(1)
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    unavailable = LabUnavailableTime(day, start, dur, id=1, schedule=sched)
    assert unavailable.day == day and unavailable.start == start and unavailable.duration == dur \
           and unavailable.schedule == sched


@db_session
def test_constructor_updates_db():
    """Verifies that the initializer updates the database when no ID is passed to the
    constructor. """
    sched = Schedule.read_DB(1)
    day = "mon"
    start = "8:30"
    dur = 2
    num = 1
    unavailable = LabUnavailableTime(day, start, dur, schedule=sched)
    flush()
    db_unavailable = dbUnavailableTime[1]
    flush()
    db_sched = dbSchedule[1]
    flush()
    assert db_unavailable.id == unavailable.id and db_unavailable.day == unavailable.day \
           and db_unavailable.start == unavailable.start \
           and db_unavailable.duration == unavailable.duration \
           and db_unavailable.schedule_id == db_sched


@db_session
def test_id():
    """Verifies that the ID assigned to a LabUnavailableTime object increments automatically."""
    sched = Schedule.read_DB(1)
    times = []
    for x in range(5):
        times.append(LabUnavailableTime(schedule=sched))
        commit()
    last_time = times[-1]
    assert last_time.id == len(times)

@db_session
def test_delete():
    """Verifies that delete() works as intended."""
    LabUnavailableTime.reset()
    sched = Schedule.read_DB(1)
    unavailable = LabUnavailableTime("mon", "8:30", 2, schedule=sched)
    flush()
    unavailable.delete()
    flush()
    times = LabUnavailableTime.list()
    assert len(times) == 0


@db_session
def test_delete_updates_database():
    """Verifies that delete() removes the corresponding record from the database."""
    sched = Schedule.read_DB(1)
    unavailable = LabUnavailableTime("mon", "8:30", 2, schedule=sched)
    flush()
    unavailable.delete()
    flush()
    db_times = dbUnavailableTime.select()
    assert len(db_times) == 0


@db_session
def test_save():
    """Verifies that save() works as intended."""
    sched = Schedule.read_DB(1)
    unavailable = LabUnavailableTime("mon", "8:30", 2, schedule=sched)
    flush()
    new_start = "10:30"
    new_duration = 1.5
    unavailable.start = new_start
    unavailable.duration = new_duration
    d_unavailable = unavailable.save()
    commit()
    assert d_unavailable.start == new_start and d_unavailable.duration == new_duration


def test_list():
    """Verifies that list() returns a tuple containing all extant LabUnavailableTime objects."""
    LabUnavailableTime.reset()
    sched = Schedule.read_DB(1)
    unavailable_1 = LabUnavailableTime("mon", "8:30", 2, schedule=sched)
    unavailable_2 = LabUnavailableTime("tue", "10:00", 1.5, schedule=sched)
    times = LabUnavailableTime.list()
    assert isinstance(times, tuple) and len(times) == 2 and unavailable_1 in times \
           and unavailable_2 in times
