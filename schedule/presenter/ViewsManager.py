# IN PROGRESS
"""ViewsManager - Manage all of the views (presentations of schedules)"""
from .View import View
from ..gui_pages.ViewsManagerTk import ViewsManagerTk
from ..model.Block import Block
from ..model.conflicts import Conflict
from ..model.schedule import Schedule
from ..model.ScheduleEnums import ConflictType, ResourceType
from ..model.undo import Undo
from ..Utilities.AllResources import AllResources


class ViewsManager:
    """This class creates a button interface to access all of the schedule views,
    and it manages those views.

    Manages all the 'undo' and 'redo' of actions taken upon the views."""

    # =================================================================
    # Class Variables
    # =================================================================
    max_id = 0

    # =================================================================
    # new
    # =================================================================
    def __init__(self, gui_main, dirty_flag_ptr, schedule: Schedule):
        """Creates a ViewsManager object.

        Parameters:
            gui_main: The gui that is used by whatever class invokes this class, because we need to know the main_window etc.
            dirty_flag_ptr: Pointer to a flag that indicates if the schedule has been changed since the last save.
            schedule: Where course-sections/teacher_ids/lab_ids/stream_ids are defined."""
        gui = ViewsManagerTk(gui_main)
        self.gui = gui
        self.gui_main = gui_main
        ViewsManager.max_id += 1
        self._id = ViewsManager.max_id
        self.dirty_flag = dirty_flag_ptr  # NOTE: Replace this w/ call to the globals object?
        self.schedule = schedule
        self._undoes: list[Undo] = []
        self._redoes: list[Undo] = []
        self._views: dict[int, View] = {}

    # =================================================================
    # getters/setters
    # =================================================================
    @property
    def id(self):
        """Returns the unique ID for this ViewsManager object."""
        return self._id

    def set_dirty(self):
        self.dirty_flag = True

    # =================================================================
    # Undo and redo
    # =================================================================
    def undoes(self):
        """Gets the Undo objects of this ViewsManager object."""
        return self._undoes

    def redoes(self):
        """Gets the Redoes of this ViewsManager object."""
        return self._redoes

    def undo(self, type: str):
        """Undo or Redo the last action.

        Parameters:
            type: 'undo' or 'redo'.
            """
        # NOTE: The parameter title in the Perl code, previously transcribed above,
        # is misleading.

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
        """Add an Undo to the list of Undoes for this ViewsManager object.

        Returns the modified ViewsManager object."""
        self._undoes.append(undo)
        return self

    def add_redo(self, redo: Undo):
        """Adds a Redo to the list of Redoes for this ViewsManager object.

        Returns the modified ViewsManager object."""
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
        """Removes all Undoes associated with this ViewsManager object.

        Returns the modified ViewsManager object."""
        self._undoes.clear()
        return self

    def remove_all_redoes(self):
        """Removes all Redoes associated with this ViewsManager object.

        Returns the modified ViewsManager object."""
        self._redoes.clear()
        return self

    # ============================================================================
    # house keeping
    # ============================================================================
    def add_manager_to_views(self):
        """Makes sure that the views have access to the ViewsManager."""
        open_views = self.views()
        for view in open_views.values():
            view.views_manager = self

    # =================================================================
    # keeping track of the views
    # =================================================================
    def close_view(self, view: View):
        """Close the gui window, and remove the view from the list of 'open' views.

        Parameters:
            view: The view to close and remove."""
        view.close()
        del self._views[view.id]
        return self

    def destroy_all(self):
        """Closes all open views."""
        open_views = self.views()

        for view in open_views.values():
            self.close_view(view)
        self.remove_all_undoes()
        self.remove_all_redoes()

    def is_open(self, id: int, type):
        """Checks if the View corresponding to the button pressed by the user is open.

        Parameters:
            id: The ID of the view that you want to check on.
            type: The resource_type of view that you want to check.

        Returns:
            The View object if the View is open, False otherwise."""
        open_views: dict = self.views()
        for view in open_views.values():
            if view.type == type:
                if view.schedulable.number == id:
                    return view

        return False

    def views(self):
        """Get the Views of this ViewsManager object."""
        return self._views

    def add_view(self, view: View):
        """Add a View to the list of Views for this ViewsManager object.

        Parameters:
            view: The View to be added."""
        self._views[view.id] = view
        return self

    # =================================================================
    # update the views
    # =================================================================
    def update_all_views(self, block: Block):
        """Updates the position of the current moving GuiBlock across all open Views.

        Parameters:
            block: the blocks object."""
        open_views = self.views()

        # Go through all currently open views.
        for view in open_views.values():
            # update the GuiBlocks on the view.
            view.update(block)

    def redraw_all_views(self):
        """Redraw all open views with new GuiBlocks, if any."""
        open_views = self.views()

        for view in open_views.values():
            view.redraw()

    def update_for_conflicts(self):
        """Goes through all open Views and updates their GuiBlocks for any new Conflicts."""
        open_views = self.views()

        for view in open_views.values():
            view.update_for_conflicts(view.type)

    def get_all_scheduables(self):
        """Gets a list of all schedulable objects and organizes them by resource_type (teacher/lab/stream).
        Contains a list of the schedulable objects, the names to be displayed in the GUI_Pages, etc.

        Returns:
            An array of ScheduablesByType."""
        return AllResources(self.schedule)

    def determine_button_colours(self, all_view_choices=None):
        """Finds the highest conflict for each teacher/lab/stream in the array and sets the
        Colour of the button accordingly. """
        if not all_view_choices:
            all_view_choices = self.get_all_scheduables()

        for type in all_view_choices.valid_types():
            scheduable_objs = all_view_choices.by_type(type).scheduable_objs

            # Calculate conflicts.
            self.schedule.calculate_conflicts()

            # blocks = []

            # For every teacher, lab, stream schedule
            for scheduable_obj in scheduable_objs:
                blocks = self.schedule.get_blocks_for_obj(scheduable_obj)

                # What is this view's conflict? Start with 0.
                view_conflict: ConflictType | int = 0

                # for every blocks...
                for block in blocks:
                    # NOTE: ConflictTypes cannot be compared with integers.
                    # If Conflict.most_severe() returns a ConflictType object,
                    # use its value instead.
                    if isinstance(view_conflict, ConflictType):
                        view_conflict = view_conflict.value
                    # NOTE: Conflict.most_severe() may return None if no conflicts were found. In
                    # such a case, change view_conflict to 0, as NoneType can't be compared with
                    # integers either.
                    if view_conflict is None:
                        view_conflict = 0
                    view_conflict = Conflict.most_severe(view_conflict | block.conflicted_number,
                                                         type)
                    if view_conflict == Conflict._sorted_conflicts[0]:
                        break

                self.gui.set_button_colour(scheduable_obj, view_conflict)

    # =================================================================
    # callbacks used by View objects
    # =================================================================
    def create_view_containing_block(self, schedulable_objs, type: ResourceType | str, ob: Block = None):
        """Used as a callback function for View objects.

        Find a scheduable object(s) in the given list. If the given blocks object is also part of
        that specific schedule, then create a new view.

        Parameters:
            schedulable_objs: A list of objects (teacher_ids/lab_ids/stream_ids) where a schedule can be created for them, and so a view is created for each of these objects.
            type: Type of view to draw (teacher/lab/stream).
            ob: Block object."""
        obj_id = ob.id if ob is not None else None

        # Note: The original Perl code had a to-do in the title that went like this:
        # TODO: Clarify what the hell this is doing, once we are working on the View.pm file
        # I'm beginning to see why.

        if type == 'teacher' or type == ResourceType.Teacher:
            type = ResourceType.Lab
        else:
            type = ResourceType.Teacher

        for scheduable_obj in schedulable_objs:
            if not (obj_id and obj_id == scheduable_obj.number):
                self.create_new_view(None, scheduable_obj, type)

    def create_new_view(self, undef, scheduable_obj, type):
        """Creates a new View for the selected Teacher, Lab, or Stream, depending on the
        scheduable object.

        If the View is already open, the View for that object is brought to the front.

        Parameters:
            undef: Set None as the first parameter, since this is an unnecessary parameter due to it being a callback function(?)
            scheduable_obj: An object that can have a schedule (teacher/lab/stream).
            type: Type of view to show (teacher/lab/stream)."""
        open_view: View | False = self.is_open(scheduable_obj.number, type)

        if not open_view:
            view = View(self, self.gui.mw, self.schedule, scheduable_obj)
            self.add_view(view)
            self.add_manager_to_views()
        else:
            # NOTE: Someone left this to-do in the Perl code:
            # TODO: Should have a View method for this instead of View->gui.
            open_view: View
            open_view.gui._toplevel.lift()
            open_view.gui._toplevel.focus()

    def get_create_new_view_callback(self, *args):
        """Creates a callback function from create_new_view that includes this object as the
        first parameter.
        Returns:
            The new callback function."""

        def dummy(*args):
            self.create_new_view(*args)

        return dummy


# =================================================================
# footer
# =================================================================
"""
=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns

Translated to Python by Evan Laverdiere

=head1 COPYRIGHT

Copyright (c) 2016, Jack Burns, Sandy Bultena, Ian Clement. 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut

1;


"""
