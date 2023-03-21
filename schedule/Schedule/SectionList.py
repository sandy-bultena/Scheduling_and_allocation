from __future__ import annotations
from Section import Section

class SectionList(list):
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
    
    @staticmethod
    def lists() -> tuple[SectionList]:
        """ Returns a tuple of all instances of SectionList. """
        return tuple(SectionList.__instances)