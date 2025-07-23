from __future__ import annotations
import re
from functools import partial
from turtledemo.rosette import mn_eck
from typing import TYPE_CHECKING, Optional

from schedule.Tk import MenuItem, MenuType
from schedule.Utilities.id_generator import IdGenerator
from schedule.gui_pages.view_dynamic_tk import ViewDynamicTk
from schedule.model import Block, Teacher, Stream, Lab, Schedule, ScheduleTime
from schedule.model.enums import ResourceType
if TYPE_CHECKING:
    from schedule.presenter.views_controller import ViewsController

# =====================================================================================================================
# use an generator to always guarantee that the new id will be unique
# =====================================================================================================================
_gui_block_ids = IdGenerator()

# =====================================================================================================================
# View
# =====================================================================================================================
class View:
    """View - describes the visual representation of a Schedule."""
    def __init__(self, views_controller: ViewsController, frame, schedule: Schedule, resource: Teacher | Stream | Lab):
        self.views_controller = views_controller
        self.frame = frame
        self.resource = resource
        self.schedule = schedule
        self.gui_blocks: dict[str, Block] = {}

        # get the resource type from the resource object, and all its blocks
        resource_type = ResourceType.none
        if isinstance(resource, Teacher):
            resource_type = ResourceType.teacher
        elif isinstance(resource, Stream):
            resource_type = ResourceType.stream
        elif isinstance(resource, Lab):
            resource_type = ResourceType.lab
        self.resource_type = resource_type

        self.blocks: list[Block] = []

        # create the gui representation of the view
        self.gui: ViewDynamicTk = ViewDynamicTk(self.frame, str(resource),
                                                refresh_blocks_handler=self.draw_blocks,
                                                on_closing_handler=self.on_closing,
                                                double_click_block_handler=self.open_companion_view,
                                                gui_block_is_moving_handler=self.gui_block_is_moving,
                                                gui_block_has_dropped_handler=self.gui_block_has_dropped,
                                                get_popup_menu_handler=self.popup_menu,
                                                undo_handler=self.views_controller.undo,
                                                redo_handler=self.views_controller.redo,
                                                )
        self._block_original_start_time: Optional[float]= None
        self._block_original_day: Optional[float] = None
        self.gui.draw()

    # ----------------------------------------------------------------------------------------------------------------
    # get all the blocks for this resource/schedule (refresh_blocks_handler)
    # ----------------------------------------------------------------------------------------------------------------
    def draw_blocks(self):

        # get all the blocks for this resource/schedule
        blocks = []
        match self.resource_type:
            case ResourceType.teacher:
                blocks = self.schedule.get_blocks_for_teacher(self.resource)
            case ResourceType.stream:
                blocks = self.schedule.get_blocks_for_stream(self.resource)
            case ResourceType.lab:
                blocks = self.schedule.get_blocks_in_lab(self.resource)

        # create all the gui blocks and draw them
        self.gui_blocks.clear()

        for block in blocks:

            gui_block_id: int = _gui_block_ids.get_new_id()
            gui_tag = f"gui_tag_{gui_block_id}"
            self.gui_blocks[gui_tag] = block

            text = self.get_block_text(block)
            day, start_time, duration = self._block_to_floats(block)

            self.gui.draw_block(resource_type=self.resource_type,
                                day=day, start_time=start_time, duration=duration,
                                text=text,
                                gui_block_id=gui_tag,
                                movable=block.movable())
            self.gui.colour_block(gui_tag, self.resource_type, block.movable(), conflict=block.conflict)

    # ----------------------------------------------------------------------------------------------------------------
    # important tidy-up stuff (on_closing_handler)
    # ----------------------------------------------------------------------------------------------------------------
    def on_closing(self, _):
        """When the view closes, clean up"""
        self.views_controller.view_is_closing(self.resource)

    # ----------------------------------------------------------------------------------------------------------------
    # open companion view (double_click_handler)
    # ----------------------------------------------------------------------------------------------------------------
    def open_companion_view(self, gui_tag: str):
        """
        Based on the resource_type of this view, will open another view which has this Block.
        :param gui_tag:
        """
        block = self.gui_blocks[gui_tag]
        self.views_controller.open_companion_view(block)

    # ----------------------------------------------------------------------------------------------------------------
    # gui_block_is_moving (gui_block_is_moving_handler)
    # ----------------------------------------------------------------------------------------------------------------
    def gui_block_is_moving(self, gui_id: str,  day: float, start_time: float, duration: float):
        """
        Update block and conflict information as the user is dragging the gui block
        :param gui_id: the id of the gui representation of the block
        :param day: the position of the gui block
        :param start_time: the start time of the gui block
        :param duration: (not sure if we need this, TBD)
        """

        block: Block = self.gui_blocks.get(gui_id,None)
        if block is None:
            return

        # capture the info about the block before it starts moving
        if self._block_original_start_time is None and self._block_original_day is None:
            self._block_original_start_time = block.time_slot.time_start.hours
            self._block_original_day = block.time_slot.day.value

        """update the block by snapping to time and day, although it doesn't update the gui block"""
        block.time_slot.time_start = ScheduleTime(start_time)
        block.time_slot.snap_to_day(day)
        block.time_slot.duration = duration
        block.time_slot.snap_to_time()
        self.schedule.calculate_conflicts()
        self.refresh_block_colours()
        self.gui.colour_block(gui_id, self.resource_type, is_movable=block.movable(), conflict = block.conflict)

        # very important, let the gui controller _know_ that the gui block has been moved
        self.views_controller.notify_block_move(self.resource.number, block,  day, start_time)

    # ----------------------------------------------------------------------------------------------------------------
    # gui_block_has_dropped (gui_block_has_dropped_handler)
    # ----------------------------------------------------------------------------------------------------------------
    def gui_block_has_dropped(self, gui_id: str):
        """
        User has stopped dragging the gui block, so adjust gui block to block's new location
        :param gui_id: the id of the gui representation of the block
        """

        block: Block = self.gui_blocks.get(gui_id,None)
        if block is None:
            return

        # has the block actually moved?
        if self._block_original_start_time is None or self._block_original_day is None:
            return

        if (self._block_original_start_time == block.time_slot.time_start.hours and
            self._block_original_day == block.time_slot.day.value):
            return

        # set the gui block coordinates to match the block (which is constantly being snapped to grid
        # during the move process
        self.gui.move_gui_block(gui_id, block.time_slot.day.value,block.time_slot.time_start.hours)

        # very important, let the gui controller _know_ that the gui block has been moved
        self.views_controller.notify_block_move(self.resource.number, block, block.time_slot.day.value,
                                block.time_slot.time_start.hours)

        # save the action so that it can be undone
        self.views_controller.remove_all_redoes()
        self.views_controller.add_move_to_undo(block, self._block_original_day, block.time_slot.day.value,
                                               self._block_original_start_time, block.time_slot.time_start.hours)
        self._block_original_start_time = None
        self._block_original_day = None

    # ----------------------------------------------------------------------------------------------------------------
    # get popup menu (get_popup_menu_handler)
    # ----------------------------------------------------------------------------------------------------------------
    def popup_menu(self, gui_id) -> Optional[list[MenuItem]]:
        block = self.gui_blocks.get(gui_id, None)

        if block is None:
            return

        if self.resource_type == ResourceType.stream:
            return

        # get the resources (note we cannot swap blocks between streams)
        resources = set()
        match self.resource_type:
            case ResourceType.teacher:
                resources = set(self.schedule.teachers()) - set(block.teachers())
            case ResourceType.lab:
                resources = set(self.schedule.labs()) - set(block.labs())
        if len(resources) == 0:
            return

        # create the menu
        menu_list: list[MenuItem] = []
        for resource in sorted(resources):
            menu_list.append(MenuItem(menu_type=MenuType.Command, label=f"Move to {resource}",
                                      command=partial(self.views_controller.move_block_to_resource,
                                                      self.resource_type,
                                                      block,
                                                      self.resource,
                                                      resource)
                                      )
                             )
        return menu_list


    # ----------------------------------------------------------------------------------------------------------------
    # move_gui_block_to (used by Views Controller)
    # ----------------------------------------------------------------------------------------------------------------
    def move_gui_block_to(self, block: Block, day: float, start_time: float):
        """
        move the gui block (associated with block) to a new position (used by Views Controller)
        :param block: block that is associated with the gui image
        :param day: the day that the **gui block** needs to be moved to (not necessarily the same as the block)
        :param start_time: the time that the **gui block** needs to be moved to (not necessarily the same as the block)
        """
        gui_id = self._get_gui_id_from_block(block.number)
        self.gui.move_gui_block(gui_id, day, start_time)


    # ----------------------------------------------------------------------------------------------------------------
    # refresh block colour (used by Views Controller & View)
    # ----------------------------------------------------------------------------------------------------------------
    def refresh_block_colours(self):
        """Go through all blocks, and adjust colours as required"""

        for gui_tag, block in self.gui_blocks.items():
            self.gui.colour_block(gui_tag, self.resource_type, is_movable=block.movable(), conflict = block.conflict)

    # ----------------------------------------------------------------------------------------------------------------
    # get block text
    # ----------------------------------------------------------------------------------------------------------------
    def get_block_text(self, block: Block):
        """
        :param block: The block object
        """
        scale = self.gui.view_canvas.scale.current_scale
        resource_type = self.resource_type

        # course & section & streams
        course_number = ""
        section_number = ""
        stream_numbers = ""
        if block.section:
            course_number = block.section.course.number if scale > 0.5 else re.split("[-*]", block.section.course.number)
            section_number = block.section.title
            stream_numbers = ",".join((stream.number for stream in block.section.streams()))

        # labs
        lab_numbers = ",".join(l.number for l in block.labs())
        lab_numbers = lab_numbers if scale > .75 else lab_numbers[0:11] + "..."
        lab_numbers = lab_numbers if scale > .50 else lab_numbers[0:7] + "..."
        lab_numbers = lab_numbers if resource_type != ResourceType.lab and scale > .75 else ""

        # streams
        stream_numbers = stream_numbers if scale > .75 else stream_numbers[0:11] + "..."
        stream_numbers = stream_numbers if scale > .50 else stream_numbers[0:7] + "..."
        stream_numbers = stream_numbers if resource_type != ResourceType.stream and scale > .75 else ""

        # teachers
        teachers_name = ""
        for t in block.teachers():
            if len(str(t)) > 15:
                teachers_name = teachers_name + f"{t.firstname[0:1]} {t.lastname}\n"
            else:
                teachers_name = teachers_name + f"{str(t)}\n"
        teachers_name = teachers_name.rstrip()
        teachers_name = teachers_name if scale > .75 else teachers_name[0:11] + "..."
        teachers_name = teachers_name if scale > .50 else teachers_name[0:7] + "..."
        teachers_name = teachers_name if resource_type != ResourceType.stream and scale > .75 else ""

        # define what to display
        block_text = f"{course_number}\n{section_number}\n"
        block_text = block_text + teachers_name + "\n" if teachers_name else block_text
        block_text = block_text + lab_numbers + "\n" if lab_numbers else block_text
        block_text = block_text + stream_numbers + "\n" if stream_numbers else block_text

        block_text = block_text.rstrip()
        return block_text

    # ----------------------------------------------------------------------------------------------------------------
    # draw - called by Views Controller
    # ----------------------------------------------------------------------------------------------------------------
    def draw(self):
        self.gui.draw()

    # ----------------------------------------------------------------------------------------------------------------
    # block to floats
    # ----------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _block_to_floats( block) -> tuple[int,float,float]:
        """take a block and return number representations of its properties"""
        return block.time_slot.day.value, block.time_slot.time_start.hours, block.time_slot.duration

    # ----------------------------------------------------------------------------------------------------------------
    # get gui id from block
    # ----------------------------------------------------------------------------------------------------------------
    def _get_gui_id_from_block(self, block_number: str) -> Optional[str]:
        for g,b in self.gui_blocks.items():
            if b.number == block_number:
                return g
        return None

