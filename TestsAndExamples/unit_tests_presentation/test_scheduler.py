import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))

from typing import Callable, Optional

from schedule.UsefulClasses import NoteBookPageInfo
from schedule.Presentation.Scheduler import Scheduler
from schedule.Model.schedule import Schedule
from schedule.UsefulClasses.MenuItem import MenuItem, MenuType, ToolbarItem

import pytest
from os import path

schedule_file = path.dirname(__file__) + "/test.csv"


# ============================================================================
# gui Main for testing
# ============================================================================
class GuiMainTest:
    def __init__(self):
        self.create_front_page_called = False
        self.create_standard_page_called = False
        self.start_event_loop_called = False
        self.create_menu_and_toolbars_called = False
        self.draw_overview_called = False
        self.create_status_bar_called = False
        self.select_file_called = False

    def create_menu_and_toolbars(self, buttons: list[str], toolbar_info: dict[str:ToolbarItem],
                                 menu_details: list[MenuItem]):
        self.create_menu_and_toolbars_called = True
        self.toolbar_buttons = buttons
        self.toolbar_info = toolbar_info
        self.menu_details = menu_details

    def create_front_page(self, open_schedule_callback: Callable[[str, str], None],
                          new_schedule_callback: Callable[[], None]):
        self.create_front_page_called = True
        self.open_schedule_callback = open_schedule_callback
        self.new_schedule_callback = new_schedule_callback

    def create_status_bar(self):
        self.create_status_bar_called = True

    def start_event_loop(self):
        self.start_event_loop_called = True

    def select_file(self):
        self.select_file_called = True

    def draw_overview(self, page_name: str, course_text: tuple[str], teachers_text: tuple[str]):
        self.draw_overview_called = True
        self.page_name = page_name
        self.course_text = course_text
        self.teachers_text = teachers_text

    def create_standard_page(self, notebook_pages_info: Optional[list[NoteBookPageInfo]] = None):
        self.create_standard_page_called = True
        self.notebook_pages_info = notebook_pages_info

# ============================================================================
# tests
# ============================================================================

def test_init():
    gui = GuiMainTest()
    obj = Scheduler(gui)
    assert gui.create_front_page_called
    assert gui.toolbar_buttons == obj._toolbar_buttons
    assert gui.toolbar_info == obj._button_properties
    assert gui.menu_details == obj._menu
    assert gui.start_event_loop_called

def test_open_existing_file_directly():
    gui = GuiMainTest()
    obj = Scheduler(gui)
    obj.open_schedule(schedule_file)
    assert isinstance(obj.schedule, Schedule)
    assert len(obj.schedule.teachers) == 15

def test_open_new_file():
    gui = GuiMainTest()
    obj = Scheduler(gui)
    obj.new_schedule()
    assert isinstance(obj.schedule, Schedule)
    assert len(obj.schedule.teachers) == 0

def test_open_new_file_from_toolbar():
    gui = GuiMainTest()
    obj = Scheduler(gui)
    obj._button_properties['new'].command()
    assert isinstance(obj.schedule, Schedule)
    assert len(obj.schedule.teachers) == 0


def test_open_new_file_from_menu():
    gui = GuiMainTest()
    obj = Scheduler(gui)
    menu: list[MenuItem]
    (_, _, menu) = obj._menu_and_toolbar_info()
    new_menu: MenuItem = None
    for m in menu:
        if m.menu_type == MenuType.Cascade:
            for mm in m.children:
                if mm.name == 'new':
                    new_menu = mm

    if new_menu:
        new_menu.command()
        assert isinstance(obj.schedule, Schedule)
        assert len(obj.schedule.teachers) == 0
    else:
        assert False


def test_select_file():
    gui = GuiMainTest()
    obj = Scheduler(gui)
    obj.select_file()
    assert gui.select_file_called


def test_select_file_from_taskbar():
    gui = GuiMainTest()
    obj = Scheduler(gui)
    obj._button_properties['open'].command()
    assert gui.select_file_called


def test_select_file_from_menu():
    gui = GuiMainTest()
    obj = Scheduler(gui)
    menu: list[MenuItem]
    (_, _, menu) = obj._menu_and_toolbar_info()
    open_menu: MenuItem = None
    for m in menu:
        if m.menu_type == MenuType.Cascade:
            for mm in m.children:
                if mm.name == 'open':
                    open_menu = mm

    if open_menu:
        open_menu.command()
        assert gui.select_file_called
    else:
        assert False


def test_update_overview_no_schedule():
    gui = GuiMainTest()
    obj = Scheduler(gui)
    obj.update_overview()
    assert gui.draw_overview_called
    assert len(gui.course_text) == 1
    assert gui.course_text[0] == 'There is no schedule, please open one'
    assert len(gui.teachers_text) == 1
    assert gui.teachers_text[0] == 'There is no schedule, please open one'


def test_update_overview_no_teachers_or_courses():
    gui = GuiMainTest()
    obj = Scheduler(gui)
    obj.new_schedule()
    obj.update_overview()
    assert gui.draw_overview_called
    assert len(gui.course_text) == 1
    assert gui.course_text[0] == 'No courses defined in this schedule'
    assert len(gui.teachers_text) == 1
    assert gui.teachers_text[0] == 'No teachers defined in this schedule'


def test_update_overview_teachers_and_courses():
    gui = GuiMainTest()
    obj = Scheduler(gui)
    obj.open_schedule(schedule_file)
    obj.update_overview()
    assert gui.draw_overview_called
    assert len(gui.course_text) > 1
    assert gui.course_text[0] == str(obj.schedule.courses[0])
    assert len(gui.teachers_text) > 1
    assert gui.teachers_text[0] == obj.schedule.teacher_details(obj.schedule.teachers[0])


def test_update_overview_changing_schedules():
    gui = GuiMainTest()
    obj = Scheduler(gui)
    obj.open_schedule(schedule_file)
    obj.update_overview()
    assert gui.draw_overview_called
    assert len(gui.course_text) > 1
    assert gui.course_text[0] == str(obj.schedule.courses[0])
    assert len(gui.teachers_text) > 1
    assert gui.teachers_text[0] == obj.schedule.teacher_details(obj.schedule.teachers[0])

    obj.new_schedule()
    obj.update_overview()
    assert gui.draw_overview_called
    assert len(gui.course_text) == 1
    assert gui.course_text[0] == 'No courses defined in this schedule'
    assert len(gui.teachers_text) == 1
    assert gui.teachers_text[0] == 'No teachers defined in this schedule'
