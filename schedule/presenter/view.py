#
#
# from .AssignToResource import AssignToResource
# from ..Export import DrawView
# from ..gui_pages.GuiBlock import GuiBlock
# from ..gui_pages.ViewTk import ViewTk
# from ..model.Block import Block
# from ..model.conflicts import Conflict
# from ..model.Labs import Lab
# from ..model.schedule import Schedule
# from ..model.ScheduleEnums import ConflictType, ResourceType
# from ..model.stream import Stream
# from ..model.teacher import Teacher
# from ..model.undo import Undo
# from ..PerlLib import Colour
# from ..Utilities.AllResources import AllResources
#
#
from typing import Optional

from schedule.gui_pages.view_dynamic_tk import ViewDynamicTk
from schedule.model import Block, Teacher, Stream, Lab, Schedule, ClockTime, ScheduleTime
from schedule.model.enums import WeekDay, ResourceType
from schedule.presenter.gui_block import GuiBlock


class View:
    """View - describes the visual representation of a Schedule."""
    def __init__(self, mw, schedule: Schedule, resource: Teacher|Stream|Lab ):
        self.mw = mw
        self.resource = resource
        self.schedule = schedule
        self.gui_blocks: dict[str, Block] = {}

        resource_type = ResourceType.none
        if isinstance(resource, Teacher):
            resource_type = ResourceType.teacher
        elif isinstance(resource, Stream):
            resource_type = ResourceType.stream
        elif isinstance(resource, Lab):
            resource_type = ResourceType.lab
        self.resource_type = resource_type

        self.blocks: list[Block] = []
        self.gui: ViewDynamicTk = ViewDynamicTk(mw, str(resource),
                                                refresh_blocks_handler=self.event_redraw,
                                                on_closing_handler=self.on_closing,
                                                double_click_block_handler=self.open_companion_view,
                                                gui_block_is_moving_handler=self.gui_block_is_moving,
                                                gui_block_has_dropped_handler=self.gui_block_has_dropped,
                                                )
        self.draw()


    def get_blocks(self):
        blocks = []
        match self.resource_type:
            case ResourceType.teacher:
                blocks = self.schedule.get_blocks_for_teacher(self.resource)
            case ResourceType.stream:
                blocks = self.schedule.get_blocks_for_stream(self.resource)
            case ResourceType.lab:
                blocks = self.schedule.get_blocks_in_lab(self.resource)
        return blocks

    def draw(self):
        self.gui.draw()

    def event_redraw(self):
        self.gui_blocks.clear()
        for block in self.get_blocks():
            gui_block = GuiBlock(block, self.resource_type)
            self.gui_blocks[gui_block.gui_tag]= block
            text = gui_block.get_block_text(self.gui.view_canvas.scale.current_scale)
            self.gui.draw_block(self.resource_type, gui_block.day, gui_block.start_time, gui_block.duration, text, gui_block.gui_tag)
            self.gui.colour_block(gui_block.gui_tag, self.resource_type, conflict=block.conflict)

    def on_closing(self, gui):
        print("Do stuff with views manager")

    def gui_block_is_moving(self, gui_id: str,  day, start_time, duration):
        block: Block = self.gui_blocks.get(gui_id,None)
        if block is None:
            return
        self._update_block(block, day, start_time, duration)
        self.gui.colour_block(gui_id, self.resource_type, conflict = block.conflict)

    def _update_block(self, block,  day, start_time, duration):
        block.time_slot.time_start = ScheduleTime(start_time)
        block.time_slot.snap_to_day(day)
        block.time_slot.duration = duration
        block.time_slot.snap_to_time()
        self.schedule.calculate_conflicts()

    def gui_block_has_dropped(self, gui_id: str,  day, start_time, duration):
        block: Block = self.gui_blocks.get(gui_id,None)
        if block is None:
            return
        self._update_block(block, day, start_time, duration)
        self.gui.move_block(gui_id, block.time_slot.day.value,
                            block.time_slot.time_start.hours, block.time_slot.duration)
        for gui_tag, block in self.gui_blocks.items():
            self.gui.colour_block(gui_tag, self.resource_type, conflict = block.conflict)

    def open_companion_view(self, gui_id: str):
        """
        Based on the resource_type of this view, will open another view which has this Block.

        lab/stream -> teacher_ids
        teacher_ids -> stream_ids

        :param self:
        :param gui_id:
        :return:
        """

        resource_type = self.resource_type

        # # in lab or stream, open teacher schedules
        # # no teacher schedules, then open other lab schedules
        #
        # if (resource_type == "lab" or resource_type == ResourceType.Lab) or (resource_type == "stream" or resource_type == ResourceType.Stream):
        #     teachers = guiblock.block.teacher_ids()
        #     if len(teachers) > 0:
        #         self.views_manager.create_view_containing_block(teachers, self.resource_type)
        #     else:
        #         labs = guiblock.block.lab_ids()
        #         if len(labs) > 0:
        #             self.views_manager.create_view_containing_block(labs, 'teacher',
        #                                                             self.schedulable)
        # # ---------------------------------------------------------------
        # # in teacher schedule, open lab schedules
        # # no lab schedules, then open other teacher schedules
        # # ---------------------------------------------------------------
        # elif resource_type == "teacher" or resource_type == ResourceType.Teacher:
        #     labs = guiblock.block.lab_ids()
        #     if len(labs) > 0:
        #         self.views_manager.create_view_containing_block(labs, self.resource_type)
        #     else:
        #         teachers = guiblock.block.teacher_ids()
        #         if len(teachers) > 0:
        #             self.views_manager.create_view_containing_block(teachers, 'lab',
        #                                                             self.schedulable)
        #
