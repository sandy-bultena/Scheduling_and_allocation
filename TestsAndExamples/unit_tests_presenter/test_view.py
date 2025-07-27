from typing import Callable, Optional

import pytest
from _pytest.fixtures import fixture

from schedule.Tk import MenuItem, MenuType
from schedule.model import ResourceType, ConflictType, SemesterType, WeekDay, TimeSlot, Schedule, ScheduleTime, Block
from schedule.presenter.view import View


def _default_menu(*_) -> list[MenuItem]:
    menu = MenuItem(name="nothing", label="nothing", menu_type=MenuType.Command, command=lambda: None)
    return [menu, ]

# =====================================================================================================================
# View Gui Test class
# =====================================================================================================================

class ViewDynamicTkTest:

    def __init__(self, frame, title: str,resource_type: ResourceType):
        # ------------------------------------------------------------------------------------------------------------
        # handlers
        # ------------------------------------------------------------------------------------------------------------
        # returns menu info for gui block popup menu
        self.get_popup_menu_handler: Callable[[str], list[MenuItem]] = _default_menu

        # redraws all the appropriate blocks on the canvas
        self.refresh_blocks_handler: Callable[[], None] = lambda: None

        # handles the closing of this view
        self.on_closing_handler: Callable = lambda *_: None

        # handles a double click on a gui block
        self.double_click_block_handler: Callable[[str], None] = lambda gui_id: None

        # handles the movement of a gui block
        self.gui_block_is_moving_handler: Callable[[str, float, float], None] = lambda gui_id, day, start: None

        # handles the dropping of a gui block
        self.gui_block_has_dropped_handler: Callable[[str], None] = lambda gui_id: None


        # undo/redo handlers
        self.undo_handler: Callable[[], None] = lambda: None
        self.redo_handler: Callable[[], None] = lambda: None

        self.draw_blocks_info = {}
        self.colour_blocks_info = {}

    def get_scale(self):
        return 1

    def draw(self, scale_factor: float = 1.0):
        self.refresh_blocks_handler()


    def draw_block(self, resource_type: ResourceType, day: int, start_time: float,
                   duration: float, text: str, gui_block_id, movable=True):
        self.draw_blocks_info[gui_block_id] = (day, start_time, duration, movable)

    def colour_block(self, gui_block_id: str, resource_type: ResourceType, is_movable=True,
                     conflict: ConflictType = None):
        self.colour_blocks_info[gui_block_id] = (resource_type, is_movable, conflict)

    def move_gui_block(self, gui_block_id: str, day_number, start_number):
        pass


# =====================================================================================================================
# Views Controller
# =====================================================================================================================
class ViewsControllerTest:

    def __init__(self, dirty_flag_method, frame, schedule):
        self.notified_toggled = None
        self.remove_redoes = False
        self.action_toggle = None
        self.on_closing_called = False
        self.notify_move_block_to_resource_args = {}
        self.open_companion_view_called = None
        self.action_resource_saved = {}
        self.block_move = {}
        self.action_moved = {}
        self.undo_called = False
        self.redo_called = False

    def notify_block_move(self, resource_number: Optional[str], moved_block: Block, day: float, start_time:float):
        self.block_move["id"] = resource_number
        self.block_move["block"] = moved_block
        self.block_move["day"] = day
        self.block_move["start"] = start_time


    def notify_block_movable_toggled(self, modified_block):
        self.notified_toggled = modified_block

    def notify_move_block_to_resource(self, resource_type: ResourceType, block, from_resource, to_resource):
        self.notify_move_block_to_resource_args["block"] = block
        self.notify_move_block_to_resource_args["from"] = from_resource
        self.notify_move_block_to_resource_args["to_resource"] = to_resource
        self.notify_move_block_to_resource_args["type"] = resource_type

    def open_companion_view(self, block):
        self.open_companion_view_called = block

    def view_is_closing(self, resource):
        self.on_closing_called = True

    def save_action_block_move(self, block, from_day:float, to_day:float, from_time:float, to_time:float):
        self.action_moved['block'] = block
        self.action_moved['from'] = from_day
        self.action_moved['to'] = to_day
        self.action_moved['from_time'] = from_time
        self.action_moved['to_time'] = to_time

    def save_action_block_resource_changed(self, resource_type: ResourceType, block, from_resource, to_resource):
        self.action_resource_saved["block"] = block
        self.action_resource_saved["from"] = from_resource
        self.action_resource_saved["to_resource"] = to_resource
        self.action_resource_saved["type"] = resource_type

    def save_action_block_movable_toggled(self, block, was: bool):
        self.action_toggle = (block, was)

    def remove_all_redoes(self):
        self.remove_redoes = True

    def undo(self):
        self.undo_called = True

    def redo(self):
        self.redo_called = True


# =====================================================================================================================
# fixtures
# =====================================================================================================================
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

def dirty_flag_method():
    pass

@fixture
def gui():
    gui = ViewDynamicTkTest("frame", "title", ResourceType.none)
    return gui

