from functools import partial
from tkinter import *
from os import path
import sys
from typing import Optional

from schedule.gui_pages.scheduler_entry_point_tk import SchedulerTk
from schedule.Utilities.Preferences import Preferences
from schedule.Utilities.NoteBookPageInfo import NoteBookPageInfo

main_page: Optional[SchedulerTk] = None


def main():
    global main_page
    # create the top-level window with menu, _toolbar and status bar
    p = Preferences()
    p.semester("fall")
    main_page = SchedulerTk('My App', p)
    file = path.dirname(__file__) + "/empty_file.csv"
    p.previous_file(file)

    # create the front page with _logo
    main_page.create_front_page(open_file, lambda: print("Create new file"))

    main_page.define_exit_callback(lambda *_: print("Application exited"))

    main_page.start_event_loop()


def open_file(filename, schedule=None):
    print(f"Open file <{filename}>")
    notebook_info = get_notebook_info()
    main_page.create_standard_page(notebook_info)


def get_notebook_info():
    nb1 = NoteBookPageInfo("Schedules", event_handler=lambda *_: print("Schedules called"),
                           frame_callback=lambda *_: print("Schedules frame callback"))

    nb1.subpages = [
        NoteBookPageInfo("Schedules-3", lambda *_: print("Schedules/Overview/Schedules-3 called")),
        NoteBookPageInfo("Overview-3", lambda *_: print("Schedules/Overview/Overview-3 called")),
        NoteBookPageInfo("Courses-3", lambda *_: print("Schedules/Overview/Courses-3 called")),
        NoteBookPageInfo("Teachers-3", lambda *_: print("Schedules/Overview/Teachers-3 called")),
        NoteBookPageInfo("Labs-3", lambda *_: print("Schedules/Overview/Labs-3 called")),
        NoteBookPageInfo("Streams-3", lambda *_: print("Schedules/Overview/Streams-3 called")),
    ]

    return [
        nb1,
        NoteBookPageInfo("Overview", event_handler=_show_overview,
                         frame_callback=lambda *_: print("Overview frame method called")),
        NoteBookPageInfo("Courses", lambda *_: print("Courses called"), frame_args={'background': 'purple'}, ),
        NoteBookPageInfo("Teachers", lambda *_: print("Teachers called")),
        NoteBookPageInfo("Labs", lambda *_: print("Labs called")),
        NoteBookPageInfo("Streams", lambda *_: print("Streams called"))
    ]


main()
