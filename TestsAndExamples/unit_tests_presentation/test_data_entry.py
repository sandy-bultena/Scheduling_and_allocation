import pytest
import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))
from schedule.GUI_Pages.EditResourcesTk import DEColumnDescription
from typing import Any
from schedule.Schedule.Schedule import Schedule
from schedule.Presentation.EditResources import EditResources
from schedule.Schedule.ScheduleEnums import ResourceType
from schedule.Presentation.globals import *


class Gui:
    def __init__(self):
        self.called_initialize_columns = False
        self.called_refresh = False
        self.called_get_all_data = False
        self.data: list[list[Any]] = list(list())
        self.column_descriptions = None

    def initialize_columns(self, column_descriptions: list[DEColumnDescription]):
        self.called_initialize_columns = True
        self.column_descriptions = column_descriptions

    def refresh(self, data: list[list[Any]]):
        self.called_refresh = True
        self.data = data

    def get_all_data(self) -> list[list[str]]:
        self.called_get_all_data = True
        return self.data


def test_constructor():
    schedule = Schedule()
    t1 = schedule.add_teacher("Jane", "Doe")
    t1.release = 0
    t2 = schedule.add_teacher("John", "Doe")
    t3 = schedule.add_teacher("Babe", "Ruth")
    gui = Gui()
    de = EditResources("", ResourceType.teacher, schedule, gui)
    assert gui.called_initialize_columns == True
    columns = gui.column_descriptions
    assert columns[0].property == 'id'
    assert columns[1].property == 'firstname'

def test_refresh():
    schedule = Schedule()
    unset_dirty_flag()
    t1 = schedule.add_teacher("Jane", "Doe")
    t1.release = 0.3
    t2 = schedule.add_teacher("John", "Doe")
    t3 = schedule.add_teacher("Babe", "Ruth")
    gui = Gui()
    de = EditResources("", ResourceType.teacher, schedule, gui)
    de.refresh()
    assert gui.called_refresh
    assert len(gui.data) == 3
    assert not is_data_dirty()

def test_handle_empty_rows():
    schedule = Schedule()
    unset_dirty_flag()
    assert not is_data_dirty()
    t1 = schedule.add_teacher("Jane", "Doe")
    t1.release = 0.25
    t2 = schedule.add_teacher("John", "Doe")
    t3 = schedule.add_teacher("Babe", "Ruth")
    gui = Gui()
    de = EditResources("", ResourceType.teacher, schedule, gui)
    de.refresh()
    assert gui.called_refresh
    gui.data.append(["", "", "", ""])
    de._cb_save()
    assert gui.called_get_all_data
    assert len(schedule.teachers) == 3
    assert not is_data_dirty()


def test_adding_new_teacher():
    schedule = Schedule()
    unset_dirty_flag()
    assert not is_data_dirty()
    t1 = schedule.add_teacher("Jane", "Doe")
    t1.release = 0.25
    t2 = schedule.add_teacher("John", "Doe")
    t3 = schedule.add_teacher("Babe", "Ruth")
    gui = Gui()
    de = EditResources("", ResourceType.teacher, schedule, gui)
    de.refresh()
    assert gui.called_refresh
    gui.data.append(["", "New", "Teacher", ".21"])
    de._cb_save()
    assert gui.called_get_all_data
    assert len(schedule.teachers) == 4
    new_teacher = schedule.get_teacher_by_name("New", "Teacher")
    assert new_teacher is not None
    assert new_teacher.release == 0.21
    assert is_data_dirty()

def test_modifying_teacher():
    schedule = Schedule()
    unset_dirty_flag()
    assert not is_data_dirty()
    t1 = schedule.add_teacher("Jane", "Doe")
    t1.release = 0.25
    t2 = schedule.add_teacher("John", "Doe")
    t3 = schedule.add_teacher("Babe", "Ruth")
    gui = Gui()
    de = EditResources("", ResourceType.teacher, schedule, gui)
    de.refresh()
    assert gui.called_refresh
    gui.data[0][1] = "Janet"
    de._cb_save()
    assert gui.called_get_all_data
    assert len(schedule.teachers) == 3
    mod_teacher = schedule.get_teacher_by_name("Janet", "Doe")
    assert mod_teacher is not None
    assert mod_teacher == t1
    assert is_data_dirty()