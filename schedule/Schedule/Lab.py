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
    max_id = 0

    def __init__(self, number: int = 100, descr: str = ''):
        """Creates and returns a new Lab object."""
        self.__number = number
        self.__descr = descr
        Lab.max_id += 1
        self.__id = Lab.max_id

    @property
    def id(self):
        return self.__id

    @property
    def number(self):
        return self.__number

    @number.setter
    def number(self, new_value):
        self.__number = new_value

    @property
    def descr(self):
        return self.__descr

    @descr.setter
    def descr(self, new_value):
        self.__descr = new_value

    # =================================================
    # add_unavailable
    # =================================================
    def add_unavailable(self):
        """Creates a time slot where this lab is not available."""
        # TODO: Come back to this when TimeSlot is defined.
        pass

    # =================================================
    # add_unavailable
    # =================================================
    def remove_unavailable(self, id):
        """Remove the unavailable time slot from this lab.
        
        Parameters:
        ---
        id: int
            The id of the time slot to be removed.
        """
        # TODO: Come back to this when TimeSlot is defined.
        pass

    def get_unavailable(self, id):
        """Return the unavailable time slot object for this Lab.
        
        Parameters:
        ---
        id: int
            The id of the time slot to be returned.
        
        Returns:
        ---
        The TimeSlot object.
        """
        # TODO: Come back to this when TimeSlot is defined.
        pass

    def unavailable(self):
        """Returns all unavailable time slot objects for this lab."""
        pass

    def print_description(self):
        """Returns a text string that describes the Lab."""
        if self.__descr is None:
            return f"{self.__number}"
        return f"{self.__number}: {self.__descr}"
