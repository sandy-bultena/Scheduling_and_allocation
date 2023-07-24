# IN PROGRESS
from __future__ import annotations

from typing import Optional, Protocol

# from .ViewsManager import ViewsManager
from ..GUI_Pages.SchedulerTk import SchedulerTk
from ..Schedule.Schedule import Schedule
from ..UsefulClasses.NoteBookPageInfo import NoteBookPageInfo
from ..UsefulClasses.Preferences import Preferences
from ..Presentation.globals import *
from ..Schedule.ScheduleEnums import ResourceType
from ..Presentation.EditResources import EditResources
from ..Presentation.Overview import Overview

from schedule.UsefulClasses.MenuItem import MenuItem, MenuType, ToolbarItem


class GuiContainer(Protocol):
    ...


# #####################################################################################
# Prototype for the 'gui' support required by the Scheduler class
# #####################################################################################
class GuiMain(Protocol):
    def create_menu_and_toolbars(self, buttons: list[str], toolbar_info: dict[str:ToolbarItem],
                                 menu_details: list[MenuItem]): ...

    def create_front_page(self, open_schedule_callback: Callable[[Scheduler, str], None],
                          new_schedule_callback: Callable[[Scheduler], None]): ...

    def create_status_bar(self): ...

    def start_event_loop(self): ...

    def select_file(self): ...

    def create_standard_page(self, notebook_pages_info: Optional[list[NoteBookPageInfo]] = None): ...

    def get_gui_container(self, page_name: str) -> Optional[GuiContainer]: ...


# #####################################################################################
# CLASS
# #####################################################################################

