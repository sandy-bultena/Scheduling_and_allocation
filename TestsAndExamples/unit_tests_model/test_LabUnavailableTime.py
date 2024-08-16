import pytest
from schedule.Model._lab_unavailable_time import LabUnavailableTime
from schedule.Model import TimeSlot


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    pass


@pytest.fixture(autouse=True)
def run_before():
    pass


def test_properties():
    lu = LabUnavailableTime("wed", "9:30", 2, False)
    assert lu.day == "wed"
    assert lu.start == "9:30"
    assert lu.duration == 2
    assert lu.movable is False


def test_isa_time_slot():
    lu = LabUnavailableTime("wed", "9:30", 2, False)
    assert isinstance(lu, TimeSlot)

# ################### Incomplete testing #########################
# Should verify that setting lu.start behaves the same as TimeSlot, lu.duration is limited to 1/2 hours, etd
# ################################################################
