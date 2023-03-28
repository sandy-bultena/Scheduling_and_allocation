from abc import ABC


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
    def mw(self):
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

    # =================================================================
    # Public methods
    # =================================================================
    def __init__(self, mw, conflict_info):
        """Creates a new View object, but does NOT draw the view.

        Parameters:
            mw: Main Window
            conflict_info: a ptr to an array of hashes. Each hash has a key for the conflict text and the foreground and background colours."""
        self.mw = mw

