# IN PROGRESS
from __future__ import annotations

from enum import Enum
from typing import Optional, TYPE_CHECKING

from schedule.presenter.edit_resources import EditResources
from schedule.presenter.edit_courses import EditCourses

# from .ViewsHubControl import ViewsHubControl

from .menus_main_menu import set_menu_event_handler, main_menu
from schedule.Utilities import Preferences
from schedule.gui_pages import SchedulerTk, set_main_page_event_handler
from schedule.Utilities.notebook_page_info import NoteBookPageInfo
from schedule.model import Schedule, ResourceType
from schedule.exceptions import CouldNotReadFileError
from schedule.gui_generics.read_only_text_tk import ReadOnlyText
from schedule.gui_pages.view_choices_tk import ViewChoicesTk

if TYPE_CHECKING:
    from tkinter import Event

class NoteBookPageNames(Enum):
    overview_course = "by Course"
    overview_teacher = "by Teacher"
    schedule = "Schedules"
    overview = "Overview"
    course = "Courses"
    teacher = "Teachers"
    lab = "Labs"
    stream = "Streams"

# =====================================================================================
# CLASS
# =====================================================================================

DIRECTORY = str


class Scheduler:
    """
    This is the main entry point for the Scheduler Program
    """

    def __init__(self, bin_dir: DIRECTORY, gui: Optional[SchedulerTk] = None):
        # self.bin_dir: Optional[DIRECTORY] = None
        # self.user_base_dir: Optional[DIRECTORY] = None

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
        by_course_page = NoteBookPageInfo(NoteBookPageNames.overview_course.value, self.update_course_text)
        by_teacher_page = NoteBookPageInfo(NoteBookPageNames.overview_teacher.value, self.update_teacher_text)
        self._required_pages: list[NoteBookPageInfo] = [
            NoteBookPageInfo(NoteBookPageNames.schedule.value, self.update_choices_of_resource_views),
            NoteBookPageInfo(NoteBookPageNames.overview.value, self.update_overview, subpages=[by_course_page, by_teacher_page]),
            NoteBookPageInfo(NoteBookPageNames.course.value, self.update_edit_courses),
            NoteBookPageInfo(NoteBookPageNames.teacher.value, self.update_edit_teachers),
            NoteBookPageInfo(NoteBookPageNames.lab.value, self.update_edit_labs),
            NoteBookPageInfo(NoteBookPageNames.stream.value, self.update_edit_streams)
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
    def new_menu_event(self):
        self.schedule = Schedule()
        self.schedule_filename = ""
        self.gui.create_standard_page(self._required_pages)
        self.dirty_flag = True

    def open_menu_event(self):
        filename = self.gui.select_file_to_open()
        self._open_file(filename)

    def open_previous_file_event(self):
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

    def save_menu_event(self):
        self._save_schedule(self.schedule_filename)

    def save_as_menu_event(self):
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

    def exit_event(self):
        if self.dirty_flag:
            ans = self.gui.ask_yes_no("File", "Save File?")
            if ans:
                self.save_menu_event()

    def menu_ignore(self):
        print("still a To Do!!")
        pass

    # ==================================================================
    # update_choices_of_resource_views
    # (what teacher_ids/lab_ids/stream_ids) can we create schedules for?
    # ==================================================================
    def update_choices_of_resource_views(self):
        notebook_name = NoteBookPageNames.schedule.value.lower()
        views_frame = self.gui.get_notebook_frame(notebook_name)
        resources = {
            ResourceType.teacher: list(self.schedule.teachers()),
            ResourceType.lab: list(self.schedule.labs()),
            ResourceType.stream: list(self.schedule.streams()),
        }

        # create a global view hub manager
        # on moving away from this page, must remove all the views (check previous version to see what it did)
        # it would be too hard to manage the views, if the contents of the schedule were changing
        view_choice = ViewChoicesTk(views_frame,resources, lambda *args: print(*args))
        # data_entry = EditResources(self.set_dirty_method, teachers_frame, ResourceType.teacher, self.schedule)
        # data_entry.schedule = self.schedule
        # data_entry.refresh()


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
        self.update_course_text()
        self.update_teacher_text()

    def update_course_text(self):
        text: list[str] = list()
        if self.schedule is None:
            text.append('There is no schedule, please open one')
        else:
            if not self.schedule.courses:
                text.append('No courses defined in this schedule')
            else:
                for c in self.schedule.courses():
                    text.append(str(c))
        notebook_name = NoteBookPageNames.overview_course.value.lower()
        frame = self.gui.get_notebook_frame(notebook_name)
        data_entry = ReadOnlyText(frame, text)
        data_entry.write(text)

    def update_teacher_text(self):
        text = []
        if not self.schedule.teachers:
            text.append('No teachers defined in this schedule')
        else:
            for t in self.schedule.teachers():
                text.append(self.schedule.teacher_details(t))
        notebook_name = NoteBookPageNames.overview_teacher.value.lower()
        frame = self.gui.get_notebook_frame(notebook_name)
        data_entry = ReadOnlyText(frame, text)
        data_entry.write(text)

    # ==================================================================
    # update_edit_teachers
    # - A page where teacher_ids can be added/modified or deleted
    # ==================================================================
    def update_edit_teachers(self):
        notebook_name = NoteBookPageNames.teacher.value.lower()
        teachers_frame = self.gui.get_notebook_frame(notebook_name)
        data_entry = EditResources(self.set_dirty_method, teachers_frame, ResourceType.teacher, self.schedule)
        data_entry.schedule = self.schedule
        data_entry.refresh()

    # ==================================================================
    # update_edit_streams
    # - A page where stream_ids can be added/modified or deleted
    # ==================================================================
    def update_edit_streams(self):
        notebook_name = NoteBookPageNames.stream.value.lower()
        streams_frame = self.gui.get_notebook_frame(notebook_name)
        data_entry = EditResources(self.set_dirty_method, streams_frame, ResourceType.stream, self.schedule)
        data_entry.schedule = self.schedule
        data_entry.refresh()

    # ==================================================================
    # update_edit_labs
    # - A page where lab_ids can be added/modified or deleted
    # ==================================================================
    def update_edit_labs(self):
        notebook_name = NoteBookPageNames.lab.value.lower()
        labs_frame = self.gui.get_notebook_frame(notebook_name)
        data_entry = EditResources(self.set_dirty_method, labs_frame, ResourceType.lab, self.schedule)
        data_entry.schedule = self.schedule
        data_entry.refresh()

    # ==================================================================
    # draw_edit_courses
    # - A page where courses can be added/modified or deleted
    # ==================================================================
    def update_edit_courses(self):
        print( "Update edit courses")
        notebook_name = NoteBookPageNames.course.value.lower()
        edit_course_frame = self.gui.get_notebook_frame(notebook_name)
        data_entry = EditCourses(self.set_dirty_method, edit_course_frame, self.schedule)
        data_entry.schedule = self.schedule
        data_entry.refresh()



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
    # ==================================================================
    # update_edit_teachers
    # - A page where teacher_ids can be added/modified or deleted
    # ==================================================================
    def set_dirty_method(self, value: Optional[bool] = None) -> bool:
        if value is not None:
            self.dirty_flag = value
        return self.dirty_flag

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
#     #     # TODO: Implement ViewsHubControl class.
#     #     views_manager = ViewsHubControl(gui, is_data_dirty(), schedule)
#     #     gui.set_views_manager(views_manager)
#     #
