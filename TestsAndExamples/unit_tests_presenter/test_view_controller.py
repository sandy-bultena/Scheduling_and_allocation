from __future__ import annotations
from typing import Callable

import pytest
from unittest.mock import patch

import schedule.presenter.view
from schedule.model import TimeSlot, WeekDay, SemesterType, ScheduleTime, Schedule, ResourceType, ConflictType
from schedule.presenter.views_controller import ViewsController

# =====================================================================================================================
# Dummy classes
# =====================================================================================================================
"""Provides code to deal with user modifying the gui view.  Most actions are passed onto the View Controller"""

from schedule.Utilities.id_generator import IdGenerator
from schedule.model import Block, Teacher, Stream, Lab, Schedule, ScheduleTime

RESOURCE = Lab | Stream | Teacher

# =====================================================================================================================
# use an generator to always guarantee that the new id will be unique
# =====================================================================================================================
_gui_block_ids = IdGenerator()

# =====================================================================================================================
# ViewTest
# =====================================================================================================================
class GUI:
    def raise_to_top(self): pass

VIEW_TEST_CALLED = 0
REFRESH_BLOCKS_CALLED = 0
class ViewTest:

    def __init__(self, views_controller, frame, schedule, resource, gui=None):
        self.gui = GUI()
        global VIEW_TEST_CALLED
        VIEW_TEST_CALLED += 1
        self.gui_blocks = {}

    def move_gui_block_to(self, block: Block, day: float, start_time: float):
        pass

    def refresh_block_colours(self):
        global REFRESH_BLOCKS_CALLED
        REFRESH_BLOCKS_CALLED += 1

    def get_block_text(self, block: Block):
        return "hi"

    def draw(self):
        pass

# =====================================================================================================================
# ViewsControllerTestTkTest
# =====================================================================================================================

class ViewsControllerTkTest:
    def __init__(self, parent, resources:dict[ResourceType,list], btn_callback: Callable):
        self.btn_colours = []

    def set_button_colour(self, button_id: str, resource_type, view_conflict: ConflictType = None):
        self.btn_colours.append((button_id, resource_type, view_conflict))

# =====================================================================================================================
# fixtures
# =====================================================================================================================
@pytest.fixture()
def gui():
    return ViewsControllerTkTest("",{},lambda x: None)

@pytest.fixture()
def schedule_obj():
    schedule = Schedule()

    # teachers
    t1 = schedule.add_update_teacher("Jane", "Doe", "0.25", teacher_id="1")
    t2 = schedule.add_update_teacher("John", "Doe", teacher_id="2")
    t3 = schedule.add_update_teacher("Babe", "Ruth", teacher_id="3")
    t4 = schedule.add_update_teacher("Bugs", "Bunny", teacher_id = "4")

    # labs
    l1 = schedule.add_update_lab("P107", "C-Lab")
    l2 = schedule.add_update_lab("P322", "Mac Lab")
    l3 = schedule.add_update_lab("P325")
    l4 = schedule.add_update_lab("BH311", "Britain Hall")

    # streams
    st1 = schedule.add_update_stream("1A", "calculus available")
    st2 = schedule.add_update_stream("1B", "no calculus")
    st3 = schedule.add_update_stream("2A")
    st4 = schedule.add_update_stream("2B")

    # courses
    c_001 = schedule.add_update_course("001","BasketWeaving", SemesterType.fall )
    s_001_1 = c_001.add_section("1", section_id=1)
    s_001_1.add_stream(st1)
    b_001_1_1 = s_001_1.add_block(TimeSlot(WeekDay.Monday, ScheduleTime( 8) ))
    b_001_1_2 = s_001_1.add_block(TimeSlot(WeekDay.Monday, ScheduleTime( 10) ))
    b_001_1_1.add_teacher(t1)
    b_001_1_2.add_teacher(t1)
    b_001_1_1.add_lab(l1)
    b_001_1_2.add_lab(l1)

    s_001_2 = c_001.add_section("2",section_id=2)
    s_001_2.add_stream(st2)
    b_001_2_1 = s_001_2.add_block(TimeSlot(WeekDay.Tuesday, ScheduleTime( 8) ))
    b_001_2_2 = s_001_2.add_block(TimeSlot(WeekDay.Tuesday, ScheduleTime( 10) ))
    b_001_2_1.add_teacher(t2)
    b_001_2_2.add_teacher(t3)
    b_001_2_1.add_lab(l2)
    b_001_2_2.add_lab(l3)


    c_002 = schedule.add_update_course("002","Thumb Twiddling", SemesterType.fall )
    s_002_1 = c_002.add_section("1",)
    b_002_1_1 = s_002_1.add_block(TimeSlot(WeekDay.Monday, ScheduleTime( 8) ))
    b_002_1_2 = s_002_1.add_block(TimeSlot(WeekDay.Monday, ScheduleTime( 10) ))
    s_002_2 = c_002.add_section("2",)
    b_002_2_1 = s_002_2.add_block(TimeSlot(WeekDay.Tuesday, ScheduleTime( 8) ))
    b_002_2_2 = s_002_2.add_block(TimeSlot(WeekDay.Tuesday, ScheduleTime( 10) ))



    return schedule

