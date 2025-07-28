
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from functools import partial
from typing import Optional, TYPE_CHECKING, Any, Callable


from schedule.presenter.edit_resources import EditResources
from schedule.presenter.edit_courses import EditCourses

# from .ViewsHubControl import ViewsHubControl

from .menus_main_menu import set_menu_event_handler, main_menu
from schedule.Utilities import Preferences
from schedule.gui_pages import SchedulerTk, set_main_page_event_handler
from schedule.model import Schedule, ResourceType
from schedule.exceptions import CouldNotReadFileError
from schedule.gui_generics.read_only_text_tk import ReadOnlyText
from schedule.presenter.view import View
from schedule.presenter.views_controller import ViewsController
from schedule.export.view_export_canvases import PDFCanvas, LatexCanvas
from schedule.gui_pages.view_canvas_tk import ViewCanvasTk

class CanvasType(Enum):
    latex = 1
    pdf = 2

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


# =====================================================================================
# Scheduler
# =====================================================================================

DIRECTORY = str


class Scheduler:
    """
    This is the main entry point for the Scheduler Program
    """

    NB_overview_course = "by Course"
    NB_overview_teacher = "by Teacher"
    NB_schedule = "Schedules"
    NB_overview = "Overview"
    NB_course = "Courses"
    NB_teacher = "Teachers"
    NB_lab = "Labs"
    NB_stream = "Streams"

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

        # --------------------------------------------------------------------
        # required notebook pages
        # --------------------------------------------------------------------
        by_course_page = NBTabInfo(label=self.NB_overview_course, name=self.NB_overview_course)
        by_teacher_page = NBTabInfo(label=self.NB_overview_teacher, name=self.NB_overview_teacher)

        self._required_tabs: list[NBTabInfo] = [
            NBTabInfo(label=self.NB_schedule, name=self.NB_schedule),
            NBTabInfo(label=self.NB_overview, name=self.NB_overview, subpages=[by_course_page, by_teacher_page]),
            NBTabInfo(label=self.NB_course, name=self.NB_course),
            NBTabInfo(label=self.NB_teacher, name=self.NB_teacher),
            NBTabInfo(label=self.NB_lab, name=self.NB_lab),
            NBTabInfo(label = self.NB_stream, name = self.NB_stream)
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
        set_menu_event_handler("print_pdf_teacher", partial(self.print_views, ResourceType.teacher, CanvasType.pdf))
        set_menu_event_handler("print_pdf_lab", partial(self.print_views, ResourceType.lab, CanvasType.pdf))
        set_menu_event_handler("print_pdf_streams", partial(self.print_views, ResourceType.stream, CanvasType.pdf))
        set_menu_event_handler("print_latex_teacher", partial(self.print_views, ResourceType.teacher, CanvasType.latex))
        set_menu_event_handler("print_latex_lab", partial(self.print_views, ResourceType.lab, CanvasType.latex))
        set_menu_event_handler("print_latex_streams", partial(self.print_views, ResourceType.stream, CanvasType.latex))

        # TODO
        set_menu_event_handler("print_text", self.menu_ignore)

        (self._toolbar_buttons, self._button_properties, self._menu) = main_menu()

        self.gui.create_menu_and_toolbars(self._toolbar_buttons, self._button_properties, self._menu)
        self.gui.create_front_page(self.preferences.semester())
        self.gui.create_status_bar()
        self.gui.notebook_tab_changed_handler = self.notebook_tab_has_changed


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
        self.gui.create_standard_page(self._required_tabs)
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
                self.gui.create_standard_page(self._required_tabs)

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
    # notebook tab has changed
    # ==================================================================
    def notebook_tab_has_changed(self, name: str, frame):

        if name == self.NB_overview_course:
            self.update_course_text(frame)
        elif name == self.NB_overview_teacher:
            self.update_teacher_text(frame)
        elif name == self.NB_schedule:
            self.update_choices_of_resource_views(frame)
        elif name == self.NB_overview:
            self.update_overview(frame)
        elif name == self.NB_course:
            self.update_edit_courses(frame)
        elif name == self.NB_teacher:
            self.update_edit_teachers(frame)
        elif name == self.NB_lab:
            self.update_edit_labs(frame)
        elif name == self.NB_stream:
            self.update_edit_streams(frame)

    # ==================================================================
    # update_choices_of_resource_views
    # (what teacher_ids/lab_ids/stream_ids) can we create schedules for?
    # ==================================================================
    def update_choices_of_resource_views(self, frame):
        view_choice = ViewsController(self.set_dirty_method, frame, self.schedule)
        view_choice.refresh()

    # ==================================================================
    # update_overview
    # A text representation of the schedules
    # ==================================================================
    def update_overview(self, frame):
        pass

    def update_course_text(self, frame):
        text: list[str] = list()
        if self.schedule is None:
            text.append('There is no schedule, please open one')
        else:
            if not self.schedule.courses:
                text.append('No courses defined in this schedule')
            else:
                for c in self.schedule.courses():
                    text.append(str(c))
        data_entry = ReadOnlyText(frame, text)
        data_entry.write(text)

    def update_teacher_text(self, frame):
        text = []
        if not self.schedule.teachers:
            text.append('No teachers defined in this schedule')
        else:
            for t in self.schedule.teachers():
                text.append(self.schedule.teacher_details(t))
        data_entry = ReadOnlyText(frame, text)
        data_entry.write(text)

    # ==================================================================
    # update_edit_teachers
    # - A page where teacher_ids can be added/modified or deleted
    # ==================================================================
    def update_edit_teachers(self, frame):
        data_entry = EditResources(self.set_dirty_method, frame, ResourceType.teacher, self.schedule)
        data_entry.schedule = self.schedule
        data_entry.refresh()

    # ==================================================================
    # update_edit_streams
    # - A page where stream_ids can be added/modified or deleted
    # ==================================================================
    def update_edit_streams(self, frame):
        data_entry = EditResources(self.set_dirty_method, frame, ResourceType.stream, self.schedule)
        data_entry.schedule = self.schedule
        data_entry.refresh()

    # ==================================================================
    # update_edit_labs
    # - A page where lab_ids can be added/modified or deleted
    # ==================================================================
    def update_edit_labs(self, frame):
        data_entry = EditResources(self.set_dirty_method, frame, ResourceType.lab, self.schedule)
        data_entry.schedule = self.schedule
        data_entry.refresh()

    # ==================================================================
    # draw_edit_courses
    # - A page where courses can be added/modified or deleted
    # ==================================================================
    def update_edit_courses(self, frame):
        data_entry = EditCourses(self.set_dirty_method, frame, self.schedule)
        data_entry.schedule = self.schedule
        data_entry.refresh()



        pass

    # ==================================================================
    # print_views
    # - print the schedule 'views'
    # - resource_type defines the output resource_type, PDF, Latex
    # ==================================================================
    def print_views(self, resource_type, canvas_type):

        # no schedule yet

        if not self.schedule:
            self.gui.show_error("Export", "Cannot export - There is no schedule")

        # should not print if the schedule is not saved
        if self.dirty_flag:
            self.gui.show_message(
                title="Unsaved Changes",
                msg="There are unsaved changes",
                detail="You cannot print schedules if the schedule is not saved"
                )
            return

        # gather info
        resources = ()
        match resource_type:
            case ResourceType.teacher:
                resources = self.schedule.teachers()
            case ResourceType.lab:
                resources = self.schedule.labs()
            case ResourceType.stream:
                resources = self.schedule.streams()

        # loop over each resource and create file
        for resource in resources:
            if canvas_type == CanvasType.pdf:
                cn = PDFCanvas(title=str(resource), schedule_name=self.schedule.filename)
                vc = ViewCanvasTk(cn, 0.8)
            else:
                cn = LatexCanvas(title=str(resource), schedule_name=self.schedule.filename)
                vc = cn

            blocks = ()
            match resource_type:
                case ResourceType.teacher:
                    blocks = self.schedule.get_blocks_for_teacher(resource)
                case ResourceType.lab:
                    blocks = self.schedule.get_blocks_in_lab(resource)
                case ResourceType.stream:
                    blocks = self.schedule.get_blocks_for_stream(resource)

            for block in blocks:
                text = View.get_block_text(block, scale=1, resource_type=ResourceType.teacher)

                day, start_time, duration = View._block_to_floats(block)

                vc.draw_block(resource_type=ResourceType.teacher,
                              day=day, start_time=start_time, duration=duration,
                              text=text,
                              gui_tag="",
                              movable=True,
                              )
            cn.save()






    # ==================================================================
    # update_edit_teachers
    # - A page where teacher_ids can be added/modified or deleted
    # ==================================================================
    def set_dirty_method(self, value: Optional[bool] = None) -> bool:
        if value is not None:
            self.dirty_flag = value
        return self.dirty_flag

    """
    (c) Sandy Bultena 2025
    Copyrighted by the standard GPL License Agreement

    All Rights Reserved.
    """
