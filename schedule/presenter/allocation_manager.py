
"""Entry point for the GUI_Pages Allocation Management Tool"""
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Callable, Optional

from schedule.Utilities import Preferences
from schedule.exceptions import CouldNotReadFileError
from schedule.gui_pages.allocation_manager_tk import AllocationManagerTk, set_main_page_event_handler
from schedule.presenter.edit_courses import EditCourses
from schedule.presenter.edit_resources import EditResources
from schedule.presenter.menus_main_menu_allocation import set_menu_event_handler_allocation, main_menu_allocation
from schedule.model import Schedule, SemesterType, ResourceType
from schedule.presenter.notebook_tab_data import NBTabInfo
from schedule.presenter.student_numbers import StudentNumbers


# =====================================================================================
# Notebook book-keeping
# =====================================================================================
@dataclass
class NBTabInfo:
        name: str
        label: str
        subpages: list = field(default_factory=list)
        frame_args: dict[str, Any] =  field(default_factory=dict)
        creation_handler: Callable = lambda *_: None
        is_default_page: bool = False

DIRECTORY = str
PATH = str

class AllocationManager:
    NB_fall = "Fall"
    NB_fall_course = "Fall Courses"
    NB_fall_teacher = "Fall Teachers"
    NB_fall_students = "Fall Students"
    NB_winter = "Winter"
    NB_winter_course = "Winter Courses"
    NB_winter_teacher = "Winter Teachers"
    NB_winter_students = "Winter Students"

    def __init__(self, bin_dir: DIRECTORY, gui: Optional[AllocationManagerTk] = None):

        self.preferences: Preferences = Preferences()
        self.schedules: dict[SemesterType, Optional[Schedule]] = {SemesterType.fall:None, SemesterType.winter:None}
        self._dirty_flag = False
        self.current_tab: Optional[str] = None

        # gui is optional so that we can test the presenter more readily
        if gui:
            self.gui = gui
        else:
            self.gui: AllocationManager = AllocationManagerTk('Allocation', self.preferences, bin_dir)

        self._schedule_filenames: dict[SemesterType, PATH] = {
            SemesterType.fall: "",
            SemesterType.winter: "",
        }

        # --------------------------------------------------------------------
        # required notebook pages
        # --------------------------------------------------------------------
        fall_course_tab = NBTabInfo(label=self.NB_fall_course, name=self.NB_fall_course)
        fall_teacher_tab = NBTabInfo(label=self.NB_fall_teacher, name=self.NB_fall_teacher)
        fall_student_tab = NBTabInfo(label=self.NB_fall_students, name=self.NB_fall_students)
        winter_course_tab = NBTabInfo(label=self.NB_winter_course, name=self.NB_winter_course)
        winter_teacher_tab = NBTabInfo(label=self.NB_winter_teacher, name=self.NB_winter_teacher)
        winter_student_tab = NBTabInfo(label=self.NB_winter_students, name=self.NB_winter_students)
        self._required_tabs: list[NBTabInfo] = [
            NBTabInfo(label=self.NB_fall, name=self.NB_fall, subpages=[fall_course_tab, fall_teacher_tab, fall_student_tab]),
            NBTabInfo(label=self.NB_winter, name=self.NB_winter, subpages=[winter_course_tab, winter_teacher_tab, winter_student_tab]),
        ]

        # --------------------------------------------------------------------
        # create the Menu and Toolbars
        # --------------------------------------------------------------------
        set_menu_event_handler_allocation("file_new", self.new_menu_event)
        set_menu_event_handler_allocation("file_open", self.open_menu_event)
        set_menu_event_handler_allocation("file_save", self.save_menu_event)
        set_menu_event_handler_allocation("file_save_as", self.save_as_menu_event)
        set_menu_event_handler_allocation("file_exit", self.menu_exit_event)
        set_main_page_event_handler("go", self.go)
        set_main_page_event_handler("exit", self.exit_event)
        set_main_page_event_handler("fall_file_open", partial(self.open_menu_event, SemesterType.fall))
        set_main_page_event_handler("fall_file_open_previous", partial(self.open_previous_file_event,SemesterType.fall))
        set_main_page_event_handler("winter_file_open", partial(self.open_menu_event,SemesterType.winter))
        set_main_page_event_handler("winter_file_open_previous", partial(self.open_previous_file_event,SemesterType.winter))

        (self._toolbar_buttons, self._button_properties, self._menu) = main_menu_allocation()

        # --------------------------------------------------------------------
        # create the Gui Main Window
        # --------------------------------------------------------------------
        self.gui.create_menu_and_toolbars(self._toolbar_buttons, self._button_properties, self._menu)
        self.gui.create_welcome_page()
        self.gui.create_status_bar()
        self.gui.notebook_tab_changed_handler = self.notebook_tab_has_changed



        self._previous_filenames: dict[SemesterType, PATH] = {}
        self.preferences.semester("fall")
        self.previous_filename_fall = self.preferences.previous_file()
        self.preferences.semester("winter")
        self.previous_filename_winter = self.preferences.previous_file()

        self.gui.start_event_loop()


    # ============================================================================================
    #  Properties - filenames
    # ============================================================================================
    @property
    def schedule_filename_fall(self):
        """The filename associated with this file"""
        return self._schedule_filenames[SemesterType.fall]

    @schedule_filename_fall.setter
    def schedule_filename_fall(self, value: Optional[str]):
        self._schedule_filenames[SemesterType.fall] = value
        self.gui.schedule_filename_fall = value
        if value is not None and value != "":
            self.previous_filename_fall = value

    @property
    def previous_filename_fall(self):
        """what was the last opened file"""
        return self._previous_filenames[SemesterType.fall]

    @previous_filename_fall.setter
    def previous_filename_fall(self, value):
        self.preferences.semester(SemesterType.fall.name)
        self.preferences.previous_file(value)
        self._previous_filenames[SemesterType.fall] = value
        self.gui.previous_file_fall = value
        self.preferences.save()

    @property
    def schedule_filename_winter(self):
        """The filename associated with this file"""
        return self._schedule_filenames[SemesterType.winter]

    @schedule_filename_winter.setter
    def schedule_filename_winter(self, value: Optional[str]):
        self._schedule_filenames[SemesterType.winter] = value
        self.gui.schedule_filename_winter = value
        if value is not None and value != "":
            self.previous_filename_winter = value

    @property
    def previous_filename_winter(self):
        """what was the last opened file"""
        return self._previous_filenames[SemesterType.winter]

    @previous_filename_winter.setter
    def previous_filename_winter(self, value):
        self.preferences.semester(SemesterType.winter.name)
        self.preferences.previous_file(value)
        self._previous_filenames[SemesterType.winter] = value
        self.gui.previous_file_winter = value
        self.preferences.save()

    # ============================================================================================
    # Properties - is data changed (dirty)
    # ============================================================================================
    @property
    def dirty_flag(self) -> bool:
        """is the data different than what was saved on disk?"""
        return self._dirty_flag

    @dirty_flag.setter
    def dirty_flag(self, value):
        if self.gui:
            if value:
                self.gui.dirty_text = "UNSAVED"
            else:
                self.gui.dirty_text = ""
        self._dirty_flag = value

    def open_menu_event(self, semester):
        """open a file"""
        self.preferences.semester(semester.name)
        filename = self.gui.select_file_to_open()
        self._open_file(filename, semester)

    def open_previous_file_event(self, semester):
        """open previously opened file"""
        self.preferences.semester(semester.name)
        filename = self.preferences.previous_file()
        self._open_file(filename, semester)

    def _open_file(self, filename: str, semester):
        """generic open file method"""
        if filename:
            try:
                schedule = Schedule(filename)
                self.schedules[semester] = schedule
                match semester:
                    case SemesterType.fall:
                        self.schedule_filename_fall = filename
                    case SemesterType.winter:
                        self.schedule_filename_winter = filename
                self.dirty_flag = False
                print("opened filename", filename)

            except CouldNotReadFileError as e:
                self.gui.show_error("Read File", str(e))

    # ============================================================================================
    # Event handlers - file open/close/save/new
    # ============================================================================================
    def new_menu_event(self, semester: SemesterType):
        """create a new file"""
        schedule = Schedule()
        self.schedules[semester] = schedule
        match semester:
            case SemesterType.fall:
                self.schedule_filename_fall = ""
            case SemesterType.winter:
                self.schedule_filename_winter = ""
        self.dirty_flag = True

    def save_menu_event(self, semester:SemesterType):
        """save file"""
        self._save_schedule(self._schedule_filenames[semester], semester)

    def save_as_menu_event(self, semester:SemesterType):
        """save as file"""
        self._save_schedule(None, semester)

    def _save_schedule(self, filename: Optional[str], semester: SemesterType):
        """generic save file method"""

        if self.schedules[semester] is None:
            self.gui.show_error("Save Schedule", "There is no schedule to save!")
            return

        if filename is None or filename == "":
            filename = self.gui.select_file_to_save()

        if filename is not None and filename != "":
            self.schedules[semester].write_file(filename)
            self.dirty_flag = False
            match semester:
                case SemesterType.fall:
                    self.schedule_filename_fall = filename
                case SemesterType.winter:
                    self.schedule_filename_winter = filename

    def exit_event(self):
        """program is exiting"""
        if self.dirty_flag:
            ans = self.gui.ask_yes_no("File", "Save File?")
            if ans:
                self.save_menu_event(SemesterType.fall)

    def menu_exit_event(self, _:SemesterType):
        self.gui.exit_schedule()

    def go(self):

        for semester in SemesterType.fall, SemesterType.winter:
            if self._schedule_filenames[semester] == "":
                print("creating new schedule for ", semester)
                self.new_menu_event(semester)

        self.gui.create_standard_page(self._required_tabs)

        pass

    # ==================================================================
    # notebook tab has changed
    # ==================================================================
    def notebook_tab_has_changed(self, name: str, frame):
        """
        the standard page notebook tab has been change
        :param name: name of the tab
        :param frame: container where the gui is stored
        """
        self.current_tab = name
        if name == self.NB_fall:
            pass
            #self.fall_selected(frame)
        elif name == self.NB_winter:
            pass
            #self.winter_selected(frame)
        elif name == self.NB_fall_course:
            self.update_edit_courses(frame, SemesterType.fall)
        elif name == self.NB_fall_teacher:
            self.update_edit_teachers(frame, SemesterType.fall)
        elif name == self.NB_fall_students:
            self.update_edit_students(frame, SemesterType.fall)
        elif name == self.NB_winter_course:
            self.update_edit_courses(frame, SemesterType.winter)
        elif name == self.NB_winter_teacher:
            self.update_edit_teachers(frame, SemesterType.winter)
        elif name == self.NB_winter_students:
            self.update_edit_students(frame, SemesterType.winter)

        # elif name == self.NB_overview_teacher:
        #     self.update_teacher_text(frame)
        # elif name == self.NB_schedule:
        #     self.update_choices_of_resource_views(frame)
        # elif name == self.NB_overview:
        #     self.update_overview(frame)
        # elif name == self.NB_course:
        #     self.update_edit_courses(frame)
        # elif name == self.NB_teacher:
        #     self.update_edit_teachers(frame)
        # elif name == self.NB_lab:
        #     self.update_edit_labs(frame)
        # elif name == self.NB_stream:
        #     self.update_edit_streams(frame)

    def fall_selected(self, frame):
        self.update_edit_courses(frame, SemesterType.fall)
        self.update_edit_teachers(frame, SemesterType.fall)
        self.update_edit_students(frame, SemesterType.fall)

    def winter_selected(self, frame):
        self.update_edit_courses(frame, SemesterType.winter)
        self.update_edit_teachers(frame, SemesterType.winter)
        self.update_edit_students(frame, SemesterType.winter)

    # ==================================================================
    # draw_edit_courses
    # ==================================================================
    def update_edit_courses(self, frame, semester):
        """A page where courses can be added/modified or deleted"""
        data_entry = EditCourses(self.set_dirty_method, frame, self.schedules[semester])
        data_entry.schedule = self.schedules[semester]
        data_entry.refresh()

    # ==================================================================
    # update_edit_teachers
    # ==================================================================
    def update_edit_teachers(self, frame, semester):
        """A page where teacher can be added/modified or deleted"""
        data_entry = EditResources(self.set_dirty_method, frame, ResourceType.teacher,
                                   self.schedules[semester])
        data_entry.schedule = self.schedules[semester]
        data_entry.refresh()

    # ==================================================================
    # update_edit_students
    # ==================================================================
    def update_edit_students(self, frame, semester):
        print("hi", semester, frame)
        data_entry = StudentNumbers(frame, self.schedules[semester])
        data_entry.refresh()

    # ==================================================================
    # schedule has been modified, update gui as required
    # ==================================================================
    def set_dirty_method(self, value: Optional[bool] = None) -> bool:

        if value is not None:
            self.dirty_flag = value
        return self.dirty_flag


