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
from __future__ import annotations
import re
from typing import TYPE_CHECKING

from schedule.Utilities.id_generator import IdGenerator
from schedule.gui_pages.view_dynamic_tk import ViewDynamicTk
from schedule.model import Block, Teacher, Stream, Lab, Schedule, ScheduleTime
from schedule.model.enums import ResourceType
if TYPE_CHECKING:
    from schedule.presenter.view_choices import ViewChoices

_gui_block_ids = IdGenerator()


class View:
    """View - describes the visual representation of a Schedule."""
    def __init__(self, views_controller: ViewChoices, frame, schedule: Schedule, resource: Teacher|Stream|Lab ):
        self.views_controller = views_controller
        self.frame = frame
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
        self.gui: ViewDynamicTk = ViewDynamicTk(self.frame, str(resource),
                                                refresh_blocks_handler=self.redraw,
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

    def _block_to_floats(self, block) -> tuple[int,float,float]:
        return block.time_slot.day.value, block.time_slot.time_start.hours, block.time_slot.duration

    def redraw(self):
        self.gui_blocks.clear()
        for block in self.get_blocks():
            gui_block_id: int = _gui_block_ids.get_new_id()
            gui_tag = f'gui_tag_{gui_block_id}'
            self.gui_blocks[gui_tag]= block
            text = self.get_block_text(block, self.gui.view_canvas.scale.current_scale)
            day, start_time, duration = self._block_to_floats(block)
            self.gui.draw_block(self.resource_type, day, start_time, duration, text, gui_tag, block.movable())
            self.gui.colour_block(gui_tag, self.resource_type, block.movable(), conflict=block.conflict)

    def on_closing(self, gui):
        print("Do stuff with views manager")

    def gui_block_is_moving(self, gui_id: str,  day, start_time, duration):
        block: Block = self.gui_blocks.get(gui_id,None)
        if block is None:
            return
        self._update_block(block, day, start_time, duration)
        self.gui.colour_block(gui_id, self.resource_type, is_movable=block.movable(), conflict = block.conflict)

    def _update_block(self, block,  day, start_time, duration):
        """update the block by snapping to time and day, although it doesn't update the gui block"""

        block.time_slot.time_start = ScheduleTime(start_time)
        block.time_slot.snap_to_day(day)
        block.time_slot.duration = duration
        block.time_slot.snap_to_time()
        self.schedule.calculate_conflicts()
        self.views_controller.notify_block_move(block)

    def gui_block_has_dropped(self, gui_id: str,  day, start_time, duration):
        block: Block = self.gui_blocks.get(gui_id,None)
        if block is None:
            return
        self._update_block(block, day, start_time, duration)

        self.gui.move_block(gui_id, block.time_slot.day.value,
                            block.time_slot.time_start.hours, block.time_slot.duration)

        for gui_tag, block in self.gui_blocks.items():
            self.gui.colour_block(gui_tag, self.resource_type, is_movable=block.movable(), conflict = block.conflict)

    def get_block_text(self, block, scale):
        """Get the text for a specific resource_type of blocks"""

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


        # --------------------------------------------------------------------
        # define what to display
        # --------------------------------------------------------------------
        block_text = f"{course_number}\n{section_number}\n"
        block_text = block_text + teachers_name + "\n" if teachers_name else block_text
        block_text = block_text + lab_numbers + "\n" if lab_numbers else block_text
        block_text = block_text + stream_numbers + "\n" if stream_numbers else block_text

        block_text = block_text.rstrip()
        return block_text



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
