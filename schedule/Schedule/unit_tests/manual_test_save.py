"""
A manual test for the Schedule.write_DB() method. Initializes and populates the DB_NAME database,
then reads the data using Schedule.read_DB() and disconnects from the DB. Then creates a new DB with "_2" appended to the name,
which is populated by using Schedule.write_DB() on the read_DB generated object.

NOTE: This script will not clear either database before or after it is run. The end result will include DB_NAME with its starting data and the dummy data, as well as
DB_NAME_2 with the same data.
"""

import sys

# https://stackoverflow.com/a/28154841 Solution #2
if not __package__:
    from pathlib import Path
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[3]

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError: # Already removed
        pass

    __package__ = "schedule.Schedule.unit_tests"

from ..Schedule import Schedule as mSchedule
from .test_Schedule import populate_db
from ..database.PonyDatabaseConnection import Schedule as dbSchedule, Scenario as dbScenario
from ..database.generic_db import *

db: Database
s: dbSchedule
s2: dbSchedule
sched: mSchedule


@db_session
def init():
    global s, s2
    sc = dbScenario()
    flush()
    s = dbSchedule(official=False, scenario_id=sc.id)
    s2 = dbSchedule(official=False, scenario_id=sc.id)


if __name__ == "__main__":
    db = create_db()
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    init()
    populate_db(s.id)
    populate_db(s2.id)

    if False:
        sched = mSchedule.read_DB(1)

        db.disconnect()
        db.provider = db.schema = None
        db = create_db(DB_NAME + "_2")
        db.drop_all_tables(with_all_data=True)
        db.create_tables()

        sched.write_DB()