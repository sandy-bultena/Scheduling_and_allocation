from __future__ import annotations

from filecmp import cmp

import pytest
import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))
import schedule.Schedule.Schedule as s


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    pass


@pytest.fixture(autouse=True)
def before_and_after():
    pass


def test_read_write():
    """stupidest simplest test whatsoever"""

    # logic is that what it reads in is saved in the schedule object, so it should print out the
    # same info to the output file

    # TODO: not a good test
    schedule = s.Schedule(path.dirname(__file__) + "/test.csv")
    schedule.write_file(path.dirname(__file__) + "/test_output.csv")
    assert (cmp(path.dirname(__file__) + "/test.csv", path.dirname(__file__) + "/test_output.csv"))

#schedule = s.Schedule(path.dirname(__file__) + "/test.csv")
def test_schedule_actually_has_stuff_in_it():
    """smoke test to see if schedule is actually populated with data - not validating data though"""
    schedule = s.Schedule(path.dirname(__file__) + "/test.csv")
    assert len(schedule._teachers) != 0
    assert len(schedule.courses) != 0
    assert len(schedule.labs) != 0
    assert len(schedule._streams) != 0
