import tkinter
from tkinter import *
from tkinter import ttk


# ===================================================================
# Create a tool for Entering text (spreadsheet style?)
# ===================================================================

class TableEntry(Frame):
    def __init__(self, parent):
        super().__init__(parent)

    # ===================================================================
    # populate
    # ===================================================================
    def populate(self, *args):
        pane = Frame(self, name='TableEntry', border=2, relief='flat')
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
