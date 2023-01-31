from ..Time_slot import TimeSlot


def test_id():
    slot = TimeSlot()
    assert slot.id == 1


def test_id_incrementation():
    """Verifies that the ID assigned to a TimeSlot increments automatically."""
    slots = []
    for x in range(5):
        slots.append(TimeSlot())
    last_slot = slots[-1]
    assert last_slot.id == len(slots)


def test_day_getter_default():
    """Verifies that a TimeSlot is created with a default day value of 'mon'."""
    slot = TimeSlot()
    assert slot.day == 'mon'


def test_day_setter():
    slot = TimeSlot()
    new_day = 'Sunday'
    slot.day = new_day

    real_val = 'sun'
    assert slot.day == real_val


def test_start_getter_default():
    """Verifies that a TimeSlot is created with a default start value of '8:00'."""
    slot = TimeSlot()
    assert slot.start == "8:00"


def test_start_setter():
    slot = TimeSlot()
    new_start = "10:00"
    slot.start = new_start
    assert slot.start == new_start


def test_end():
    assert False


def test_duration():
    assert False


def test_duration():
    assert False


def test_movable():
    assert False


def test_movable():
    assert False


def test_start_number():
    assert False


def test_start_number():
    assert False


def test_day_number():
    assert False


def test_day_number():
    assert False


def test_snap_to_time():
    assert False


def test__snap_to_time():
    assert False


def test_snap_to_day():
    assert False


def test__snap_to_day():
    assert False


def test_conflicts_time():
    assert False
