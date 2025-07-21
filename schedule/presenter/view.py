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
from schedule.model import Block, Teacher, Stream, Lab, Schedule
from schedule.model.enums import WeekDay, ResourceType
from schedule.presenter.gui_block import GuiBlock


class View:
    """View - describes the visual representation of a Schedule."""
    def __init__(self, mw, schedule: Schedule, resource: Teacher|Stream|Lab ):
        self.mw = mw
        self.resource = resource
        self.schedule = schedule
        self.gui_blocks = {}

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
                                                refresh_blocks_handler=self.event_redraw)
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
        self.gui.draw_view_canvas()

    def event_redraw(self, gui_view):
        self.gui_blocks.clear()
        self.gui = gui_view
        for block in self.get_blocks():
            gui_block = GuiBlock(block, self.resource_type)
            self.gui_blocks[gui_block.gui_tag]= block
            text = gui_block.get_block_text(self.gui.view_canvas.scale.current_scale)
            self.gui.draw_block(self.resource_type, gui_block.day, gui_block.start_time, gui_block.duration, text, gui_block.gui_tag)


