class Stream:
    """
    Describes a group of students whose classes cannot overlap.
    """
    __max_id = 0

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, number : str = "A", descr : str = ""):
        """
        Creates an instance of the Stream class.
        - Parameter number -> defines the stream number.
        - Parameter desc -> defines the stream description.
        """
        Stream.__max_id += 1
        self.__id = Stream.__max_id
        self.number = number
        self.descr = descr
    
    # ========================================================
    # PROPERTIES
    # ========================================================
    
    # --------------------------------------------------------
    # id
    # --------------------------------------------------------
    @property
    def id(self) -> int:
        """ Gets the id of the stream. """
        return self.__id
    
    # ========================================================
    # METHODS
    # ========================================================

    # --------------------------------------------------------
    # __str__
    # --------------------------------------------------------
    def __str__(self) -> str:
        """ Returns a text string with the stream's number """
        return self.number
    
    # --------------------------------------------------------
    # print_description     # note: called print_description2 in the Perl version
    # --------------------------------------------------------
    def print_description(self) -> str:
        """ Returns a text string that describes the stream """
        return f"{self.number}: {self.descr}"