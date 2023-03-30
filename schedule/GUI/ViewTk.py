from functools import partial
from tkinter import *
from tkinter import ttk

from .ViewBaseTk import ViewBaseTk


class ViewTk(ViewBaseTk):
    # ============================================================================
    # Global variables
    # ============================================================================
    global mw
    global clicked_block
    global select_colour
    select_colour = "royalblue"
    global selected_assign_block_completed_cb

    # ============================================================================
    # properties
    # ============================================================================

    def __init__(self, view, mw, conflict_info):
        """Creates a new ViewTk object.

        - view: the View that is calling this function.

        - mw: The main window (TK main window)."""
        self.view = view
        mw = mw
        self.conflict_info = conflict_info

    # ============================================================================
    # setup_popup_menu("teacher" | "lab" | "stream")
    # ============================================================================
    def setup_popup_menu(self, type, named_schedulables, toggle_movement_cb, move_block_cb):
        """Create a popup menu to be used when right-clicking a GuiBlock.

        Create the pop-up menu BEFORE drawing the blocks, so that it can be bound to each block
        (done in self.redraw()).

        Parameters:
            - type: type of View (teacher/lab/stream)
            - named_schedulables: all schedulable objects of this type.
            - toggle_movement_cb: callback routine to change a block from movable/unmovable.

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
        pm.add_cascade(menu=mm, label="Mobe block(s) to ")

        for named_schedulable in named_schedulables:
            mm.add_command(label=named_schedulable.name, command=partial(
                move_block_cb, view, named_schedulable.object
            ))

        # save.
        self._popup_menu(pm)

    # ============================================================================
    # setup_undo_redo(number, number, def ())
    # ============================================================================
    def setup_undo_redo(self, undo_number_ptr, redo_number_ptr, callback):
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
        #TODO: Come back to this once you understand what this is meant to be.

