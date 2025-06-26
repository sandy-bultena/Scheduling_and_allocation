from schedule.model.schedule_time import ScheduleTime, ClockTime


def test_schedule_time_properties():
    st = ScheduleTime(3.5)
    assert st.hours == 3.5
    assert st.minute == 30
    assert st.hour == 3
    assert str(st) == "3:30"


def test_clock_time_properties():
    st = ClockTime("3:30")
    assert st.hours == 3.5
    assert st.minute == 30
    assert st.hour == 3
    assert str(st) == "3:30"


def test_time_subtract():
    st1 = ClockTime("3:30")
    st2 = ScheduleTime(5.5)
    assert st2 - st1 == 2


def test_time_equality():
    st1 = ClockTime("3:30")
    st2 = ScheduleTime(3.5)
    assert st1 == st2


def test_time_sort():
    st1 = ClockTime("16:30")
    st2 = ScheduleTime(3.5)
    st3 = ClockTime("12:30")
    st4 = ScheduleTime(1.5)
    times = sorted([st1, st2, st3, st4])
    assert times[0] is st4
    assert times[1] is st2
    assert times[2] is st3
    assert times[3] is st1


def test_already_snapped():
    st1 = ClockTime("16:30")
    assert not st1.snap_to_time(duration=1, round_to_minutes=15, min_start_time=8, max_end_time=18)
    assert str(st1) == "16:30"


def test_snap_passes_end_time():
    st1 = ClockTime("16:30")
    assert st1.snap_to_time(duration=1, round_to_minutes=15, min_start_time=8, max_end_time=17)
    assert str(st1) == "16:00"


def test_snap_starts_too_soon():
    st1 = ClockTime("6:30")
    assert st1.snap_to_time(duration=1, round_to_minutes=15, min_start_time=8, max_end_time=17)
    assert str(st1) == "8:00"


def test_snap_to_nearest_hour():
    st1 = ClockTime("8:30")
    assert st1.snap_to_time(duration=1, round_to_minutes=60, min_start_time=8, max_end_time=17)
    assert str(st1) == "8:00"


def test_snap_to_nearest_hour2():
    st1 = ClockTime("8:31")
    assert st1.snap_to_time(duration=1, round_to_minutes=60, min_start_time=8, max_end_time=17)
    assert str(st1) == "9:00"


def test_snap_to_nearest_half_hour():
    st1 = ClockTime("8:29")
    assert st1.snap_to_time(duration=1, round_to_minutes=30, min_start_time=8, max_end_time=17)
    assert str(st1) == "8:30"


def test_snap_to_nearest_half_hour2():
    st1 = ClockTime("8:31")
    assert st1.snap_to_time(duration=1, round_to_minutes=30, min_start_time=8, max_end_time=17)
    assert str(st1) == "8:30"
