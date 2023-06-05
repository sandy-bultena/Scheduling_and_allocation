import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))
import pytest
from schedule.Schedule.Streams import Streams


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    pass


@pytest.fixture(autouse=True)
def before_and_after():
    pass


# ============================================================================
# Stream
# ============================================================================
def test_descr_getter():
    streams = Streams()
    descr = "Worst place in the world."
    stream = streams.add("AB", descr)
    assert stream.description == descr


def test_number_getter():
    streams = Streams()
    descr = "Worst place in the world."
    stream = streams.add("AB", descr)
    assert stream.number == "AB"


def test_string_representation_short():
    streams = Streams()
    descr = "Worst place in the world."
    stream = streams.add("AB", descr)
    assert str(stream) == stream.number


# ============================================================================
# Collection
# ============================================================================
def test_id():
    """Verifies that the id property works as intended."""
    streams = Streams()
    stream = streams.add()
    old_id = stream.id
    stream = streams.add()
    assert stream.id == old_id + 1


def test_id_with_id_given():
    """Verifies that the id property works as intended."""
    existing_id = 112
    streams = Streams()
    stream1 = streams.add(stream_id=existing_id)
    assert stream1.id == existing_id
    stream1 = streams.add(stream_id=existing_id-5)
    assert stream1.id == existing_id - 5
    stream2 = streams.add()
    assert stream2.id == existing_id + 1
    stream3 = streams.add()
    assert stream3.id == existing_id + 2
    stream4 = streams.add()
    assert stream4.id == existing_id + 3


def test_clear_removes_all_labs():
    """verify that clear works as expected"""
    streams = Streams()
    streams.add("R-101", "Worst place in the world")
    streams.add("R-102", "Second-worst place in the world")
    streams.clear()
    all_streams = streams.get_all()
    assert len(all_streams) == 0


def test_get_all():
    """Verifies that get_all() returns a tuple of all extant Lab objects."""
    streams = Streams()
    stream1 = streams.add("R-101", "Worst place in the world")
    stream2 = streams.add("R-102", "Second-worst place in the world")
    all_streams = streams.get_all()
    assert len(all_streams) == 2 and stream1 in all_streams and stream2 in all_streams


def test_get_all_is_empty():
    """Verifies that get_all() returns an empty tuple if no Labs have been created."""
    streams = Streams()
    all_streams = streams.get_all()
    assert len(all_streams) == 0


def test_remove():
    """Verifies that the remove() method works as intended."""
    streams = Streams()
    stream1 = streams.add("R-101", "Worst place in the world")
    stream2 = streams.add("R-102", "Second-worst place in the world")
    streams.remove(stream1)
    all_streams = streams.get_all()
    assert len(all_streams) == 1 and stream1 not in all_streams


def test_get_by_id_good():
    """Verifies that get_by_id() returns the first Lab matches the id."""
    streams = Streams()
    stream1 = streams.add("R-101", "Worst place in the world", stream_id=11)
    stream2 = streams.add("R-102", "Second-worst place in the world", stream_id=14)
    assert streams.get_by_id(stream1.id) == stream1
    assert stream1.id == 11
    assert streams.get_by_id(stream2.id) == stream2
    assert stream2.id == 14


def test_get_by_id_not_valid():
    streams = Streams()
    streams.add("R-101", "Worst place in the world", stream_id=11)
    streams.add("R-102", "Second-worst place in the world", stream_id=14)
    assert streams.get_by_id(666) is None


def test_get_by_id_on_empty_list():
    streams = Streams()
    assert streams.get_by_id(666) is None

