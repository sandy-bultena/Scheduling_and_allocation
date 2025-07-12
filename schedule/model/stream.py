from __future__ import annotations
from typing import Generator
from .enums import ResourceType

""" SYNOPSIS/EXAMPLE:
    from Schedule.Stream import Stream

    stream = Stream(number = "P322")
    
    all_labs = Stream.list()
"""


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: _Stream - should never be instantiated directly!
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Stream:
    """ Describes a group of students whose classes cannot overlap. """

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, number: str = "A", description: str = ""):
        """
        Creates an instance of the Stream class.
        - Parameter number -> defines the stream number.
        - Parameter desc -> defines the stream title.
        """
        self._number = number
        self.description = description
        self.resource_type = ResourceType.stream

    # --------------------------------------------------------
    # unique identifier
    # --------------------------------------------------------
    @property
    def number(self) -> str:
        return self._number

    # --------------------------------------------------------
    # conversion to string
    # --------------------------------------------------------
    def __str__(self) -> str:
        """ Returns a text string with the Stream's number """
        return self.number + " " + self.description

    def __repl__(self) -> str:
        return str(self)

    # ------------------------------------------------------------------------
    # for sorting
    # ------------------------------------------------------------------------
    def __lt__(self, other):
        return self.number < other.number

    def __eq__(self, other):
        return self.number == other.number

    def __hash__(self):
        return hash(self.number)
