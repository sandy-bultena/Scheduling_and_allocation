from functools import partial
from tkinter import *
from tkinter import ttk
from typing import Callable

from .ViewBaseTk import ViewBaseTk

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

    def __init__(self, view, mw: Tk, conflict_info):
        """Creates a new ViewTk object.

        - view: the View that is calling this function.

        - mw: The main window (TK main window)."""
        super().__init__(mw, conflict_info)
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
        pm = Menu(mw)

        # toggle block from movable to unmovable.
        pm.add_command(label="Toggle Movable/Fixed", command=partial(
            toggle_movement_cb, view
        ))

        # create sub menu
        mm = Menu(pm)
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
            '<Control-KeyPress-z>', callback(self.view, 'undo')
        )
        tl.bind('<Meta-Key-z', callback(self.view, 'undo'))
        tl.bind('<Control-KeyPress-y', callback(self.view, 'redo'))
        tl.bind('<Meta-Key-y', callback(self.view, 'redo'))

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
            ass_block = None # AssignBlockTk.find(x, y, assignable_blocks) TODO: Come back to this once AssignBlockTk has been implemented.
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


