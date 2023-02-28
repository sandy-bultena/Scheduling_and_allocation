"""
A manual test for the Schedule.write_DB() method. Initializes and populates the DB_NAME database,
then reads the data using Schedule.read_DB() and disconnects from the DB. Then creates a new DB titled
"test_pony_db_3", which is populated by using Schedule.write_DB() on the read_DB generated object.
"""
import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__)))
from pony.orm import *
from unit_tests.db_constants import *
from Schedule import Schedule
from database.PonyDatabaseConnection import\
    define_database, Schedule as dbSchedule, Scenario as dbScenario, Lab as dbLab, Teacher as dbTeacher, Section_Teacher as dbSecTeach,\
    Course as dbCourse, TimeSlot as dbTimeSlot, Section as dbSection, Stream as dbStream, Block as dbBlock, Schedule_Teacher as dbSchedTeach

db : Database
s : dbSchedule
sched : Schedule

def pre_init():
    global db
    db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)

@db_session
def init():
    global s
    sc = dbScenario()
    flush()
    s = dbSchedule(semester="Winter 2023", official=False, scenario_id=sc.id)

@db_session
def main():
    global db

    c1 = dbCourse(name="Course 1")
    c2 = dbCourse(name="Course 2")
    c3 = dbCourse(name="Course 3")
    c4 = dbCourse(name="Course 4")
    st1 = dbStream(number="3A")
    st2 = dbStream(number="3B")
    st3 = dbStream(number="3C")
    st4 = dbStream(number="3D")
    t1 = dbTeacher(first_name="Jane", last_name="Doe")
    t2 = dbTeacher(first_name="John", last_name="Doe")
    t3 = dbTeacher(first_name="Joe", last_name="Smith")
    l1 = dbLab(number="P325")
    l2 = dbLab(number="P326")
    l3 = dbLab(number="P327")
    flush()

    ts1 = dbTimeSlot(day="mon", duration=1, start="8:00", unavailable_lab_id=l1.id)
    ts2 = dbTimeSlot(day="tue", duration=1, start="9:00")
    ts3 = dbTimeSlot(day="wed", duration=2, start="10:00")
    ts4 = dbTimeSlot(day="wed", duration=2, start="10:00")
    se1 = dbSection(course_id=c1.id, schedule_id=s.id)
    se2 = dbSection(course_id=c2.id, schedule_id=s.id)
    se3 = dbSection(course_id=c3.id, schedule_id=s.id)
    se4 = dbSection(course_id=c4.id, schedule_id=s.id)
    se1.streams.add(st1)
    se2.streams.add(st2)
    se3.streams.add(st3)
    se4.streams.add(st4)
    sc_te1 = dbSchedTeach(teacher_id=t1.id, schedule_id=s.id, work_release=3)
    sc_te2 = dbSchedTeach(teacher_id=t2.id, schedule_id=s.id, work_release=4)
    sc_te3 = dbSchedTeach(teacher_id=t3.id, schedule_id=s.id, work_release=5)
    flush()

    se_te1 = dbSecTeach(teacher_id=t1.id, section_id=se1.id, allocation=3)
    se_te2 = dbSecTeach(teacher_id=t2.id, section_id=se2.id, allocation=4)
    se_te3 = dbSecTeach(teacher_id=t3.id, section_id=se3.id, allocation=5)
    b1 = dbBlock(section_id=se1.id, time_slot_id=ts2.id, number=3)
    b2 = dbBlock(section_id=se2.id, time_slot_id=ts3.id, number=2)
    b3 = dbBlock(section_id=se4.id, time_slot_id=ts4.id, number=4)
    b1.teachers.add(t1)
    b2.teachers.add(t2)
    b3.teachers.add(t2)
    b1.labs.add(l1)
    b2.labs.add(l2)
    b3.labs.add(l3)
    flush()


def mid():
    global db
    DB_NAME = "test_pony_db_3"
    db.disconnect()
    db.provider = db.schema = None
    db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)

pre_init()
init()
main()
sched = Schedule.read_DB(1)
mid()
sched.write_DB()