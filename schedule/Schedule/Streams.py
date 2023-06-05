from __future__ import annotations
from typing import *
import schedule.Schedule.IDGeneratorCode as id_gen

""" SYNOPSIS/EXAMPLE:
    from Schedule.Stream import Stream

    stream = Stream(number = "P322")
    
    all_labs = Stream.list()
"""

_stream_id_generator: Generator[int, int, None] = id_gen.get_id_generator()


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: _Stream - should never be instantiated directly!
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Stream:
    """ Describes a group of students whose classes cannot overlap. """

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, number: str = "A", description: str = "", *, stream_id: int = None):
        """
        Creates an instance of the Stream class.
        - Parameter number -> defines the stream number.
        - Parameter desc -> defines the stream title.
        """
        self.number = number
        self.description = description

        self.__id = id_gen.set_id(_stream_id_generator, stream_id)

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


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Collection
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Streams(dict[int, Stream]):

    # =====================================================================================
    # all
    # =====================================================================================
    def get_all(self) -> tuple[Stream, ...]:
        return tuple(self.values())

    # =====================================================================================
    # by id
    # =====================================================================================
    def get_by_id(self, stream_id: int) -> Stream | None:
        return self.get(stream_id)

    # =================================================================
    # add
    # =================================================================
    def add(self, number: str = "A", descr: str = "", *, stream_id: int = None) -> Stream:
        stream = Stream(number, descr, stream_id=stream_id)
        self[stream.id] = stream
        return stream

    # =================================================================
    # remove
    # =================================================================
    def remove(self, stream: Stream) -> None:
        if stream.id in self:
            del (self[stream.id])
