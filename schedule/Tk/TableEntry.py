import tkinter
from tkinter import *
from tkinter import ttk


# ===================================================================
# Create a tool for Entering text (spreadsheet style?)
# ===================================================================

class TableEntry(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.populate()

    # ===================================================================
    # populate
    # ===================================================================
    def populate(self, *args):
        pane = Frame(self, name='tableEntry', border=2, relief='flat')
        pane.pack(side='left', fill='both')

        self.pane = pane
        x_scrollbar = Scrollbar(self.pane, elementborderwidth=2,
                                relief='ridge',
                                width=12,
                                orient=HORIZONTAL)
        y_scrollbar = Scrollbar(self.pane, elementborderwidth=2,
                                relief='ridge',
                                width=12,
                                orient=VERTICAL)

        # ---------------------------------------------------------------
        # create defaults here, because ConfigSpecs doesn't set
        # those specifications until later, but we need this stuff
        # now
        # ---------------------------------------------------------------
        defaults = {
            'rows': 10,             # Number of rows to start
            'bg_entry': '#ffffff',  # Background color of the entry widget.
            'columns': 10,          # Number of columns
            'titles': [],           # Title of columns
            'colwidths': [],        # Width of columns
            'disabled': [],         # Which columns are read-only
            'defwidth': 8           # Default width of the columns
        }

        bg = self.winfo_toplevel().cget('bg')  #TODO: Verify the actual property name.

        # ---------------------------------------------------------------
        # define ConfigSpecs
        # ---------------------------------------------------------------
        #super().populate(*args)
        # NOTE: The above line of code seems to be something unique to Perl/TK. Tkinter does not
        # seem to have a "populate" method, as far as I can tell.
        # self.configure(
        #
        # )
