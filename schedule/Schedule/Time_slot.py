import re


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
    reverse_week = {
        1: "mon",
        2: "tue",
        3: "wed",
        4: "thu",
        5: "fri",
        6: "sat",
        7: "sun"
    }
    default_day = "mon"
    default_start = "8:00"
    default_duration = 1.5

    def __init__(self, day: str = default_day, start: str = default_start, duration: float = default_duration,
                 movable=True):
        self.__day = day
        self.__start = start
        self.__duration = duration
        self.__movable = movable
        TimeSlot.max_id += 1
        self.__id = TimeSlot.max_id

    # ====================================
    # id
    # ====================================
    @property
    def id(self):
        """Returns the unique ID for this TimeSlot object."""
        return self.__id

    # ====================================
    # day
    # ====================================
    @property
    def day(self):
        "Get/set the day of the week for this TimeSlot."
        return self.__day
    
    @day.setter
    def day(self, new_day):
        if new_day in TimeSlot.week.keys():
            self.__day = new_day
            self.day_number = TimeSlot.week[new_day]
        elif new_day in range(1, 8):
            self.day_number = new_day
            self.__day = TimeSlot.reverse_week[new_day]
        else:
            self.__day = TimeSlot.default_day
            self.day_number = TimeSlot.week[new_day]

            
    