@fixture
def view_control():
    vc = ViewsControllerTest("", "", "")
    return vc

# ===================================================================================================================
# Testing View
# ===================================================================================================================
def test_init(schedule_obj, view_control, gui):
    """Create a view    """

    # execute
    view = View(view_control,"", schedule_obj, resource=schedule_obj.get_teacher_by_name("Jane", "Doe"), gui=gui )

def test_draw_blocks_called_during_init(schedule_obj, view_control, gui):
    """Create a view
    1. all blocks have a gui_id
    2. each gui block is drawn with the appropriate parameters
    3. each gui block is told to colour with each of the appropriate parameters
    """
    # prepare
    teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    blocks = schedule_obj.get_blocks_for_teacher(teacher)
    blocks[0].add_conflict(ConflictType.LUNCH)


    # execute: (view is drawn after block has been modified)
    view = View(view_control,"", schedule_obj, resource=teacher, gui=gui )

    # verify
    for block in blocks:
        assert block in view.gui_blocks.values()

    for gui_id in view.gui_blocks:
        block: Block = view.gui_blocks[gui_id]
        assert gui_id in gui.draw_blocks_info
        assert gui.draw_blocks_info[gui_id] == (block.time_slot.day.value, block.time_slot.time_start.hours,
                                                block.time_slot.duration, block.movable())
        assert gui.colour_blocks_info[gui_id] == (ResourceType.teacher, block.movable(), block.conflict )


def test_draw_blocks(schedule_obj, view_control, gui):
    """draw all the blocks
    1. all blocks have a gui_id
    2. each gui block is drawn with the appropriate parameters
    3. each gui block is told to colour with each of the appropriate paramters
    """

    # prepare
    teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    view = View(view_control,"", schedule_obj, resource=teacher, gui=gui )
    blocks = schedule_obj.get_blocks_for_teacher(teacher)
    blocks[0].add_conflict(ConflictType.LUNCH)

    # execute
    view.draw_blocks()

    # verify
    for block in blocks:
        assert block in view.gui_blocks.values()

    for gui_id in view.gui_blocks:
        block: Block = view.gui_blocks[gui_id]
        assert gui_id in gui.draw_blocks_info
        assert gui.draw_blocks_info[gui_id] == (block.time_slot.day.value, block.time_slot.time_start.hours,
                                                block.time_slot.duration, block.movable())
        assert gui.colour_blocks_info[gui_id] == (ResourceType.teacher, block.movable(), block.conflict )

def test_view_keeps_track_of_blocks_and_gui_ids(schedule_obj, view_control, gui):
    """Create the view
    1. Able to determine if a certain block is in the view
    """
    # prepare
    teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    block = schedule_obj.get_blocks_for_teacher(teacher)[0]

    # execute
    view = View(view_control,"", schedule_obj, resource=teacher, gui=gui )

    # validate
    assert view.is_block_in_view(block)
# ===================================================================================================================
# Testing View Popup and Popup Handlers
# ===================================================================================================================
def test_popup_menu(schedule_obj, view_control, gui):
    """Invoke pop-up menu
    1. returns a MenuItem list
    2. has a 'Toggle' option on list
    3. has move resource to... on list
    """

    # prepare
    teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    view = View(view_control,"", schedule_obj, resource=teacher, gui=gui )
    gui_id = list(view.gui_blocks.keys())[0]

    # execute
    menu = gui.get_popup_menu_handler(gui_id)

    # verify
    assert len(menu) != 0
    mi = None
    for m in menu:
        if "Toggle" in m.label:
            mi = m.command
    assert mi is not None
    assert "Move to Bugs Bunny" in (m.label for m in menu)

def test_toggle_movable(schedule_obj, view_control, gui):
    """from pop-up menu, toggle block movability
    1. modify the block accordingly
    2. notify view controller that block has changed
    3. remove all 'redoes' because user had done something
    4. add action to the 'undo' list
    """

    # prepare
    teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    view = View(view_control,"", schedule_obj, resource=teacher, gui=gui )
    gui_id = list(view.gui_blocks.keys())[0]
    block = view.gui_blocks[gui_id]
    block.time_slot.movable = True
    menu = gui.get_popup_menu_handler(gui_id)

    # execute
    for m in menu:
        if "Toggle" in m.label:
            m.command()

    # verify
    assert not block.movable()

    # execute
    view.toggle_is_movable(block)

    # verify
    assert block.movable()
    assert view_control.remove_redoes
    assert view_control.notified_toggled == block
    assert view_control.action_toggle == (block, False)

