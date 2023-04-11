"""Initializes an SQLite database file containing test data for the whole application."""
from pony.orm import db_session, commit

from schedule.Schedule.Course import Course
from schedule.Schedule.Schedule import Schedule
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
    print(course_a)


if __name__ == "__main__":
    main()
