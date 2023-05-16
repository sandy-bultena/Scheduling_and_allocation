import sys
from os import path
sys.path.append(path.dirname(path.dirname(__file__)))
import pytest
from .db_constants import *

from schedule.Schedule.Stream import Stream
from schedule.Schedule.Block import Block
from schedule.Schedule.Section import Section
from schedule.Schedule.Course import Course
from ..database.PonyDatabaseConnection import define_database, Schedule as dbSchedule, Scenario as dbScenario, Stream as dbStream
from pony.orm import *

db : Database

@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    global db
    if PROVIDER == "mysql":
        db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)
    elif PROVIDER == "sqlite":
        db = define_database(provider=PROVIDER, filename=DB_NAME, create_db=CREATE_DB)
    init_scenario_schedule_course()
    yield
    db.drop_all_tables(with_all_data = True)
    db.disconnect()
    db.provider = db.schema = None

@db_session
def init_scenario_schedule_course():
    sc = dbScenario()
    flush()
    s = dbSchedule(official=False, scenario_id=sc.id)

@pytest.fixture(autouse=True)
def before_and_after():
    db.create_tables()
    Stream.reset()
    yield
    db.drop_table(table_name = 'stream', if_exists = True, with_all_data = True)
    db.drop_table(table_name = 'course', if_exists = True, with_all_data = True)

def test_constructor_default_values():
    """Checks that the constructor uses default values when arguments aren't provided"""
    s = Stream()
    assert s.number  # check has value
    assert isinstance(s.descr, str)  # check no value and is string (ie empty string)


def test_stream_created_success():
    """Checks that Stream is created correctly"""
    num = "3A"
    descr = "Third year, first section"
    s = Stream(num, descr)
    assert s.number == num
    assert s.descr == descr


def test_stream_is_added_to_collection():
    """Checks that newly created Stream is added to the collection"""
    s = Stream()
    assert s in Stream.list()


def test_confirm_Stream_can_be_iterated():
    """Confirms that Stream can be iterated over"""
    Stream.reset()
    for x in range(5):
        Stream()
    for i in Stream.list():
        assert i


@db_session
def test_confirm_id_increments():
    """Confirm that IDs increment correctly"""
    for _ in range(5):
        Stream()
    max_id = max(s.id for s in dbStream)
    for index, i in enumerate(Stream.list()):
        assert i.id == index + (max_id - 4)  # A bit of a hack, but this works.


def test_confirm_description_includes_num_and_descr():
    """Confirm that the Stream's description print includes its number and description"""
    num = "3A"
    descr = "Third year, first section"
    s = Stream(num, descr)
    assert num in s.description and descr in s.description


@db_session
def test_confirm_can_get_by_id():
    """Confirm that Streams can be retrieved by ID"""
    s = Stream()
    max_id = max(s.id for s in dbStream)
    assert Stream.get(max_id) is s


def test_share_blocks_finds_shared():
    """Confirm that share_blocks finds streams with both blocks"""
    c = Course()
    b1 = b2 = Block('mon', '13:00', 2, 1)
    se = Section(course = c, schedule_id = 1)
    s = Stream()
    se.assign_stream(s)
    b1.section = b2.section = se
    assert Stream.share_blocks(b1, b2)


def test_share_blocks_ignores_non_shared():
    """Confirm that share_blocks ignores streams without both blocks"""
    c = Course()
    b1 = b2 = Block('mon', '13:00', 2, 1)
    b1.section = (se := Section(number=1, course = c, schedule_id = 1))
    b2.section = Section(number=2, course = c, schedule_id = 1)
    se.assign_stream(Stream())
    assert not Stream.share_blocks(b1, b2)



@db_session
def test_confirm_delete():
    """Confirm that calling delete will remove the stream"""
    s = Stream()
    id = s.id
    s.delete()
    assert s not in Stream.list()
    assert dbStream.get_by_id(id = id) is None


@db_session
def test_save():
    """Confirm that save saves the stream to the database."""
    s = Stream()
    flush()
    s.descr = "All New, All Different Stream!"
    d_s = s.save()
    assert d_s.descr == s.descr and d_s.number == s.number
