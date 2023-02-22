import sys
from os import path
sys.path.append(path.dirname(path.dirname(__file__)))
import pytest
from unit_tests.db_constants import *

from Stream import Stream
from Block import Block
from Section import Section
from Course import Course
from database.PonyDatabaseConnection import define_database, Schedule as dbSchedule, Scenario as dbScenario
from pony.orm import *

db : Database

@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    global db
    db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)
    yield
    db.drop_all_tables(with_all_data = True)
    db.disconnect()
    db.provider = db.schema = None

@db_session
def init_scenario_schedule_course():
    sc = dbScenario()
    flush()
    s = dbSchedule(semester="Winter 2023", official=False, scenario_id=sc.id)

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


def test_confirm_id_increments():
    """Confirm that IDs increment correctly"""
    for _ in range(5):
        Stream()
    for index, i in enumerate(Stream.list()):
        assert i.id == index + 1


def test_confirm_description_includes_num_and_descr():
    """Confirm that the Stream's description print includes its number and description"""
    num = "3A"
    descr = "Third year, first section"
    s = Stream(num, descr)
    assert num in s.print_description() and descr in s.print_description()


def test_confirm_can_get_by_id():
    """Confirm that Streams can be retrieved by ID"""
    s = Stream()
    assert Stream.get(1) is s


def test_share_blocks_finds_shared():
    """Confirm that share_blocks finds streams with both blocks"""
    c = Course(semester = "summer")
    b1 = b2 = Block('Mon', '13:00', 2, 1)
    se = Section(course = c, schedule_id = 1)
    s = Stream()
    se.assign_stream(s)
    b1.section = b2.section = se
    assert Stream.share_blocks(b1, b2)


def test_share_blocks_ignores_non_shared():
    """Confirm that share_blocks ignores streams without both blocks"""
    c = Course(semester = "summer")
    b1 = b2 = Block('Mon', '13:00', 2, 1)
    se = Section(course = c, schedule_id = 1)
    s = Stream()
    b1.section = se
    b2.section = Section(course = c, schedule_id = 1)
    se.assign_stream(s)
    assert not Stream.share_blocks(b1, b2)


def test_confirm_delete():
    """Confirm that calling delete will remove the stream"""
    s = Stream()
    s.delete()
    assert s not in Stream.list()
