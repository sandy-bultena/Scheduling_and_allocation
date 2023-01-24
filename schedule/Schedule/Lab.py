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

    def __init__(self, number: int = 100, desc: str = ''):
        """Creates and returns a new Lab object."""
        self.__number = number
        self.desc = desc
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
