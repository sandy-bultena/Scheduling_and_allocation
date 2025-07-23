from tkinter import Frame

from schedule.gui_pages.view_choices_tk import ViewChoicesTk
from schedule.model import ResourceType, Schedule, ConflictType, Stream, Teacher, Lab
from schedule.presenter.view import View

RESOURCE = Teacher | Lab | Stream

class ViewChoices:
    def __init__(self, frame, schedule: Schedule):
        self.frame = frame
        self.schedule = schedule
        self._views: dict[RESOURCE, View] = {}


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
        view = View(self, self.frame, self.schedule, resource)
        self._views[resource.number] = view


    #
    #     #     global views_manager, gui
    #     #     btn_callback = views_manager.get_create_new_view_callback
    #     #     all_view_choices = views_manager.get_all_scheduables()
    #     #     page_name = pages_lookup['Schedules'].name
    #     #     gui.draw_view_choices(page_name, all_view_choices, btn_callback)
    #     #
    #     #     views_manager.determine_button_colours()
    #

    def notify_block_move(self, block):
        self.refresh()