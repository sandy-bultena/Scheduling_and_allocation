from Time_slot import TimeSlot
from Block import Block


class LabMeta(type):
    """Metaclass for Lab, making the latter iterable."""
    _instances = []

    def __iter__(self):
        return iter(getattr(self, '_instances', []))

    # =================================================================
    # share_blocks
    # =================================================================

    def share_blocks(self, block1: Block, block2: Block):
        """Checks whether there are Labs which share the two specified Blocks."""

        # Count occurrences in both sets and ensure that all values are < 2
        occurrences = {}
        for lab in block1.labs():
            if lab.id not in occurrences.keys():
                occurrences[lab.id] = 0
            occurrences[lab.id] += 1
        for lab in block2.labs():
            if lab.id not in occurrences.keys():
                occurrences[lab.id] = 0
            occurrences[lab.id] += 1

        # A count of 2 means that they are in both sets.
        for lab_count in occurrences.values():
            if lab_count >= 2:
                return True

        return False

    # =================================================================
    # add
    # =================================================================
    def add(self, *args):
        """Adds a new Lab to the Labs object.

        Returns the modified Labs object."""
        for lab in args:
            if not isinstance(lab, Lab):
                raise TypeError(f"<{lab}>: invalid lab - must be a Lab object")

            # Cannot have two distinct labs with the same room number.
            my_obj = self.get_by_number(lab.number)
            if my_obj and my_obj.id != lab.id:
                # TODO: Raise some kind of Exception.
                pass
            self._instances[lab.id] = lab
        return self

    # =================================================================
    # get
    # =================================================================
    def get(self, lab_id: int):
        """Returns the Lab object matching the specified ID, if it exists."""
        for lab in self._instances:
            if lab.id == lab_id:
                return lab
        return None

    # =================================================================
    # get_by_number
    # =================================================================
    def get_by_number(self, number: str):
        """Returns the Lab which matches this Lab number, if it exists."""
        if not number:
            return

        for lab in self._instances:
            if lab.number == number:
                return lab
        return None

    # =================================================================
    # remove lab
    # =================================================================
    def remove(self, lab_obj):
        """Removes the specified Lab from the Labs object.
        
        Returns the modified Labs."""
        if not isinstance(lab_obj, Lab):
            raise TypeError(f"<{lab_obj}>: invalid lab - must be a Lab object")

        # Remove the passed Lab object only if it's actually contained in the list of instances.
        if lab_obj in self._instances:
            self._instances.remove(lab_obj)
        return self

    # =================================================================
    # list
    # =================================================================
    def list(self):
        """Returns the array of Lab objects."""
        return self._instances


class Lab(metaclass=LabMeta):
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
        Lab._instances.append(self)

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
