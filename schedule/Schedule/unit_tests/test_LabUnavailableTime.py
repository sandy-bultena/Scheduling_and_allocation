import pytest
import sys
from os import path
from pony.orm import *

sys.path.append(path.dirname(path.dirname(__file__)))

from Schedule import Schedule
from LabUnavailableTime import LabUnavailableTime
from Lab import Lab
from database.PonyDatabaseConnection import define_database, Scenario as dbScenario, \
    Schedule as dbSchedule, Lab as dbLab, LabUnavailableTime as dbUnavailableTime
from unit_tests.db_constants import *
from ScheduleEnums import WeekDay

db: Database
s: dbSchedule

@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    global db
    db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)
    yield
    db.drop_all_tables(with_all_data=True)
    db.disconnect()
    db.provider = db.schema = None


@db_session
def init_scenario_and_schedule():
    global s
    sc = dbScenario()
    flush()
    s = dbSchedule(semester="Winter 2023", official=False, scenario_id=sc.id, description="W23")


@pytest.fixture(autouse=True)
def run_before():
    db.create_tables()
    init_scenario_and_schedule()
    Schedule.reset_local()
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
