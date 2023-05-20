import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))
import pytest
import schedule.Schedule.Streams as Streams
from schedule.Schedule.Streams import Stream


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    pass


@pytest.fixture(autouse=True)
def before_and_after():
    Streams.clear_all()
    pass


def test_clear_all_removes_all_streams():
    """verify that clear_all works as expected"""
    Stream("1A", "first years A")
    Stream("1B", "first years B")
    Stream("2A", "second years A")
    Streams.clear_all()
    all_streams = Streams.get_all()
    assert len(all_streams) == 0


def test_id():
    """"Verifies that Teacher IDs are incremented automatically."""
    Streams.id_generator = Streams.stream_id_generator(2)
    stream1 = Stream("1A", "first years A")
    assert stream1.id == 3
    stream2 = Stream("1A", "first years A")
    assert stream2.id == 4


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
    assert s in Streams.get_all()


def test_stream_is_deleted_from_collection():
    """Checks that newly created Stream is added to the collection"""
    s1 = Stream()
    s2 = Stream()
    s3 = Stream()
    s4 = Stream()
    s2.delete()
    assert s2 not in Streams.get_all()
    assert s1 in Streams.get_all()
    assert s3 in Streams.get_all()
    assert s4 in Streams.get_all()
    assert len(Streams.get_all()) == 3


def test_confirm_streams_can_be_iterated():
    """Confirms that Stream can be iterated over"""
    Streams.clear_all()
    for x in range(5):
        Stream()
    for i in Streams.get_all():
        assert i


def test_confirm_description_includes_num_and_descr():
    """Confirm that the Stream's description print includes its number and description"""
    num = "3A"
    descr = "Third year, first section"
    s = Stream(num, descr)
    assert num in s.description and descr in s.description
