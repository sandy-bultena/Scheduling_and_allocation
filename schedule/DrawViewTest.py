from tkinter import *
from tkinter import ttk

from schedule.Export import DrawView
from schedule.Schedule.Teacher import Teacher
from schedule.Schedule.Block import Block
from schedule.Schedule.ScheduleEnums import WeekDay
from schedule.Schedule.database import PonyDatabaseConnection
from schedule.Schedule.database.db_constants import *


def main():
    # ----------------------------------------------------------
    # connect to the database, instantiate a Teacher and some Blocks.
    # ----------------------------------------------------------
    db = PonyDatabaseConnection.define_database(host=HOST, db=DB_NAME, user=USERNAME,
                                                        passwd=PASSWD, provider=PROVIDER)

    teacher = Teacher("John", "Smith")
    block_1 = Block(WeekDay.Monday, "8:30", 1.5, 1)
    block_2 = Block(WeekDay.Wednesday, "8:30", 1.5, 1)
    block_1.assign_teacher(teacher)
    block_2.assign_teacher(teacher)

    blocks = [block_1, block_2]

    # ----------------------------------------------------------
    # Create the Tk main window and the canvas
    # ----------------------------------------------------------
    main_window = Tk()
    # main_window.geometry('500x600-300-40')
    cn = Canvas(main_window)
    cn.pack(fill=BOTH)

    # ----------------------------------------------------------
    # Define what scale you want
    # ----------------------------------------------------------
    scl = {
        'xoff': 1,
        'yoff': 1,
        'xorg': 0,
        'yorg': 0,
        'xscl': 100,
        'yscl': 60,
        'scale': 1
    }

    # ----------------------------------------------------------
    # draw the grid on the canvas.
    # ----------------------------------------------------------
    DrawView.draw_background(cn, scl)

    # ----------------------------------------------------------
    # Draw the teacher blocks on canvas.
    # ----------------------------------------------------------
    for block in blocks:
        DrawView.draw_block(cn, block, scl, "stream")
    main_window.mainloop()


if __name__ == "__main__":
    main()
