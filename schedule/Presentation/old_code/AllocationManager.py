# IN PROGRESS
"""Entry point for the GUI_Pages Allocation Management Tool"""

# TODO: Currently crashes when opening the same schedule twice, including when selecting a schedule
# then re-opening the same semester selector and selecting that schedule again,
# due to Schedule.Course.Course.add_sections not adding the same section twice
# based on ID rather than object instance.

import json
from Schedule.ScheduleWrapper import ScheduleWrapper
from Schedule.Schedule import Schedule
# import EditCourses
from Presentation import NumStudents
from .EditAllocation import EditAllocation
from GUI.AllocationManagerTk import AllocationManagerTk
from PerlLib import Colours
# from Presentation import EditResources
from UsefulClasses.NoteBookPageInfo import NoteBookPageInfo
import Presentation.globals as gl
from Schedule.database.generic_db import REQUIRES_LOGIN, create_db
from functools import partial
from Schedule.Scenario import Scenario
from Tk.scrolled import Scrolled

semesters = ['fall', 'winter']
schedules = ScheduleWrapper()

dirty = False
gui: AllocationManagerTk

required_pages: list = []
pages_lookup: dict[str, NoteBookPageInfo] = {}

preferences = dict()

user_base_dir: str = None

scenarios: dict[str, Scenario] = {}


def main():
    global gui
    gui = AllocationManagerTk()
    get_user_preferences()
    create_main_window()
    pre_process_stuff()
    gui.start_event_loop()


# ==================================================================
# user _preferences saved in ini file (JSON format)
# ==================================================================
def get_user_preferences():
    global user_base_dir
    import platform
    import os
    O = platform.system().lower()

    if 'darwin' in O:
        user_base_dir = os.environ["HOME"] # Mac OS linux
    elif 'windows' in O:
        user_base_dir = os.environ["USERPROFILE"]
    else:
        user_base_dir = os.environ["HOME"]

    read_ini()


# ==================================================================
# _read_ini
# ==================================================================
def read_ini():
    from os import path

    global preferences, current_directory
    if user_base_dir and path.isfile(f"{user_base_dir}/.allocation"):
        # Perl ver used YAML, but that requires an extra package we're no longer using
        # going to use JSON instead, which is built-in

        f = open(f"{user_base_dir}/.allocation", 'r')
        try:
            preferences = json.loads(f.read())
        # JSON failed, probably invalid. just ignore it
        except json.JSONDecodeError:
            pass
        finally:
            f.close()
        current_directory = preferences['current_dir']\
            if ('current_dir' in preferences and preferences['current_dir']) else user_base_dir


# ==================================================================
# _write_ini
# ==================================================================
def write_ini():
    # open file
    f = open(f"{user_base_dir}/.allocation", "w")

    # write JSON data
    json.dump(preferences, f)

    # finish up
    f.close()


# ==================================================================
# create_start_window
# ==================================================================
def create_main_window():
    gui.create_start_window()
    toolbar_buttons, button_properties, menu = menu_info()
    gui.create_menu_and_toolbars(toolbar_buttons, button_properties, menu)
    gui.create_front_page_base(preferences, semesters, _open_schedule, get_schedule)


# ==================================================================
# menu_info
# ==================================================================
def menu_info():
    """Define what goes in the menu and _toolbar"""
    # button names
    buttons = ['open_fall', 'open_winter', 'save']  # ,'new_fall', 'new_winter']

    # actions associated w/ the menu items
    actions = {
        # no longer necessary? new schedules are made directly in the open menu now
        # 'new_fall': {
        #    'cb': partial(new_schedules, 'fall'),
        #    'hn': 'Create new Fall schedule'
        # },
        # 'new_winter': {
        #    'cb': partial(new_schedules, 'winter'),
        #    'hn': 'Create new Winter schedule'
        # },
        'open_fall': {
            'code': partial(get_schedule, 'fall'),
            'hint': 'Open Fall schedule'
        },
        'open_winter': {
            'code': partial(get_schedule, 'winter'),
            'hint': 'Open Winter schedule'
        },
        'save': {
            'code': save_schedule,
            'hint': 'Save Schedules'
        }
    }

    # menu structure
    menu = [
        {
            'itemType': 'cascade',
            'label': 'File',
            'tearoff': 0,
            'menuitems': [
                # no longer necessary? new schedules are made directly in the open menu now
                # (using pound, so it isn't read as a string in the list)
                # {
                #    'itemType': 'command',
                #    'label': 'New Fall',
                #    'accelerator': 'Ctrl-n',
                #    'command': actions['new_fall']['cb']
                # },
                # {
                #    'itemType': 'command',
                #    'label': 'New Winter',
                #    'accelerator': 'Ctrl-n',
                #    'command': actions['new_winter']['cb']
                # },
                {
                    'itemType': 'command',
                    'label': 'Open Fall',
                    'accelerator': 'Ctrl-o',
                    'command': actions['open_fall']['code']
                },
                {
                    'itemType': 'command',
                    'label': 'Open Winter',
                    'accelerator': 'Ctrl-o',
                    'command': actions['open_winter']['code']
                },
                {
                    'itemType': 'command',
                    'label': 'Save',
                    'underline': 0,
                    'accelerator': 'Ctrl-s',
                    'command': actions['save']['code']
                },
                {
                    'itemType': 'command',
                    'label': 'Save As',
                    'command': save_as_schedule
                },
                {
                    'itemType': 'command',
                    'label': 'Exit',
                    'underline': 0,
                    'accelerator': 'Ctrl-e',
                    'command': exit_schedule
                },
            ]
        }
    ]

    return buttons, actions, menu


