class TimeSlot:
    """
    A time slot is specified by a day of the week, start time, length (in hours), and whether or not it is allowed to
    move.
    
    Example: The 'Block' object has a time slot used for teaching, whilst a 'Lab' object has a time slot indicating
    when it is not available.
    """
    max_id = 0
    week = {
        "mon": 1,
        "tue": 2,
        "wed": 3,
        "thu": 4,
        "fri": 5,
        "sat": 6,
        "sun": 7
    }
    max_hour_div = 2
    default_day = "mon"
    default_start = "8:00"
    default_duration = 1.5

    def __init__(self, day: str = default_day, start: str = default_start, duration: float = default_duration,
                 movable=True):
        self.day = day
        self.start = start
        self.duration = duration
        self.movable = movable
