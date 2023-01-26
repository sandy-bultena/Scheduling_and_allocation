from Time_slot import TimeSlot

class Lab:
    """
    Describes a distinct, contiguous course/section/class.

    Attributes:
    -----------
    number: int
        The room number.
    desc: str
        The description of the Lab.
    """
    _max_id = 0

    # -------------------------------------------------------------------
    # new
    # --------------------------------------------------------------------

    def __init__(self, number: str = "100", descr: str = ''):
        """Creates and returns a new Lab object."""
        self.number = number
        self.descr = descr
        Lab._max_id += 1
        self.__id = Lab._max_id

    # =================================================================
    # id
    # =================================================================

    @property
    def id(self):
        """Returns the unique ID for this Lab object."""
        return self.__id

    # =================================================================
    # number
    # =================================================================

    @property
    def number(self):
        """Sets/returns the room number for this Lab object."""
        return self.__number

    @number.setter
    def number(self, new_value):
        self.__number = new_value

    # =================================================================
    # descr
    # =================================================================

    @property
    def descr(self):
        """Sets/returns the description for this Lab object."""
        return self.__descr

    @descr.setter
    def descr(self, new_value: str):
        self.__descr = new_value

    # =================================================
    # add_unavailable
    # =================================================
    def add_unavailable(self, day: str, start: str, duration: float):
        """Creates a time slot where this lab is not available.
        
        - Parameter day => 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'

        - Parameter start => start time using 24 h clock (i.e., 1pm is "13:00")

        - Parameter duration => how long does this class last, in hours
        """
        if not hasattr(self, '_unavailable'):
            self._unavailable: dict[int, TimeSlot] = {}

        # Create a TimeSlot.
        slot = TimeSlot(day, start, duration)

        # Save it.
        self._unavailable[slot.id] = slot

        return self

    # =================================================
    # remove_unavailable
    # =================================================
    def remove_unavailable(self, target_id: int):
        """Remove the unavailable time slot from this lab.
        
        - Parameter target_id -> The ID of the time slot to be removed.

        Returns the modified Lab object.
        """
        if hasattr(self, '_unavailable') and target_id in self._unavailable.keys():
            del self._unavailable[target_id]

        return self

    # =================================================================
    # get_unavailable
    # =================================================================

    def get_unavailable(self, target_id: int):
        """Return the unavailable time slot object for this Lab.
        
        - Parameter target_id -> The ID of the TimeSlot to be returned.
             
        Returns the TimeSlot object.
        """
        if hasattr(self, '_unavailable') and target_id in self._unavailable.keys():
            return self._unavailable[target_id]
        return None

    # =================================================================
    # unavailable
    # =================================================================

    def unavailable(self):
        """Returns all unavailable time slot objects for this lab."""
        if hasattr(self, '_unavailable'):
            return list(self._unavailable.values())
        return []

    # =================================================================
    # print_description
    # =================================================================

    def print_description(self):
        """Returns a text string that describes the Lab."""
        if self.__descr is None:
            return f"{self.__number}"
        return f"{self.__number}: {self.__descr}"
