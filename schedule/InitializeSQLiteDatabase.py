"""Initializes an SQLite database file containing test data for the whole application."""
from pony.orm import db_session, commit

from schedule.Schedule.Course import Course
from schedule.Schedule.Lab import Lab
from schedule.Schedule.Schedule import Schedule
from schedule.Schedule.Section import Section
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
        db_lab = PonyDatabaseConnection.Lab(number="R-101",
                                            description="Test Lab")
        commit()
        my_lab = Lab(db_lab.number, db_lab.description, id=db_lab.id)

    return my_lab


def create_section(ent_sched: Schedule, ent_course: Course):
    db_sched = PonyDatabaseConnection.Schedule[ent_sched.id]
    db_course = PonyDatabaseConnection.Course[ent_course.id]
    commit()
    if PonyDatabaseConnection.Section.get(id=1) is None:
        my_sect = Section(name="Test Section", number="S-1", course=ent_course, schedule_id=ent_sched.id)
    else:
        db_sect = PonyDatabaseConnection.Section.get(id=1)
        my_sect = Section(number=db_sect.number, hours=db_sect.hours,
                          name=db_sect.name, course=ent_course,
                          id=db_sect.id)
    return my_sect


def create_block():
    pass


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
        block_a = create_block()
    print(course_a)
    course_a.assign_lab(lab_a)


if __name__ == "__main__":
    main()
