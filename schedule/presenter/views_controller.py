from dataclasses import dataclass
from typing import Callable, Optional, Literal

from schedule.gui_pages.view_choices_tk import ViewChoicesTk
from schedule.model import ResourceType, Schedule, Stream, Teacher, Lab, Block, ScheduleTime
from schedule.presenter.view import View

RESOURCE = Teacher | Lab | Stream

# =====================================================================================================================
# Actions
# =====================================================================================================================

class Action:
    def __init__(self, block: Block, action: Literal['move', 'change_resource'],
            from_day: Optional[float] = None,
            from_time: Optional[float] = None,
            to_day: Optional[float] = None,
            to_time: Optional[float] = None,
            from_resource: Optional[RESOURCE] = None,
            to_resource: Optional[RESOURCE] = None,
            resource_type:Optional[ResourceType] = None,
                 ):
        self.action = action
        self.block = block
        self.to_day = to_day
        self.to_time = to_time
        self.from_day = from_day
        self.from_time = from_time
        self.from_resource = from_resource
        self.to_resource = to_resource
        self.resource_type = resource_type

    def __str__(self):
        if self.action == 'move':
            return f"move {self.block} from {self.from_day} to {self.to_day} and from {self.from_time} to {self.to_time}"
        elif self.action == "change_resource":
            return f"{self.block} change from {self.from_resource} to {self.to_resource}"
        else:
            return "Action with no action"

# =====================================================================================================================
# Views Controller
# =====================================================================================================================
class ViewsController:
    """Controls all of the views and their inter-view communication"""

    # -----------------------------------------------------------------------------------------------------------------
    # init
    # -----------------------------------------------------------------------------------------------------------------
    def __init__(self, dirty_flag_method: Callable[[Optional[bool]], bool], frame, schedule: Schedule):
        """
        :param dirty_flag_method: method used to indicate that data has changed
        :param frame: where the view choices will be displayed
        :param schedule:
        """
        self.dirty_flag_method=dirty_flag_method
        self.frame = frame
        self.schedule = schedule
        self._views: dict[str, View] = {}
        self._undo: list[Action] = []
        self._redo: list[Action] = []


        self.resources = {
            ResourceType.teacher: list(self.schedule.teachers()),
            ResourceType.lab: list(self.schedule.labs()),
            ResourceType.stream: list(self.schedule.streams())
        }

        self.gui = ViewChoicesTk(frame, self.resources, self.call_view)

    # -----------------------------------------------------------------------------------------------------------------
    # refresh
    # -----------------------------------------------------------------------------------------------------------------
    def refresh(self):
        """
        sets the button colours for view choices depending on the most severe conflict for that resource
        """
        self.schedule.calculate_conflicts()
        for resource_type in self.resources:
            for resource in self.resources[resource_type]:
                conflict = self.schedule.resource_conflict(resource)
                conflict = conflict.most_severe(resource_type)
                self.gui.set_button_colour(resource.number, resource_type, conflict)


    # -----------------------------------------------------------------------------------------------------------------
    # call view
    # -----------------------------------------------------------------------------------------------------------------
    def call_view(self, resource):
        """
        creates the view for this resource, or if it already exists, makes it visible
        :param resource:
        """
        if resource.number in self._views:
            self._views[resource.number].gui.raise_to_top()
            return

        self._views[resource.number] = View(self, self.frame, self.schedule, resource)


    # -----------------------------------------------------------------------------------------------------------------
    # notify block move
    # -----------------------------------------------------------------------------------------------------------------
    def notify_block_move(self, resource_number: Optional[str], moved_block: Block, day: float, start_time:float):
        """A block has been moved in a view, so propogate this information to the other views"""

        self.dirty_flag_method(True)
        self.refresh()
        self.schedule.calculate_conflicts()

        # update any view that has the same block that was moved
        for view_id, view in self._views.items():
            if resource_number is None or view_id != resource_number:
                for gui_id, block in view.gui_blocks.items():
                    if block.number == moved_block.number:
                        view.move_gui_block_to(moved_block, day, start_time)
                view.refresh_block_colours()

    # -----------------------------------------------------------------------------------------------------------------
    # save changes to undo db
    # -----------------------------------------------------------------------------------------------------------------
    def add_move_to_undo(self, block: Block, from_day:float, to_day:float, from_time:float, to_time:float):

        # add to undo list
        self._undo.append(Action(block=block, action="move", from_day=from_day, from_time=from_time,
                                 to_day = to_day, to_time = to_time))

    def add_change_resource_to_undo(self, resource_type: ResourceType, block: Block, from_resource, to_resource):

        # add to undo list
        self._undo.append(Action(block=block, action="change_resource",
                                 from_resource=from_resource,
                                 to_resource=to_resource,
                                 resource_type=resource_type))


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

    # ----------------------------------------------------------------------------------------------------------------
    # view is closing
    # ----------------------------------------------------------------------------------------------------------------
    def view_is_closing(self, resource: RESOURCE):
        """view for resource has been closed, update our internal database"""
        try:
            self._views.pop(resource.number)
        except KeyError:
            pass

    # ----------------------------------------------------------------------------------------------------------------
    # move block to a different resource
    # ----------------------------------------------------------------------------------------------------------------
    def move_block_to_resource(self, resource_type: ResourceType, block: Block, from_resource: RESOURCE, to_resource: RESOURCE):
        """
        a block has been moved from one resource to another, update appropriate views, adjust 'undo' and 'redo' appropriately
        :param resource_type:
        :param block:
        :param from_resource:
        :param to_resource:
        """

        # if user has made a change, then we can no longer do 'redo'
        self.remove_all_redoes()

        # update
        self._update_move_block_to_resource(resource_type, block, from_resource, to_resource)

        # add the user change to 'undo'
        self._undo.append(Action(block=block, action="change_resource", resource_type=resource_type,
                                 from_resource=from_resource, to_resource=to_resource))

    def _update_move_block_to_resource(self, resource_type: ResourceType, block: Block, from_resource: RESOURCE, to_resource: RESOURCE):
        """
        a block has been moved from one resource to another, update appropriate views
        :param resource_type:
        :param block:
        :param from_resource:
        :param to_resource:
        """
        match resource_type:
            case ResourceType.teacher:
                print(f"... removing {from_resource} from block")
                print(f"... adding {to_resource} to block")
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

    # ----------------------------------------------------------------------------------------------------------------
    # undo/redo last actions
    # ----------------------------------------------------------------------------------------------------------------
    def undo(self):
        if len(self._undo) == 0:
            return

        action = self._undo.pop()
        print(action)
        self._process_action(action, self._redo)

    def redo(self):
        if len(self._redo) == 0:
            return

        action = self._redo.pop()
        print(action)
        self._process_action(action, self._undo)

    def _process_action(self, action, other_list):
        match action.action:
            case 'move':
                other_list.append(Action(action='move', block= action.block,
                                         from_day = action.to_day, from_time=action.to_time,
                                         to_day = action.from_day, to_time=action.from_time,
                                         ))
                action.block.time_slot.time_start = ScheduleTime(action.from_time)
                action.block.time_slot.snap_to_day(action.from_day)
                self.schedule.calculate_conflicts()
                self.notify_block_move(None, action.block, action.from_day, action.from_time)
            case 'change_resource':
                other_list.append(Action(action='change_resource', block=action.block,
                                         from_resource=action.to_resource,
                                         to_resource=action.from_resource,
                                         resource_type=action.resource_type,
                                  ))
                self.schedule.calculate_conflicts()
                self._update_move_block_to_resource(resource_type=action.resource_type, block=action.block,
                                                    from_resource=action.to_resource,
                                                    to_resource=action.from_resource)


    def remove_all_redoes(self):
        self._redo.clear()

