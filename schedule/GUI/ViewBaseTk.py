from abc import ABC
from tkinter import *
from tkinter import ttk


class ViewBaseTk(ABC):
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
            ttk.Label(f, text=c.text, width=10, background=c.bg, foreground=c.fg)\
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
        view_menu = Menu(main_menu)
        main_menu.add_cascade(menu=view_menu, label="View", underline=0)
        view_menu.add_command(label="50%", underline=0, command=_resize_view(self, 0.50))
        view_menu.add_command(label="100%", underline=0, command=_resize_view(self, 1.00))
        self._main_menu = main_menu

        # ---------------------------------------------------------------
        # if there is a popup menu defined, make sure you can make it
        # go away by clicking the toplevel (as opposed to the menu)
        # ---------------------------------------------------------------
        # TODO: Verify that this works.
        if self._popup_menu:
            tl.bind('<1>', _unpost_menu(self))
            tl.bind(('<2>', _unpost_menu(self)))

        # ---------------------------------------------------------------
        # create status bar
        # ---------------------------------------------------------------
        status
        self._status_bar = self._create_status_bar(status)