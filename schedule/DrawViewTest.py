from tkinter import *
from tkinter import ttk

from schedule.Export import DrawView
from schedule.Schedule.Teacher import Teacher


def main():
    teacher = Teacher("John", "Smith", id=1)

    main_window = Tk()
    cn = Canvas(main_window)
    cn.pack()

    scl = {
        'xoff': 1,
        'yoff': 1,
        'xorg': 0,
        'yorg': 0,
        'xscl': 100,
        'yscl': 60,
        'scale': 1
    }

    DrawView.draw_background(cn, scl)
    main_window.mainloop()


if __name__ == "__main__":
    main()
