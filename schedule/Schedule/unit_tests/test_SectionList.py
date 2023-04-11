import sys
from os import path
sys.path.append(path.dirname(path.dirname(__file__)))

import pytest

from ..Section import Section
from ..Course import Course
from ..SectionList import SectionList

from .db_constants import *
from pony.orm import *
from ..database.PonyDatabaseConnection import define_database, Schedule as dbSchedule, Scenario as dbScenario

s : dbSchedule

@db_session
def init_constants():
    global s, c
    sc = dbScenario()
    flush()
    s = dbSchedule(official=False, scenario_id=sc.id)

@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    global db
    if PROVIDER == "mysql":
        db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)
    elif PROVIDER == "sqlite":
        db = define_database(provider=PROVIDER, filename=DB_NAME, create_db=CREATE_DB)
    init_constants()
    yield
    db.drop_all_tables(with_all_data=True)
    db.disconnect()
    db.provider = db.schema = None

@pytest.fixture(autouse=True)
def before_and_after():
    db.create_tables()
    yield
    Section.reset()
    db.drop_table(table_name='section', if_exists=True, with_all_data=True)

def test_constructor():
    """Verifies that the constructor works the same as the default list constructor"""
    c = Course()
    sl = SectionList([Section(1, schedule_id=s.id, course=c), Section(2, schedule_id=s.id, course=c), se := Section(3, schedule_id=s.id, course=c)])
    assert se in sl
    assert len(sl) == 3

def test_del():
    """Verifies that the del keyword completely deletes the section"""
    c = Course()
    sl = SectionList([Section(1, schedule_id=s.id, course=c), Section(2, schedule_id=s.id, course=c), se := Section(3, schedule_id=s.id, course=c)])
    del sl[2]
    assert se not in Section.list()

def test_pop():
    """Verifies that the pop method completely deletes the section, and returns None"""
    c = Course()
    sl = SectionList([Section(1, schedule_id=s.id, course=c), Section(2, schedule_id=s.id, course=c), se := Section(3, schedule_id=s.id, course=c)])
    assert sl.pop(2) is None
    assert se not in sl
    assert se not in Section.list()

def test_remove():
    """Verifies that the remove method completely deletes the section"""
    c = Course()
    sl = SectionList([Section(1, schedule_id=s.id, course=c), Section(2, schedule_id=s.id, course=c), se := Section(3, schedule_id=s.id, course=c)])
    sl.remove(se)
    assert se not in sl
    assert se not in Section.list()

def test_remove_not_found():
    """Verifies that the remove method doesn't throw an error if the section is already absent"""
    c = Course()
    sl = SectionList([Section(1, schedule_id=s.id, course=c), se1 := Section(2, schedule_id=s.id, course=c)])
    se2 = Section(3, schedule_id=s.id, course=c)

    # Section was never in SectionList
    sl.remove(se2)
    assert se2 not in sl
    assert se2 in Section.list()

    # Section has already been removed from SectionList
    sl.remove(se1)
    sl.remove(se1)
    assert se1 not in sl
    assert se1 not in Section.list()

def test_deleteless_remove():
    """Verifies that the deleteless_remove method will remove the Section without deleting it"""
    c = Course()
    sl = SectionList([Section(1, schedule_id=s.id, course=c), Section(2, schedule_id=s.id, course=c), se := Section(3, schedule_id=s.id, course=c)])
    sl.deleteless_remove(se)
    assert se not in sl
    assert se in Section.list()

def test_append_only_allows_sections():
    """Verifies that the append method only allows Section objects"""
    sl = SectionList()
    with pytest.raises(ValueError) as e:
        sl.append(1)
    assert "can only contain section objects" in str(e.value).lower()

def test_insert_only_allows_sections():
    """Verifies that the insert method only allows Section objects"""
    c = Course()
    sl = SectionList([Section(1, schedule_id=s.id, course=c), Section(2, schedule_id=s.id, course=c), Section(3, schedule_id=s.id, course=c)])
    with pytest.raises(ValueError) as e:
        sl.insert(0, 1)
    assert "can only contain section objects" in str(e.value).lower()

def test_lists():
    """Verifies that the lists method returns all SectionList instances"""
    c = Course()
    sl1 = SectionList([Section(1, schedule_id=s.id, course=c), Section(2, schedule_id=s.id, course=c), Section(3, schedule_id=s.id, course=c)])
    sl2 = SectionList([Section(4, schedule_id=s.id, course=c), Section(5, schedule_id=s.id, course=c), Section(6, schedule_id=s.id, course=c)])

    assert sl1 in SectionList.lists()
    assert sl2 in SectionList.lists()