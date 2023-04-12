"""Entry point for the GUI Allocation Management Tool"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(__file__)))

import json
from Schedule.ScheduleWrapper import ScheduleWrapper
from Schedule.Schedule import Schedule
#import EditCourses
from Presentation import NumStudents
#import EditAllocation
#from GUI import AllocationManagerTk
from PerlLib import Colours
#from Presentation import DataEntry
#from UsefulClasses import NoteBookPageInfo

from Schedule.Scenario import Scenario

semesters = ['fall', 'winter']
#schedules = ScheduleWrapper()

dirty = False
# $gui

# @Required_pages
# %Pages_lookup

preferences = dict()

user_base_dir : str = None

scenario : list[Scenario]

def main(scens : list[Scenario]):
    global scenario
    scenario = scens
    # gui = AllocationManagerTk.new()
    get_user_preferences()
    create_main_window()
    #pre_process_stuff()
    #Gui.start_event_loop()

# ==================================================================
# user preferences saved in ini file (JSON format)
# ==================================================================
def get_user_preferences():
    global user_base_dir
    import platform
    import os
    O = platform.system().lower()

    if 'darwin' in O: user_base_dir = os.environ("HOME") # Mac OS linux
    elif 'windows' in O: user_base_dir = os.environ("USERPROFILE")
    else: user_base_dir = os.environ("HOME")

    read_ini()

# ==================================================================
# read_ini
# ==================================================================
def read_ini():
    global preferences, current_directory
    if user_base_dir and path.isfile(f"{user_base_dir}/.allocation"):
        # Perl ver used YAML, but that requires an extra package we're no longer using
        # going to use JSON instead, which is built-in

        f = open(f"{user_base_dir}/.allocation", 'r')
        preferences = json.load(f.read())
        f.close()
        current_directory = preferences['current_dir']\
            if ('current_dir' in preferences and preferences['current_dir']) else user_base_dir

# ==================================================================
# write_ini
# ==================================================================
def write_ini():
    # open file
    f = open(f"{user_base_dir}/.allocation", "w")

    # write JSON data
    data = json.dump(preferences)
    f.write(data)

    # finish up
    f.close()


# ==================================================================
# create_main_window
# ==================================================================
def create_main_window():
    #Gui.create_main_window()
    pass


# ==================================================================
# menu_info
# ==================================================================
def menu_info():
    """Define what goes in the menu and toolbar"""
    # button names
    buttons = ['new_fall', 'new_winter', 'open_fall', 'open_winter', 'save']

    # actions associated w/ the menu items
    actions = {
        'new_fall': {
            'cb': [new_schedules, 'fall'],
            'hn': 'Create new Fall schedule'
        },
        'new_winter': {
            'cb': [new_schedules, 'winter'],
            'hn': 'Create new Winter schedule'
        },
        'open_fall': {
            'cb': [_open_schedule, 'fall'],
            'hn': 'Open Fall schedule'
        },
        'open_winter': {
            'cb': [_open_schedule, 'winter'],
            'hn': 'Open Winter schedule'
        },
        'save': {
            'cb': None,#save_schedule,
            'hn': 'Save Schedules'
        }
    }

# ==================================================================
# new_schedules
# ==================================================================
def new_schedules(semester):
    #schedules[semester] = Schedule(None, "", "Pending", scenario.id)
    dirty = True
    #front_page_done()

# ==================================================================
# _open_schedule
# ==================================================================
def _open_schedule():
    pass