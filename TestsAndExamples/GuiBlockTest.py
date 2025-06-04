from tkinter import Tk

from pony.orm import commit, db_session

from schedule.GUI_Pages.GuiBlockTk import GuiBlockTk
from schedule.Presentation.View import View

from schedule.Model.schedule import Schedule
from schedule.Model.teacher import Teacher
from schedule.Model.Block import Block

from schedule.Model.database import PonyDatabaseConnection
from schedule.Model.database.db_constants import *


# ----------------------------------------------------------
# connect to the database, instantiate a Scenario.
# ----------------------------------------------------------
def main():
    if PROVIDER == "mysql":
        db = PonyDatabaseConnection.define_database(host=HOST, db=DB_NAME, user=USERNAME,
                                                passwd=PASSWD, provider=PROVIDER)
    elif PROVIDER == "sqlite":
        db = PonyDatabaseConnection.define_database(provider=PROVIDER, filename=DB_NAME,
                                                    create_db=CREATE_DB)

    mw = Tk()
    db_schedule = get_db_schedule()

    # ----------------------------------------------------------
    # create a Schedule for the Scenario. Create a teacher and
    # add a Block to it.
    # ----------------------------------------------------------
    my_schedule = Schedule.read_DB(db_schedule.number)
    teacher = Teacher.get_by_name("John", "Smith")

    my_view = View(views_manager=None, mw=mw, schedule=my_schedule, schedulable_object=teacher)

    block = Block("Wed", "9:30", 1.5, 1)
    block.assign_teacher_by_id(teacher)

    gui_block = GuiBlockTk("stream", my_view.gui, block)
    gui_block.change_colour("red")

    mw.mainloop()


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
    db_schedule.teacher_ids.add(sched_teach)
    return db_schedule


if __name__ == "__main__":
    main()