DIRTY_FLAG = False
def dirty_flag_method(value=None):
    global DIRTY_FLAG
    if value is not None:
        DIRTY_FLAG = value
    return DIRTY_FLAG

# =====================================================================================================================
# Testing
# =====================================================================================================================
def test_init(schedule_obj, gui):
    """create views controller
    1. all resources are saved in object
    """
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)
    assert vc.resources[ResourceType.teacher] == list(schedule_obj.teachers())
    assert vc.resources[ResourceType.lab] == list(schedule_obj.labs())
    assert vc.resources[ResourceType.stream] == list(schedule_obj.streams())

def test_create_view_only_once(schedule_obj, gui, monkeypatch):
    """create multiple views, but only end up with single view for each resource"""

    # prepare
    monkeypatch.setattr("schedule.presenter.views_controller.View", ViewTest)
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)
    teacher1: Teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    teacher2: Teacher = schedule_obj.get_teacher_by_name("John","Doe")

    # execute
    vc.call_view(teacher1)
    vc.call_view(teacher2)
    vc.call_view(teacher1)
    vc.call_view(teacher2)
    vc.call_view(teacher1)
    vc.call_view(teacher2)

    # validate
    assert len(vc._views) == 2


def test_refresh(schedule_obj, gui):
    """refresh views controller
    1. conflicts are recalculated
    2. all buttons in resources have their colour updated
    """

    # prepare
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)
    teacher: Teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    blocks = schedule_obj.get_blocks_for_teacher(teacher)
    block1 = blocks[0]
    block2 = blocks[1]
    block1.time_slot.day = block2.time_slot.day
    block1.time_slot.time_start = block2.time_slot.time_start
    assert not block1.conflict
    assert not block2.conflict

    # execute
    vc.refresh()

    # validate
    assert block1.conflict
    assert block2.conflict
    assert (len(gui.btn_colours) == len(vc.resources[ResourceType.teacher])
            + len(vc.resources[ResourceType.lab])
            + len(vc.resources[ResourceType.stream])
            )


def test_block_moved(schedule_obj, gui, monkeypatch):
    global REFRESH_BLOCKS_CALLED
    """block has moved
    1. dirty flag has been reset
    2. refresh was called (which recalculates conflicts)
    3. all currently open views colours are updated 
    4. views are told to update their gui_block positions (not tested)
    """
    # prepare
    monkeypatch.setattr("schedule.presenter.views_controller.View", ViewTest)
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)
    teacher: Teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    teacher1: Teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    teacher2: Teacher = schedule_obj.get_teacher_by_name("John","Doe")
    blocks = schedule_obj.get_blocks_for_teacher(teacher)
    block1 = blocks[0]
    block2 = blocks[1]
    block1.time_slot.day = block2.time_slot.day
    block1.time_slot.time_start = block2.time_slot.time_start
    dirty_flag_method(False)
    vc.call_view(teacher1)
    vc.call_view(teacher2)

    # execute
    REFRESH_BLOCKS_CALLED = 0
    vc.notify_block_move("", block1, block1.time_slot.day.value, block1.time_slot.time_start.hours)

    # verify
    assert dirty_flag_method()
    assert block1.conflict
    assert block2.conflict
    assert REFRESH_BLOCKS_CALLED == 2



