from tkinter import Tk

from pony.orm import commit, db_session

from schedule.GUI.GuiBlockTk import GuiBlockTk
from schedule.Presentation.View import View

from schedule.Schedule.Schedule import Schedule
from schedule.Schedule.Teacher import Teacher
from schedule.Schedule.Block import Block

from schedule.Schedule.database import PonyDatabaseConnection
from schedule.Schedule.database.db_constants import *


# ----------------------------------------------------------
# connect to the database, instantiate a Scenario.
# ----------------------------------------------------------
def main():
    db = PonyDatabaseConnection.define_database(host=HOST, db=DB_NAME, user=USERNAME,
                                                passwd=PASSWD, provider=PROVIDER)

    mw = Tk()
    db_schedule = get_db_schedule()

    # ----------------------------------------------------------
    # create a Schedule for the Scenario. Create a teacher and
    # add a Block to it.
    # ----------------------------------------------------------
    my_schedule = Schedule.read_DB(db_schedule.id)
    teacher = Teacher.get_by_name("John", "Smith")

    my_view = View(views_manager=None, mw=mw, schedule=my_schedule, schedulable_object=teacher)

    block = Block("Wed", "9:30", 1.5, 1)

    gui_block = GuiBlockTk("teacher", my_view, block)
    gui_block.change_colour("red")


@db_session
def get_db_schedule():
    db_scenario = PonyDatabaseConnection.Scenario()
    commit()
    db_schedule = PonyDatabaseConnection.Schedule(official=False, scenario_id=db_scenario)
    commit()
    teacher = PonyDatabaseConnection.Teacher(first_name="John", last_name="Smith")
    commit()
    sched_teach = PonyDatabaseConnection.Schedule_Teacher(teacher_id=teacher,
                                                          schedule_id=db_schedule,
                                                          work_release=3)
    db_schedule.teachers.add(sched_teach)
    return db_schedule


if __name__ == "__main__":
    main()
