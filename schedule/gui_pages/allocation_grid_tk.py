import schedule.Utilities.Colour as colour
import tkinter as tk
import tkinter.ttk as ttk

from schedule.Tk.Pane import Pane
from idlelib.tooltip import Hovertip

from schedule.gui_generics.number_validations import entry_float
from schedule.Tk import InitGuiFontsAndColours as fac

# =====================================================================================================================
# globals
# =====================================================================================================================

# colours
header_colour1           = "#abcdef"
header_colour2           = colour.lighten(header_colour1, 15)
very_light_grey          = "#dddddd"
row_col_indicator_colour = colour.lighten("#cdefab", 5)
totals_header_colour     = colour.string("lemonchiffon")
totals_colour            = colour.lighten(totals_header_colour, 5)
fg_colour                = "black"
bg_colour                = "white"
needs_update_colour      = colour.string("mistyrose")
not_ok_colour            = needs_update_colour
border_colour            = "#eeeeee"

width = 5

# =====================================================================================================================
# Allocation Grid Tk
# =====================================================================================================================
class AllocationGridTk:

    @property
    def num_summary_col(self):
        return len(self.summary_header_widgets)

    @property
    def num_summary_sub_col(self):
        return len(self.summary_sub_header_widgets)

    @property
    def num_rows(self):
        return len(self.title_widgets)

    @property
    def num_cols(self):
        return len(self.sub_header_widgets)

    fonts: fac.TkFonts = fac.fonts
    colours: fac.TkColours = fac.colours

    # -----------------------------------------------------------------------------------------------------------------
    # constructor
    # -----------------------------------------------------------------------------------------------------------------
    def __init__(self, frame: tk.Frame, rows,
                 col_merge: list[int],
                 summary_merge: list[int],
                 cb_data_entry = lambda *_, **__: True,
                 cb_process_data_change = lambda *_, **__: True,
                 cb_bottom_row_ok = lambda *_, **__: True):
        """

        :param frame: where to put this grid
        :param rows: number of rows in the grid
        :param col_merge: list, each item represents a group of columns (affects colouring)
        :param summary_merge: list, each item represents a group of columns in the totals sections
        :param cb_data_entry:
        :param cb_process_data_change:
        :param cb_bottom_row_ok:
        """
        # setup fonts if they have not already been set up
        if self.fonts is None:
            self.fonts = fac.TkFonts(frame.winfo_toplevel())

        self.data_entry_handler = cb_data_entry
        self.process_data_change_handler = cb_process_data_change
        self.bottom_row_ok_handler = cb_bottom_row_ok
        self.entry_padding = 1
        self.background="black"
        self.title_width = 12
        self.summary_width = width+5
        self.panes = []


        # entry widget properties
        self.entry_props = {
            'width': width,
            'relief': 'ridge',
            'border': 0,
            'justify': 'center',
            'font': self.fonts.small,
            'fg': fg_colour,
            'disabledforeground': fg_colour,
            'highlightbackground': bg_colour,
            'bg': bg_colour,
            'disabledbackground': bg_colour
        }

        # get rid of anything that is currently on this frame
        for w in frame.winfo_children():
            w.destroy()

        # make the frames
        self._layout(frame)

        # make the other stuff
        self.header_widgets: list[tk.Entry] = []
        self.sub_header_widgets: list[tk.Entry] = []
        self.summary_sub_header_widgets: list[tk.Entry] = []

        self.title_widgets: list[tk.Entry] = []
        self.widgets_row_col: dict[tk.Entry, tuple[int,int]] = dict()
        self.entry_widgets: dict[tuple[int,int], tk.Entry] = dict()
        self.summary_widgets: dict[int, dict[int, tk.Entry]] = dict()
        self.summary_header_widgets: list[tk.Entry] = []

        self.bottom_title_widgets: list[tk.Entry] = []

        self.bottom_widgets: list[tk.Entry] = []
        self.column_colours: dict[int, str] = dict()

        self.make_header_columns(col_merge)
        self.make_summary_header(summary_merge)
        self.make_row_titles(rows)
        self.make_data_grid(rows, col_merge)
        self.make_summary_grid(rows, summary_merge)
        self.make_bottom_header()
        self.make_bottom(col_merge)


    # -----------------------------------------------------------------------------------------------------------------
    # layout
    # -----------------------------------------------------------------------------------------------------------------
    def _layout(self, frame):
        """
        ┌──────────────────────────────────────────────────────────────────┐
        │       ┌──────────────────────────────────────────────────┐┌────┐ │
        │       │               header                             ││  1 │ │
        │       └──────────────────────────────────────────────────┘└────┘ │
        │ ┌────┐┌──────────────────────────────────────────────────┐┌────┐ │
        │ │ t  ││                                                  ││ s  │ │
        │ │ i  ││                                                  ││ u  │ │
        │ │ t  ││                                                  ││ m  │ │
        │ │ l  ││                data                              ││ m  │ │
        │ │ e  ││                                                  ││ a  │ │
        │ │ s  ││                                                  ││ r  │ │
        │ │    ││                                                  ││ y  │ │
        │ │    ││                                                  ││    │ │
        │ └────┘└──────────────────────────────────────────────────┘└────┘ │
        │ ┌────┐┌──────────────────────────────────────────────────┐       │
        │ │  2 ││               bottom                             │       │
        │ └────┘└──────────────────────────────────────────────────┘       │
        │        <────────────────────────────────────────────────>        │
        └──────────────────────────────────────────────────────────────────┘
        1 = summary header
        2 = bottom title
        """
        x_pad_col_0 = 0
        x_pad_col_1 = 0
        x_pad_col_2 = 0
        y_pad_row_0 = 0
        y_pad_row_1 = 0
        y_pad_row_2 = 0
        # outer_pane = Pane(frame, background="blue")
        # self.outer_frame = outer_pane.frame
        # outer_pane.pack(expand=1, fill='both')
        self.outer_frame = tk.Frame(frame, background="white")
        self.outer_frame.pack(expand=1, fill='both')

        # make the frames
        header_pane = Pane(self.outer_frame, background=self.background)
        self.header_frame = header_pane.frame
        self.panes.append(header_pane)

        summary_header_pane = Pane(self.outer_frame, background=self.background)
        self.summary_header_frame = summary_header_pane.frame
        self.panes.append(summary_header_pane)

        titles_pane = Pane(self.outer_frame, background=self.background)
        self.titles_frame = titles_pane.frame
        self.panes.append(titles_pane)

        data_pane = Pane(self.outer_frame, background=self.background)
        self.data_frame = data_pane.frame
        self.panes.append(data_pane)

        summary_pane = Pane(self.outer_frame, background=self.background)
        self.summary_frame = summary_pane.frame
        self.panes.append(summary_pane)

        bottom_title_pane = Pane(self.outer_frame, background=self.background)
        self.bottom_title_frame = bottom_title_pane.frame
        self.panes.append(bottom_title_pane)

        bottom_pane = Pane(self.outer_frame, background=self.background)
        self.bottom_frame = bottom_pane.frame
        self.panes.append(bottom_pane)


        # make the scrollbars (and anything else that needs to be set????)
        scrollbar = ttk.Scrollbar(self.outer_frame, orient="horizontal")
        horizontal_scrollable = (header_pane, titles_pane, data_pane, bottom_pane)

        def sync_horizontal_scroll(*args):
            for w in horizontal_scrollable:
                w.xview(*args)

        scrollbar.config(command=sync_horizontal_scroll)
        for f in horizontal_scrollable:
            f.canvas.config(xscrollcommand=scrollbar.set)


        # configure the layout
        self.outer_frame.columnconfigure(0,weight=0)
        self.outer_frame.columnconfigure(1,weight=100)
        self.outer_frame.columnconfigure(2,weight=0)

        header_pane.grid(row=0, column=1, sticky='nsew', pady=y_pad_row_0, padx=x_pad_col_1)
        summary_header_pane.grid(row=0, column=2, sticky='nsew', pady=y_pad_row_0, padx=x_pad_col_2)
        titles_pane.grid(row=1, column=0, sticky='nsew', pady=y_pad_row_1, padx=x_pad_col_0)
        data_pane.grid(row=1, column=1, sticky='nsew', pady=y_pad_row_1, padx=x_pad_col_1)
        summary_pane.grid(row=1, column=2, sticky='nsew', pady=y_pad_row_1, padx=x_pad_col_2)
        bottom_title_pane.grid(row=2, column=0, sticky='nsew', pady=y_pad_row_2, padx=x_pad_col_0)
        bottom_pane.grid(row=2, column=1, sticky='nsew', pady=y_pad_row_2,padx=x_pad_col_1)
        scrollbar.grid(row=3, column=1, sticky='nsew', padx=x_pad_col_1)

    # -----------------------------------------------------------------------------------------------------------------
    # make the header columns
    # -----------------------------------------------------------------------------------------------------------------
    def make_header_columns(self, col_merge: list):
        prop = self.entry_props.copy()
        prop['disabledbackground'] = header_colour1
        prop['highlightbackground'] = border_colour
        prop['state'] = 'disabled'

        # merged header
        for i, header in enumerate(col_merge):

            # frame to hold the merged header, and the subheadings
            mini_frame = tk.Frame(self.header_frame)
            mini_frame.pack(side='left')
            mini_frame.configure(background=self.header_frame.cget("background"))

            # widget
            me = tk.Entry(mini_frame, **prop)
            me.pack(side='top', expand=0, fill='both', padx=self.entry_padding,pady=self.entry_padding)

            # change Colour every second merged header
            if i % 2:
                me.configure(disabledbackground=header_colour2)
                me.configure(highlightbackground=header_colour2)

            # keep these widgets so that they can be configured later
            self.header_widgets.append(me)

            # subsections
            for sub_section in range(header):
                # frame within the mini-frame, so we can stack 'left'
                (hf2 := tk.Frame(mini_frame)).pack(side='left')
                hf2.configure(background=self.header_frame.cget("background"))

                # widget
                (se := tk.Entry(hf2, **prop)).pack(side='left', padx=self.entry_padding,pady=self.entry_padding)

                # change Colour every second merged header
                if i % 2:
                    se.configure(disabledbackground=header_colour2)
                    se.configure(highlightbackground=header_colour2)

                # keep these widgets so that they can be configured later
                self.sub_header_widgets.append(se)

    # -----------------------------------------------------------------------------------------------------------------
    # summary header
    # -----------------------------------------------------------------------------------------------------------------
    def make_summary_header(self, totals_merge):
        prop = self.entry_props.copy()
        prop['width'] = self.summary_width
        prop['disabledbackground'] = totals_header_colour
        prop['state'] = 'disabled'

        for header in totals_merge:

            # frame to hold the totals header, and the subheadings
            (mini_frame := tk.Frame(self.summary_header_frame)).pack(side='left')
            mini_frame.configure(background=self.header_frame.cget("background"))

            # widget
            (me := tk.Entry(mini_frame, **prop)).pack(side='top', expand=0, fill='both', padx=self.entry_padding,pady=self.entry_padding)

            # keep these widgets so that they can be configured later
            self.summary_header_widgets.append(me)

            for sub_section in range(1, header):
                # frame within the mini-frame so we can stack left
                (hf2 := tk.Frame(mini_frame)).pack(side='left')
                hf2.configure(background=self.header_frame.cget("background"))

                # widget
                (se := tk.Entry(hf2, **prop)).pack(side='left', padx=self.entry_padding,pady=self.entry_padding)

                # keep these widgets so that they can be configured later
                self.summary_sub_header_widgets.append(se)

    # -----------------------------------------------------------------------------------------------------------------
    # row titles
    # -----------------------------------------------------------------------------------------------------------------
    def make_row_titles(self, rows):
        prop = self.entry_props.copy()
        prop['width'] = self.title_width
        for _ in range(rows):
            re = tk.Entry(self.titles_frame, **prop, state='disabled')
            re.pack(side='top', padx=self.entry_padding,pady=self.entry_padding)

            self.title_widgets.append(re)

    # -----------------------------------------------------------------------------------------------------------------
    # data grid
    # -----------------------------------------------------------------------------------------------------------------
    def make_data_grid(self, rows, col_merge: list):

        for row in range(rows):
            (df1 := tk.Frame(self.data_frame)).pack(side='top', expand=1, fill='x')
            df1.configure(background=self.data_frame.cget("background"))

            # foreach header
            col: int = 0
            for column_index, header in enumerate(col_merge):

                # subsections
                for subsection in range(header):

                    # data entry box
                    var = tk.StringVar(value=f"{row}.{col}")
                    de = entry_float(df1, textvariable=var, **self.entry_props)
                    de.pack(side='left', padx=self.entry_padding,pady=self.entry_padding)

                    # save row/column with data entry, and vice versa
                    self.entry_widgets[row,col] = de
                    self.widgets_row_col[de] = row, col

                    # set_default_fonts_and_colours Colour in column to make it easier to read
                    de_colour = de.cget('background')
                    if column_index % 2 == 0:
                        de_colour = very_light_grey
                    self.column_colours[col] = de_colour
                    de.configure(background=de_colour)
                    de.configure(highlightbackground=de_colour)

                    # TODO: do this binding later

                    # de.bind("<Tab>", partial(self._move, 'nextCell'))
                    # de.bind("<Key-Return>", partial(self._move, 'nextRow'))
                    # de.bind("<Shift-Tab>", partial(self._move, 'prevCell'))
                    # de.bind("<Key-Up>", partial(self._move, 'prevRow'))
                    # de.bind("<Key-uparrow>", partial(self._move, 'prevRow'))
                    # de.bind("<Key-Down>", partial(self._move, 'nextRow'))
                    # de.bind("<Key-downarrow>", partial(self._move, 'nextRow'))
                    #
                    # de.bind("<FocusIn>", partial(self.focus_changed, 'focusIn', colour=row_col_indicator_colour))
                    # de.bind("<FocusOut>", partial(self.focus_changed, 'focusOut'))
                    # de.bindtags([*de.bindtags(), 1, 0, 2, 3])

                    col += 1

    # -----------------------------------------------------------------------------------------------------------------
    # summary
    # -----------------------------------------------------------------------------------------------------------------
    def make_summary_grid(self, rows, totals_merge):
        prop = self.entry_props.copy()
        prop['width'] = self.summary_width
        prop['disabledbackground'] = totals_header_colour
        prop['state'] = 'disabled'

        for row in range(rows):
            (df1 := tk.Frame(self.summary_frame)).pack(side='top', expand=1, fill='x')
            df1.configure(background=self.header_frame.cget("background"))

            # foreach header
            col = 0
            for header in range(len(totals_merge)):
                # subsections
                for _ in range(1, totals_merge[header]):

                    # data entry box
                    (de := tk.Entry(df1, **prop)).pack(side='left', padx=self.entry_padding,pady=self.entry_padding)

                    # save row/column with totals entry
                    if row not in self.summary_widgets:
                        self.summary_widgets[row] = {}
                    self.summary_widgets[row][col] = de
                    col += 1

    # -----------------------------------------------------------------------------------------------------------------
    # bottom row header
    # -----------------------------------------------------------------------------------------------------------------
    def make_bottom_header(self):
        prop = self.entry_props.copy()
        prop['width'] = self.title_width

        # widget
        se = tk.Entry(self.bottom_title_frame, **prop, state='disabled')
        se.pack(side='left', expand=1,fill='both', padx=self.entry_padding,pady=self.entry_padding)

        # keep these widgets so that they can be configured later
        self.bottom_title_widgets.append(se)


    # ============================================================================
    # bottom
    # ============================================================================
    def make_bottom(self, col_merge):
        def validate(n, w):
            if self.bottom_row_ok_handler(n):
                self.bottom_frame.nametowidget(w).configure(disabledbackground=totals_colour)
            else:
                self.bottom_frame.nametowidget(w).configure(disabledbackground=not_ok_colour)
            return True

        # merged header
        for header in col_merge:
            for sub_section in range(header):
                # widget
                prop = self.entry_props.copy()
                prop['disabledbackground'] = header_colour1
                se = tk.Entry(self.bottom_frame, **prop, state='disabled', validate='key')
                se.configure(validatecommand=(se.register(validate), '%P', '%W'))
                se.pack(side='left', padx=self.entry_padding,pady=self.entry_padding)

                # keep these widgets so that they can be configured later
                self.bottom_widgets.append(se)

    # ============================================================================
    # populate: assign text variables to each of the entry widgets
    # ============================================================================
    def populate(self, header_text: list[str], balloon_text: list[str],
                 sub_header_text: list[str], row_header_text: list[str],
                 data_vars: dict[tuple[int,int],str], summary_header_texts: list[str],
                 summary_sub_texts: list[str], summary_vars: list[list[str]],
                 bottom_header_text: str, bottom_row_vars: list[str]):
        balloon_text = list(balloon_text)

        # bottom row
        self.bottom_title_widgets[0].configure(textvariable=tk.StringVar(value=bottom_header_text))

        for c, bw in enumerate(self.bottom_widgets):
            bw.configure(textvariable=tk.StringVar(value=bottom_row_vars[c]))

        # the summary header
        for col in range(self.num_summary_col):
            self.summary_header_widgets[col].configure(textvariable=tk.StringVar(value=summary_header_texts[col]))

        # the summary sub header
        for col in range(self.num_summary_sub_col):
            self.summary_sub_header_widgets[col].configure(textvariable=tk.StringVar(value=summary_sub_texts[col]))

            # the summary data
            for row in range(self.num_rows):
                widget = self.get_summary_widget(row, col)
                if widget:
                    widget.configure(textvariable=tk.StringVar(value=summary_vars[row][col]))

        # the data grid
        for col in range(self.num_cols):
            for row in range(self.num_rows):
                widget = self.get_widget(row, col)

                bg = widget.cget('bg')
                value = data_vars[row,col] if float(data_vars[row,col]) != 0.0 else ""

                widget.configure(textvariable=tk.StringVar(value=value))
                widget.configure(bg=bg)

        # the header data
        i = 0
        for ht in header_text:
            self.header_widgets[i].configure(textvariable=tk.StringVar(value=ht))
            Hovertip(self.header_widgets[i], balloon_text[i])
            i += 1

        # the sub header data
        i = 0
        for sht in sub_header_text:
            if len(self.sub_header_widgets) > i:
                self.sub_header_widgets[i].configure(textvariable=tk.StringVar(value=sht))
                i += 1
            else:
                break

        # the row header
        i = 0
        for rht in row_header_text:
            self.title_widgets[i].configure(textvariable=tk.StringVar(value=rht))
            i += 1

        # get the panes to match their internal structure
        for pane in self.panes:
            pane.after(10, lambda *_: pane.configure_interior(*_))
        #self.header_frame.after(10, lambda *_: self.header_frame.winfo_toplevel().geometry("800x800"))

    def get_summary_widget(self, row, col):
        return self.summary_widgets.get(row, dict()).get(col, None)

    def get_widget(self, row, col):
        return self.entry_widgets[row,col]


    # # ============================================================================
    # # navigation routines
    # # ============================================================================
    # def _move(self, where, ev):
    #     w: tk.Entry = ev.widget
    #
    #     w.selection_clear()
    #     row, col = self.get_row_col(w)
    #
    #     # TODO: Find out why using tab sends KeyError -1, but still works
    #     if where == 'nextRow':
    #         row = min(max(row+1, 0), self.num_rows - 1)
    #     elif where == 'prevRow':
    #         row = min(max(row-1, 0), self.num_rows - 1)
    #     elif where == 'nextCell':
    #         col = min(max(col+1, 0), self.num_cols - 1)
    #     elif where == 'prevCell':
    #         col = min(max(col-1, 0), self.num_cols - 1)
    #
    #     e = self.get_widget(row, col)
    #     self.set_focus(e)
    #
    #     # forces Tk to not continue applying any binding routines after this
    #     return "break"
    #
    # # ----------------------------------------------------------------------------
    # # what to do when the widget gets the focus
    # # ----------------------------------------------------------------------------
    # def set_focus(self, e):
    #     self.center_col.see(e)
    #     e.focus()
    #
    # # ----------------------------------------------------------------------------
    # # focus has changed - indicate what row/col we are on, callback process change
    # # ----------------------------------------------------------------------------
    # def focus_changed(self, inout, e, *_, colour = None):
    #     w: tk.Entry = e.widget
    #     if inout == "focusIn":
    #         w.selection_range(0, 'end')
    #     else:
    #         w.selection_clear()
    #
    #     # set_default_fonts_and_colours data Colour and totals Colour
    #     dcolour = colour or bg_colour
    #     tcolour = colour
    #
    #     # are we processing a 'data change'?
    #     original_colour = w.cget('bg')
    #     data_changed = original_colour == needs_update_colour and inout == 'focusOut'
    #
    #     # get the widget
    #     r, c = self.get_row_col(w)
    #
    #     # set_default_fonts_and_colours colors for rows (data)
    #     col_colour = colour.add(dcolour, self.column_colours.get(c))
    #     for row in range(self.num_rows):
    #         wid = self.get_widget(row, c)
    #         wid.configure(bg=col_colour)
    #
    #     # set_default_fonts_and_colours colors for cols (data)
    #     for col in range(self.num_cols):
    #         wid = self.get_widget(r, col)
    #         col_colour = colour.add(dcolour, self.column_colours.get(col))
    #         wid.configure(bg=col_colour)
    #
    #     # set_default_fonts_and_colours Colour for row header
    #     widget = self.title_widgets[r]
    #     widget.configure(disabledbackground=dcolour)
    #
    #     # set_default_fonts_and_colours colors for totals row
    #     if tcolour:
    #         tcolour = colour.add(tcolour, totals_colour)
    #     else:
    #         tcolour = totals_colour
    #
    #     for col in range(self.num_totals_sub_col):
    #         widget = self.summary_widgets[r][col]
    #         widget.configure(disabledbackground=tcolour)
    #
    #     # callback (only if data has changed) (indicated by the current Colour)
    #     if data_changed:
    #         self.process_data_change_handler(r, c)
    #
    # def widgets_row(self, row):
    #     widgets = []
    #     for col in range(self.num_cols):
    #         widgets.append(self.entry_widgets[row][col])
    #     return widgets
    #
    # def widgets_col(self, col) -> list[tk.Entry]:
    #     widgets = []
    #     for row in range(self.num_rows):
    #         widgets.append(self.entry_widgets[row][col])
    #     return widgets
    #
    # def get_row_col(self, widget: tk.Entry) -> tuple[int, int]:
    #     return tuple(self.widgets_row_col.get(widget, ()))
    #
    # @property
    # def num_totals_col(self):
    #     return len(self.summary_header_widgets)
    #
    # @property
    # def num_totals_sub_col(self):
    #     return len(self.summary_sub_header_widgets)
    #






