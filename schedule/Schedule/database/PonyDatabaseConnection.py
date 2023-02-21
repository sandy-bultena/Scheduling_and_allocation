from decimal import Decimal

from pony.orm import *
import mysql.connector

# Test database to verify that Pony works. Anything done here won't affect the main scheduler_db.
db_name = "pony_scheduler_db"

# Create the database if it doesn't exist. Using mysql.connector to accomplish this because Pony
# doesn't let you use the create_db option when binding to a MySQL database.
conn = mysql.connector.connect(
    host="10.101.0.27",
    username="evan_test",
    password="test_stage_pwd_23"
)

cursor = conn.cursor()

print("Initializing database...")

cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
cursor.execute(f"USE {db_name}")

# close the cursor and connection before switching over to Pony.
cursor.close()
conn.close()

# Create a Pony Database object.
db = Database()

# Turn on debug mode, so we can see the SQL statements.
set_sql_debug(True)


# Create all the Entity classes.
class Lab(db.Entity):
    # id = PrimaryKey(int)
    number = Required(str, max_len=50)
    description = Optional(str, max_len=100)
    # This field won't be present in the database, but we have to declare it here to establish a
    # one-to-many relationship between Lab and TimeSlot.
    unavailable_slots = Set('TimeSlot')
    blocks = Set('Block')


class Teacher(db.Entity):
    # id = PrimaryKey(int)
    first_name = Required(str, max_len=50)
    last_name = Required(str, max_len=50)
    dept = Optional(str, max_len=50)
    #schedules = Set('Schedule')
    schedules = Set('Schedule_Teacher')
    #sections = Set('Section')
    sections = Set('Section_Teacher')
    blocks = Set('Block')


class Course(db.Entity):
    # id = PrimaryKey(int)
    name = Required(str, max_len=50)
    number = Optional(str, max_len=15)
    allocation = Optional(bool, default=True, sql_default='1')
    sections = Set('Section')


class TimeSlot(db.Entity):
    _table_ = "time_slot"  # Give the table a custom name; otherwise it becomes "timeslot".
    # id = PrimaryKey(int)
    day = Required(str, max_len=3)
    duration = Required(Decimal, 3, 1)
    start = Required(str, max_len=5)
    movable = Optional(bool, default=True, sql_default='1')
    block_id = Optional('Block', cascade_delete=True)
    unavailable_lab_id = Optional(Lab)


class Scenario(db.Entity):
    # id = PrimaryKey(int)
    name = Optional(str, max_len=50)
    description = Optional(str, max_len=1000)
    year = Optional(int, max=2200)
    schedules = Set('Schedule')


class Schedule(db.Entity):
    # id = PrimaryKey(int)
    description = Optional(str, max_len=100)
    semester = Required(str, max_len=11)
    official = Required(bool)
    scenario_id = Required(Scenario)
    sections = Set('Section')
    #teachers = Set(Teacher)
    teachers = Set('Schedule_Teacher')

class Section(db.Entity):
    # id = PrimaryKey(int)
    name = Optional(str, max_len=50)
    number = Optional(str, max_len=15)
    hours = Optional(Decimal, 4, 2, sql_default='1.5')
    num_students = Optional(int, sql_default='0')
    course_id = Required(Course)
    schedule_id = Required(Schedule)
    streams = Set('Stream')
    #teachers = Set(Teacher)
    teachers = Set('Section_Teacher')
    blocks = Set('Block')


class Stream(db.Entity):
    # id = PrimaryKey(int)
    number = Required(str, max_len=2)
    descr = Optional(str, max_len=50)
    sections = Set(Section)


class Block(db.Entity):
    # id = PrimaryKey(int)
    # Every Block is an instance of a TimeSlot. However, using normal inheritance causes problems
    # here because you can't give the child class a different primary key from the parent class,
    # and you can't use a non-primary key as a foreign key in other tables. Because of this,
    # we've decided to simply create a link between the two tables without inheriting anything.
    time_slot_id = Required(TimeSlot)

    # Blocks have a many-to-one relationship with Sections. A Block can belong to one Section,
    # or none.
    section_id = Optional(Section)
    # Blocks have many-to-many relationships with Labs and Teachers.
    labs = Set(Lab)
    teachers = Set(Teacher)
    number = Required(int, min=0)

