import pytest

import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))

from schedule.Schedule.Undo import Undo


@pytest.fixture(autouse=True)
def run_before_and_after():
    Undo._max_id = 0


def test_constructor_created_success():
    """Checks that Undo is correctly correctly"""
    block_id = 1
    origin_start = "start"
    origin_day = "mon"
    origin_obj = 5
    move_type = "resource_type"
    new_obj = 6
    u = Undo(block_id, origin_start, origin_day, origin_obj, move_type, new_obj)
    assert u.block_id == block_id
    assert u.origin_start == origin_start
    assert u.origin_day == origin_day
    assert u.origin_obj == origin_obj
    assert u.move_type == move_type
    assert u.new_obj == new_obj