"""
        # ------------------------------------------------------------------------
        # get_by_id the undo/redo
        # ------------------------------------------------------------------------
        action = None
        if type == 'undo':
            undoes: list = self.undoes()
            action = undoes.pop() if undoes else None
        else:
            redoes: list = self.redoes()
            action = redoes.pop() if redoes else None

        if not action:
            return

        # ------------------------------------------------------------------------
        # process action
        # ------------------------------------------------------------------------

        if action.move_type == "Day/Time":
            obj = action.origin_obj
            block: Block = self._find_block_to_apply_undo_redo(action, obj)

            # --------------------------------------------------------------------
            # make new undo/redo object as necessary
            # --------------------------------------------------------------------
            redo_or_undo = Undo(block.number, block.time_start, block.day, action.origin_obj,
                                action.move_type, None)
            if type == 'undo':
                self.add_redo(redo_or_undo)
                self.remove_last_undo()
            else:
                self.add_undo(redo_or_undo)
                self.remove_last_redo()

            # --------------------------------------------------------------------
            # perform local undo/redo
            # --------------------------------------------------------------------
            block.time_start = action.origin_start
            block.day = action.origin_day

            # update all views to re-place blocks.
            self.redraw_all_views()

        # ------------------------------------------------------------------------
        # moved a teacher from one course to another, or moved blocks from
        # one lab to a different lab
        # ------------------------------------------------------------------------
        else:
            original_obj = action.origin_obj
            target_obj = action.new_obj
            block: Block = self._find_block_to_apply_undo_redo(action, target_obj)

            # --------------------------------------------------------------------
            # make new undo/redo object as necessary
            # --------------------------------------------------------------------
            redo_or_undo = Undo(block.number, block.time_start, block.day, action.new_obj,
                                action.move_type, action.origin_obj)
            if type == 'undo':
                self.add_redo(redo_or_undo)
                self.remove_last_undo()
            else:
                self.add_undo(redo_or_undo)
                self.remove_last_redo()

            # reassign teacher/lab to blocks.
            if action.move_type == 'teacher':
                block.remove_teacher_by_id(target_obj)
                block.assign_teacher_by_id(original_obj)
                block.section.remove_teacher_by_id(target_obj)
                block.section.assign_teacher_by_id(original_obj)
            elif action.move_type == 'lab':
                block.remove_lab_by_id(target_obj)
                block.assign_lab_by_id(original_obj)

            # Update all views to re-place the blocks.
            self.redraw_all_views()

    def _find_block_to_apply_undo_redo(self, action, obj) -> Block:
        block: Block
        blocks = self.schedule.get_blocks_for_obj(obj)
        for b in blocks:
            if b.id == action.block_id:
                block = b
                return block

    def add_undo(self, undo: Undo):
        self._undoes.append(undo)
        return self

    def add_redo(self, redo: Undo):
        self._redoes.append(redo)
        return self

    def remove_last_undo(self):
        # NOTE: In Perl, popping an empty list just returns undef.
        # In Python, trying to pop an empty list throws an IndexError.
        if self._undoes:
            self._undoes.pop()

    def remove_last_redo(self):
        if self._redoes:
            self._redoes.pop()

    def remove_all_undoes(self):
        self._undoes.clear()
        return self

    def remove_all_redoes(self):
        self._redoes.clear()
        return self

"""