class StreamMeta(type):
    """ Metaclass for Stream, making it iterable """
    _instances = {}

    def __iter__(self): return iter(getattr(self, '_instances', []))

    @staticmethod
    def get_by_id(id : int):
        """Returns the Stream object with matching ID"""
        for i in Stream._instances.values():
            if i.id == id: return i
    
    @staticmethod
    def list():
        """Returns the list of Stream objects"""
        return list(Stream._instances.values())
    
    @staticmethod
    def share_blocks(b1, b2):
        """Checks if there's a stream who share the two blocks provided"""
        occurences = {}
        for s in b1.section.streams: occurences[s.id] = 1
        for s in b2.section.streams:
            if s.id in occurences: return True
        return False

class Stream(metaclass=StreamMeta):
    """ Describes a group of students whose classes cannot overlap. """
    _max_id = 0

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, number : str = "A", descr : str = ""):
        """
        Creates an instance of the Stream class.
        - Parameter number -> defines the stream number.
        - Parameter desc -> defines the stream description.
        """
        Stream._max_id += 1
        self.__id = Stream._max_id
        self.number = number
        self.descr = descr
        Stream._instances[self.__id] = self
    
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