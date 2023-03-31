from __future__ import annotations
from .Section import Section

class SectionList(list):
    """
    A collection class for storing a list of sections. Primarily used to keep track of Sections inside Schedule objects.
    Functions virtually identically to a standard list, with the added static method lists(), which returns all existing SectionList instances

    Note that removing a section from a SectionList in any way (remove(), pop(), or del) is interpreted as the deletion of a Section, and it will be removed
    from the local scope and the database, as well as any other SectionList instances. To remove a section from a SectionList without deleting it, use
    deleteless_remove()
    """
    __instances : list[SectionList] = []
    def __init__(self, *args, **kwargs):
        SectionList.__instances.append(self)
        super().__init__(*args, **kwargs)

    def __delitem__(self, key):
        item : Section = self.__getitem__(key)
        super().__delitem__(key)
        item.delete()
    
    def pop(self, key):
        """ Removes the specified index from the local list and the database. Returns None """
        super().pop(key).delete()
    
    def remove(self, val : Section):
        """ Removes the specified value from the local list and the database. Returns None """
        try:
            super().remove(val)
            val.delete(True)
        except ValueError:
            # if there's a ValueError, it means the value isn't in the list
            # assume this means it's already been deleted and return
            # otherwise there's an infinite recursive loop where val.delete() calls SectionList.remove()
            return
    
    def deleteless_remove(self, val : Section):
        """ Removes the specified index from the SectionList without deleting it from local memory or the database. Returns None"""
        super().remove(val)
    
    def append(self, val : Section):
        """Appends the specified object to the end of the SectionList"""
        if not isinstance(val, Section): raise ValueError("Error: SectionList can only contain Section objects")
        super().append(val)
    
    def insert(self, index, val : Section):
        """Inserts the specified object into the SectionList at the given index"""
        if not isinstance(val, Section): raise ValueError("Error: SectionList can only contain Section objects")
        super().insert(index, val)
    
    @staticmethod
    def lists() -> tuple[SectionList]:
        """ Returns a tuple of all instances of SectionList. """
        return tuple(SectionList.__instances)