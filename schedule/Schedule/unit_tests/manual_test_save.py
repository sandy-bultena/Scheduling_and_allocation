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
from database.PonyDatabaseConnection import\
    define_database, Schedule as dbSchedule, Scenario as dbScenario, Lab as dbLab, Teacher as dbTeacher, Section_Teacher as dbSecTeach,\
    Course as dbCourse, TimeSlot as dbTimeSlot, Section as dbSection, Stream as dbStream, Block as dbBlock, Schedule_Teacher as dbSchedTeach

db : Database
s : dbSchedule
sched : Schedule

def pre_init():
    global db
    db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)
    db.drop_all_tables(with_all_data = True)
    db.create_tables()

@db_session
def init():
    global s
    sc = dbScenario()
    flush()
    s = dbSchedule(semester="Winter 2023", official=False, scenario_id=sc.id)

@db_session
def main():
    global db

    c1 = dbCourse(name="Course 1", number="101-NYA", allocation=True)
    c2 = dbCourse(name="Course 2", number="102-NYA", allocation=False)
    c3 = dbCourse(name="Course 3", number="103-NYA", allocation=True)
    c4 = dbCourse(name="Course 4", number="104-NYA", allocation=False)
    st1 = dbStream(number="3A", descr="Stream #1")
    st2 = dbStream(number="3B", descr="Stream #2")
    st3 = dbStream(number="3C", descr="Stream #3")
    st4 = dbStream(number="3D", descr="Stream #4")
    t1 = dbTeacher(first_name="0Jane", last_name="0Doe", dept="0Computer Science")
    t2 = dbTeacher(first_name="1John", last_name="1Doe", dept="1English")
    t3 = dbTeacher(first_name="2Joe", last_name="2Smith", dept="2Science")
    l1 = dbLab(number="P320", description="Computer Lab 1")
    l2 = dbLab(number="P321", description="Computer Lab 2")
    l3 = dbLab(number="P322", description="Computer Lab 3")
    flush()

    ts1 = dbTimeSlot(day="mon", duration=1, start="8:00", unavailable_lab_id=l1.id)
    ts2 = dbTimeSlot(day="tue", duration=2, start="9:00", movable = False)
    ts3 = dbTimeSlot(day="wed", duration=3, start="10:00")
    ts4 = dbTimeSlot(day="wed", duration=4, start="11:00")
    se1 = dbSection(course_id=c1.id, schedule_id=s.id, name="Section 1", number="SE1", num_students=10)
    se2 = dbSection(course_id=c2.id, schedule_id=s.id, name="Section 2", number="SE2", num_students=20)
    se3 = dbSection(course_id=c3.id, schedule_id=s.id, name="Section 3", number="SE3", num_students=30)
    se4 = dbSection(course_id=c4.id, schedule_id=s.id, name="Section 4", number="SE4", num_students=40)
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
    b1 = dbBlock(section_id=se1.id, time_slot_id=ts2.id, number=1)
    b2 = dbBlock(section_id=se2.id, time_slot_id=ts3.id, number=2)
    b3 = dbBlock(section_id=se4.id, time_slot_id=ts4.id, number=3)
    b1.teachers.add(t1)
    b2.teachers.add(t2)
    b3.teachers.add(t2)
    b1.labs.add(l1)
    b2.labs.add(l2)
    b3.labs.add(l3)
    flush()


def mid():
    global db
    db.disconnect()
    db.provider = db.schema = None
    db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME + "_2", provider=PROVIDER, user=USERNAME)
    db.drop_all_tables(with_all_data = True)
    db.create_tables()

pre_init()
init()
main()
sched = Schedule.read_DB(1)
mid()
sched.write_DB()