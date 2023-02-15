from pony.orm import *
from PonyDatabaseConnection import *


@db_session
def create_time_slots():
    """Test function which creates two TimeSlot entities and inserts them into the relevant table
    of the database.

    Because the db_session decorator has been applied to this function, the created entities will
    be inserted into the database without any need to call the commit function.

    Note also that, because we are importing everything from PonyDatabaseConnection, the program
    seems to know what database to use without any need to specify things on our part. I believe
    PonyDatabaseConnection may be being run at the same time that the contents of this page are
    being run. """
    slot_1 = TimeSlot(id=1, day="mon", duration=1.5, start="8:30")
    slot_2 = TimeSlot(id=2, day="wed", duration=3, start="14:30")


create_time_slots()
