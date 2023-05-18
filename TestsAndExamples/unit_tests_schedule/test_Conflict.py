import sys
from os import path
sys.path.append(path.dirname(path.dirname(__file__)))
import pytest
from .db_constants import *
from ..database.PonyDatabaseConnection import define_database
from pony.orm import *
from schedule.Schedule.ScheduleEnums import ConflictType, ViewType

from schedule.Schedule.Conflicts import Conflict

conflict_types = Conflict._sorted_conflicts.copy()
conflict_types.append(ConflictType.TIME_LAB)
conflict_types.append(ConflictType.TIME_STREAM)
conflict_types.append(ConflictType.TIME_TEACHER)

db : Database

@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    global db
    if PROVIDER == "mysql":
        db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)
    elif PROVIDER == "sqlite":
        db = define_database(provider=PROVIDER, filename=DB_NAME, create_db=CREATE_DB)
    yield
    db.drop_all_tables(with_all_data = True)
    db.disconnect()
    db.provider = db.schema = None

@pytest.fixture(autouse=True)
def before_and_after():
    Conflict.reset()

def test_constructor_fails_with_invalid_arguments():
    """Checks that TypeError exception is raised when incorrect arguments are provided"""
    with pytest.raises(TypeError) as e:
        Conflict(0, blocks = [1])
    assert "bad inputs" in str(e.value).lower()
    
    with pytest.raises(TypeError) as e:
        Conflict(ConflictType.MINIMUM_DAYS, [])
    assert "bad inputs" in str(e.value).lower()

def test_conflict_is_added_to_collection():
    """Checks that newly created Conflict is correctly added to the collection"""
    c = Conflict(ConflictType.LUNCH, [1])
    assert c in Conflict.list()

def test_conflict_created_success():
    """Checks that Conflict is created correctly"""
    blocks = [5, 6]
    c = Conflict(ConflictType.AVAILABILITY, blocks)
    assert c.type is ConflictType.AVAILABILITY
    assert c.blocks == blocks

def test_confirm_conflict_can_be_iterated():
    """Confirm that Conflict can be iterated over"""
    Conflict(ConflictType.TIME_LAB, [1])
    Conflict(ConflictType.TIME_TEACHER, [2])
    Conflict(ConflictType.TIME_STREAM, [3])
    Conflict(ConflictType.TIME_LAB, [1])
    Conflict(ConflictType.TIME_TEACHER, [2])
    Conflict(ConflictType.TIME_STREAM, [3])
    for i in Conflict.list():
        assert i

def test_confirm_hash_descriptions_and_colour_cover_same_types():
    """Confirms that the hash descriptions and colours cover the same types"""
    assert [c.name for c in Conflict._hash_descriptions().keys()].sort() is [c.name for c in Conflict.colours().keys()].sort()

def test_confirm_conflicts_list_is_full():
    """Confirms that the list of conflicts can be retrieved, and contains currently existing conflicts"""
    c1 = Conflict(ConflictType.TIME_LAB, [1])
    c2 = Conflict(ConflictType.TIME_TEACHER, [2])
    c3 = Conflict(ConflictType.TIME_STREAM, [3])
    l = Conflict.list()
    assert len(l) == 3
    assert c1 in l and c2 in l and c3 in l

def test_confirm_most_severe_ordered_correctly_no_special():
    """Confirms the most severe conflict is returned correctly, with no special circumstance"""
    type = 0
    for i in Conflict._sorted_conflicts[::-1]:
        type += i.value
        out = Conflict.most_severe(type, ViewType.none)
        assert out == i

def test_confirm_most_severe_ordered_correctly_lab():
    """Confirms the most severe conflict is always TIME_LAB when 'lab' is specified"""
    for i in Conflict._sorted_conflicts:
        out = Conflict.most_severe(ConflictType.TIME_LAB.value + i.value, ViewType.Lab)
        assert out == ConflictType.TIME_LAB

def test_confirm_most_severe_ordered_correctly_stream():
    """Confirms the most severe conflict is always TIME_STREAM when 'stream' is specified"""
    for i in Conflict._sorted_conflicts:
        out = Conflict.most_severe(ConflictType.TIME_STREAM.value + i.value, ViewType.Stream)
        assert out == ConflictType.TIME_STREAM

def test_confirm_most_severe_ordered_correctly_teacher():
    """Confirms the most severe conflict is always TIME_TEACHER when 'teacher' is specified"""
    for i in Conflict._sorted_conflicts:
        out = Conflict.most_severe(ConflictType.TIME_TEACHER.value + i.value, ViewType.Teacher)
        assert out == ConflictType.TIME_TEACHER

def test_confirm_get_description_returns_correct_description():
    """Confirms the get_description_of method returns the correct type description"""
    for i in conflict_types:
        assert Conflict.get_description(i) == Conflict._hash_descriptions()[i]
    
def test_confirm_colours_returns_correct_description():
    """Confirms the colours method returns the correct colours"""
    colours = Conflict.colours()
    for i in conflict_types:
        assert colours[i] == ConflictType.colours()[i]
    
def test_confirm_block_is_added():
    """Confirm new blocks are added correctly"""
    c = Conflict(ConflictType.TIME_TEACHER, [1])
    new_block = "new block"
    c.add_block(new_block)
    assert new_block in c.blocks

def test_confirm_conflict_is_deleted():
    """Confirm conflicts are deleted correctly"""
    c = Conflict(ConflictType.TIME, [1])
    assert c in Conflict.list()
    c.delete()
    assert c not in Conflict.list()

def test_reset_works():
    """Confirms Conflict.reset() works correctly"""
    c1 = Conflict(ConflictType.TIME_LAB, [1])
    c2 = Conflict(ConflictType.TIME_TEACHER, [2])
    c3 = Conflict(ConflictType.TIME_STREAM, [3])
    assert len(Conflict.list()) > 0
    Conflict.reset()
    assert len(Conflict.list()) == 0
