from __future__ import annotations
from functools import partial
from tkinter import *
from tkinter import ttk
from typing import Callable, TYPE_CHECKING

from .AssignBlockTk import AssignBlockTk
from .ViewBaseTk import ViewBaseTk

if TYPE_CHECKING:
    from .GuiBlockTk import GuiBlockTk

global mw
global clicked_block
global select_colour
global selected_assign_block_completed_cb


class ViewTk(ViewBaseTk):
    # ============================================================================
    # Global variables
    # ============================================================================
    select_colour = "royalblue"

    # ============================================================================
    # properties
    # ============================================================================

    def __init__(self, view, new_mw: Tk, conflict_info):
        """Creates a new ViewTk object.

        - view: the View that is calling this function.

        - mw: The main window (TK main window)."""
        global mw
        mw = new_mw
        super().__init__(new_mw, conflict_info)
        self.view = view

    # ============================================================================
    # setup_popup_menu("teacher" | "lab" | "stream")
    # ============================================================================
    def setup_popup_menu(self, type: str, named_schedulables, toggle_movement_cb: Callable,
                         move_block_cb: Callable):
        """Create a popup menu to be used when right-clicking a GuiBlock.

        Create the pop-up menu BEFORE drawing the blocks, so that it can be bound to each block
        (done in self.redraw()).

        Parameters:
            type: type of View (teacher/lab/stream)
            named_schedulables: all schedulable objects of this type.
            toggle_movement_cb: callback routine to change a block from movable/unmovable.
            move_block_cb: callback routine if block is moved from one view to another.

        Inputs to Callback:
            - view object
            - Schedulable object (Teacher / Lab / Stream)"""
        view = self.view

        # create a menu.
        global mw
        pm = Menu(mw, tearoff=0)

        # toggle block from movable to unmovable.
        pm.add_command(label="Toggle Movable/Fixed", command=partial(
            toggle_movement_cb, view
        ))

        # create sub menu
        mm = Menu(pm, tearoff=0)
        pm.add_cascade(menu=mm, label="Move block(s) to ")

        for named_schedulable in named_schedulables:
            mm.add_command(label=named_schedulable.name, command=partial(
                move_block_cb, view, named_schedulable.object
            ))

        # save.
        self._popup_menu = pm

    # ============================================================================
    # setup_undo_redo(number, number, def ())
    # ============================================================================
    def setup_undo_redo(self, undo_number_ptr, redo_number_ptr, callback: Callable):
        """Set up the gui to show undo/redo numbers, add actions to the main menu, and add shortcut
        keys.

        Parameters:
            undo_number_ptr: The address of the undo_number maintained by the View object.
            redo_number_ptr: The address of the redo_number maintained by the View object.
            callback: The callback function that does the undo, or redo. Accepts an input string of value 'undo' or 'redo'."""
        tl: Toplevel = self._toplevel

        # ---------------------------------------------------------------
        # bind keys
        # ---------------------------------------------------------------
        tl.bind(
            '<Control-KeyPress-z>', partial(callback, self.view, 'undo')
        )
        tl.bind('<Meta-Key-z>', partial(callback, self.view, 'undo'))
        tl.bind('<Control-KeyPress-y>', partial(callback, self.view, 'redo'))
        tl.bind('<Meta-Key-y>', partial(callback, self.view, 'redo'))

        # ---------------------------------------------------------------
        # add undo/redo to main menu
        # ---------------------------------------------------------------
        main_menu: Menu = self._main_menu
        main_menu.add_command(label="Undo", command=partial(
            callback, self.view, 'undo'
        ))
        main_menu.add_command(label="Redo", command=partial(
            callback, self.view, 'redo'
        ))

        # ---------------------------------------------------------------
        # add undo/redo to status_frame
        # ---------------------------------------------------------------
        status_frame = self._status_bar
        Label(status_frame, textvariable=undo_number_ptr, borderwidth=1, relief='ridge', width=15) \
            .pack(side='right', fill='x')
        Label(status_frame, textvariable=redo_number_ptr, borderwidth=1, relief='ridge', width=15) \
            .pack(side='right', fill='x')

    # ============================================================================
    # Assign blocks
    # ============================================================================
    def setup_assign_blocks(self, assignable_blocks, callback: Callable):
        """Assign blocks are 1/2 hr sections that can be selected, and then, if desired, used to
        create guiblocks.

        Parameters:
            assignable_blocks: array of assignable blocks that are available.
            callback: Callback function called once a selection of assign_blocks is complete.

        Inputs to Callback:
            View object
            A ptr to a list of AssignBlock objects."""
        # save for later
        global selected_assign_block_completed_cb
        selected_assign_block_completed_cb = callback

        # what we are drawing on
        cn = self.canvas

        # BIND MOUSE 1 to the setup of AssignBlock selection, then calls a function to bind the
        # mouse movement.
        def dummy(cn, x, y):
            # Not the ideal way to do this, but I couldn't figure out a way to imitate what Sandy
            # was doing in the Perl code.
            if clicked_block: return  # allow another event to take control

            # if mouse is not on an assignable block, bail out
            ass_block = AssignBlockTk.find(x, y, assignable_blocks)
            if not ass_block:
                return

            # get day of assignable block that was clicked.
            day = ass_block.day()

            # set mouse_motion binding
            self._prepare_to_select_assign_blocks(cn, day, x, y, assignable_blocks)

        cn.bind(
            '<Button-1>', partial(
                dummy, cn, self.mw.winfo_pointerx(), self.mw.winfo_pointery()
            )
        )

    def _prepare_to_select_assign_blocks(self, cn: Canvas, day, x1, y1, assignable_blocks):
        """Binds mouse movement for selecting AssignBlocks.

        Binds mouse release for processing selected AssignBlocks.

        Want to add (or subtract) any AssignBlocks if the mouse passes over said blocks.

        Once mouse has been pressed, the selection of 'selectable' AssignBlocks is limited to the day of the initial selection.

        Parameters:
            cn: The canvas object.
            day: Day of the first selection.
            x1: X canvas coordinate of the mouse when it was initially clicked.
            y1: Y canvas coordinate of the mouse when it was initially clicked.
            assignable_blocks: array of all assignable blocks."""
        selected_assigned_blocks = []

        # Get a list of all the AssignBlocks associated with a given day.
        assign_blocks_day = [b.day for b in assignable_blocks if b.day == day]

        # Binds motion to a motion sub to handle the selection of multiple time slots when moving
        # mouse.
        cn.bind('<Motion>', partial(
            self._selecting_assigned_blocks,
            self.mw.winfo_pointerx(),
            self.mw.winfo_pointery(),
            x1,
            y1,
            selected_assigned_blocks,
            assign_blocks_day
        ))

        # Binds the release of Mouse 1 to process the selection of AssignBlocks.
        def dummy(cn: Canvas, x, y1, y2, selected_assigned_blocks):
            # Unbind everything.
            cn.bind('<Motion>', "")
            cn.bind('<ButtonRelease-1>', "")

            something_to_do = selected_assigned_blocks
            if not something_to_do or len(something_to_do) == 0:
                return
            self._selectedAssignBlocks(cn, selected_assigned_blocks)

        cn.bind('<ButtonRelease-1>', partial(
            dummy, x1, y1, self.mw.winfo_pointery(), selected_assigned_blocks
        ))

    @staticmethod
    def _selecting_assigned_blocks(cn: Canvas, x2, y2, x1, y1,
                                   selected_assigned_blocks: list[AssignBlockTk],
                                   assign_blocks_day: list[AssignBlockTk]):
        """Called when the mouse is moving, and in the process of selecting AssignBlocks.

        Parameters:
            cn: canvas object
            x2: current x position of mouse
            y2: current y position of mouse
            x1: x position of mouse when first clicked
            y1: y position of mouse when first clicked
            selected_assigned_blocks: array of selected AssignBlocks (reset in this method)
            assign_blocks_day: list of AssignBlocks for the day (when the mouse was first clicked, the day was calculated"""
        # Temporarily unbind motion
        cn.bind('<Motion>', "")

        # get the AssignBlocks currently under the selection window
        selected_assigned_blocks = AssignBlockTk.in_range(x1, y1, x2, y2, assign_blocks_day)

        # colour the selection blue
        for blk in assign_blocks_day:
            blk.unfill()
        for blk in selected_assigned_blocks:
            blk.set_colour(select_colour)

        # rebind Motion
        cn.bind('<Motion>', partial(
            ViewTk._selecting_assigned_blocks,
            mw.winfo_pointerx(),
            mw.winfo_pointery(),
            x1, y1, selected_assigned_blocks, assign_blocks_day
        ))

    def _selectedAssignBlocks(self, cn: Canvas, selected_assigned_blocks: list[AssignBlockTk]):
        """Mouse is up, AssignBlocks have been selected. Deal with it!

        Calls the callback routine defined in setup_assign_blocks.

        Parameters:
            cn: Canvas object.
            selected_assigned_blocks: Array of selected AssignBlocks."""

        # Unbind everything.
        cn.bind('<Motion>', "")
        cn.bind('<ButtonRelease-1>', "")

        something_to_do = selected_assigned_blocks
        if not something_to_do or len(something_to_do) == 0:
            return
        selected_assign_block_completed_cb(self.view, selected_assigned_blocks)

    # ============================================================================
    # Dragging Guiblocks around
    # ============================================================================

    # NOTE: Since we don't plan to have drag-&-drop between views in this version of the app,
    # and since the methods in this section seem to be doing just that, I'm not sure if I should
    # skip them.
    def set_bindings_for_dragging_guiblocks(self, view, guiblock: GuiBlockTk, moving_cb: Callable,
                                            after_release_cb: Callable, update_after_cb: Callable):
        """Create the necessary binding to allow guiblocks to be grabbed from one place and
        dropped into another place.

        Parameters:
            view: View object that called this function.
            guiblock: The object that the methods will be bound to.
            moving_cb: Callback to invoke while the guiblock is being moved. Takes view and guiblock as inputs.
            after_release_cb: Callback to invoke when the dragging has stopped. Takes view and guiblock as inputs.
            update_after_cb: Callback to invoke when everything is finished and updates are possibly required. Takes the view and guiblock as inputs."""

        self._moving_cb = moving_cb
        self._after_release_cb = after_release_cb
        self._update_after_cb = update_after_cb

        # Get the actual canvas objects that make up this object.
        group_of_canvas_objs = guiblock.group

        self.canvas.tag_bind(
            group_of_canvas_objs,
            "<1>",
            partial(
                self._select_guiblock_to_move, guiblock, self, view,
                self.mw.winfo_pointerx(), self.mw.winfo_pointery()
            )
        )

    def _select_guiblock_to_move(self, guiblock: GuiBlockTk, view, x_start, y_start):
        """Set up for drag and drop of GuiBlock. Binds motion and button release events to GuiBlock.

        Parameters:
            guiblock: GuiBlock that we want to move.
            view: The View object that setup these functions.
            x_start: X position of mouse when mouse was clicked.
            y_start: Y position of mouse when mouse was clicked."""

        (starting_x, starting_y) = self.canvas.coords(guiblock.rectangle)

        # We are processing a click on a GuiBlock, so tell the click event for the canvas to not
        # do anything.
        global clicked_block
        clicked_block = 1

        # This block is being controlled by the mouse.
        guiblock.is_controlled = True

        # Unbind any previous binding for clicking and motion, just in case.
        self.canvas.bind("<Motion>", "")
        self.canvas.bind("<ButtonRelease-1>", "")

        # bind for mouse motion.
        self.canvas.bind(
            "<Motion>",
            partial(
                self._gui_block_is_moving,
                guiblock,
                view,
                x_start, y_start,
                mw.winfo_pointerx(),
                mw.winfo_pointery(),
                starting_x,
                starting_y
            )
        )

        # bind for release of mouse up.
        self.canvas.bind(
            "<ButtonRelease-1>",
            partial(
                self._gui_block_has_stopped_moving,
                view,
                guiblock
            )
        )

    def _gui_block_is_moving(self, guiblock: GuiBlockTk, view, x_start, y_start, x_mouse, y_mouse,
                             starting_x, starting_y):
        """The GuiBlock is moving... need to update stuff as it is being moved.

        Invokes moving_cb callback (defined in set_bindings_for_dragging_guiblocks).

        Parameters:
            guiblock: The guiblock that is moving.
            x_start: initial mouse position when mouse was clicked.
            y_start: initial mouse position when mouse was clicked.
            starting_x: current mouse position.
            starting_y: current mouse position."""

        # Temporarily disable motion while we process stuff (keeps execution cycles down)
        self.canvas.bind("<Motion>", "")

        # raise the block.
        guiblock.gui_view.canvas.lift(guiblock.group)

        # Where Block needs to go
        desired_x = x_mouse - x_start + starting_x
        desired_y = y_mouse - y_start + starting_y

        # current x/y coordinates of the rectangle
        (cur_x_pos, cur_y_pos) = self.canvas.coords(guiblock.rectangle)

        # check for valid move.
        if cur_x_pos and cur_y_pos:
            # Where block is moving to:
            delta_x = desired_x - cur_x_pos
            delta_y = desired_y - cur_y_pos

            # Move the GuiBlock
            self.canvas.move(guiblock.group, delta_x, delta_y)
            self._refresh_gui

            # set the block's new coordinates (time/day).
            self._set_block_coords(guiblock, cur_x_pos, cur_y_pos)

            self._moving_cb(view, guiblock)

        # ------------------------------------------------------------------------
        # rebind to the mouse movements
        # ------------------------------------------------------------------------
        # what if we had a mouse up while processing this code?
        # (1) handle the stopped moving functionality
        # (2) do NOT rebind the motion even handler

        if not guiblock.is_controlled:
            self._gui_block_has_stopped_moving(view, guiblock)
        # else - rebind the motion event handler
        else:
            self.canvas.bind(
                "<Motion>",
                partial(
                    self._gui_block_is_moving,
                    guiblock,
                    view,
                    x_start,
                    y_start,
                    self.mw.winfo_pointerx(),
                    self.mw.winfo_pointery(),
                    starting_x,
                    starting_y
                )
            )

    def _gui_block_has_stopped_moving(self, view, guiblock: GuiBlockTk):
        """Moves the GuiBlock to the cursor's current position on the View and updates the Block's
        time in the Schedule.

        Invokes after_release_cb callback (defined in set_bindings_for_dragging_guiblocks).

        Invokes update_after_cb callback (defined in set_bindings_for_dragging_guiblocks).

        Parameters:
            view: The View object.
            guiblock: The GuiBlock that has been moved."""

        # If is ok now to process a click on the canvas.
        global clicked_block
        clicked_block = 0  # TODO: Make this a boolean.

        # unbind the motion on the gui_block.
        self.canvas.bind("<Motion>", "")
        self.canvas.bind("<ButtonRelease-1>", "")

        guiblock.is_controlled = False

        # Let the View do what it needs to do once the block has been dropped.
        self._after_release_cb(view, guiblock)

        # Get the GuiBlock's new coordinates (closest day/time).
        block = guiblock.block
        coords = self.get_time_coords(block.day_number, block.start_number, block.duration)

        # Current x/y coordinates of the rectangle.
        (cur_x_pos, cur_y_pos) = self.canvas.coords(guiblock.rectangle)

        # Move the GuiBlock to new position.
        self.canvas.move(guiblock.group, coords[0] - cur_x_pos, coords[1] - cur_y_pos)
        self._refresh_gui()

        # Update everything that needs to be updated once the block data is finalized.
        self._update_after_cb(view, block)

    # ============================================================================
    # Double clicking guiblock
    # ============================================================================
    def bind_double_click(self, view, guiblock: GuiBlockTk, callback: Callable):
        """

        Parameters:
            view: The view object that called this method.
            guiblock: The guiblock that we want to bind the double click event to.
            callback: Callback function that handles the double click.
        """

        # Get the actual canvas objects that make up this object.
        group_of_canvas_objs = guiblock.group
        self.canvas.tag_bind(
            group_of_canvas_objs,
            "<Double-1>",
            partial(
                self._was_double_clicked,
                view,
                guiblock,
                callback
            )
        )

    def _was_double_clicked(self, view, guiblock: GuiBlockTk, callback: Callable):
        """Invokes callback defined in bind_double_click.

        Parameters:
            view: View object.
            guiblock: GuiBlock that was double-clicked."""
        callback(view, guiblock)


# =================================================================
# footer
# =================================================================
"""
=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns - 2016

Sandy Bultena 2020 - Major Update

Rewritten for Python by Evan Laverdiere - 2023

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
