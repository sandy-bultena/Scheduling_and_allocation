from __future__ import annotations
from typing import *

""" SYNOPSIS/EXAMPLE:
    from Schedule.Stream import Stream

    stream = Stream(number = "P322")
    
    all_labs = Stream.list()
"""

_instances: dict[int, Stream] = {}


# ============================================================================
# auto id generator
# ============================================================================
def stream_id_generator(max_id: int = 0):
    the_id = max_id + 1
    while True:
        yield the_id
        the_id = the_id + 1


id_generator: Generator[int, Any, None] = stream_id_generator()


# ============================================================================
# get_all
# ============================================================================
def get_all() -> tuple[Stream]:
    """Returns an immutable tuple containing all instances of the Teacher class."""
    return tuple(_instances.values())


# =================================================================
# get_by_id
# =================================================================
def get_by_id(stream_id: int) -> Stream | None:
    """Returns the Teacher object matching the specified ID, if it exists."""
    if stream_id in _instances.keys():
        return _instances[stream_id]
    return None


# ============================================================================
# reset
# ============================================================================
def clear_all():
    """Reset the local list of labs"""
    _instances.clear()


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: Stream
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Stream:
    """ Describes a group of students whose classes cannot overlap. """

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

        self.__id = stream_id if stream_id else next(id_generator)
        _instances[self.__id] = self

    # --------------------------------------------------------
    # id
    # --------------------------------------------------------
    @property
    def id(self) -> int:
        """ Gets the id of the Stream. """
        return self.__id

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
        del _instances[self.id]

    def remove(self):
        self.delete()
