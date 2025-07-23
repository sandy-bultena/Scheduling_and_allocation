from typing import Callable, Optional

from schedule.gui_pages.view_choices_tk import ViewChoicesTk
from schedule.model import ResourceType, Schedule, Stream, Teacher, Lab, Block
from schedule.presenter.view import View

RESOURCE = Teacher | Lab | Stream

class ViewChoices:
    def __init__(self, dirty_flag_method: Callable[[Optional[bool]], bool], frame, schedule: Schedule):
        self.dirty_flag_method=dirty_flag_method
        self.frame = frame
        self.schedule = schedule
        self._views: dict[str, View] = {}


        self.resources = {
            ResourceType.teacher: list(self.schedule.teachers()),
            ResourceType.lab: list(self.schedule.labs()),
            ResourceType.stream: list(self.schedule.streams())
        }

        self.gui = ViewChoicesTk(frame, self.resources, self.call_view)

    def refresh(self):
        self.schedule.calculate_conflicts()
        for resource_type in self.resources:
            for resource in self.resources[resource_type]:
                conflict = self.schedule.resource_conflict(resource)
                conflict = conflict.most_severe(resource_type)
                self.gui.set_button_colour(resource.number, resource_type, conflict)


    def call_view(self, resource):
        if resource.number in self._views:
            self._views[resource.number].gui.raise_to_top()
            return

        self._views[resource.number] = View(self, self.frame, self.schedule, resource)

    def notify_block_move(self, resource_number, moved_block, day, start_time):
        self.dirty_flag_method(True)
        self.refresh()
        for view_id, view in self._views.items():
            if view_id != resource_number:
                for gui_id, block in view.gui_blocks.items():
                    if block.number == moved_block.number:
                        view.move_gui_block_to(moved_block, day, start_time)
                view.refresh_block_colours()

    # ----------------------------------------------------------------------------------------------------------------
    # open companion view (double_click_handler)
    # ----------------------------------------------------------------------------------------------------------------
    def open_companion_view(self, block: Block):
        """
        Based on the resource_type open other views which have this Block.
        :param block:
        """
        teachers = block.teachers()
        labs = block.labs()
        streams = block.streams()

        for resource in (*teachers, *labs, *streams):
            self.call_view(resource)

    def view_is_closing(self, resource: RESOURCE):
        try:
            self._views.pop(resource.number)
        except KeyError:
            pass

    def move_block_to_resource(self, resource_type: ResourceType, block: Block, from_resource: RESOURCE, to_resource: RESOURCE):
        match resource_type:
            case ResourceType.teacher:
                block.remove_teacher(from_resource)
                block.add_teacher(to_resource)
            case ResourceType.lab:
                block.remove_lab(from_resource)
                block.add_lab(to_resource)
        self.schedule.calculate_conflicts()
        self.dirty_flag_method(True)

        if from_resource.number in self._views.keys():
            self._views[from_resource.number].draw()
        else:
            self.call_view(from_resource)

        if to_resource.number in self._views.keys():
            self._views[to_resource.number].draw()
        else:
            self.call_view(to_resource)