class Scheduler:
    """
    # ==================================================================
    # This is the main entry point for the Scheduler Program
    # ==================================================================
    """

    def __init__(self, gui: Optional[GuiMain] = None):
        self.user_base_dir: Optional[str] = None
        self.schedule: Optional[Schedule] = None
        self._teachers_de: Optional[EditResources] = None
        self._streams_de: Optional[EditResources] = None
        self._labs_de: Optional[EditResources] = None
        self._overview: Optional[Overview] = None

        self.preferences: Preferences = Preferences()
        # gui is optional for testing purposes
        if gui:
            self.gui = gui
        else:
            self.gui = SchedulerTk('Scheduler', self.preferences)

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
        (self._toolbar_buttons, self._button_properties, self._menu) = self._menu_and_toolbar_info()

        self.gui.create_menu_and_toolbars(self._toolbar_buttons, self._button_properties, self._menu)
        self.gui.create_front_page(self.open_schedule, self.new_schedule)
        self.gui.create_status_bar()
        # pre_process_stuff()
        self.gui.start_event_loop()

    # ==================================================================
    # open/new schedule
    # TODO: maybe save current schedule first?
    # ==================================================================
    def select_file(self, *_):
        self.gui.select_file()

    def open_schedule(self, filename: str, *_):
        if filename:
            self.preferences.current_file(filename)
        self.schedule = Schedule(filename)
        self.gui.schedule_filename = filename
        self.gui.create_standard_page(self._required_pages)

    def new_schedule(self, *_):
        self.schedule = Schedule()
        self.gui.schedule_filename = ""
        self.gui.create_standard_page(self._required_pages)

    # ==================================================================
    # define what goes in the menu and _toolbar
    # ==================================================================
    def _menu_and_toolbar_info(self) -> (list[str], list[ToolbarItem], list[MenuItem]):
        menu = list()

        # -----------------------------------------------------------------------------------------
        # File menu
        # -----------------------------------------------------------------------------------------
        file_menu = MenuItem(name='file', menu_type=MenuType.Cascade, label='File')
        file_menu.add_child(MenuItem(name='new', menu_type=MenuType.Command, label='New', accelerator='Ctrl-n',
                                     command=self.new_schedule))
        file_menu.add_child(MenuItem(name='open', menu_type=MenuType.Command, label='Open', accelerator='Ctrl-o',
                                     command=self.select_file))

        file_menu.add_child(MenuItem(menu_type=MenuType.Separator))

        file_menu.add_child(MenuItem(name='save', menu_type=MenuType.Command, label='Save', accelerator='Ctrl-s',
                                     underline=0,
                                     command=lambda *_: print("'File/Save' selected")))
        file_menu.add_child(MenuItem(name='save_as', menu_type=MenuType.Command, label='Save As',
                                     command=lambda *_: print("'File/Save As' selected")))

        file_menu.add_child(MenuItem(menu_type=MenuType.Separator))

        file_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Exit', accelerator='Ctrl-e',
                                     command=lambda *_: print("'File/Exit' selected")))

        # -----------------------------------------------------------------------------------------
        # Print menu
        # -----------------------------------------------------------------------------------------
        print_menu = MenuItem(name='print', menu_type=MenuType.Cascade, label='Print')
        pdf_menu = MenuItem(menu_type=MenuType.Cascade, label='PDF')
        latex_menu = MenuItem(menu_type=MenuType.Cascade, label='Latex')
        print_menu.add_child(pdf_menu)
        print_menu.add_child(latex_menu)

        # pdf sub-menu
        pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Teacher Schedules',
                                    command=lambda *_: print("'Print/Teacher Schedules' selected")))
        pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Lab Schedules',
                                    command=lambda *_: print("'Print/Lab Schedules' selected")))
        pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Stream Schedules',
                                    command=lambda *_: print("'Print/Stream Schedules' selected")))

        pdf_menu.add_child(MenuItem(menu_type=MenuType.Separator))

        pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Text Output',
                                    command=lambda *_: print("'Print/Text Output' selected")))

        # latex sub menu
        latex_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Teacher Schedules',
                                      command=lambda *_: print("'Print/Teacher Schedules' selected")))
        latex_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Lab Schedules',
                                      command=lambda *_: print("'Print/Lab Schedules' selected")))
        latex_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Stream Schedules',
                                      command=lambda *_: print("'Print/Stream Schedules' selected")))

        latex_menu.add_child(MenuItem(menu_type=MenuType.Separator))

        latex_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Text Output',
                                      command=lambda *_: print("'Print/Text Output' selected")))

        # -----------------------------------------------------------------------------------------
        # _toolbar
        # -----------------------------------------------------------------------------------------
        toolbar_info = dict()
        toolbar_info['new'] = ToolbarItem(command=MenuItem.all_menu_items['new'].command,
                                          hint='Create new Schedule File')
        toolbar_info['open'] = ToolbarItem(command=MenuItem.all_menu_items['open'].command, hint='Open Schedule File')
        toolbar_info['save'] = ToolbarItem(command=MenuItem.all_menu_items['save'].command, hint='Save Schedule File')
        toolbar_order = ['new', 'open', 'save']

        # return list of top level menu items
        menu.append(file_menu)
        menu.append(print_menu)
        return toolbar_order, toolbar_info, menu

    # # ==================================================================
    # # save (as) schedule
    # # ==================================================================
    # def save_schedule():
    #     _save_schedule(False)
    #
    #
    # def save_as_schedule():
    #     _save_schedule(True)
    #
    #
    # def _save_schedule(save_as: bool):
    #     global schedule, gui
    #
    #     if schedule is None:
    #         gui.show_error("Save Schedule", "There is no schedule to save!")
    #         return
    #
    #     # get_by_id file to save to
    #     file: str
    #     global current_schedule_file
    #     if save_as or not current_schedule_file:
    #         file = gui.choose_file()
    #         # NOTE: This probably doesn't need to be implemented anymore.
    #         if not file:
    #             return
    #     else:
    #         file = current_schedule_file
    #
    #     # Save to database.
    #     try:
    #         schedule.write_DB()
    #     except pony.orm.Error as err:
    #         gui.show_error("Save Schedule", f"Cannot save schedule:\nError: {err}")
    #
    #     # save the current file for later use.
    #     # NOTE: We probably don't need these anymore.
    #
    #     return
    #
    #
    # # ==================================================================
    # # update_choices_of_resource_views
    # # (what teacher_ids/lab_ids/stream_ids) can we create schedules for?
    # # ==================================================================
    def update_choices_of_resource_views(self):
        pass

    #     global views_manager, gui
    #     btn_callback = views_manager.get_create_new_view_callback
    #     all_view_choices = views_manager.get_all_scheduables()
    #     page_name = pages_lookup['Schedules'].name
    #     gui.draw_view_choices(page_name, all_view_choices, btn_callback)
    #
    #     views_manager.determine_button_colours()

    # ==================================================================
    # update_overview
    # A text representation of the schedules
    # ==================================================================
    def update_overview(self):
        if self._overview is None:
            overview_frame = self.gui.get_gui_container("Overview")
            self._overview = Overview(overview_frame, self.schedule)

        # reset the schedule object just in case the schedule file has changed
        self._overview.schedule = self.schedule
        self._overview.refresh()

    # ==================================================================
    # update_edit_teachers
    # - A page where teacher_ids can be added/modified or deleted
    # ==================================================================
    def update_edit_teachers(self):
        if self._teachers_de is None:
            teachers_frame = self.gui.get_gui_container("teachers")
            self._teachers_de = EditResources(teachers_frame, ResourceType.teacher, self.schedule)

        # reset the schedule object just in case the schedule file has changed
        self._teachers_de.schedule = self.schedule
        self._teachers_de.refresh()

    # ==================================================================
    # update_edit_streams
    # - A page where stream_ids can be added/modified or deleted
    # ==================================================================
    def update_edit_streams(self):
        if self._streams_de is None:
            streams_frame = self.gui.get_gui_container("streams")
            self._streams_de = EditResources(streams_frame, ResourceType.stream, self.schedule)

        # reset the schedule object just in case the schedule file has changed
        self._streams_de.schedule = self.schedule
        self._streams_de.refresh()

    # ==================================================================
    # update_edit_labs
    # - A page where lab_ids can be added/modified or deleted
    # ==================================================================
    def update_edit_labs(self):
        if self._labs_de is None:
            labs_frame = self.gui.get_gui_container("labs")
            self._labs_de = EditResources(labs_frame, ResourceType.lab, self.schedule)

        # reset the schedule object just in case the schedule file has changed
        self._labs_de.schedule = self.schedule
        self._labs_de.refresh()

    # ==================================================================
    # draw_edit_courses
    # - A page where courses can be added/modified or deleted
    # ==================================================================
    def update_edit_courses(self):from schedule.Schedule.ScheduleEnums import ResourceType

        pass

    # ==================================================================
    # print_views
    # - print the schedule 'views'
    # - resource_type defines the output resource_type, PDF, Latex
    # ==================================================================
    def print_views(self, print_type, view_type):
        pass
        # global gui
        # # --------------------------------------------------------------
        # # no schedule yet
        # # --------------------------------------------------------------
        #
        # if not schedule:
        #     gui.show_error("Export", "Cannot export - There is no schedule")
        #
        # # --------------------------------------------------------------
        # # cannot print if the schedule is not saved
        # # --------------------------------------------------------------
        # if is_data_dirty():
        #     ans = gui.question(
        #         "Unsaved Changes",
        #         "There are unsaved changes.\nDo you want to save them?" )
        #
        #     if ans:
        #         save_schedule()
        #     else:
        #         return
        #
        # # --------------------------------------------------------------
        # # define base file name
        # # --------------------------------------------------------------
        # # NOTE: Come back to this later.
        # pass
        #
        #

    # ==================================================================
    # exit_schedule
    # ==================================================================
    def exit_schedule(self):
        pass
        # global gui
        # if is_data_dirty():
        #     answer = gui.question("Save Schedule", "Do you want to save changes?")
        #     if answer == "Yes":
        #         save_schedule()
        #     elif answer == "Cancel":
        #         return
        # _write_ini()
        #

    """
    Rewritten for Python by Evan Laverdiere
    
    Originally written by Sandy Bultena
    
    Copyrighted by the standard GPL License Agreement
    
    All Rights Reserved.
    """
    # # ==================================================================
    # # pre-process procedures
    # # ==================================================================
    # def pre_process_stuff():
    #     gui.bind_dirty_flag()
    #     gui.define_notebook_tabs(required_pages)
    #
    #     gui.define_exit_callback(exit_schedule)
    #
    #     # Create the view manager (which shows all the schedule views, etc.)
    #     global views_manager, schedule
    #     # TODO: Implement ViewsManager class.
    #     views_manager = ViewsManager(gui, is_data_dirty(), schedule)
    #     gui.set_views_manager(views_manager)
    #
