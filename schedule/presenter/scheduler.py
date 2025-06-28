# IN PROGRESS
from __future__ import annotations

from typing import Optional, TYPE_CHECKING
# TODO: finish 'exit'

# from .ViewsManager import ViewsManager
# from ..Utilities.Preferences import Preferences
# from ..Presentation.dirty_flags import *
# from ..Model import ResourceType
# from ..Presentation.EditResources import EditResources
# from ..Presentation.Overview import Overview
#
from .menus import set_menu_event_handler, main_menu
from schedule.Utilities import Preferences
from schedule.gui_pages import SchedulerTk, set_main_page_event_handler
from schedule.Utilities.NoteBookPageInfo import NoteBookPageInfo
from schedule.model import Schedule
from schedule.exceptions import CouldNotReadFileError

if TYPE_CHECKING:
    from tkinter import Event

    pass
    # from .menus import ToolbarItem, MenuItem

    # from .time_slot import TimeSlot, ClockTime
    # from .lab import Lab
    # from .teacher import Teacher
    # from .section import Section

# =====================================================================================
# CLASS
# =====================================================================================

DIRECTORY = str


class Scheduler:
    """
    # ==================================================================
    # This is the main entry point for the Scheduler Program
    # ==================================================================
    """

    def __init__(self, bin_dir: DIRECTORY, gui: Optional[SchedulerTk] = None):
        # self.bin_dir: Optional[DIRECTORY] = None
        # self.user_base_dir: Optional[DIRECTORY] = None
        # self._teachers_de: Optional[EditResources] = None
        # self._streams_de: Optional[EditResources] = None
        # self._labs_de: Optional[EditResources] = None
        # self._overview: Optional[Overview] = None

        self.preferences: Preferences = Preferences()
        self.schedule: Optional[Schedule] = None
        self._dirty_flag = False

        # gui is optional so that we can test the presenter more readily
        if gui:
            self.gui = gui
        else:
            self.gui: SchedulerTk = SchedulerTk('Scheduler', self.preferences, bin_dir)

        self._schedule_filename = ""
        self._previous_filename = self.preferences.previous_file()

        #        self.views_manager: Optional[viewsManager] = None

        # --------------------------------------------------------------------
        # required notebook pages
        # --------------------------------------------------------------------
        self._required_pages: list[NoteBookPageInfo] = [
            NoteBookPageInfo("Schedules", self.update_choices_of_resource_views),
            NoteBookPageInfo("Overview", self.update_overview),
            NoteBookPageInfo("Courses", self.update_edit_courses),
            NoteBookPageInfo("Teachers", self.update_edit_teachers),
            NoteBookPageInfo("Labs", self.update_edit_labs),
            NoteBookPageInfo("Streams", self.update_edit_streams)
        ]

        # --------------------------------------------------------------------
        # create the Gui Main Window
        # --------------------------------------------------------------------
        set_menu_event_handler("file_new", self.new_menu_event)
        set_menu_event_handler("file_open", self.open_menu_event)
        set_menu_event_handler("file_save", self.save_menu_event)
        set_menu_event_handler("file_save_as", self.save_as_menu_event)
        set_menu_event_handler("file_exit", self.exit_event)
        set_main_page_event_handler("file_exit", self.exit_event)
        set_main_page_event_handler("file_open", self.open_menu_event)
        set_main_page_event_handler("file_new", self.new_menu_event)
        set_main_page_event_handler("file_open_previous", self.open_previous_file_event)
        set_main_page_event_handler("semester_change", self.semester_change)

        # TODO
        set_menu_event_handler("print_pdf_teacher", self.menu_ignore)
        set_menu_event_handler("print_pdf_lab", self.menu_ignore)
        set_menu_event_handler("print_pdf_streams", self.menu_ignore)
        set_menu_event_handler("print_text", self.menu_ignore)
        set_menu_event_handler("print_latex_teacher", self.menu_ignore)
        set_menu_event_handler("print_latex_lab", self.menu_ignore)
        set_menu_event_handler("print_latex_streams", self.menu_ignore)

        (self._toolbar_buttons, self._button_properties, self._menu) = main_menu()

        self.gui.create_menu_and_toolbars(self._toolbar_buttons, self._button_properties, self._menu)
        self.gui.create_front_page(self.preferences.semester())
        self.gui.create_status_bar()
        # pre_process_stuff()

        self.gui.start_event_loop()

    # ============================================================================================
    #  Properties - filenames
    # ============================================================================================
    @property
    def schedule_filename(self):
        return self._schedule_filename

    @schedule_filename.setter
    def schedule_filename(self, value: Optional[str]):
        self._schedule_filename = value
        self.gui.schedule_filename = value
        if value is not None and value != "":
            self.previous_filename = value

    @property
    def previous_filename(self):
        return self._previous_filename

    @previous_filename.setter
    def previous_filename(self, value):
        self.preferences.previous_file(value)
        self._previous_filename = value
        self.gui.previous_file = value
        self.preferences.save()

    # ============================================================================================
    # Properties - is data changed (dirty)
    # ============================================================================================
    @property
    def dirty_flag(self) -> bool:
        return self._dirty_flag

    @dirty_flag.setter
    def dirty_flag(self, value):
        if self.gui:
            if value:
                self.gui.dirty_text = "UNSAVED"
            else:
                self.gui.dirty_text = ""
        self._dirty_flag = value

    # ============================================================================================
    # Event handlers - file open/close/save/new
    # ============================================================================================
    def new_menu_event(self, _: Event = None):
        self.schedule = Schedule()
        self.schedule_filename = ""
        self.gui.create_standard_page(self._required_pages)
        self.dirty_flag = True

    def open_menu_event(self, _: Event = None):
        filename = self.gui.select_file_to_open()
        self._open_file(filename)

    def open_previous_file_event(self, _: Event = None):
        filename = self.preferences.previous_file()
        self._open_file(filename)

    def _open_file(self, filename: str):
        if filename:
            try:
                schedule = Schedule(filename)
                self.schedule = schedule
                self.schedule_filename = filename
                self.dirty_flag = False
                self.gui.create_standard_page(self._required_pages)

            except CouldNotReadFileError as e:
                self.gui.show_error("Read File", str(e))

    def save_menu_event(self, _: Event = None):
        self._save_schedule(self.schedule_filename)

    def save_as_menu_event(self, _: Event = None):
        self._save_schedule(None)

    def _save_schedule(self, filename: Optional[str]):

        if self.schedule is None:
            self.gui.show_error("Save Schedule", "There is no schedule to save!")
            return

        if filename is None or filename == "":
            print("Select file to save")
            filename = self.gui.select_file_to_save()

        if filename is not None and filename != "":
            self.schedule.write_file(filename)
            self.schedule_filename = filename
            self.gui.show_message("Save File", "File saved as", detail=f"{filename}")
            self.dirty_flag = False

    # ============================================================================================
    # Event handlers - semester change
    # ============================================================================================
    def semester_change(self, *_):
        self.preferences.semester(self.gui.current_semester)
        self.previous_filename = self.preferences.previous_file()
        self.preferences.save()

    # ============================================================================================
    # Event handlers - exit
    # ============================================================================================

    def exit_event(self, _: Event = None):
        print("in exit event")
        if self.dirty_flag:
            ans = self.gui.ask_yes_no("File", "Save File?")
            if ans:
                self.save_menu_event()

    def menu_ignore(self, _: Event = None):
        print("still a To Do!!")
        pass

    # ==================================================================
    # update_choices_of_resource_views
    # (what teacher_ids/lab_ids/stream_ids) can we create schedules for?
    # ==================================================================
    def update_choices_of_resource_views(self):
        pass

    #
    #     #     global views_manager, gui
    #     #     btn_callback = views_manager.get_create_new_view_callback
    #     #     all_view_choices = views_manager.get_all_scheduables()
    #     #     page_name = pages_lookup['Schedules'].name
    #     #     gui.draw_view_choices(page_name, all_view_choices, btn_callback)
    #     #
    #     #     views_manager.determine_button_colours()
    #
    # ==================================================================
    # update_overview
    # A text representation of the schedules
    # ==================================================================
    def update_overview(self):
        pass
        # if self._overview is None:
        #     overview_frame = self.gui.get_gui_container("Overview")
        #     self._overview = Overview(overview_frame, self.schedule)
        #
        # # reset the schedule object just in case the schedule file has changed
        # self._overview.schedule = self.schedule
        # self._overview.refresh()

    # ==================================================================
    # update_edit_teachers
    # - A page where teacher_ids can be added/modified or deleted
    # ==================================================================
    def update_edit_teachers(self):
        pass
        # if self._teachers_de is None:
        #     teachers_frame = self.gui.get_gui_container("teachers")
        #     self._teachers_de = EditResources(teachers_frame, ResourceType.teacher, self.schedule)
        #
        # # reset the schedule object just in case the schedule file has changed
        # self._teachers_de.schedule = self.schedule
        # self._teachers_de.refresh()

    # ==================================================================
    # update_edit_streams
    # - A page where stream_ids can be added/modified or deleted
    # ==================================================================
    def update_edit_streams(self):
        pass
        # if self._streams_de is None:
        #     streams_frame = self.gui.get_gui_container("streams")
        #     self._streams_de = EditResources(streams_frame, ResourceType.stream, self.schedule)
        #
        # # reset the schedule object just in case the schedule file has changed
        # self._streams_de.schedule = self.schedule
        # self._streams_de.refresh()

    # ==================================================================
    # update_edit_labs
    # - A page where lab_ids can be added/modified or deleted
    # ==================================================================
    def update_edit_labs(self):
        pass
        # if self._labs_de is None:
        #     labs_frame = self.gui.get_gui_container("labs")
        #     self._labs_de = EditResources(labs_frame, ResourceType.lab, self.schedule)
        #
        # # reset the schedule object just in case the schedule file has changed
        # self._labs_de.schedule = self.schedule
        # self._labs_de.refresh()

    # ==================================================================
    # draw_edit_courses
    # - A page where courses can be added/modified or deleted
    # ==================================================================
    def update_edit_courses(self):
        pass
