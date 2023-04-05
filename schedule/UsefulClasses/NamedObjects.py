class NamedObject:
    """Data struct that has a name for an object, and the object itself."""
    def __init__(self, name, nameless_object):
        """Create a new Named schedulable object.

        Parameters:
            name: The name of the object.
            nameless_object: The object proper. Can be a Teacher, Lab or Stream.
        """
        self.name = name
        self.object = nameless_object