# TODO: Currently crashes when opening the same schedule twice, including when selecting a schedule
# then re-opening the same semester selector and selecting that schedule again,
# due to Schedule.Course.Course.add_sections not adding the same section twice
# based on ID rather than object instance.

#from schedule.model import Schedule

#
# semesters = ['fall', 'winter']
# schedules = ScheduleWrapper()
#
# dirty = False
# gui: AllocationManagerTk
#
# required_pages: list = []
# pages_lookup: dict[str, NoteBookPageInfo] = {}
#
# preferences = dict()
#
# user_base_dir: str = None
#
# scenarios: dict[str, Scenario] = {}
#
#
# def main():
#     global gui
#     gui = AllocationManagerTk()
#     get_user_preferences()
#     create_main_window()
#     pre_process_stuff()
#     gui.start_event_loop()
#
#
# # ==================================================================
# # user _preferences saved in ini file (JSON format)
# # ==================================================================
# def get_user_preferences():
#     global user_base_dir
#     import platform
#     import os
#     O = platform.system().lower()
#
#     if 'darwin' in O:
#         user_base_dir = os.environ["HOME"] # Mac OS linux
#     elif 'windows' in O:
#         user_base_dir = os.environ["USERPROFILE"]
#     else:
#         user_base_dir = os.environ["HOME"]
#
#     read_ini()
#
#
# # ==================================================================
# # _read_ini
# # ==================================================================
# def read_ini():
#     from os import path
#
#     global preferences, current_directory
#     if user_base_dir and path.isfile(f"{user_base_dir}/.allocation"):
#         # Perl ver used YAML, but that requires an extra package we're no longer using
#         # going to use JSON instead, which is built-in
#
#         f = open(f"{user_base_dir}/.allocation", 'r')
#         try:
#             preferences = json.loads(f.read())
#         # JSON failed, probably invalid. just ignore it
#         except json.JSONDecodeError:
#             pass
#         finally:
#             f.close()
#         current_directory = preferences['current_dir']\
#             if ('current_dir' in preferences and preferences['current_dir']) else user_base_dir
#
#
# # ==================================================================
# # _write_ini
# # ==================================================================
# def write_ini():
#     # open file
#     f = open(f"{user_base_dir}/.allocation", "w")
#
#     # write JSON data
#     json.dump(preferences, f)
#
#     # finish up
#     f.close()
#
#
# # ==================================================================
# # create_start_window
# # ==================================================================
# def create_main_window():
#     gui.create_start_window()
#     toolbar_buttons, button_properties, menu = menu_info()
#     gui.create_menu_and_toolbars(toolbar_buttons, button_properties, menu)
#     gui.create_welcome_page_base(preferences, semesters, _open_schedule, get_schedule)
#
#
# # ==================================================================
# # menu_info
# # ==================================================================
# def menu_info():
#     """Define what goes in the menu and _toolbar"""
#     # button names
#     buttons = ['open_fall', 'open_winter', 'save']  # ,'new_fall', 'new_winter']
#
#     # actions associated w/ the menu items
#     actions = {
#         # no longer necessary? new schedules are made directly in the open menu now
#         # 'new_fall': {
#         #    'cb': partial(new_schedules, 'fall'),
#         #    'hn': 'Create new Fall schedule'
#         # },
#         # 'new_winter': {
#         #    'cb': partial(new_schedules, 'winter'),
#         #    'hn': 'Create new Winter schedule'
#         # },
#         'open_fall': {
#             'code': partial(get_schedule, 'fall'),
#             'hint': 'Open Fall schedule'
#         },
#         'open_winter': {
#             'code': partial(get_schedule, 'winter'),
#             'hint': 'Open Winter schedule'
#         },
#         'save': {
#             'code': save_schedule,
#             'hint': 'Save Schedules'
#         }
#     }
#
#     # menu structure
#     menu = [
#         {
#             'itemType': 'cascade',
#             'label': 'File',
#             'tear_off': 0,
#             'menuitems': [
#                 # no longer necessary? new schedules are made directly in the open menu now
#                 # (using pound, so it isn't read as a string in the list)
#                 # {
#                 #    'itemType': 'command',
#                 #    'label': 'New Fall',
#                 #    'accelerator': 'Ctrl-n',
#                 #    'command': actions['new_fall']['cb']
#                 # },
#                 # {
#                 #    'itemType': 'command',
#                 #    'label': 'New Winter',
#                 #    'accelerator': 'Ctrl-n',
#                 #    'command': actions['new_winter']['cb']
#                 # },
#                 {
#                     'itemType': 'command',
#                     'label': 'Open Fall',
#                     'accelerator': 'Ctrl-o',
#                     'command': actions['open_fall']['code']
#                 },
#                 {
#                     'itemType': 'command',
#                     'label': 'Open Winter',
#                     'accelerator': 'Ctrl-o',
#                     'command': actions['open_winter']['code']
#                 },
#                 {
#                     'itemType': 'command',
#                     'label': 'Save',
#                     'underline': 0,
#                     'accelerator': 'Ctrl-s',
#                     'command': actions['save']['code']
#                 },
#                 {
#                     'itemType': 'command',
#                     'label': 'Save As',
#                     'command': save_as_schedule
#                 },
#                 {
#                     'itemType': 'command',
#                     'label': 'Exit',
#                     'underline': 0,
#                     'accelerator': 'Ctrl-e',
#                     'command': exit_schedule
#                 },
#             ]
#         }
#     ]
#
#     return buttons, actions, menu
#
#
# # ==================================================================
# # new_schedules; does this need to be implemented? probably not
# # ==================================================================
# def new_schedules(semester):
#     # schedules[semester] = Schedule(None, "", "Pending", scenario.id)
#     dirty = True
#     # front_page_done()
#
#
# # ==================================================================
# # _open_schedule
# # ==================================================================
# def get_schedule(semester: str):
#     from GuiSchedule.ScenarioSelector import ScenarioSelector
#     from GuiSchedule.ScheduleSelector import ScheduleSelector
#     # Based on Scheduler.open_schedule
#
#     db = create_db()
#
#     global scenarios, schedules
#
#     for sem in semesters:
#         if sem not in scenarios:
#             scenarios[sem] = None
#
#     def _get_scenario(func):
#         global scenarios
#         scenarios[semester] = func()
#
#     if REQUIRES_LOGIN:
#         pass  # TODO: Implement this
#     else:
#         # Open a ScenarioSelector window
#         ScenarioSelector(parent=gui.mw, db=db, callback=_get_scenario)
#
#         if scenarios[semester]:
#             def _get_schedule(func):
#                 global schedules
#                 schedules.schedules[semester] = func()
#
#             ScheduleSelector(parent=gui.mw, db=db, scenario=scenarios[semester], callback=_get_schedule)
#
#             if schedules.schedules[semester]:
#                 return schedules.schedules[semester]
#
#
# # ==================================================================
# # _open_schedule
# # ==================================================================
# def _open_schedule():
#     for semester in semesters:
#         if semester not in schedules.schedules or not schedules.schedules[semester]: return
#     front_page_done()
#
#
# def front_page_done():
#     gui.update_for_new_schedule_and_show_page()
#     gl.unset_dirty_flag()
#
#
# def pre_process_stuff():
#     gui.bind_dirty_flag()
#     define_notebook_pages()
#     gui.define_notebook_tabs(required_pages)
#     gui.define_exit_callback(exit_schedule)
#
#
# def define_notebook_pages():
#     from tkinter import LabelFrame  # BAD, tkinter in presentation
#     global required_pages
#     required_pages = [
#         NoteBookPageInfo("Allocation",
#                          event_handler=draw_allocation().__next__,
#                          frame_type=LabelFrame),
#         NoteBookPageInfo("Student Numbers", draw_student_numbers)
#     ]
#
#     # one page for each semester
#     sub_notebook = {}
#     for semester in semesters:
#         label = semester.capitalize()
#         sub_notebook[semester] = []
#
#         def tab_pressed(sem, *_):
#             update_edit_courses(sem)
#             update_edit_teachers(sem)
#
#         required_pages.append(NoteBookPageInfo(label, partial(tab_pressed, semester), sub_notebook[semester]))
#
#     # Semester Courses and Teachers
#     for semester in semesters:
#         label = semester.capitalize()
#         sub_notebook[semester].append(
#             (c := NoteBookPageInfo(f"{label} Courses", partial(update_edit_courses, semester))))
#         sub_notebook[semester].append(
#             (t := NoteBookPageInfo(f"{label} Teachers", partial(update_edit_teachers, semester)))
#         )
#
#         pages_lookup[f"{label} Courses"] = c
#         pages_lookup[f"{label} Teachers"] = t
#
#     for page in required_pages:
#         pages_lookup[page.name] = page
#
#
# def exit_schedule():
#     if gl.is_data_dirty():
#         answer = gui.question("Save Schedule", "Do you want to save your changes?")
#         if answer.lower() == 'yes':
#             save_schedule()
#         elif answer.lower() == 'cancel':
#             return
#
#     write_ini()
#     # Perl ver called Tk::exit() here, but it's already being called in MainPageBaseTk
#
#
# def save_schedule():
#     _save_schedule(0)
#
#
# def save_as_schedule():
#     _save_schedule(1)
#
#
# def _save_schedule(save_as : int):
#     for semester in semesters:
#         if semester not in schedules.schedules:
#             gui.show_error('Save Schedule', f'Missing allocation file for {semester}')
#             return
#
#     # a bunch of saving stuff here
#     # uses the YAML file saving, so outdated; needs to be updated eventually
#     # will need to use autosave anyway
#
#
# # ==================================================================
# # draw_allocation
# # ==================================================================
# # TODO: Finish implementing below functions
# # Use generators to yield the same object; if de doesn't exist then create it, otherwise yield de
#
# def draw_allocation(*_):
#     f = gui.get_notebook_page(pages_lookup["Allocation"].number)
#     de: EditAllocation = None
#     while True:
#         if de is None:
#             de = EditAllocation(f, schedules.schedules)
#         else:
#             de.draw(schedules.schedules)
#         yield de
#
#
# def draw_student_numbers(*_):
#     pass
#
#
# def update_edit_courses(*_):
#     pass
#
#
# def update_edit_teachers(*_):
#     pass