"""
#!/usr/bin/perl
use strict;
use warnings;

# =================================================================
# Allocation Grid
# -----------------------------------------------------------------
# INPUTS:
#   frame
#   rows            - number of rows in the grid
#   col_merge       - array of numbers, where each item is used to
#                     represent a group of columns (affects colouring)
#   summary_merge    - array of numbers, where each item is used to
#                     represent a group of columns in the 'totals'
#                     section
#   fonts           - hash of fonts,
#                     required: small
#   cb_data_entry               - event handler
#   cb_process_data_change      - event handler
#   cb_bottom_row_ok            - event handler
#
# METHODS:
#   populate        - sets text variables to entry widgets
#                     ... in other words, all data info is available outside of this class
#    - header_text        array containing the main category texts
#    - balloon_text       array of mouse over text for headers
#    - sub_header_text    array of text for each sub header
#    - row_header_text    array of text for each row header
#    - data_vars          array of arrays for each data entry widget
#    - summary_header_texts array of texts for totals column titles
#    - summary_sub_texts    array of texts for totals sub column titles
#    - summary_vars         array of arrays for each total data entry widget
#    - bottom_header_text last bottom row text
#    - bottom_row_vars    array for each bottom data entry widget
#
# RETURNS:
#   - nothing -
#
# REQUIRED EVENT HANDLERS:
#    cb_data_entry              (row, col, proposed_new_text)->bool
#    cb_process_data_change     (row, col)
#    cb_bottom_row_ok           (text_of_entry_widget)->bool
# =================================================================

package AllocationGridTk;
use FindBin;
use Carp;
use Tk;
use lib "$FindBin::Bin/..";
use PerlLib::Colours;
use Tk::Dialog;
use Tk::Menu;
use Tk::LabEntry;
use Tk::Pane;

# ============================================================================
# globals
# ============================================================================
our $Fonts;

my $header_colour1           = "#abcdef";
my $header_colour2           = Colour->lighten( 5, $header_colour1 );
my $very_light_grey          = "#eeeeee";
my $row_col_indicator_colour = Colour->lighten( 5, "#cdefab" );
my $totals_header_colour     = Colour->new("lemonchiffon")->string;
my $totals_colour            = Colour->lighten( 5, $totals_header_colour );
my $fg_colour                = "black";
my $bg_colour                = "white";
my $needs_update_colour      = Colour->new("mistyrose")->string;
my $not_ok_colour            = $needs_update_colour;

# width of the data entry (fixed for now... maybe make it configurable
# at a later date)
my $width = 5;

# generic properties for entry widgets
my %entry_props;

# ============================================================================
# new
# ============================================================================

=head2 new

Creates the Grid.  Is a rather generic grid, even though it is called
AllocationGrid.  Could be repurposed for other things (maybe become a Tk widget)

B<Parameters>

* class - class type

* frame - Tk frame to draw on

* rows - how many rows do you want

* col_merge - array of sub headings 

Example, if you want this for your 2 heading rows
    
    +-------------+----------+--------------------+
    | heading1    | heading2 | heading3           |
    +------+------+----------+------+------+------+
    | sub1 | sub2 | sub1     | sub1 | sub2 | sub3 |
    +------+------+----------+------+------+------+

use col_merge = [2,1,3]

* summary_merge - array to total columns sub headings

* data_entry_callback - a callback function called everytime
there data widget is modified.  row/col are sent as parameters
to the callback

B<Returns>

AllocationGrid object

=cut 

sub new {
    my $class        = shift;
    my $frame        = shift;
    my $rows         = shift;
    my $col_merge    = shift;
    my $summary_merge = shift;
    $Fonts = shift;
 
    my @col_merge              = @$col_merge;
    my $cb_data_entry          = shift;
    my $cb_process_data_change = shift;
    my $cb_bottom_row_ok       = shift;

    my $self = bless {}, $class;
    $self->cb_data_entry($cb_data_entry);
    $self->cb_process_data_change($cb_process_data_change);
    $self->cb_bottom_row_ok($cb_bottom_row_ok);

    # ------------------------------------------------------------------------
    # entry widget properties
    # ------------------------------------------------------------------------
    %entry_props = (
        -width              => $width,
        -relief             => 'flat',
        -borderwidth        => 1,
        -justify            => 'center',
        -font               => $Fonts->{small},
        -fg                 => $fg_colour,
        -disabledforeground => $fg_colour,
        -bg                 => $bg_colour,
        -disabledbackground => $bg_colour,
    );

    # ------------------------------------------------------------------------
    # get rid of anything that is currently on this frame
    # ------------------------------------------------------------------------
    foreach my $w ( $frame->packSlaves ) {
        $w->destroy;
    }

    # ------------------------------------------------------------------------
    # make a 2x3 grid with frames for
    # blank | header | blank
    # teacher | data | totals
    # ------------------------------------------------------------------------
    my $pane = $frame->Frame();
    $pane->pack( -side => 'top', -expand => 1, -fill => 'both' );

    # make the frames
    my $header_frame = $pane->Pane( -sticky => 'nsew' );
    my $row_title_frame    = $pane->Pane( -sticky => 'nsew' );
    my $data_frame   = $pane->Pane( -sticky => 'nsew' );
    my $totals_frame = $pane->Frame();
    my $totals_header_frame = $pane->Frame();
    my $bottom_header_frame = $pane->Pane( -sticky => 'nsew' );
    my $bottom_frame        = $pane->Pane( -sticky => 'nsew' );

    # save them
    $self->header_frame($header_frame);
    $self->data_frame($data_frame);
    $self->row_title_frame($row_title_frame);
    $self->totals_frame($totals_frame);
    $self->totals_header_frame($totals_header_frame);
    $self->bottom_header_frame($bottom_header_frame);
    $self->bottom_frame($bottom_frame);

    # configure the layout
    $header_frame->grid(
        -row    => 0,
        -column => 1,
        -sticky => 'nsew',
        -pady   => 2
    );
    $totals_header_frame->grid(
        -row    => 0,
        -column => 2,
        -padx   => 3,
        -pady   => 2
    );
    $row_title_frame->grid( -row => 1, -column => 0, -sticky => 'nsew', -padx => 3, );
    $data_frame->grid( -row => 1, - column => 1, -sticky => 'nsew', );
    $totals_frame->grid(
        -row    => 1,
        -column => 2,
        -sticky => 'nsew',
        -padx   => 3,

    );
    $bottom_header_frame->grid(
        -row    => 2,
        -column => 0,
        -sticky => 'nsew',
        -padx   => 3,
        -pady   => 2,
    );
    $bottom_frame->grid(
        -row    => 2,
        -column => 1,
        -sticky => 'nsew',
        -pady   => 2,
    );
    $pane->gridColumnconfigure( 0, -weight => 0 );
    $pane->gridColumnconfigure( 1, -weight => 5 );
    $pane->gridColumnconfigure( 2, -weight => 0 );

    # ------------------------------------------------------------------------
    # make scrollbars
    # ------------------------------------------------------------------------
    my $horiz_scroll = $frame->Scrollbar(
        -orient       => 'horizontal',
        -activerelief => 'flat',
        -relief       => 'flat'
    );
    my $vert_scroll = $frame->Scrollbar(
        -orient       => 'vertical',
        -activerelief => 'flat',
        -relief       => 'flat'
    );

    my $scroll_horz_widgets = [ $header_frame, $data_frame, $bottom_frame ];
    $horiz_scroll->pack( -side => 'bottom', -expand => 1, -fill => 'x' );

    # configure widgets so scroll bar works properly
    foreach my $w (@$scroll_horz_widgets) {
        $w->configure(
            -xscrollcommand => sub {
                my (@args) = @_;
                $horiz_scroll->set(@args);
            },
        );
    }

    $horiz_scroll->configure(
        -command => sub {
            foreach my $w (@$scroll_horz_widgets) {
                $w->xview(@_);
            }
        }
    );

    # ------------------------------------------------------------------------
    # make the other stuff
    # ------------------------------------------------------------------------
    $self->make_header_columns($col_merge);
    $self->make_row_titles($rows);
    $self->make_data_grid( $rows, $col_merge );
    $self->make_total_grid( $rows, $summary_merge );
    $self->make_bottom_header();
    $self->make_bottom($col_merge);

    return $self;

}

# ============================================================================
# make the header columns
# ============================================================================
sub make_header_columns {
    my $self      = shift;
    my $col_merge = shift;

    # merged header
    foreach my $header ( 0 .. @$col_merge - 1 ) {

        # frame to hold the merged header, and the sub-headings
        my $mini_frame = $self->header_frame->Frame()->pack( -side => 'left' );

        # widget
        my $me = $mini_frame->Entry(
            %entry_props,
            -disabledbackground => $header_colour1,
            -state              => 'disabled',
        )->pack( -side => 'top', -expand => 0, -fill => 'both' );

        # balloon
        my $balloon = $mini_frame->Balloon();
        push @{ $self->balloon_widgets }, $balloon;

        # change colour every second merged header
        if ( $header % 2 ) {
            $me->configure( -disabledbackground => $header_colour2 );
        }

        # keep these widgets so that they can be configured later
        push @{ $self->header_widgets }, $me;

        # --------------------------------------------------------------------
        # subsections
        # --------------------------------------------------------------------
        foreach my $sub_section ( 1 .. $col_merge->[$header] ) {

            # frame within the mini-frame so we can stack 'left'
            my $hf2 = $mini_frame->Frame()->pack( -side => 'left' );

            # widget
            my $se = $hf2->Entry(
                %entry_props,
                -disabledbackground => $header_colour1,
                -state              => 'disabled',
            )->pack( -side => 'left' );

            # change colour every second merged header
            if ( $header % 2 ) {
                $se->configure( -disabledbackground => $header_colour2 );
            }

            # keep these widgets so that they can be configured later
            push @{ $self->sub_header_widgets }, $se;
        }
    }

    return;
}

# ============================================================================
# bottom row
# ============================================================================
sub make_bottom {
    my $self      = shift;
    my $col_merge = shift;

    # merged header
    foreach my $header ( 0 .. @$col_merge - 1 ) {

        foreach my $sub_section ( 1 .. $col_merge->[$header] ) {

            # widget
            my $se;
            $se = $self->bottom_frame->Entry(
                %entry_props,
                -disabledbackground => $totals_colour,
                -state              => 'disabled',
                -validate           => 'key',
                -validatecommand    => sub {
                    my $n = shift;
                    if ( $self->cb_bottom_row_ok->($n) ) {
                        $se->configure( -disabledbackground => $totals_colour );
                    }
                    else {
                        $se->configure( -disabledbackground => $not_ok_colour );
                    }
                    return 1;
                },
            )->pack( -side => 'left' );

            # keep these widgets so that they can be configured later
            push @{ $self->bottom_widgets }, $se;
        }
    }

    return;
}

# ============================================================================
# bottom row header
# ============================================================================
sub make_bottom_header {
    my $self = shift;

    # widget
    my $se = $self->bottom_header_frame->Entry(
        %entry_props,
        -state => 'disabled',
        -width => 12,
    )->pack( -side => 'top' );

    # keep these widgets so that they can be configured later
    push @{ $self->bottom_title_widgets }, $se;
    return;
}

# ============================================================================
# row titles
# ============================================================================
sub make_row_titles {
    my $self = shift;
    my $rows = shift;

    foreach my $row ( 0 .. $rows - 1 ) {
        my $re = $self->row_title_frame->Entry(
            %entry_props,
            -width => 12,
            -state => 'disabled',
        )->pack( -side => 'top' );

        push @{ $self->title_widgets }, $re;
    }

    return;
}

# ============================================================================
# total grid and total header
# ============================================================================
sub make_total_grid {
    my $self         = shift;
    my $rows         = shift;
    my $summary_merge = shift;

    # totals header
    if (1) {
        foreach my $header ( 0 .. @$summary_merge - 1 ) {

            # frame to hold the totals header, and the sub-headings
            my $mini_frame =
              $self->totals_header_frame->Frame()->pack( -side => 'left' );

            # widget
            my $me = $mini_frame->Entry(
                %entry_props,
                -width              => $width + 1,
                -state              => 'disabled',
                -disabledbackground => $totals_header_colour,
            )->pack( -side => 'top', -expand => 0, -fill => 'both' );

            # keep these widgets so that they can be configured later
            push @{ $self->summary_header_widgets }, $me;

            # subsections
            foreach my $sub_section ( 1 .. $summary_merge->[$header] ) {

                # frame within the mini-frame so we can stack 'left'
                my $hf2 = $mini_frame->Frame()->pack( -side => 'left' );

                # widget
                my $se = $hf2->Entry(
                    %entry_props,
                    -width              => $width + 1,
                    -disabledbackground => $totals_header_colour,
                    -state              => 'disabled',

                )->pack( -side => 'left' );

                # keep these widgets so that they can be configured later
                push @{ $self->summary_sub_header_widgets }, $se;
            }
        }
    }

    # ------------------------------------------------------------------------
    # grid
    # ------------------------------------------------------------------------
    my %totals;
    foreach my $row ( 0 .. $rows - 1 ) {
        my $df1 = $self->totals_frame->Frame()
          ->pack( -side => 'top', -expand => 1, -fill => 'x' );

        # foreach header
        my $col = 0;
        foreach my $header ( 0 .. @$summary_merge - 1 ) {

            # subsections
            foreach my $sub_section ( 1 .. $summary_merge->[$header] ) {

                # data entry box
                my $de = $df1->Entry(
                    %entry_props,
                    -width              => $width + 1,
                    -state              => 'disabled',
                    -disabledbackground => $totals_colour,
                )->pack( -side => 'left' );

                # save row/column with totals entry
                $self->summary_widgets->{$row}{$col} = $de;

                $col++;
            }
        }
    }

    return;
}

# ============================================================================
# data grid
# ============================================================================
sub make_data_grid {
    my $self      = shift;
    my $rows      = shift;
    my $col_merge = shift;

    my %data;
    my $col = 0;
    foreach my $row ( 0 .. $rows - 1 ) {
        my $df1 = $self->data_frame->Frame()
          ->pack( -side => 'top', -expand => 1, -fill => 'x' );

        # foreach header
        $col = 0;
        foreach my $header ( 0 .. @$col_merge - 1 ) {

            # subsections
            foreach my $sub_section ( 1 .. $col_merge->[$header] ) {

                # data entry box
                my $de;
                $de = $df1->Entry(
                    %entry_props,
                    -validate        => 'key',
                    -validatecommand => [
                        sub {
                            $de->configure( -bg => $needs_update_colour );
                            return $self->cb_data_entry->(@_);
                        },
                        $row,
                        $col
                    ],
                    -invalidcommand => sub { $df1->bell },
                )->pack( -side => 'left' );

                # save row/column with dataentry, and vice-versa
                $self->entry_widgets->{$row}{$col} = $de;
                $self->widgets_row_col->{$de} = [ $row, $col ];

                # set colour in column to make it easier to read
                my $colour = $de->cget( -bg );
                $colour = $very_light_grey unless $header % 2;
                $self->column_colours->[$col] = $colour;
                $de->configure( -bg => $colour );

               # set bindings for navigation
               #$de->bind( "<Key-Left>",       [ \&_move, $self, 'prevCell' ] );
               #$de->bind( "<Key-leftarrow>",  [ \&_move, $self, 'prevCell' ] );
               #$de->bind( "<Key-Right>",      [ \&_move, $self, 'nextCell' ] );
               #$de->bind( "<Key-rightarrow>", [ \&_move, $self, 'nextCell' ] );
                $de->bind( "<Tab>",           [ \&_move, $self, 'nextCell' ] );
                $de->bind( "<Key-Return>",    [ \&_move, $self, 'nextRow' ] );
                $de->bind( "<Shift-Tab>",     [ \&_move, $self, 'prevCell' ] );
                $de->bind( "<Key-Up>",        [ \&_move, $self, 'prevRow' ] );
                $de->bind( "<Key-uparrow>",   [ \&_move, $self, 'prevRow' ] );
                $de->bind( "<Key-Down>",      [ \&_move, $self, 'nextRow' ] );
                $de->bind( "<Key-downarrow>", [ \&_move, $self, 'nextRow' ] );

                $de->bind(
                    "<FocusIn>",
                    [
                        \&focus_changed, $self,
                        'focusIn',       $row_col_indicator_colour
                    ]
                );
                $de->bind( "<FocusOut>",
                    [ \&focus_changed, $self, 'focusOut' ] );
                $de->bindtags( [ ( $de->bindtags )[ 1, 0, 2, 3 ] ] );

                $col++;
            }
        }
    }

    return;
}

# ============================================================================
# populate: assign textvariables to each of the entry widgets
# ============================================================================
sub populate {
    my $self               = shift;
    my $header_text        = shift;
    my $balloon_text       = shift;
    my $sub_header_text    = shift;
    my $row_header_text    = shift;
    my $data_vars          = shift;
    my $summary_header_texts = shift;
    my $summary_sub_texts    = shift;
    my $summary_vars         = shift;
    my $bottom_header_text = shift;
    my $bottom_row_vars    = shift;

    # bottom row
    my $bottom_header_widget = $self->bottom_title_widgets->[0];
    $bottom_header_widget->configure( -textvariable => $bottom_header_text );

    my $bottom_widgets = $self->bottom_widgets;
    foreach my $col ( 0 .. scalar(@$bottom_widgets) - 1 ) {
        $bottom_widgets->[$col]
          ->configure( -textvariable => $bottom_row_vars->[$col] );
    }

    # the totals header
    my $summary_widgets = $self->summary_header_widgets;
    foreach my $col ( 0 .. $self->num_totals_col - 1 ) {
        $summary_widgets->[$col]
          ->configure( -textvariable => \$summary_header_texts->[$col] );
    }

    # the totals sub header
    my $totals_sub_widgets = $self->summary_sub_header_widgets;
    foreach my $col ( 0 .. $self->num_totals_sub_col - 1 ) {
        $totals_sub_widgets->[$col]
          ->configure( -textvariable => \$summary_sub_texts->[$col] );
    }

    # the totals data
    foreach my $col ( 0 .. $self->num_totals_sub_col - 1 ) {

        foreach my $row ( 0 .. $self->num_rows - 1 ) {
            my $widget = $self->get_totals_widget( $row, $col );
            $widget->configure( -textvariable => $summary_vars->[$row]->[$col] );
        }

    }

    # the data grid
    foreach my $col ( 0 .. $self->num_cols - 1 ) {
        foreach my $row ( 0 .. $self->num_rows - 1 ) {
            my $widget = $self->get_widget( $row, $col );

            # note... want the widget colour to go back to what it was,
            # even if the data has changed
            my $bg = $widget->cget( -bg );
            $widget->configure( -textvariable => $data_vars->[$row][$col] );
            $widget->configure( -bg           => $bg );
        }
    }

    # the header data
    my $i               = 0;
    my $header_widgets  = $self->header_widgets;
    my $balloon_widgets = $self->balloon_widgets;
    while ( my $var = shift @$header_text ) {
        $header_widgets->[$i]->configure( -textvariable => \$var );
        $balloon_widgets->[$i]
          ->attach( $header_widgets->[$i], -msg => $balloon_text->[$i] );
        $i++;
    }

    # the sub header data
    $i = 0;
    my $sub_header_widgets = $self->sub_header_widgets;
    while ( my $var = shift @$sub_header_text ) {
        if ( exists $sub_header_widgets->[$i] ) {
            $sub_header_widgets->[$i]->configure( -textvariable => \$var );
            $i++;
        }
    }

    # the row header
    $i = 0;
    my $title_widgets = $self->title_widgets;
    while ( my $var = shift @$row_header_text ) {
        $title_widgets->[$i]->configure( -textvariable => \$var );
        $i++;
    }

}

# ============================================================================
# navigation routines
# ============================================================================

sub _move {
    my $w     = shift;
    my $self  = shift;
    my $where = shift;
    $w->selectionClear();
    my ( $row, $col ) = $self->get_row_col($w);

    my $old_row = $row;
    my $old_col = $col;

    $row = int_clamp( ++$row, $self->num_rows ) if $where eq 'nextRow';
    $row = int_clamp( --$row, $self->num_rows ) if $where eq 'prevRow';
    $col = int_clamp( ++$col, $self->num_cols ) if $where eq 'nextCell';
    $col = int_clamp( --$col, $self->num_cols ) if $where eq 'prevCell';

    my $e = $self->get_widget( $row, $col );
    $self->set_focus($e);

    # forces Tk to not continue applying any binding routines after this
    $w->break();
}

# ----------------------------------------------------------------------------
# what to do when the widget gets the focus
# ----------------------------------------------------------------------------
sub set_focus {
    my $self = shift;
    my $e    = shift;
    if ($e) {
        my ( $r, $c ) = $self->get_row_col($e);
        $self->header_frame->see($e);
        $self->data_frame->see($e);
        $self->bottom_frame->see( $self->bottom_widgets->[$c] );
        $e->focus();
    }
}

# ----------------------------------------------------------------------------
# focus has changed - indicate what row/col we are on, callback process change
# ----------------------------------------------------------------------------
sub focus_changed {
    my $w      = shift;
    my $self   = shift;
    my $inout  = shift;
    my $colour = shift;

    # update selection
    if ( $inout eq 'focusIn' ) {
        $w->selectionRange( 0, 'end' );
    }
    else {
        $w->selectionClear();
    }

    # set data colour and totals colour
    my $dcolour = $colour || $bg_colour;
    my $tcolour = $colour;

    # are we processing a 'data change?'
    my $original_colour = $w->cget( -bg );
    my $data_changed =
      $original_colour eq $needs_update_colour && $inout eq 'focusOut';

    # get the widget
    my ( $row, $col ) = $self->get_row_col($w);

    # set colours for rows (data)
    my $col_colour = Colour->add( $dcolour, $self->column_colours->[$col] );
    foreach my $row ( 0 .. $self->num_rows - 1 ) {
        my $e = $self->get_widget( $row, $col );
        $e->configure( -bg => $col_colour );
    }

    # set colours for cols (data)
    foreach my $col ( 0 .. $self->num_cols - 1 ) {
        my $e = $self->get_widget( $row, $col );
        $col_colour = Colour->add( $dcolour, $self->column_colours->[$col] );
        $e->configure( -bg => $col_colour );
    }

    # set colour for row header
    my $widget = $self->title_widgets->[$row];
    $widget->configure( -disabledbackground => $dcolour );

    # set colours for totals row
    no warnings;
    if ($tcolour) {
        $tcolour = Colour->add( $tcolour, $totals_colour );
    }
    else {
        $tcolour = $totals_colour;
    }
    foreach my $col ( 0 .. $self->num_totals_sub_col - 1 ) {
        $widget = $self->summary_widgets->{$row}{$col};
        $widget->configure( -disabledbackground => $tcolour );
    }

    # callback (only if data has changed) (indicated by the current colour)
    $self->update_data( $row, $col ) if $data_changed;
}

# ----------------------------------------------------------------------------
# return a number between 0 and $max (non inclusive)
# ----------------------------------------------------------------------------
sub int_clamp {
    my $num = shift;
    my $max = shift;
    return 0 if $num < 0;
    return $max - 1 if $num > $max - 1;
    return $num;
}

# ============================================================================
# Getters and setters
# ============================================================================

# ----------------------------------------------------------------------------
# frames
# ----------------------------------------------------------------------------
# Subroutine names are "header_frame", "data_frame", etc.

foreach
  my $frame (qw(header data row totals totals_header bottom bottom_header))
{
    no strict 'refs';
    *{ $frame . "_frame" } = sub {
        my $self = shift;
        $self->{ "-" . $frame . "_frame" } = shift if @_;
        return $self->{ "-" . $frame . "_frame" };
      }
}

# ----------------------------------------------------------------------------
# widgets
# ----------------------------------------------------------------------------
# Subroutine names are "header_widgets",  etc.

foreach my $widget (
    qw(header balloon sub_header row_header totals_header totals_sub_header bottom_header bottom)
  )
{
    no strict 'refs';
    *{ $widget . "_widgets" } = sub {
        my $self = shift;
        $self->{ "-" . $widget . "_widgets" } = shift if @_;
        $self->{ "-" . $widget . "_widgets" } = []
          unless $self->{ "-" . $widget . "_widgets" };
        return $self->{ "-" . $widget . "_widgets" };
      }
}

# ----------------------------------------------------------------------------
# other getters and setters
# ----------------------------------------------------------------------------
sub cb_process_data_change {
    my $self = shift;
    $self->{-process_data_change} = sub { return 1; }
      unless $self->{-process_data_change};
    $self->{-process_data_change} = shift if @_;
    return $self->{-process_data_change};
}

sub cb_data_entry {
    my $self = shift;
    $self->{-process_data_entry} = sub { return 1; }
      unless $self->{-process_data_entry};
    $self->{-process_data_entry} = shift if @_;
    return $self->{-process_data_entry};
}

sub cb_bottom_row_ok {
    my $self = shift;
    $self->{-bottom_row_ok} = sub { return 1; }
      unless $self->{-bottom_row_ok};
    $self->{-bottom_row_ok} = shift if @_;
    return $self->{-bottom_row_ok};
}

sub update_data {
    my $self = shift;
    my $row  = shift;
    my $col  = shift;
    $self->cb_process_data_change->( $row, $col );
}

sub column_colours {
    my $self = shift;
    $self->{-col_colours} = [] unless $self->{-col_colours};
    $self->{-col_colours} = shift if @_;
    return $self->{-col_colours};
}

sub entry_widgets {
    my $self = shift;
    $self->{-widgets} = {} unless $self->{-widgets};
    $self->{-widgets} = shift if @_;
    return $self->{-widgets};
}

sub summary_widgets {
    my $self = shift;
    $self->{-twidgets} = {} unless $self->{-twidgets};
    $self->{-twidgets} = shift if @_;
    return $self->{-twidgets};
}

sub widgets_row_col {
    my $self = shift;
    $self->{-widgets_row_col} = shift if @_;
    $self->{-widgets_row_col} = {} unless $self->{-widgets_row_col};
    return $self->{-widgets_row_col};
}

sub widgets_row {
    my $self    = shift;
    my $row     = shift;
    my $widgets = $self->entry_widgets;
    my @widgets;
    foreach my $col ( 0 .. $self->num_cols - 1 ) {
        push @widgets, $widgets->{$row}{$col};
    }
    return \@widgets;
}

sub widgets_col {
    my $self    = shift;
    my $col     = shift;
    my $widgets = $self->entry_widgets;
    my @widgets;
    foreach my $row ( 0 .. $self->num_rows - 1 ) {
        push @widgets, $widgets->{$row}{$col};
    }
    return \@widgets;
}

sub get_widget {
    my $self    = shift;
    my $row     = shift;
    my $col     = shift;
    my $widgets = $self->entry_widgets;
    return $widgets->{$row}{$col};
}

sub get_row_col {
    my $self     = shift;
    my $widget   = shift;
    my $row_cols = $self->widgets_row_col;
    return @{ $row_cols->{$widget} };
}

sub num_rows {
    my $self = shift;
    my $rows = $self->title_widgets;
    return scalar( @{$rows} );
}

sub num_cols {
    my $self = shift;
    my $cols = $self->sub_header_widgets;
    return scalar( @{$cols} );
}

sub get_totals_widget {
    my $self    = shift;
    my $row     = shift;
    my $col     = shift;
    my $widgets = $self->summary_widgets;
    return $widgets->{$row}{$col};
}

sub num_totals_col {
    my $self = shift;
    my $cols = $self->summary_header_widgets;
    return scalar( @{$cols} );
}

sub num_totals_sub_col {
    my $self = shift;
    my $cols = $self->summary_sub_header_widgets;
    return scalar( @{$cols} );
}

1;

"""