from PerlLib import Colours, Colour
from tkinter import simpledialog, Menu, Label, Entry, PanedWindow, Frame

# ============================================================================
# globals
# ============================================================================

# fonts

header_colour1           = "#abcdef"
header_colour2           = Colour.lighten(header_colour1, 5)
very_light_grey          = "#eeeeee"
row_col_indicator_colour = Colour.lighten("cdefab", 5)
totals_header_colour     = Colour.string("lemonchiffon")
totals_colour            = Colour.lighten(totals_header_colour, 5)
fg_colour                = "black"
bg_colour                = "white"
needs_update_colour      = Colour.string("mistyrose")
not_ok_colour            = needs_update_colour

# width of the data entry; Perl includes a comment about making if configurable in the future
width = 5

# generic properties for entry widgets
entry_props = {}

class AllocationGridTk:
    def __init__(self, frame: Frame, rows, col_merge, totals_merge, fonts,
                 cb_data_entry, cb_process_data_change, cb_bottom_row_ok):
        self.cb_data_entry = cb_data_entry
        self.cb_process_data_change = cb_process_data_change
        self.cb_bottom_row_ok = cb_bottom_row_ok

        # ------------------------------------------------------------------------
        # entry widget properties
        # ------------------------------------------------------------------------
        entry_props = {
            'width': width,
            'relief': 'flat',
            'borderwidth': 1,
            'justify': 'center',
            'font': fonts['small'],
            'fg': fg_colour,
            'disabledforeground': fg_colour,
            'bg': bg_colour,
            'disabledbackground': bg_colour
        }

        # ------------------------------------------------------------------------
        # get rid of anything that is currently on this frame
        # ------------------------------------------------------------------------
        for w in frame.pack_slaves():
            w.destroy()

        # ------------------------------------------------------------------------
        # make a 2x3 grid with frames for
        # blank   | header | blank
        # teacher | data   | totals
        # ------------------------------------------------------------------------
        pane = Frame(frame)
        pane.pack(side='top', expand=1, fill='both')

        # make the frames

        # perl version uses Pane, doesn't seem to exist in tkinter; is it PanedWindow?
        # if not find an alternative
        #header_frame =
