"""
A manual test for the Schedule.write_DB() method. Initializes and populates the DB_NAME database,
then reads the data using Schedule.read_DB() and disconnects from the DB. Then creates a new DB with "_2" appended to the name,
which is populated by using Schedule.write_DB() on the read_DB generated object.
"""
import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__)))
from pony.orm import *
from unit_tests.db_constants import *
from Schedule import Schedule
from unit_tests.test_Schedule import populate_db
from database.PonyDatabaseConnection import define_database, Schedule as dbSchedule, Scenario as dbScenario

db : Database
s : dbSchedule
sched : Schedule

@db_session
def init():
    global s
    sc = dbScenario()
    flush()
    s = dbSchedule(semester="Winter 2023", official=False, scenario_id=sc.id)

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