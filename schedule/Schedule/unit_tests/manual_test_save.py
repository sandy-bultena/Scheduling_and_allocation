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
    print('e')
    from pathlib import Path
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[3]

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError: # Already removed
        pass

    import schedule.Schedule.unit_tests
    __package__ = "schedule.Schedule.unit_tests"

from pony.orm import *
from .db_constants import *
from ..Schedule import Schedule
from .test_Schedule import populate_db
from ..database.PonyDatabaseConnection import define_database, Schedule as dbSchedule, Scenario as dbScenario

db : Database
s : dbSchedule
sched : Schedule

@db_session
def init():
    global s
    sc = dbScenario()
    flush()
    s = dbSchedule(official=False, scenario_id=sc.id)

if __name__ == "__main__":
    db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)
    db.drop_all_tables(with_all_data = True)
    db.create_tables()

    init()
    populate_db(s.id)

    sched = Schedule.read_DB(1)

    db.disconnect()
    db.provider = db.schema = None
    db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME + "_2", provider=PROVIDER, user=USERNAME)
    db.drop_all_tables(with_all_data = True)
    db.create_tables()

    sched.write_DB()