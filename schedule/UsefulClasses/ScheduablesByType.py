from ..Schedule.ScheduleEnums import ViewType


class ScheduablesByType:
    def __init__(self, type: ViewType, title, names, scheduable_objs):
        """A collection of Scheduable objects belonging to a common type.

        Parameters:
            type: What type of schedulables are these?
            title: Title of this collection of schedulables.
            names: Array of names used for each schedulable object.
            scheduable_objs: The list of schedulable objects."""
        # Validation (may not be necessary, thanks to the enum.
        if type not in ViewType:
            raise ValueError(f"You have specified an invalid type ({type}) for a ViewChoice")

        # Make an ordered list of names for the schedulable objects.from
        named_schedulable_objs = []
        for i in range(len(names)):
            named_schedulable_objs.append(NamedObject(names[i], scheduable_objs[i]))