# ==================================================================
# new_schedules; does this need to be implemented? probably not
# ==================================================================
def new_schedules(semester):
    # schedules[semester] = Schedule(None, "", "Pending", scenario.id)
    dirty = True
    # front_page_done()


# ==================================================================
# _open_schedule
# ==================================================================
def get_schedule(semester: str):
    from GuiSchedule.ScenarioSelector import ScenarioSelector
    from GuiSchedule.ScheduleSelector import ScheduleSelector
    # Based on Scheduler.open_schedule

    db = create_db()

    global scenarios, schedules

    for sem in semesters:
        if sem not in scenarios:
            scenarios[sem] = None

    def _get_scenario(func):
        global scenarios
        scenarios[semester] = func()

    if REQUIRES_LOGIN:
        pass  # TODO: Implement this
    else:
        # Open a ScenarioSelector window
        ScenarioSelector(parent=gui._mw, db=db, callback=_get_scenario)

        if scenarios[semester]:
            def _get_schedule(func):
                global schedules
                schedules.schedules[semester] = func()

            ScheduleSelector(parent=gui._mw, db=db, scenario=scenarios[semester], callback=_get_schedule)

            if schedules.schedules[semester]:
                return schedules.schedules[semester]


# ==================================================================
# _open_schedule
# ==================================================================
def _open_schedule():
    for semester in semesters:
        if semester not in schedules.schedules or not schedules.schedules[semester]: return
    front_page_done()


def front_page_done():
    gui.update_for_new_schedule_and_show_page()
    gl.unset_dirty_flag()


def pre_process_stuff():
    gui.bind_dirty_flag()
    define_notebook_pages()
    gui.define_notebook_tabs(required_pages)
    gui.define_exit_callback(exit_schedule)


def define_notebook_pages():
    from tkinter import LabelFrame  # BAD, tkinter in presentation
    global required_pages
    required_pages = [
        NoteBookPageInfo("Allocation",
                         event_handler=draw_allocation().__next__,
                         frame_type=LabelFrame),
        NoteBookPageInfo("Student Numbers", draw_student_numbers)
    ]

    # one page for each semester
    sub_notebook = {}
    for semester in semesters:
        label = semester.capitalize()
        sub_notebook[semester] = []

        def tab_pressed(sem, *_):
            update_edit_courses(sem)
            update_edit_teachers(sem)

        required_pages.append(NoteBookPageInfo(label, partial(tab_pressed, semester), sub_notebook[semester]))

    # Semester Courses and Teachers
    for semester in semesters:
        label = semester.capitalize()
        sub_notebook[semester].append(
            (c := NoteBookPageInfo(f"{label} Courses", partial(update_edit_courses, semester))))
        sub_notebook[semester].append(
            (t := NoteBookPageInfo(f"{label} Teachers", partial(update_edit_teachers, semester)))
        )

        pages_lookup[f"{label} Courses"] = c
        pages_lookup[f"{label} Teachers"] = t

    for page in required_pages:
        pages_lookup[page.name] = page


def exit_schedule():
    if gl.is_data_dirty():
        answer = gui.question("Save Schedule", "Do you want to save your changes?")
        if answer.lower() == 'yes':
            save_schedule()
        elif answer.lower() == 'cancel':
            return

    write_ini()
    # Perl ver called Tk::exit() here, but it's already being called in MainPageBaseTk


def save_schedule():
    _save_schedule(0)


def save_as_schedule():
    _save_schedule(1)


def _save_schedule(save_as : int):
    for semester in semesters:
        if semester not in schedules.schedules:
            gui.show_error('Save Schedule', f'Missing allocation file for {semester}')
            return

    # a bunch of saving stuff here
    # uses the YAML file saving, so outdated; needs to be updated eventually
    # will need to use autosave anyway


# ==================================================================
# draw_allocation
# ==================================================================
# TODO: Finish implementing below functions
# Use generators to yield the same object; if de doesn't exist then create it, otherwise yield de

def draw_allocation(*_):
    f = gui.get_notebook_page(pages_lookup["Allocation"].number)
    de: EditAllocation = None
    while True:
        if de is None:
            de = EditAllocation(f, schedules.schedules)
        else:
            de.draw(schedules.schedules)
        yield de


def draw_student_numbers(*_):
    pass


def update_edit_courses(*_):
    pass


def update_edit_teachers(*_):
    pass
