from __future__ import annotations

from .Block import Block

""" SYNOPSIS/EXAMPLE:
    from Schedule.Stream import Stream

    stream = Stream(number = "P322")
    
    all_labs = Stream.list()
"""


def stream_id_generator(max_id: int = 0):
    the_id = max_id + 1
    while True:
        yield the_id
        the_id = the_id + 1


class Stream:
    """ Describes a group of students whose classes cannot overlap. """
    __instances: dict[int, Stream] = dict()
    stream_id_gen = stream_id_generator()

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, number: str = "A", descr: str = "", *, stream_id: int = None):
        """
        Creates an instance of the Stream class.
        - Parameter number -> defines the stream number.
        - Parameter desc -> defines the stream description.
        """
        self.number = number
        self.descr = descr

        self.__id = stream_id if stream_id else next(Stream.stream_id_gen)
        Stream.__instances[self.__id] = self

    # ========================================================
    # ITERATING RELATED (STATIC)
    # ========================================================
    # --------------------------------------------------------
    # list
    # --------------------------------------------------------
    @staticmethod
    def list() -> tuple[Stream]:
        """ Gets all instances of Stream. Returns a tuple object. """
        return tuple(Stream.__instances.values())

    # --------------------------------------------------------
    # get
    # --------------------------------------------------------
    @staticmethod
    def get(stream_id: int) -> Stream | None:
        """ Gets a Stream with a given ID. If ID doesn't exist, returns None."""
        return Stream.__instances[stream_id] if stream_id in Stream.__instances else None

    # =================================================================
    # reset
    # =================================================================
    @staticmethod
    def reset():
        """Reset the local list of streams"""
        Stream.__instances = dict()

    # ========================================================
    # PROPERTIES
    # ========================================================

    # --------------------------------------------------------
    # id
    # --------------------------------------------------------
    @property
    def id(self) -> int:
        """ Gets the id of the Stream. """
        return self.__id

    # ========================================================
    # METHODS
    # ========================================================

    # --------------------------------------------------------
    # share_blocks (STATIC)
    # --------------------------------------------------------
    @staticmethod
    def share_blocks(b1: Block, b2: Block) -> bool:
        """Checks if there's a Stream that shares the two blocks provided"""
        occurrences = set()
        if b1.section is None or b2.section is None:
            return False
        for s in b1.section.streams:
            occurrences.add(s.id)
        for s in b2.section.streams:
            if s.id in occurrences:
                return True
        return False

    # --------------------------------------------------------
    # conversion to string
    # --------------------------------------------------------
    def __str__(self) -> str:
        """ Returns a text string with the Stream's number """
        return self.number

    def __repl__(self) -> str:
        return str(self)

    # --------------------------------------------------------
    # description
    # --------------------------------------------------------
    @property
    def description(self) -> str:
        """ Returns a text string that describes the Stream (number & descr) """
        return f"{self.number}: {self.descr}"

    # --------------------------------------------------------
    # delete
    # --------------------------------------------------------
    def delete(self):
        """ Deletes the current instance of Stream """
        del Stream.__instances[self.id]

    def remove(self):
        self.delete()
