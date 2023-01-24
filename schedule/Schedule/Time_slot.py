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
        """Get/set the day of the week for this TimeSlot."""
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

    # ====================================
    # start
    # ====================================
    @property
    def start(self):
        """Get/set the start time of the TimeSlot, in 24hr clock."""
        return self.__start

    @start.setter
    def start(self, new_value):
        if not re.match("^[12]?[0-9]:(00|15|30|45)$", new_value):
            print(f"<{new_value}>: invalid start time\nchanged to {TimeSlot.default_start}")
            new_value = TimeSlot.default_start

        self.start = new_value
        hour, minute = re.split(":", new_value)
        # TODO: Figure out what's going on here with self.start_number.

    # ====================================
    # end
    # ====================================

    def end(self):
        """Gets the end time in 24-hour clock."""
        current_start = self.start_number
        end = current_start + self.__duration
        hour = f"{int(end)}"
        minute = f"{int((end * 60) % 60)}"
        return f"{hour}:{minute}"

    # ====================================
    # duration
    # ====================================
    @property
    def duration(self):
        """Gets and sets the length of the TimeSlot, in hours."""
        return self.__duration

    @duration.setter
    def duration(self, new_val):
        if new_val < .25 and new_val > 0:
            new_val = .5
        else:
            temp = 2 * new_val
            rounded = int(temp + 0.5)
            new_val = rounded / 2
        if new_val > 8:
            new_val = 8
        if new_val <= 0:
            print(f"<{new_val}>: invalid duration\nchanged to {TimeSlot.default_duration}")
        self.__duration = new_val

    # ====================================
    # movable
    # ====================================
    @property
    def movable(self):
        """Gets and sets the course section object which contains this time_slot."""
        return self.__movable

    @movable.setter
    def movable(self, movable: bool):
        self.__movable = movable

    # ====================================
    # start_number
    # ====================================
    @property
    def start_number(self):
        """
        Sets or returns the start time in hours (i.e., 1:30 pm = 13.5 hours)
        
        This time info is set every time the start method is invoked on the object. Modifying it directly does NOT modify the values stored in 'day'.

        To set the day according to the data in this hash, use the method "snap_to_time".
        """
        return self.start_number

    @start_number.setter
    def start_number(self, new_val):
        self.start_number = new_val

    # ====================================
    # day_number
    # ====================================
    @property
    def day_number(self):
        return self.day_number

    @day_number.setter
    def day_number(self, new_val):
        self.day_number = new_val

    # ====================================
    # snap_to_time
    # ====================================
    def snap_to_time(self, time):
        """
        Takes the start number, and converts it to the nearest fraction of an hour (if max_hour_div = 2, then snaps to every 1/2 hour).

        Resets the 'start' property to the new clock time.

        Returns true if the new time is different than the previous time.
        """
        hour = self._snap_to_time(time)
        minute = int((hour - int(hour)) * 60)
        start = f"{int(hour)}:{minute:2d}"

        changed = False
        if start != self.__start:
            changed = True
        self.start(start)
        return changed

    def _snap_to_time(self, time):
        min_time = time if time else 8
        max_time = time if time else 18

        TimeSlot.max_hour_div = 1 if TimeSlot.max_hour_div < 1 else TimeSlot.max_hour_div

        r_hour = self.start_number
        start = ""

        # Get hour and fractional hour
        hour = int(r_hour)
        frac = r_hour = hour

        # Create array of allowed fractions.
        fracs = []
        for i in range(TimeSlot.max_hour_div + 1):
            fracs.append(i / TimeSlot.max_hour_div)

        # Sort according to which one is closest to our fraction. TODO: Come back to this part.
        sorted_frac = sorted(fracs, )

        # add hour fraction to hour.
        hour = hour + sorted_frac[0]

        # Adjust hour to minimum or maximum
        hour = min_time if hour < min_time else hour
        hour = max_time - self.__duration if hour > max_time - self.__duration else hour

        return hour

    # =================================================================
    # snap_to_day
    # =================================================================
    def snap_to_day(self, *args: int):
        """
        Takes the start_day and converts it to the nearest day.

        Resets the 'day' property to the appropriate string.

        """
        day = self._snap_to_day(args)

        changed = False
        if TimeSlot.reverse_week[day] != self.__day:
            changed = True
        self.day(TimeSlot.reverse_week[day])
        # return day  # TODO: Ask Sandy if this is the correct return type.

    def _snap_to_day(self, *args: int):
        min_day = args[0] if args[0] else 1
        max_day = args[1] if args[1] else 7

        r_day = self.day_number

        day = r_day if r_day == int(r_day) else int(r_day + 0.5)
        day = min_day if not day else day
        day = max_day if day > max_day else day
        return day

    # =================================================================
    # conflicts
    # =================================================================
    def conflicts_time(self, rhs):
        """
        Tests that the current Time_Slot conflicts with another TimeSlot.
        """
        # Detect time collisions up to this error factor. Also useful for graphical applications that require a small
        # error threshold when moving a block into place.
        delta = 0.05

        # detect date collisions
        if abs(self.day_number - rhs.day_number) >= 1 - delta:
            return False
        
        # Calculate the start/end for each block with the error factor removed.
        self_start = self.start_number + delta
        self_end = self.start_number + self.duration - delta
        rhs_end = rhs.start_number + rhs.duration - delta
        rhs_start = rhs.start_number + delta

        return (self_start < rhs_end) and (rhs_start < self_end)