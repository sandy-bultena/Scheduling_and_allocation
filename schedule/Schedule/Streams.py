from __future__ import annotations
from typing import *
import schedule.Schedule.IDGeneratorCode as id_gen


""" SYNOPSIS/EXAMPLE:
    from Schedule.Stream import Stream

    stream = Stream(number = "P322")
    
    all_labs = Stream.list()
"""

_instances: dict[int, Stream] = {}
_stream_id_generator: Generator[int, int, None] = id_gen.get_id_generator()


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

        self.__id = id_gen.set_id(_stream_id_generator, stream_id)
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