class Schedule_Teacher(db.Entity):
    teacher_id = Required(Teacher)
    schedule_id = Required(Schedule)
    work_release = Required(Decimal, 4, 2)
    PrimaryKey(teacher_id, schedule_id)

class Section_Teacher(db.Entity):
    teacher_id = Required(Teacher)
    section_id = Required(Section)
    allocation = Required(Decimal, 3, 1)
    PrimaryKey(teacher_id, section_id)

def bind_entities(**db_params):
    # Binds all entities created in this script to the specified database. If the database doesn't
    # exist, it will be created. (I hope) NOTE: Verified that this does not work. MySQL binding
    # doesn't accept a create_db option. Have to use mysql.connector to ensure the database's
    # creation, done above.
    db_params['database'].bind(db_params)


def map_entities(db):
    # Map the Entity classes to the database tables once the entities have been defined and the
    # database has been bound.
    db.generate_mapping(create_tables=True)


def define_entities(db):
    class Lab(db.Entity):
        # id = PrimaryKey(int)
        name = Required(str, max_len=50)
        description = Optional(str, max_len=100)
        # This field won't be present in the database, but we have to declare it here to establish a
        # one-to-many relationship between Lab and TimeSlot.
        unavailable_slots = Set('TimeSlot')
        blocks = Set('Block')

    class Teacher(db.Entity):
        # id = PrimaryKey(int)
        first_name = Required(str, max_len=50)
        last_name = Required(str, max_len=50)
        dept = Optional(str, max_len=50)
        schedules = Set('Schedule')
        sections = Set('Section')
        blocks = Set('Block')

    class Course(db.Entity):
        # id = PrimaryKey(int)
        name = Required(str, max_len=50)
        number = Optional(str, max_len=15)
        allocation = Optional(bool, default=True, sql_default='1')
        sections = Set('Section')

    class TimeSlot(db.Entity):
        _table_ = "time_slot"  # Give the table a custom name; otherwise it becomes "timeslot".
        # id = PrimaryKey(int)
        day = Required(str, max_len=3)
        duration = Required(Decimal, 3, 1)
        start = Required(str, max_len=5)
        movable = Optional(bool, default=True, sql_default='1')
        block_id = Optional('Block', cascade_delete=True)
        unavailable_lab_id = Optional(Lab)

    class Scenario(db.Entity):
        # id = PrimaryKey(int)
        name = Optional(str, max_len=50)
        description = Optional(str, max_len=1000)
        year = Optional(int, max=2200)
        schedules = Set('Schedule')

    class Schedule(db.Entity):
        # id = PrimaryKey(int)
        description = Optional(str, max_len=100)
        semester = Required(str, max_len=11)
        official = Required(bool)
        scenario_id = Required(Scenario)
        sections = Set('Section')
        teachers = Set(Teacher)

    class Section(db.Entity):
        # id = PrimaryKey(int)
        name = Optional(str, max_len=50)
        number = Optional(str, max_len=15)
        hours = Optional(Decimal, 4, 2, sql_default='1.5')
        num_students = Optional(int, sql_default='0')
        course_id = Required(Course)
        schedule_id = Required(Schedule)
        streams = Set('Stream')
        teachers = Set(Teacher)
        blocks = Set('Block')

    class Stream(db.Entity):
        # id = PrimaryKey(int)
        number = Required(str, max_len=2)
        descr = Optional(str, max_len=50)
        sections = Set(Section)

    class Block(db.Entity):
        # id = PrimaryKey(int)
        # Every Block is an instance of a TimeSlot. However, using normal
        # inheritance causes problems here because you can't give the child class a different
        # primary key from the parent class, and you can't use a non-primary key as a foreign key
        # in other tables. Because of this, we've decided to simply create a link between the two
        # tables without inheriting anything.
        time_slot_id = Required(TimeSlot)

        # Blocks have a many-to-one relationship with Sections. A Block can belong to one Section,
        # or none.
        section_id = Optional(Section)
        # Blocks have many-to-many relationships with Labs and Teachers.
        labs = Set(Lab)
        teachers = Set(Teacher)
        number = Required(int, min=0)


def define_database(**db_params):
    if db_params['provider'] == 'mysql':
        conn = mysql.connector.connect(host=db_params['host'], username=db_params['user'],
                                       password=db_params['passwd'])
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_params['db']}")
        cursor.close()
        conn.close()
    # db = Database()
    # define_entities(db)
    db_params['database'] = db
    bind_entities(**db_params)
    map_entities(db)
    return db
