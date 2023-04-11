"""Initializes an SQLite database file containing test data for the whole application."""
from pony.orm import db_session, commit

from schedule.Schedule.database import PonyDatabaseConnection
from schedule.Schedule.database.db_constants import *


@db_session
def create_scenario() -> PonyDatabaseConnection.Scenario:
    if PonyDatabaseConnection.Scenario.get(id=1) is None:
        db_scenario = PonyDatabaseConnection.Scenario(name="Test Scenario",
                                                      description="This is a test",
                                                      semester="Fall 2023")
    else:
        db_scenario = PonyDatabaseConnection.Scenario.get(id=1)
    commit()
    return db_scenario


@db_session
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


def main():
    if PROVIDER != "sqlite":
        raise ValueError(f"Invalid pony provider format retrieved from .env file: {PROVIDER}")
    db = PonyDatabaseConnection.define_database(provider=PROVIDER, filename=DB_NAME,
                                                create_db=CREATE_DB)
    db_scen = create_scenario()
    db_sched = create_schedule(db_scen)


if __name__ == "__main__":
    main()