def test_move_block_to_different_resource(schedule_obj, view_control, gui):
    """from pop-up menu, move block to different resource
    1. notify view controller that block has changed
    2. remove all 'redoes' because user had done something
    3. add action to the 'undo' list
       NOTE: block is not changed in view, it is changed in the view_controller
    """

    # prepare
    teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    view = View(view_control,"", schedule_obj, resource=teacher, gui=gui )
    gui_id = list(view.gui_blocks.keys())[0]
    block = view.gui_blocks[gui_id]
    block.time_slot.movable = True
    menu = gui.get_popup_menu_handler(gui_id)

    # execute
    for m in menu:
        if "John Doe" in m.label:
            m.command()

    # verify
    assert len(view_control.notify_move_block_to_resource_args) != 0
    jd = schedule_obj.get_teacher_by_name("John","Doe")
    assert view_control.remove_redoes

    assert view_control.notify_move_block_to_resource_args["block"] == block
    assert view_control.notify_move_block_to_resource_args["from"] == teacher
    assert view_control.notify_move_block_to_resource_args["to_resource"] == jd
    assert view_control.notify_move_block_to_resource_args["type"] == ResourceType.teacher

    assert view_control.action_resource_saved["block"] == block
    assert view_control.action_resource_saved["from"] == teacher
    assert view_control.action_resource_saved["to_resource"] == jd
    assert view_control.action_resource_saved["type"] == ResourceType.teacher



def test_on_closing_informs_view_controller(schedule_obj, view_control, gui):
    """close the view
    1. view controller is informed
    """

    # prepare
    teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    view = View(view_control,"", schedule_obj, resource=teacher, gui=gui )

    # execute
    view.on_closing()

    # verify
    assert view_control.on_closing_called

def test_handle_double_click(schedule_obj, view_control, gui):
    """Block is doubled clicked on view
    1. View control is asked to pop up companion views
    """

    # prepare
    teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    view = View(view_control,"", schedule_obj, resource=teacher, gui=gui )
    gui_id = list(view.gui_blocks.keys())[0]
    block = view.gui_blocks[gui_id]

    # execute
    gui.double_click_block_handler(gui_id)

    # verify
    assert view_control.open_companion_view_called == block

def test_gui_block_is_moving(schedule_obj, view_control, gui):
    """block is moving
    1. view_control is informed
    2. block is moving (snapping to time as it goes)
    3. conflicts are recalculated
    """

    # prepare
    teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    view = View(view_control,"", schedule_obj, resource=teacher, gui=gui )
    gui_id = list(view.gui_blocks.keys())[0]
    block = view.gui_blocks[gui_id]
    o_day = block.time_slot.day.value

    # execute
    gui.gui_block_is_moving_handler( gui_id,  block.time_slot.day.value-0.2, 9.45)

    # validate
    assert view_control.block_move['block'] == block
    assert view_control.block_move['id'] == teacher.number
    assert view_control.block_move['day'] == block.time_slot.day.value-0.2

    assert block.time_slot.day.value == o_day
    assert block.time_slot.time_start.hours == 9.50

    assert block.conflict


def test_gui_block_has_dropped(schedule_obj, view_control, gui):
    """block has dropped
    1. view_control is informed
    2. block is moving (snapping to time as it goes)
    3. conflicts are recalculated
    4. action has been saved
    5. redo has cleared
    6. gui block has been updated (don't know how to test this)
    """

    # prepare
    teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    view = View(view_control,"", schedule_obj, resource=teacher, gui=gui )
    gui_id = list(view.gui_blocks.keys())[0]
    block = view.gui_blocks[gui_id]
    o_day = block.time_slot.day.value
    o_start = block.time_slot.time_start.hours
    gui.gui_block_is_moving_handler( gui_id,  3, 9.45)

    # execute
    gui.gui_block_has_dropped_handler( gui_id)

    # validate
    assert block.time_slot.day.value == 3
    assert block.time_slot.time_start.hours == 9.5

    assert block.conflict

    assert view_control.remove_redoes
    assert view_control.action_moved['block'] == block
    assert view_control.action_moved['from'] == o_day
    assert view_control.action_moved['to'] == 3
    assert view_control.action_moved['from_time'] == o_start
    assert view_control.action_moved['to_time'] == 9.5

def test_gui_block_has_dropped_but_not_moved(schedule_obj, view_control, gui):
    """block has dropped, but wasn't moved
    1. view_control is not called
    """

    # prepare
    teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    view = View(view_control,"", schedule_obj, resource=teacher, gui=gui )
    gui_id = list(view.gui_blocks.keys())[0]
    block = view.gui_blocks[gui_id]

    # execute
    gui.gui_block_has_dropped_handler( gui_id)

    # validate
    assert not view_control.remove_redoes
    assert len(view_control.action_moved) == 0

def test_gui_undo_passed_to_controller(schedule_obj, view_control, gui):
    """user triggered a undo
    1. undo trigger is passed to controller
    """

    # prepare
    teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    view = View(view_control,"", schedule_obj, resource=teacher, gui=gui )

    # execute
    gui.undo_handler()

    # validate
    assert view_control.undo_called

def test_gui_redo_passed_to_controller(schedule_obj, view_control, gui):
    """user triggered a redo
    1. redo trigger is passed to controller
    """

    # prepare
    teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    view = View(view_control,"", schedule_obj, resource=teacher, gui=gui )

    # execute
    gui.redo_handler()

    # validate
    assert view_control.redo_called

