"""Initializes an SQLite database file containing test data for the whole application."""
from pony.orm import db_session, commit

from schedule.Schedule.Block import Block
from schedule.Schedule.Course import Course
from schedule.Schedule.Lab import Lab
from schedule.Schedule.LabUnavailableTime import LabUnavailableTime
from schedule.Schedule.Schedule import Schedule
from schedule.Schedule.Section import Section
from schedule.Schedule.Stream import Stream
from schedule.Schedule.Teacher import Teacher
from schedule.Schedule.database import PonyDatabaseConnection
from schedule.Schedule.database.db_constants import *


def create_scenario() -> PonyDatabaseConnection.Scenario:
    if PonyDatabaseConnection.Scenario.get(id=1) is None:
        db_scenario = PonyDatabaseConnection.Scenario(name="Test Scenario",
                                                      description="This is a test",
                                                      semester="Fall 2023")
    else:
        db_scenario = PonyDatabaseConnection.Scenario.get(id=1)
    commit()
    return db_scenario


def create_schedule(db_scen: PonyDatabaseConnection.Scenario) -> PonyDatabaseConnection.Schedule:
    if PonyDatabaseConnection.Schedule.get(id=1) is None:
        db_schedule = PonyDatabaseConnection.Schedule(
            description="Test Schedule",
            official=False,
            scenario_id=db_scen
        )
    else:
        db_schedule = PonyDatabaseConnection.Schedule.get(id=1)
    commit()
    return db_schedule


def create_course() -> Course:
    if PonyDatabaseConnection.Course.get(id=1) is None:
        my_course = Course("420-101", "Intro to Programming", 1)
    else:
        db_course = PonyDatabaseConnection.Course.get(id=1)
        commit()
        my_course = Course(db_course.number, db_course.name, db_course.semester,
                           db_course.allocation, id=db_course.id)
    return my_course


def create_lab():
    if PonyDatabaseConnection.Lab.get(id=1) is None:
        my_lab = Lab("R-101", "Test Lab")
    else:
        db_lab = PonyDatabaseConnection.Lab.get(id=1)
        commit()
        my_lab = Lab(db_lab.number, db_lab.description, id=db_lab.id)

    return my_lab


def create_section(ent_sched: Schedule, ent_course: Course):
    if PonyDatabaseConnection.Section.get(id=1) is None:
        my_sect = Section(name="Test Section", number="S-1", course=ent_course,
                          schedule_id=ent_sched.id)
    else:
        db_sect = PonyDatabaseConnection.Section.get(id=1)
        my_sect = Section(number=db_sect.number, hours=db_sect.hours,
                          name=db_sect.name, course=ent_course,
                          id=db_sect.id)
    return my_sect


def create_block(sect: Section = None) -> Block:
    if PonyDatabaseConnection.Block.get(id=1) is None:
        my_block = Block("mon", "8:30", 1.5, 1)
    else:
        db_block = PonyDatabaseConnection.Block.get(id=1)
        my_block = Block(db_block.day, db_block.start, db_block.duration, db_block.number,
                         db_block.movable, id=db_block.id)
    commit()
    if isinstance(sect, Section):
        my_block.section = sect
        commit()
    return my_block


def create_teacher():
    if PonyDatabaseConnection.Teacher.get(id=1) is None:
        my_teach = Teacher("John", "Smith", "Computer Science")
    else:
        db_teach = PonyDatabaseConnection.Teacher.get(id=1)
        my_teach = Teacher(db_teach.first_name, db_teach.last_name, db_teach.dept, id=db_teach.id)
    return my_teach


def create_stream(sect: Section) -> Stream:
    if PonyDatabaseConnection.Stream.get(id=1) is None:
        my_stream = Stream("A")
    else:
        db_stream = PonyDatabaseConnection.Stream.get(id=1)
        my_stream = Stream(db_stream.number, db_stream.descr, id=db_stream.id)
    commit()
    sect.assign_stream(my_stream)
    return my_stream


def create_unavailable_time(lab: Lab, sched: Schedule):
    if PonyDatabaseConnection.LabUnavailableTime.get(id=1) is None:
        my_time = LabUnavailableTime(schedule=sched)
    else:
        db_time = PonyDatabaseConnection.LabUnavailableTime.get(id=1)
        my_time = LabUnavailableTime(
            day=db_time.day,
            start=db_time.start,
            duration=db_time.duration,
            movable=db_time.movable,
            id=db_time.id,
            schedule=sched
        )
    commit()
    return my_time


def main():
    if PROVIDER != "sqlite":
        raise ValueError(f"Invalid pony provider format retrieved from .env file: {PROVIDER}")
    db = PonyDatabaseConnection.define_database(provider=PROVIDER, filename=DB_NAME,
                                                create_db=CREATE_DB)
    with db_session:
        db_scen = create_scenario()
        db_sched = create_schedule(db_scen)
        my_sched = Schedule.read_DB(db_sched.id)

    print(my_sched)

    with db_session:
        course_a = create_course()
        lab_a = create_lab()
        section_a = create_section(my_sched, course_a)
        block_a = create_block(section_a)
    print(course_a)
    section_a.add_block(block_a)
    course_a.add_section(section_a)
    course_a.assign_lab(lab_a)

    with db_session:
        teacher_a = create_teacher()
        stream_a = create_stream(section_a)
        unvailable_a = create_unavailable_time(lab_a, my_sched)

    lab_a.add_unavailable_slot(unvailable_a)
    course_a.assign_teacher(teacher_a)
    course_a.assign_stream(stream_a)
    print(course_a)
    print(my_sched.teachers())
    print(my_sched.blocks())
    print(my_sched.labs())
    print(my_sched.courses())
    print(my_sched.sections)

    with db_session:
        my_sched.write_DB()


if __name__ == "__main__":
    main()