#
#     # ==================================================================
#     # print_views
#     # - print the schedule 'views'
#     # - resource_type defines the output resource_type, PDF, Latex
#     # ==================================================================
#     def print_views(self, print_type, view_type):
#         pass
#         # global gui
#         # # --------------------------------------------------------------
#         # # no schedule yet
#         # # --------------------------------------------------------------
#         #
#         # if not schedule:
#         #     gui.show_error("Export", "Cannot export - There is no schedule")
#         #
#         # # --------------------------------------------------------------
#         # # cannot print if the schedule is not saved
#         # # --------------------------------------------------------------
#         # if is_data_dirty():
#         #     ans = gui.question(
#         #         "Unsaved Changes",
#         #         "There are unsaved changes.\nDo you want to save them?"
#         #         )
#         #
#         #     if ans:
#         #         save_schedule()
#         #     else:
#         #         return
#         #
#         # # --------------------------------------------------------------
#         # # define base file name
#         # # --------------------------------------------------------------
#         # # NOTE: Come back to this later.
#         # pass
#         #
#         #
#
#     """
#     (c) Sandy Bultena 2025
#     Copyrighted by the standard GPL License Agreement
#
#     All Rights Reserved.
#     """
#     # # ==================================================================
#     # # pre-process procedures
#     # # ==================================================================
#     # def pre_process_stuff():
#     #     gui.bind_dirty_flag()
#     #     gui.define_notebook_tabs(required_pages)
#     #
#     #     gui.define_exit_callback(exit_schedule)
#     #
#     #     # Create the view manager (which shows all the schedule views, etc.)
#     #     global views_manager, schedule
#     #     # TODO: Implement ViewsManager class.
#     #     views_manager = ViewsManager(gui, is_data_dirty(), schedule)
#     #     gui.set_views_manager(views_manager)
#     #
