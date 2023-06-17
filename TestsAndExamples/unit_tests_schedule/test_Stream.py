import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))
import pytest
from schedule.Schedule.Streams import Stream


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
    descr = "Worst place in the world."
    stream = Stream("AB", descr)
    assert stream.description == descr


def test_number_getter():
    descr = "Worst place in the world."
    stream = Stream("AB", descr)
    assert stream.number == "AB"


def test_string_representation_short():
    descr = "Worst place in the world."
    stream = Stream("AB", descr)
    assert str(stream) == stream.number
