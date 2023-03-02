import tkinter
from tkinter import *
from tkinter import ttk
from typing import Any


# ===================================================================
# Create a tool for Entering text (spreadsheet style?)
# ===================================================================

class TableEntry(Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.populate(**kwargs)

    # ===================================================================
    # populate
    # ===================================================================
    def populate(self, **args):
        self.pane = Frame(self, name='tableEntry', border=2, relief='flat')
        self.pane.grid(row=0, column=0)

        # self.pane = pane
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
        defaults: dict[str, Any] = {
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

        # TODO: The call to configure() fails because Frame doesn't have a "-rows" option.
        # configure = dict(defaults, **args)
        # self.configure(configure)
        self.__titles = args['titles'] if args['titles'] else []
        self.__columns = args['columns'] if args['columns'] else 0
        self.__rows = args['rows'] if args['rows'] else 0

        # ---------------------------------------------------------------
        # where we keep lookup info (widget to cell, cell to widget)
        # ---------------------------------------------------------------
        self._reverse = {}
        self._lookup = []
        self._te_init()
        self.test_label = Label(self, text="Can you see me, tommy?").grid(row=0, column=0)
        
    def _te_init(self):
        # Create header row.
        self._create_header_row()
        
        # add rows
        for row in range(1, self.__rows):
            self.add_empty_row(row)
            
        # Calculate the width of the row, to set the pane width.
        xtot = 0
        # for col in self.columns:
        #     w = self.get_widget
        self.configure(width=1000)

    # ===================================================================
    # basic getter/setters
    # ===================================================================
    @property
    def rows(self):
        return self.cget('rows')

    @property
    def columns(self):
        return self.cget('columns')

    # ===================================================================
    # reconfigure the titles of the columns
    # ===================================================================
    @property
    def titles(self):
        # NOTE: The Frame widget doesn't have a config option for 'titles' in Tkinter, and the
        # Scrollable and Pane widgets from Perl TK don't exist here. Have to improvise.
        return self.__titles
        return self.cget('titles')

    @titles.setter
    def titles(self, r):
        if r:
            self.configure()

    # ===================================================================
    # insert header_row
    # ===================================================================
    def _create_header_row(self):
        self._title_widgets = []
        cols = self.__columns # Fails because Frame doesn't have an option called "-columns"
        titles = self.titles
        # colwidths = self.colwidths
        row_lookups = []

        for c in range(0, cols):
            if c >= len(titles):
                titles.append('')
            w = Label(self, text=titles[c], bg="yellow", width=50)
            w.grid(column=c, row=0, sticky="nwes")
            row_lookups.append(w)
            self._reverse[w] = [0, c]
        self._lookup.append(row_lookups)

    def add_empty_row(self, row):
        # colwidths = self.colwidths
        # disabled = self.disabled
        for c in range(1, self.__columns):
            # Get the width of the columns from somewhere.
            old = None

