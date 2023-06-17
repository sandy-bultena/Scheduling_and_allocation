# =================================================================
# COMPLETED
from __future__ import annotations

from functools import partial
from tkinter import *
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .GuiBlockTk import GuiBlockTk
from ..Schedule.Block import Block
from ..Schedule.ConflictCalculations import Conflict
from ..Schedule.ScheduleEnums import ViewType, WeekDayNumber
from ..Export import DrawView


class ViewBaseTk:
    """Basic view with days/weeks printed on it.

    Don't call this class directly. This is a base class for different types of schedule views."""
    # =================================================================
    # Class Variables
    # =================================================================
    status_text: str = ""
    immovable_colour: str = "#dddddd"

    # =================================================================
    # Public Properties
    # =================================================================
    @property
    def mw(self) -> Tk:
        """Gets/sets a Tk MainWindow object."""
        return self._mw

    @mw.setter
    def mw(self, value):
        self._mw = value

    @property
    def popup_guiblock(self):
        """Gets/sets a guiblock object which is attached to the current popup menu."""
        return self._popup_guiblock

    @popup_guiblock.setter
    def popup_guiblock(self, value):
        self._popup_guiblock = value

    @property
    def on_closing(self):
        """Gets/sets the callback method called when user clicks the "X" button to close the
        window."""
        return self._closing_callback

    @on_closing.setter
    def on_closing(self, callback):
        self._closing_callback = callback

    @property
    def canvas(self) -> Canvas:
        """Gets/Sets the canvas of this View object."""
        return self.__canvas

    @canvas.setter
    def canvas(self, value: Canvas):
        self.__canvas = value

    @property
    def current_scale(self):
        """Gets/sets the current scale of this View object."""
        return self._current_scale

    @current_scale.setter
    def current_scale(self, value):
        self._current_scale = value

    # =================================================================
    # Public methods
    # =================================================================
    def __init__(self, mw: Tk, conflict_info: list):
        """Creates a new View object, but does NOT draw the view.

        Parameters:
            mw: Main Window
            conflict_info: a ptr to an array of hashes. Each hash has a key for the conflict text and the foreground and background colours."""
        self.mw = mw

        # ---------------------------------------------------------------
        # create a new toplevel window, add a canvas
        # ---------------------------------------------------------------
        tl = Toplevel(mw)
        tl.protocol('WM_DELETE_WINDOW', self._close_view)
        tl.resizable(False, False)

        # ---------------------------------------------------------------
        # Create bar at top to show colour coding of conflicts
        # ---------------------------------------------------------------
        f = Frame(tl)
        f.pack(expand=1, fill="x")

        for c in conflict_info:
            ttk.Label(f, text=c['text'], width=10, background=c['bg'], foreground=c['fg']) \
                .pack(side='left', expand=1, fill="x")

        # ---------------------------------------------------------------
        # add canvas
        # ---------------------------------------------------------------
        cn = Canvas(tl, height=700, width=700, background="white")
        cn.pack()

        # ---------------------------------------------------------------
        # create object
        # ---------------------------------------------------------------
        self.canvas = cn
        self._toplevel = tl
        self._x_offset = 1
        self._y_offset = 1
        self._x_origin = 0
        self._y_origin = 0
        self._width_scale = 100
        self._horiz_scale = 60
        self.current_scale = 1

        # ---------------------------------------------------------------
        # create scale menu
        # ---------------------------------------------------------------
        main_menu = Menu(mw)
        tl.configure(menu=main_menu)
        view_menu = Menu(main_menu, tearoff=0)
        main_menu.add_cascade(menu=view_menu, label="View", underline=0)
        view_menu.add_command(label="50%", underline=0, command=partial(
            self._resize_view, 0.50))
        view_menu.add_command(label="75%", underline=0, command=partial(
            self._resize_view, 0.75
        ))
        view_menu.add_command(label="100%", underline=0, command=partial(
            self._resize_view, 1.00))
        self._main_menu = main_menu

        # ---------------------------------------------------------------
        # if there is a popup menu defined, make sure you can make it
        # go away by clicking the toplevel (as opposed to the menu)
        # ---------------------------------------------------------------
        if hasattr(self, '__popup'):
            tl.bind('<1>', partial(self._unpostmenu))
            tl.bind('<2>', partial(self._unpostmenu))

        # ---------------------------------------------------------------
        # create status bar
        # ---------------------------------------------------------------
        # status # This variable seems to be unused.
        self._status_bar = self._create_status_bar()

    def set_title(self, title: str = ""):
        """Sets the title of the toplevel widget.

        Parameters:
            title: Text used as title for the window."""
        tl = self._toplevel
        tl.title = title

    def bind_popup_menu(self, gui_block: GuiBlockTk):
        """Draws the GuiBlock onto the view.
        Binds a popup menu if one is defined.

        Parameters:
            gui_block: object where the popup menu is being bound to."""
        # Menu bound to individual gui-blocks.
        # Had to do quite a bit of digging to figure out what the two Ev() functions were doing in
        # the original Perl script. They're getting the mouse coordinates.
        self.canvas.tag_bind(gui_block.group, '<3>', partial(
            self._postmenu, self, self.mw.winfo_pointerx(), self.mw.winfo_pointery(), gui_block
        ))
        return gui_block

    def draw_background(self):
        """Draws the Schedule timetable on the View canvas."""
        DrawView.draw_background(self.canvas, self.get_scale_info())
        return

    def unset_popup_guiblock(self):
        """No Block has a popup menu, so unset popup_guiblock."""
        del self._popup_guiblock
        return

    def move_block(self, guiblock: GuiBlockTk):
        """Moves the gui blocks to the appropriate place, based on the blocks's new day and time.

        Parameters:
            guiblock: The gui blocks to move."""
        block: Block = guiblock.block

        # Get new coordinates of the blocks.
        coords = self.get_time_coords(block.day_number, block.start_number, block.duration)

        # Get the current x/y of the guiblock.
        (cur_x_pos, cur_y_pos, _, _) = guiblock.gui_view.canvas.coords(guiblock.rectangle)

        # bring the guiblock to the front, passes over others.
        guiblock.gui_view.canvas.lift(guiblock.group_tag)

        # move guiblock to new position
        guiblock.gui_view.canvas.move(guiblock.group_tag, coords[0] - cur_x_pos,
                                      coords[1] - cur_y_pos)

    def colour_block(self, guiblock: GuiBlockTk, type: ViewType):
        """Colours the blocks according to conflicts.

        Parameters:
            guiblock: The guiblock that will be coloured.
            type: The type of schedulable object that this guiblock is attached to (Teacher/Lab/Stream)"""
        conflict = Conflict.most_severe(guiblock.block.conflicted_number, type)

        # If the blocks is unmovable, then grey it out, and do not change its colour even if
        # there is a conflict.
        if not guiblock.block.movable:
            guiblock.change_colour(ViewBaseTk.immovable_colour)
            return

        # else...

        # change the colour of the blocks to the most important conflict.
        if conflict is not None:
            guiblock.change_colour(Conflict.colours()[conflict])

        # no conflict found, reset back to default colour.
        else:
            guiblock.change_colour(guiblock.colour)

    def redraw(self):
        """Redraws the View with new GuiBlocks and their positions."""
        try:
            cn = self.canvas
        except Exception:
            return

        # remove everything on the canvas.
        cn.delete('all')

        # redraw background (things that don't change, like time, etc.)
        self.draw_background()

        # remove any binding to the canvas itself.
        self.canvas.bind("<1>", "")
        self.canvas.bind("<B1-Motion>", "")
        self.canvas.bind("<ButtonRelease-1>", "")

    def get_scale_info(self):
        """Returns a hash with the following values:
            =item * -xoff => x offset

            =item * -yoff => y offset

            =item * -xorg => x origin

            =item * -yorg => y origin

            =item * -xscl => x scale

            =item * -yscl => y scale

            =item * -scale => current scaling

        """
        return {
            "xoff": self._x_offset,
            "yoff": self._y_offset,
            "xorg": self._x_origin,
            "yorg": self._y_origin,
            "xscl": self._width_scale,
            "yscl": self._horiz_scale,
            "scale": self.current_scale
        }

    def get_time_coords(self, day, start, duration) -> tuple[int]:
        """Converts the times into x and y coordinates and returns them.

        Parameters:
            day: The day.
            start: The start time of the blocks.
            duration: Number of hours for this blocks."""
        scl = self.get_scale_info()
        coords = DrawView.get_coords(day, start, duration, scl)
        return coords

    def destroy(self):
        """Close/destroy the gui window."""
        toplevel = self._toplevel
        toplevel.destroy()

    # =================================================================
    # Private Properties
    # =================================================================
    # NOTE: Skipping _main_menu, _status_bar and _toplevel, since there's no special validation
    # required here.
    @property
    def _popup_menu(self):
        """Get/set the popup menu for this guiblock."""
        return self.__popup

    @_popup_menu.setter
    def _popup_menu(self, value: Menu):
        self.__popup = value

    # =================================================================
    # Private Methods
    # =================================================================
    def _resize_view(self, scale):
        """Resizes the View to the new scale.

        Parameters:
            scale: Scale that the view will be resized to."""
        # get_by_id height and width of toplevel.
        window_height = self._toplevel.winfo_height()
        window_width = self._toplevel.winfo_width()

        # Get height and width of canvas.
        heights = self.canvas.configure()['height']
        canvas_height = int(heights[-1])
        widths = self.canvas.configure()['width']
        canvas_width = int(widths[-1])

        # get_by_id current scaling sizes
        x_origin = self._x_origin
        y_origin = self._y_origin
        horiz_scale = self._horiz_scale
        width_scale = self._width_scale
        current_scale = self.current_scale

        # reset scales back to default value.
        x_origin /= current_scale
        y_origin /= current_scale
        width_scale /= current_scale
        horiz_scale /= current_scale
        window_height /= current_scale
        window_width /= current_scale
        canvas_height /= current_scale
        canvas_width /= current_scale

        current_scale = scale

        # set scales to new size
        x_origin *= scale
        y_origin *= scale
        width_scale *= scale
        horiz_scale *= scale
        window_height *= scale
        window_width *= scale
        canvas_height *= scale
        canvas_width *= scale

        # set the new scaling sizes.
        self._x_origin = x_origin
        self._y_origin = y_origin
        self._horiz_scale = horiz_scale
        self._width_scale = width_scale
        self.current_scale = current_scale

        # set height and width of canvas and toplevel
        self.canvas.configure(width=canvas_width,
                              height=canvas_height)
        self._toplevel.configure(width=window_width,
                                 height=window_height)

        # Now that all the sizes have changed, redraw.
        self.redraw()

    def _refresh_gui(self):
        """Forces the graphics to update."""
        self.mw.update_idletasks()

    def _create_status_bar(self):
        """Status bar at the bottom of each View to show current movement type."""
        if hasattr(self, '_status_bar'):
            return

        status_frame = Frame(self._toplevel, borderwidth=0, relief='flat')
        status_frame.pack(side='bottom', expand=0, fill='x')
        status_text_var = StringVar()
        Label(status_frame, textvariable=status_text_var, borderwidth=1, relief='ridge') \
            .pack(side='left', expand=1, fill='x')
        status_text_var.set(ViewBaseTk.status_text)

        return status_frame

    def _postmenu(self, c: Canvas, x: int, y: int, guiblock: GuiBlockTk):
        """Posts (shows) the popup menu at location (x,y).

        Parameters:
            c: The Canvas object.
            x, y: the x,y position of the mouse.
            guiblock: The guiblock associated with the popup menu."""
        if self._popup_menu:
            self._popup_guiblock = guiblock
            self._popup_menu.post(x, y)

    def _unpostmenu(self, c: Canvas = None):
        """Removes the Context Menu.

        Parameters:
            c: The Canvas object."""
        if self._popup_menu:
            self._popup_menu.unpost()

        self.unset_popup_guiblock()

    def _close_view(self):
        """Close the current View."""
        self.on_closing()

    def _set_block_coords(self, guiblock: GuiBlockTk, x, y):
        """Converts the X and Y coordinates into times and sets the time to the Block associated with the guiblock.

        Parameters:
            guiblock: The guiblock that was moved.
            x: the x position of the blocks.
            y: the y position of the blocks."""
        scl = self.get_scale_info()

        if guiblock is None:
            return

        (day, time, duration) = DrawView.coords_to_day_time_duration(x, y, y, scl)

        guiblock.block._TimeSlot__day_number = day
        guiblock.block.start_number = time


# =================================================================
# footer
# =================================================================
"""
=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns

Rewritten for Python by Evan Laverdiere

=head1 COPYRIGHT

Copyright (c) 2016, Jack Burns, Sandy Bultena, Ian Clement. 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)


"""
