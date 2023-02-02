from ..Stream import Stream
from ..Block import Block
from ..Section import Section
import pytest

@pytest.fixture(autouse=True)
def run_before_and_after():
    Stream._max_id = 0
    Stream.reset()

def test_constructor_default_values():
    """Checks that the constructor uses default values when arguments aren't provided"""
    s = Stream()
    assert s.number                                  # check has value
    assert not s.descr and isinstance(s.descr, str) # check no value and is string (ie empty string)

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
    assert Stream.get_by_id(1) is s

def test_share_blocks_finds_shared():
    """Confirm that share_blocks finds streams with both blocks"""
    b1 = b2 = Block('Mon', '13:00', 2, 1)
    se = Section()
    s = Stream()
    se.assign_stream(s)
    b1.section = b2.section = se
    assert Stream.share_blocks(b1, b2)

def test_share_blocks_ignores_non_shared():
    """Confirm that share_blocks ignores streams without both blocks"""
    b1 = b2 = Block('Mon', '13:00', 2, 1)
    se = Section()
    s = Stream()
    b1.section = se
    b2.section = Section()
    se.assign_stream(s)
    assert not Stream.share_blocks(b1, b2)

def test_confirm_remove():
    """Confirm that calling remove will remove the stream"""
    s = Stream()
    Stream.remove(s)
    assert s not in Stream.list()