from tkinter import Tk

from .AssignToResource import AssignToResource
from ..Export import DrawView
from ..GUI.GuiBlockTk import GuiBlockTk
from ..GUI.ViewTk import ViewTk
from ..Schedule.Block import Block
from ..Schedule.Conflict import Conflict
from ..Schedule.Lab import Lab
from ..Schedule.Schedule import Schedule
from ..Schedule.ScheduleEnums import ConflictType, ViewType
from ..Schedule.Stream import Stream
from ..Schedule.Teacher import Teacher
from ..Schedule.Undo import Undo
from ..PerlLib import Colour
from ..UsefulClasses.AllScheduables import AllScheduables


class View:
    """View - describes the visual representation of a Schedule."""

    # =================================================================
    # global and package variables
    # =================================================================
    undo_number = ""
    redo_number = ""
    clicked_block = 0
    days = DrawView.days
    times = DrawView.times
    earliest_time = min(times.keys())
    latest_time = max(times.keys())
    max_id = 0

    # =================================================================
    # getters/setters
    # =================================================================
    # TODO: Decide which of these to keep, beyond id and gui_blocks.
    @property
    def schedule(self) -> Schedule:
        """Get/Set the schedule object."""
        return self._schedule

    @schedule.setter
    def schedule(self, value: Schedule):
        self._schedule = value

    @property
    def gui(self) -> ViewTk:
        """Returns the GUI object for this view."""
        return self._gui

    @gui.setter
    def gui(self, value: ViewTk):
        self._gui = value

    @property
    def id(self) -> int:
        """Returns the unique ID for this View object."""
        return self._id

    @property
    def schedulable(self) -> Teacher | Lab | Stream:
        """Gets/Sets the Teacher, Lab, or Stream associated to this View."""
        return self._obj

    @schedulable.setter
    def schedulable(self, value: Teacher | Lab | Stream):
        self._obj = value

    @property
    def type(self):
        """Gets/Sets the type of this View object."""
        return self._type

    @type.setter
    def type(self, value: str):
        self._type = value

    @property
    def blocks(self) -> list[Block]:
        """Gets/Sets the Blocks of this View object. An array."""
        return self._blocks

    @blocks.setter
    def blocks(self, value: list[Block]):
        self._blocks = value

    @property
    def gui_blocks(self) -> dict[int, GuiBlockTk]:
        """Gets the GuiBlocks of this View object."""
        return self._gui_blocks

    @property
    def views_manager(self):
        """Gets/Sets the ViewsManager of this View object."""
        return self._views_manager

    @views_manager.setter
    def views_manager(self, value):
        self._views_manager = value

    # region PUBLIC METHODS

    # =================================================================
    # new
    # =================================================================

    def __init__(self, views_manager, mw: Tk, schedule: Schedule,
                 schedulable_object: Teacher | Lab | Stream):
        """Creates a View object, draws the necessary GuiBlocks, and returns the View object.

        Parameters:
            views_manager: The ViewsManager object responsible for keeping track of all the views.
            mw: Tk main window.
            schedule: Where course/sections/teachers/labs/streams are defined.
            schedulable_object: Teacher/Lab/Stream that the View is being made for."""
        View.max_id += 1
        self._id = View.max_id
        conflict_info = self._get_conflict_info()

        # ---------------------------------------------------------------
        # create the Gui
        # ---------------------------------------------------------------
        gui = ViewTk(self, mw, conflict_info)

        # ---------------------------------------------------------------
        # this is what needs to be done to close the window
        # ---------------------------------------------------------------
        gui.on_closing = self._cb_close_view

        # ---------------------------------------------------------------
        # type of view depends on which object it is for
        # ---------------------------------------------------------------
        blocks = schedule.get_blocks_for_obj(schedulable_object)
        type = schedule.get_view_type_of_object(schedulable_object)

        # ---------------------------------------------------------------
        # save some parameters
        # ---------------------------------------------------------------
        self.gui = gui
        self.views_manager = views_manager
        self.blocks = blocks
        self.schedule = schedule
        self.type = type
        self.schedulable = schedulable_object
        self._gui_blocks = {}

        # ---------------------------------------------------------------
        # set the title
        # ---------------------------------------------------------------
        title = ""
        if schedulable_object and isinstance(schedulable_object, Teacher):
            self.gui.set_title(schedulable_object.firstname[0:1].upper()
                               + " " + schedulable_object.lastname)
        elif schedulable_object:
            self.gui.set_title(schedulable_object.number)

        # --------------------------------------------------------------
        # popup menu for guiblocks
        # ---------------------------------------------------------------
        named_schedulable_objects = self._get_named_schedulable_for_popup(type)
        self.gui.setup_popup_menu(self.type, named_schedulable_objects, self._cb_toggle_movement,
                                  self._cb_move_block_between_schedulable_objects)

        # ---------------------------------------------------------------
        # undo/redo
        # ---------------------------------------------------------------
        self.gui.setup_undo_redo(View.undo_number, View.redo_number, View._cb_undo_redo)

        # ---------------------------------------------------------------
        # refresh drawing - redrawing creates the guiblocks
        # ---------------------------------------------------------------
        self.redraw()
        self.schedule.calculate_conflicts()
        self.update_for_conflicts(self.type)

    def redraw(self):
        """Redraws the View with new GuiBlocks and their positions."""
        schedule = self.schedule

        # ---------------------------------------------------------------
        # draw the background, date/time stuff, etc
        # ---------------------------------------------------------------
        self.gui.redraw()

        # ---------------------------------------------------------------
        # create and draw the gui blocks
        # ---------------------------------------------------------------

        # Get blocks for this object.
        blocks = schedule.get_blocks_for_obj(self.schedulable)

        # Remove all GuiBlocks stored in the View.
        self._remove_all_guiblocks()

        # redraw all GuiBlocks.
        for b in blocks:
            # This makes sure that synced blocks have the same start time.
            b.start = b.start
            b.day = b.day

            gui_block = GuiBlockTk(self.type, self.gui, b)

            self.gui.bind_popup_menu(gui_block)
            self._add_guiblock(gui_block)

        self.blocks = blocks
        schedule.calculate_conflicts()
        self.update_for_conflicts(self.type)

        # ---------------------------------------------------------------
        # If this is a lab or teacher view, then add 'AssignBlocks'
        # to the view, and bind as necessary
        # ---------------------------------------------------------------
        self._setup_for_assignable_blocks()

        # ---------------------------------------------------------------
        # set colour for all buttons on main window, "Schedules" tab
        # ---------------------------------------------------------------
        self._set_view_button_colours()
        if self.views_manager:
            self.views_manager.update_for_conflicts()

        # ---------------------------------------------------------------
        # bind events for each gui block
        # ---------------------------------------------------------------
        gbs = self.gui_blocks
        for guiblock in gbs.values():
            block: Block = guiblock.block

            # Bind to allow block to move if clicked and dragged.
            if block.movable:
                self.gui.set_bindings_for_dragging_guiblocks(self, guiblock,
                                                             self._cb_guiblock_is_moving,
                                                             self._cb_guiblock_has_stopped_moving,
                                                             self.cb_update_after_moving_block)

            # double click opens companion views.
            self.gui.bind_double_click(self, guiblock, self._cb_open_companion_view)

    # =================================================================
    # update
    # =================================================================
    def update(self, block: Block):
        """Updates the position of any GuiBlocks that have the same Block as the currently
        moving GuiBlock.

        Parameters:
            block: The Block object that has been modified."""
        # Go through each GuiBlock on the view.
        if hasattr(self, '_gui_blocks'):
            for guiblock in self.gui_blocks.values():
                # Race condition, no need to update the current moving block.
                if guiblock.is_controlled:
                    continue

                # GuiBlock's block is the same as the moving block?
                if guiblock.block.id == block.id:
                    self.gui.move_block(guiblock)
                    self.gui.canvas.update_idletasks()

    def update_for_conflicts(self, type):
        """Determines conflict status for all GuiBlocks on this view and colours them
        accordingly.

        Parameters:
            type: The type of the View. Can be "Teacher", "Lab" or "Stream".
        """
        guiblocks = self.gui_blocks

        view_conflict = 0

        # For every guiblock in this view,
        for guiblock in guiblocks.values():
            self.gui.colour_block(guiblock, type)

            # Colour block by conflict only if it is movable.
            if guiblock.block.movable:
                # Create conflict number for the entire View.
                view_conflict = view_conflict | guiblock.block.conflicted

        return view_conflict

    def close(self):
        """Close the view."""
        self.gui.destroy()

    # endregion

    # region CALLBACKS

    # =================================================================
    # Callbacks (event handlers)
    # =================================================================
    # TODO: Consider making these callback methods static.
    def _cb_close_view(self):
        """When the View is closed, need to let views_manager know.

        Handles Event: View is closed via the gui interface."""
        views_manager = self.views_manager
        views_manager.close_view(self)

    @staticmethod
    def _cb_undo_redo(self, type: str):
        """Lets the views_manager manage the undo/redo action.

        Parameters:
            type: string, either 'undo' or 'redo'."""
        self: View
        self.views_manager.undo(type)

        # Set colour for all buttons on main window, "Schedules" tab.
        self._set_view_button_colours()

        # Update status bar.
        self._set_status_undo_info()

    @staticmethod
    def _cb_assign_blocks(self, chosen_blocks: list, undef=None):
        """Give the option of assigning these blocks to a resource (add to course, assign block to
        teacher/lab/stream).

        Handles Event: AssignBlock objects have been selected.

        Parameters:
            chosen_blocks: Array of AssignBlocks that have been selected by the user."""

        # Get the day and time of the chosen blocks.
        from ..GUI.AssignBlockTk import AssignBlockTk
        (day, start, duration) = AssignBlockTk.get_day_start_duration(chosen_blocks)

        # Create the menu to select the block to assign to the timeslot.
        AssignToResource(self.gui.mw, self.schedule, day, start, duration, self.schedulable)

        # Redraw.
        self.redraw()

    def _cb_toggle_movement(self):
        """Toggles whether a GuiBlock is movable or not.

        Handles Event: The toggle movable/unmovable on the popup menu has been clicked."""
        # Get the block that was right-clicked.
        if not self.gui.popup_guiblock:
            return
        block = self.gui.popup_guiblock.block

        # Toggle movability.
        if block.movable:
            block.movable = False
        else:
            block.movable = True

        # Redraw, and set the dirty flag.
        self.views_manager.redraw_all_views()
        views_manager = self.views_manager
        if views_manager:
            self.views_manager.set_dirty(views_manager.dirty_flag)

    def _cb_move_block_between_schedulable_objects(self, that_schedulable: Teacher | Lab | Stream):
        """Moves the selected class(es) from the original Views Teacher/Lab to the Teacher/Lab
        object.

        Handles Event: The user has selected to move a block between one selectable object and another
        via the popup menu.

        Parameters:
            that_schedulable: Target destination of the block."""
        this_schedulable = self.schedulable

        # Get the GuiBlock that the popup_menu was invoked on.
        guiblock = self.gui.popup_guiblock

        # Reassign teacher/lab to blocks.
        if self.type == "teacher":
            guiblock.block.remove_teacher(this_schedulable)
            guiblock.block.assign_teacher(that_schedulable)
            guiblock.block.section.remove_teacher(this_schedulable)
            guiblock.block.section.assign_teacher(that_schedulable)
        elif self.type == "lab":
            guiblock.block.remove_lab(this_schedulable)
            guiblock.block.assign_lab(that_schedulable)
        elif self.type == "stream":
            guiblock.block.section.remove_stream(this_schedulable)
            guiblock.block.section.assign_stream(that_schedulable)

        # There was a change, so redraw all the views.
        undo = Undo(guiblock.block.id, guiblock.block.start, guiblock.block.day,
                    self.schedulable, self.type, that_schedulable)
        self.views_manager.add_undo(undo)

        # New move, so reset redo.
        self.views_manager.remove_all_redoes()

        # Update the status bar.
        self._set_status_undo_info()

        # Set the dirty flag, and redraw.
        self.views_manager.set_dirty()
        self.views_manager.redraw_all_views()

    def _cb_guiblock_is_moving(self, guiblock: GuiBlockTk):
        """Need to update all Views.

        Handles Event: A guiblock is being dragged about by the user.

        Parameters:
            guiblock: GuiBlock that is moving."""
        # update same block on different views.
        block = guiblock.block
        views_manager = self.views_manager
        views_manager.update_all_views(block)

        # Is current block conflicting?
        self.schedule.calculate_conflicts()
        self.gui.colour_block(guiblock, self.type)

    @staticmethod
    def _cb_open_companion_view(self, guiblock: GuiBlockTk):
        """Based on the type of this view, will open another view which has this Block.

        lab/stream -> teachers
        teachers -> streams

        Handles Event: double-clicking on a guiblock.

        Parameters:
            guiblock: The GuiBlock that was double-clicked."""
        self: View
        type = self.type

        # NOTE: Sandy, or someone else, prefaced this in the original code with "TODO: WTF?"
        # Make of that what you will.
        # ---------------------------------------------------------------
        # in lab or stream, open teacher schedules
        # no teacher schedules, then open other lab schedules
        # ---------------------------------------------------------------
        if (type == "lab" or type == ViewType.Lab) or (type == "stream" or type == ViewType.Stream):
            teachers = guiblock.block.teachers()
            if len(teachers) > 0:
                self.views_manager.create_view_containing_block(teachers, self.type)
            else:
                labs = guiblock.block.labs()
                if len(labs) > 0:
                    self.views_manager.create_view_containing_block(labs, 'teacher',
                                                                    self.schedulable)
        # ---------------------------------------------------------------
        # in teacher schedule, open lab schedules
        # no lab schedules, then open other teacher schedules
        # ---------------------------------------------------------------
        elif type == "teacher" or type == ViewType.Teacher:
            labs = guiblock.block.labs()
            if len(labs) > 0:
                self.views_manager.create_view_containing_block(labs, self.type)
            else:
                teachers = guiblock.block.teachers()
                if len(teachers) > 0:
                    self.views_manager.create_view_containing_block(teachers, 'lab',
                                                                    self.schedulable)

    @staticmethod
    def _cb_guiblock_has_stopped_moving(self, guiblock: GuiBlockTk):
        """Ensures that the GuiBlock is snapped to an appropriate location (i.e., start/end times
        must be on the hour or half-hour).

        Updates undo/redo appropriately.

        Handles Event: A GuiBlock has been placed into a new location.

        Parameters:
            guiblock: GuiBlock that has been moved."""
        self: View
        undo = Undo(guiblock.block.id, guiblock.block.start, guiblock.block.day,
                    self.schedulable, "Day/Time", self.schedulable)

        # Set guiblock's to new time and day.
        self._snap_gui_block(guiblock)

        # Don't create undo if it was moved to the starting position.
        if undo.origin_start != guiblock.block.start or undo.origin_day != guiblock.block.day:
            # Add change to undo.
            self.views_manager.add_undo(undo)

            # New move, so reset redo.
            self.views_manager.remove_all_redoes()

            # Update the status bar.
            self._set_status_undo_info()

    @staticmethod
    def cb_update_after_moving_block(self, block: Block):
        """Update all views, calculate conflicts and set button colours, and set the dirty flag.

        Handles Event: For when a GuiBlock has been dropped, and now it is time to refresh
        everything.
        Parameters:
            block: The block that has been modified by moving a GuiBlock around."""
        self: View
        # update all the views that have the block just moved to its new position. NOTE: ???
        views_manager = self.views_manager
        views_manager.update_all_views(block)

        # Calculate new conflicts and update other views to show these conflicts.
        self.schedule.calculate_conflicts()
        views_manager.update_for_conflicts()
        views_manager.set_dirty()

        # Set colour for all buttons on main window, "Schedules" tab.
        self._set_view_button_colours()

        pass

    # endregion

    # region PRIVATE METHODS
    def _add_guiblock(self, gui_block: GuiBlockTk):
        """Adds the GuiBlock to the list of GuiBlocks on the View. Returns the View object.
        Parameters:
            gui_block: The GuiBlock to be added."""
        # Save.
        self._gui_blocks[gui_block.id] = gui_block
        return self

    def _remove_all_guiblocks(self):
        """Remove all GuiBlocks associated with this View."""
        self._gui_blocks.clear()

    def _setup_for_assignable_blocks(self):
        """Find all 1/2 blocks and turn them into AssignBlocks."""
        type = self.type

        # Don't do this for 'stream' types.
        if type == "stream" or type == ViewType.Stream:
            return

        # Loop through each half hour time slot, and create and draw AssignBlock for each.
        from ..GUI.AssignBlockTk import AssignBlockTk
        assignable_blocks: list[AssignBlockTk] = []
        for day in range(1, 6):
            for start in range(View.earliest_time * 2, View.latest_time * 2):
                assignable_blocks.append(AssignBlockTk(self, day, start / 2))

        self.gui.setup_assign_blocks(assignable_blocks, self._cb_assign_blocks)

    def _get_conflict_info(self) -> list[dict[str, str]]:
        """What types of conflicts are there? What colours should they be?"""
        conflict_info = []
        for c in (ConflictType.TIME_TEACHER, ConflictType.TIME, ConflictType.LUNCH,
                  ConflictType.MINIMUM_DAYS, ConflictType.AVAILABILITY):
            bg = Conflict.colours()[c]
            fg = "white"
            if Colour.is_light(bg):
                fg = "black"
            text = Conflict.get_description(c)
            conflict_info.append({
                "bg": Colour.string(bg),
                "fg": Colour.string(fg),
                "text": text
            })
        return conflict_info

    def _get_named_schedulable_for_popup(self, type):
        """For this view, find all schedulable objects that are the same type as this view,
        but not including the schedulable associated with this view.

        Parameters:
            type: Type of schedulable object (Teacher/Lab/Stream).

        Returns:
            Array of named objects, with the object being a Teacher/Lab/Stream."""
        # Get all schedulables.
        all_schedulables = AllScheduables(self.schedule)

        # Get only the schedulables that match the type of this view.
        schedulables_by_type = all_schedulables.by_type(type)

        # remove the schedulable object that is associated with this view.
        named_schedulable_objects = [o for o in schedulables_by_type.named_scheduable_objs
                                     if o.object.id != self.schedulable.id]

        return named_schedulable_objects

    def _set_view_button_colours(self):
        """In the main window, in the schedules tab, there are buttons that are used to call up the
        various Schedule Views.

        This function will colour those buttons according to the maximum conflict for that given
        view."""
        if self.views_manager:
            self.views_manager.determine_button_colours()

    def _set_status_undo_info(self):
        View.undo_number = f"{len(self.views_manager.undoes())} undoes left"

        View.redo_number = f"{len(self.views_manager.redoes())} redoes left"

    def _snap_gui_block(self, guiblock: GuiBlockTk):
        """Takes the GuiBlock and forces it to be located on the nearest day and 1/2 boundary.

        Parameters:
            guiblock: GuiBlock that is being moved."""
        guiblock.block.snap_to_day(1, len(View.days))
        guiblock.block.snap_to_time(min(View.times.keys()), max(View.times.keys()))

    # endregion


"""
=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns - 2016

Sandy Bultena 2020

Rewritten for Python by Evan Laverdiere - 2023

Updat

=head1 COPYRIGHT

Copyright (c) 2016, Jack Burns, Sandy Bultena, Ian Clement.

Copyright (c) 2021, Sandy Bultena 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut

1;

"""
