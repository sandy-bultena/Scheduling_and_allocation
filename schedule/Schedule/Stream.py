from __future__ import annotations

from database.PonyDatabaseConnection import Stream as dbStream
from pony.orm import *

""" SYNOPSIS/EXAMPLE:
    from Schedule.Stream import Stream

    stream = Stream(number = "P322")
"""

class Stream():
    """ Describes a group of students whose classes cannot overlap. """
    _max_id = 0
    __instances = dict()

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self, number : str = "A", descr : str = "", *args, id : int = None):
        """
        Creates an instance of the Stream class.
        - Parameter number -> defines the stream number.
        - Parameter desc -> defines the stream description.
        """
        if len(args) > 0: raise ValueError("Error: too many positional arguments")
        self.number = number
        self.descr = descr

        self.__id = id if id else Stream.__create_entity(self)
        Stream.__instances[self.__id] = self

    @db_session
    @staticmethod
    def __create_entity(instance : Stream):
        entity_stream = dbStream(number = instance.number, descr = instance.descr)
        commit()
        return entity_stream.get_pk()
    
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
    def get(id : int) -> Stream:
        """ Gets a Stream with a given ID. If ID doesn't exist, returns None."""
        return Stream.__instances[id] if id in Stream.__instances else None
    
    # --------------------------------------------------------
    # reset
    # --------------------------------------------------------
    @staticmethod
    def reset():
        """ Deletes all Streams """
        for s in Stream.list(): s.delete()

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
    def share_blocks(b1, b2):
        """Checks if there's a Stream that shares the two blocks provided"""
        occurences = {}
        if not b1.section or not b2.section: return False
        for s in b1.section.streams: occurences[s.id] = 1
        for s in b2.section.streams:
            if s.id in occurences: return True
        return False

    # --------------------------------------------------------
    # __str__
    # --------------------------------------------------------
    def __str__(self) -> str:
        """ Returns a text string with the Stream's number """
        return self.number
    
    # --------------------------------------------------------
    # print_description     # note: called print_description2 in the Perl version
    # --------------------------------------------------------
    def print_description(self) -> str:
        """ Returns a text string that describes the Stream """
        return f"{self.number}: {self.descr}"
    
    # --------------------------------------------------------
    # delete
    # --------------------------------------------------------
    def delete(self):
        """ Deletes the current instance of Stream """
        if self.id in Stream.__instances: del Stream.__instances[self.id]