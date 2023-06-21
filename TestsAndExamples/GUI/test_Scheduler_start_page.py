from functools import partial
from tkinter import *
from os import path
import sys


sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))
from schedule.GUI.SchedulerTk import SchedulerTk
from schedule.UsefulClasses.Preferences import Preferences


def main():
    # create the top-level window with menu, toolbar and status bar
    p = Preferences()
    p.semester("fall")
    main_page = SchedulerTk('My App', p)
    file = path.dirname(__file__) + "/empty_file.csv"
    p.current_file(file)


    # create the front page with logo
    main_page.create_front_page(lambda f: print(f"Open file <{f}>"), lambda : print("Create new file"))

    main_page.define_exit_callback(lambda *_: print("Application exited"))

    main_page.start_event_loop()



main()