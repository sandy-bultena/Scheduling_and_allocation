from Section import Section

class SectionList(list):
    def __delitem__(self, key):
        item : Section = self.__getitem__(key)
        super().__delitem__(key)
        item.delete()
    
    def pop(self, key):
        """ Removes the specified index from the local list and the database. Returns None """
        super().pop(key).delete()
    
    def remove(self, val : Section):
        """ Removes the specified value from the local list and the database. Returns None """
        super().remove(val)
        val.delete()