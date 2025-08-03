import schedule.Utilities.Colour as colour
import tkinter as tk
from schedule.Tk.Scrolled import Scrolled
from functools import partial
from idlelib.tooltip import Hovertip


# ============================================================================
# globals
# ============================================================================

# fonts
header_colour1           = "#abcdef"
header_colour2           = colour.lighten(header_colour1, 5)
very_light_grey          = "#eeeeee"
row_col_indicator_colour = colour.lighten("#cdefab", 5)
totals_header_colour     = colour.string("lemonchiffon")
totals_colour            = colour.lighten(totals_header_colour, 5)
fg_colour                = "black"
bg_colour                = "white"
needs_update_colour      = colour.string("mistyrose")
not_ok_colour            = needs_update_colour

width = 5


class AllocationGridTk:
    def __init__(self, frame: Scrolled, rows,
                 col_merge: list[list[int]], totals_merge: list[list[int]], fonts,
                 cb_data_entry = lambda *_, **__: True,
                 cb_process_data_change = lambda *_, **__: True,
                 cb_bottom_row_ok = lambda *_, **__: True):
        """

        :param frame: where to put this grid
        :param rows: number of rows in the grid
        :param col_merge: list, each item represents a group of columns (affects colouring)
        :param totals_merge: list, each item represents a group of columns in the totals sections
        :param fonts: hash of fonts (required... small font)
        :param cb_data_entry:
        :param cb_process_data_change:
        :param cb_bottom_row_ok:
        """

        self.data_entry_handler = cb_data_entry
        self.process_data_change_handler = cb_process_data_change
        self.bottom_row_ok_handler = cb_bottom_row_ok

        # ------------------------------------------------------------------------
        # entry widget properties
        # ------------------------------------------------------------------------
        self.entry_props = {
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
        for w in frame.winfo_children():
            w.destroy()

        # make the frames
        self._make_frames(frame)

        # ------------------------------------------------------------------------
        # make a 2x3 grid with frames for
        # blank   | header | blank
        # teacher | data   | totals
        # ------------------------------------------------------------------------
        # pane = tk.Frame(frame.widget)
        # pane.pack(expand=1, fill='both')
        #
        # pane.configure(bg='pink')

        # # TODO: Verify if center_col causes alignment issues w/ rest of table
        # # If it does, revert to what the Perl ver did, creating a scrollbar and binding to
        # # all three objects
        # self.center_col = Scrolled(pane, 'Frame', scrollbars='s')
        # self.center_col.forget()
        # self.center_col.configure(bg='lime')
        #
        # self.header_frame = tk.Frame(self.center_col.widget)
        # self.row_title_frame = tk.Frame(pane)
        # self.row_title_frame.configure(bg='red')
        #
        # self.data_frame = tk.Frame(self.center_col.widget)
        # self.totals_frame = tk.Frame(pane)
        # self.totals_frame.configure(bg='blue')
        #
        # self.totals_header_frame = tk.Frame(pane)
        # self.totals_header_frame.configure(bg='green')
        #
        # self.bottom_header_frame = tk.Frame(pane)
        # self.bottom_header_frame.configure(bg='yellow')
        #
        # self.bottom_frame = tk.Frame(self.center_col.widget)
        # self.bottom_frame.configure(bg='purple')
        #
        # pane.grid_columnconfigure(0, weight=0)
        # pane.grid_columnconfigure(1, weight=5)
        # pane.grid_columnconfigure(2, weight=0)
        #
        # self.header_frame.grid(row=0, column=0, sticky='nsew', pady=2)
        # self.data_frame.grid(row=1, column=0, sticky='nsew')
        # self.bottom_frame.grid(row=2, column=0, sticky='nsew', pady=2)
        #
        # # configure the layout
        # self.center_col.grid(row=0, column=1, rowspan=3, sticky='nsew')
        # self.totals_header_frame.grid(row=0, column=2, padx=3, pady=2)
        # self.row_title_frame.grid(row=1, column=0, sticky='nsew', padx=3)
        # self.totals_frame.grid(row=1, column=2, sticky='nsew', padx=3)
        # self.bottom_header_frame.grid(row=2, column=0, sticky='nsew', padx=3, pady=2)
        #
        # scroll_options = {'relief': 'flat', 'activerelief': 'flat'}
        # frame.vertical_scrollbar.configure(**scroll_options)
        # self.center_col.horizontal_scrollbar.configure(**scroll_options)

        # ------------------------------------------------------------------------
        # make the other stuff
        # ------------------------------------------------------------------------
        self.header_widgets: list[tk.Entry] = []
        self.sub_header_widgets: list[tk.Entry] = []
        self.bottom_widgets: list[tk.Entry] = []
        self.bottom_header_widgets: list[tk.Entry] = []
        self.row_header_widgets: list[tk.Entry] = []
        self.totals_header_widgets: list[tk.Entry] = []
        self.totals_sub_header_widgets: list[tk.Entry] = []
        self.totals_widgets: dict[int, dict[int, tk.Entry]] = dict()
        self.entry_widgets: dict[int, dict[int, tk.Entry]] = dict()
        self.widgets_row_col: dict[tk.Entry, list[int]] = dict()
        self.column_colours: dict[int, str] = dict()

        self.make_header_columns(col_merge)
        self.make_row_titles(rows)
        self.make_data_grid(rows, col_merge)
        self.make_total_grid(rows, totals_merge)
        self.make_bottom_header()
        self.make_bottom(col_merge)

    def _make_frames(self, frame):
        # ------------------------------------------------------------------------
        # make a 3x3 grid with frames for
        # [--------------------------------]
        # [   blank  | header | blank      ]
        # [ [--------------------------]   ]
        # [ [ titles | data   | totals ] ^ ]
        # [ [ titles | data   | totals ] | ]
        # [ [ titles | data   | totals ] v ]
        # [ [--------------------------]   ]
        # [ [ blank  | bottom | blank  ]   ]
        # [          <========>            ]
        # [--------------------------------]
        #
        # ... middle column must be scrollable horizontal
        #
        # ... whole frame has to be scrollable vertically
        #
        # ... but everything has to line up (grid rows all have to be the same size ??)
        # ------------------------------------------------------------------------
        pane = Scrolled(frame, "Frame", scrollbars="e").widget
        pane.pack(side='top', expand=1, fill='both')

        # make the frames
        self.header_frame = Scrolled(pane, "Frame", scrollbars='s').widget
        self.center_frame = Scrolled(pane, "Frame", scrollbars='e').widget
        self.row_title_frame = tk.Frame(pane)
        self.data_frame = tk.Frame(pane)
        self.totals_frame = tk.Frame(pane)
        self.bottom_frame = tk.Frame(pane)


        """ 
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


        :return: 
        """
    # ============================================================================
    # make the header columns
    # ============================================================================
    def make_header_columns(self, col_merge: list):
        prop = self.entry_props.copy()
        prop['disabledbackground'] = header_colour1
        prop['state'] = 'disabled'

        # merged header
        for i, header in enumerate(col_merge):
            # frame to hold the merged header, and the subheadings
            mini_frame = tk.Frame(self.header_frame)
            mini_frame.pack(side='left')

            # widget
            me = tk.Entry(mini_frame, **prop)
            me.pack(side='top', expand=0, fill='both')

            # change Colour every second merged header
            if i % 2:
                me.configure(disabledbackground=header_colour2)

            # keep these widgets so that they can be configured later
            self.header_widgets.append(me)

            # --------------------------------------------------------------------
            # subsections
            # --------------------------------------------------------------------
            for sub_section in range(1, header()):
                # frame within the mini-frame, so we can stack 'left'
                (hf2 := tk.Frame(mini_frame)).pack(side='left')

                # widget
                (se := tk.Entry(hf2, **prop)).pack(side='left')

                # change Colour every second merged header
                if i % 2:
                    se.configure(disabledbackground=header_colour2)

                # keep these widgets so that they can be configured later
                self.sub_header_widgets.append(se)

    # ============================================================================
    # bottom row
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
            for sub_section in range(1, header()):
                # widget
                prop = self.entry_props.copy()
                prop['disabledbackground'] = header_colour1
                se = tk.Entry(self.bottom_frame, **prop, state='disabled', validate='key')
                se.configure(validatecommand=(se.register(validate), '%P', '%W'))
                se.pack(side='left')

                # keep these widgets so that they can be configured later
                self.bottom_widgets.append(se)

    # ============================================================================
    # bottom row header
    # ============================================================================
    def make_bottom_header(self):
        prop = self.entry_props.copy()
        prop['width'] = 12

        # widget
        se = tk.Entry(self.bottom_header_frame, **prop, state='disabled')

        # keep these widgets so that they can be configured later
        self.bottom_header_widgets.append(se)

    # ============================================================================
    # row titles
    # ============================================================================
    def make_row_titles(self, rows):
        prop = self.entry_props.copy()
        prop['width'] = 12
        for _ in range(rows):
            re = tk.Entry(self.row_title_frame, **prop, state='disabled')
            re.pack(side='top')

            self.row_header_widgets.append(re)

    # ============================================================================
    # total grid and total header
    # ============================================================================
    def make_total_grid(self, rows, totals_merge):
        prop = self.entry_props.copy()
        prop['width'] = width + 1
        prop['disabledbackground'] = totals_header_colour
        prop['state'] = 'disabled'

        # totals header
        for header in totals_merge:
            # frame to hold the totals header, and the subheadings
            (mini_frame := tk.Frame(self.totals_header_frame)).pack(side='left')

            # widget
            (me := tk.Entry(mini_frame, **prop)).pack(side='top', expand=0, fill='both')

            # keep these widgets so that they can be configured later
            self.totals_header_widgets.append(me)

            for sub_section in range(1, header):
                # frame within the mini-frame so we can stack left
                (hf2 := tk.Frame(mini_frame)).pack(side='left')

                # widget
                (se := tk.Entry(hf2, **prop)).pack(side='left')

                # keep these widgets so that they can be configured later
                self.totals_sub_header_widgets.append(se)

        for row in range(rows):
            (df1 := tk.Frame(self.totals_frame)).pack(side='top', expand=1, fill='x')

            # foreach header
            col = 0
            for header in range(len(totals_merge)):
                # subsections
                for _ in range(1, totals_merge[header]):
                    # data entry box
                    (de := tk.Entry(df1, **prop)).pack(side='left')

                    # save row/column with totals entry
                    if row not in self.totals_widgets:
                        self.totals_widgets[row] = {}
                    self.totals_widgets[row][col] = de
                    col += 1

    # ============================================================================
    # data grid
    # ============================================================================
    def make_data_grid(self, rows, col_merge: list):
        def validate(r, c, n, w):
            widget = self.data_frame.nametowidget(w)
            widget.configure(bg=needs_update_colour)
            return self.data_entry_handler([r, c, n])  # what is the point of this?

        for row in range(rows):
            (df1 := tk.Frame(self.data_frame)).pack(side='top', expand=1, fill='x')

            # foreach header
            col: int = 0
            for i, header in enumerate(col_merge):
                # subsections
                for subsection in range(header()):

                    # data entry box
                    de = tk.Entry(df1, **self.entry_props, validate='key')
                    de.configure(validatecommand=(de.register(partial(validate, row, col)), '%P', '%W'))
                    de.configure(invalidcommand=de.register(df1.bell))
                    de.pack(side='left')

                    # save row/column with dataentry, and vice-versa
                    if row not in self.entry_widgets:
                        self.entry_widgets[row] = {}
                    self.entry_widgets[row][col] = de
                    self.widgets_row_col[de] = [row, col]

                    # set_default_fonts_and_colours Colour in column to make it easier to read
                    de_colour = de.cget('bg')
                    if i % 2:
                        de_colour = very_light_grey
                    self.column_colours[col] = de_colour
                    de.configure(bg=de_colour)

                    # set_default_fonts_and_colours bindings for navigation
                    # de.bind("<Key-Left>", partial(self._move, 'prevCell'))
                    # de.bind("<Key-leftarrow>", partial(self._move, 'prevCell'))
                    # de.bind("<Key-Right>", partial(self._move, 'nextCell'))
                    # de.bind("<Key-rightarrow>", partial(self._move, 'nextCell'))
                    de.bind("<Tab>", partial(self._move, 'nextCell'))
                    de.bind("<Key-Return>", partial(self._move, 'nextRow'))
                    de.bind("<Shift-Tab>", partial(self._move, 'prevCell'))
                    de.bind("<Key-Up>", partial(self._move, 'prevRow'))
                    de.bind("<Key-uparrow>", partial(self._move, 'prevRow'))
                    de.bind("<Key-Down>", partial(self._move, 'nextRow'))
                    de.bind("<Key-downarrow>", partial(self._move, 'nextRow'))

                    de.bind("<FocusIn>", partial(self.focus_changed, 'focusIn', colour=row_col_indicator_colour))
                    de.bind("<FocusOut>", partial(self.focus_changed, 'focusOut'))
                    de.bindtags([*de.bindtags(), 1, 0, 2, 3])

                    col += 1

    # ============================================================================
    # populate: assign text variables to each of the entry widgets
    # ============================================================================
    def populate(self, header_text: list[str], balloon_text: list[str],
                 sub_header_text: list[str], row_header_text: list[str],
                 data_vars: list[list[str]], total_header_texts: list[str],
                 total_sub_texts: list[str], total_vars: list[list[str]],
                 bottom_header_text: str, bottom_row_vars: list[str]):
        balloon_text = list(balloon_text)

        # bottom row
        self.bottom_header_widgets[0].configure(textvariable=tk.StringVar(value=bottom_header_text))

        for c, bw in enumerate(self.bottom_widgets):
            bw.configure(textvariable=tk.StringVar(value=bottom_row_vars[c]))

        # the totals header
        for col in range(self.num_totals_col):
            self.totals_header_widgets[col].configure(textvariable=tk.StringVar(value=total_header_texts[col]))

        # the totals sub header
        for col in range(self.num_totals_sub_col):
            self.totals_sub_header_widgets[col].configure(textvariable=tk.StringVar(value=total_sub_texts[col]))

            # the totals data
            for row in range(self.num_rows):
                widget = self.get_totals_widget(row, col)
                if widget:
                    widget.configure(textvariable=tk.StringVar(value=total_vars[row][col]))

        # the data grid
        for col in range(self.num_cols):
            for row in range(self.num_rows):
                widget = self.get_widget(row, col)

                # note... want the widget Colour to go back to what it was,
                # even if the data has changed
                bg = widget.cget('bg')
                widget.configure(textvariable=tk.StringVar(value=data_vars[row][col]))
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
            self.row_header_widgets[i].configure(textvariable=tk.StringVar(value=rht))
            i += 1

    # ============================================================================
    # navigation routines
    # ============================================================================
    def _move(self, where, ev):
        w: tk.Entry = ev.widget

        w.selection_clear()
        row, col = self.get_row_col(w)

        # TODO: Find out why using tab sends KeyError -1, but still works
        if where == 'nextRow':
            row = min(max(row+1, 0), self.num_rows - 1)
        elif where == 'prevRow':
            row = min(max(row-1, 0), self.num_rows - 1)
        elif where == 'nextCell':
            col = min(max(col+1, 0), self.num_cols - 1)
        elif where == 'prevCell':
            col = min(max(col-1, 0), self.num_cols - 1)

        e = self.get_widget(row, col)
        self.set_focus(e)

        # forces Tk to not continue applying any binding routines after this
        return "break"

    # ----------------------------------------------------------------------------
    # what to do when the widget gets the focus
    # ----------------------------------------------------------------------------
    def set_focus(self, e):
        self.center_col.see(e)
        e.focus()

    # ----------------------------------------------------------------------------
    # focus has changed - indicate what row/col we are on, callback process change
    # ----------------------------------------------------------------------------
    def focus_changed(self, inout, e, *_, colour = None):
        w: tk.Entry = e.widget
        if inout == "focusIn":
            w.selection_range(0, 'end')
        else:
            w.selection_clear()

        # set_default_fonts_and_colours data Colour and totals Colour
        dcolour = colour or bg_colour
        tcolour = colour

        # are we processing a 'data change'?
        original_colour = w.cget('bg')
        data_changed = original_colour == needs_update_colour and inout == 'focusOut'

        # get the widget
        r, c = self.get_row_col(w)

        # set_default_fonts_and_colours colors for rows (data)
        col_colour = colour.add(dcolour, self.column_colours.get(c))
        for row in range(self.num_rows):
            wid = self.get_widget(row, c)
            wid.configure(bg=col_colour)

        # set_default_fonts_and_colours colors for cols (data)
        for col in range(self.num_cols):
            wid = self.get_widget(r, col)
            col_colour = colour.add(dcolour, self.column_colours.get(col))
            wid.configure(bg=col_colour)

        # set_default_fonts_and_colours Colour for row header
        widget = self.row_header_widgets[r]
        widget.configure(disabledbackground=dcolour)

        # set_default_fonts_and_colours colors for totals row
        if tcolour:
            tcolour = colour.add(tcolour, totals_colour)
        else:
            tcolour = totals_colour

        for col in range(self.num_totals_sub_col):
            widget = self.totals_widgets[r][col]
            widget.configure(disabledbackground=tcolour)

        # callback (only if data has changed) (indicated by the current Colour)
        if data_changed:
            self.process_data_change_handler(r, c)

    def widgets_row(self, row):
        widgets = []
        for col in range(self.num_cols):
            widgets.append(self.entry_widgets[row][col])
        return widgets

    def widgets_col(self, col) -> list[tk.Entry]:
        widgets = []
        for row in range(self.num_rows):
            widgets.append(self.entry_widgets[row][col])
        return widgets

    def get_widget(self, row, col):
        return self.entry_widgets[row][col]

    def get_row_col(self, widget: tk.Entry) -> tuple[int, int]:
        return tuple(self.widgets_row_col.get(widget, ()))

    @property
    def num_rows(self):
        return len(self.row_header_widgets)

    @property
    def num_cols(self):
        return len(self.sub_header_widgets)

    def get_totals_widget(self, row, col):
        return self.totals_widgets.get(row, dict()).get(col, None)

    @property
    def num_totals_col(self):
        return len(self.totals_header_widgets)

    @property
    def num_totals_sub_col(self):
        return len(self.totals_sub_header_widgets)


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
#   totals_merge    - array of numbers, where each item is used to
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
#    - total_header_texts array of texts for totals column titles
#    - total_sub_texts    array of texts for totals sub column titles
#    - total_vars         array of arrays for each total data entry widget
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

* totals_merge - array to total columns sub headings

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
    my $totals_merge = shift;
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
    $self->make_total_grid( $rows, $totals_merge );
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
    push @{ $self->bottom_header_widgets }, $se;
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

        push @{ $self->row_header_widgets }, $re;
    }

    return;
}

# ============================================================================
# total grid and total header
# ============================================================================
sub make_total_grid {
    my $self         = shift;
    my $rows         = shift;
    my $totals_merge = shift;

    # totals header
    if (1) {
        foreach my $header ( 0 .. @$totals_merge - 1 ) {

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
            push @{ $self->totals_header_widgets }, $me;

            # subsections
            foreach my $sub_section ( 1 .. $totals_merge->[$header] ) {

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
                push @{ $self->totals_sub_header_widgets }, $se;
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
        foreach my $header ( 0 .. @$totals_merge - 1 ) {

            # subsections
            foreach my $sub_section ( 1 .. $totals_merge->[$header] ) {

                # data entry box
                my $de = $df1->Entry(
                    %entry_props,
                    -width              => $width + 1,
                    -state              => 'disabled',
                    -disabledbackground => $totals_colour,
                )->pack( -side => 'left' );

                # save row/column with totals entry
                $self->totals_widgets->{$row}{$col} = $de;

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
    my $total_header_texts = shift;
    my $total_sub_texts    = shift;
    my $total_vars         = shift;
    my $bottom_header_text = shift;
    my $bottom_row_vars    = shift;

    # bottom row
    my $bottom_header_widget = $self->bottom_header_widgets->[0];
    $bottom_header_widget->configure( -textvariable => $bottom_header_text );

    my $bottom_widgets = $self->bottom_widgets;
    foreach my $col ( 0 .. scalar(@$bottom_widgets) - 1 ) {
        $bottom_widgets->[$col]
          ->configure( -textvariable => $bottom_row_vars->[$col] );
    }

    # the totals header
    my $totals_widgets = $self->totals_header_widgets;
    foreach my $col ( 0 .. $self->num_totals_col - 1 ) {
        $totals_widgets->[$col]
          ->configure( -textvariable => \$total_header_texts->[$col] );
    }

    # the totals sub header
    my $totals_sub_widgets = $self->totals_sub_header_widgets;
    foreach my $col ( 0 .. $self->num_totals_sub_col - 1 ) {
        $totals_sub_widgets->[$col]
          ->configure( -textvariable => \$total_sub_texts->[$col] );
    }

    # the totals data
    foreach my $col ( 0 .. $self->num_totals_sub_col - 1 ) {

        foreach my $row ( 0 .. $self->num_rows - 1 ) {
            my $widget = $self->get_totals_widget( $row, $col );
            $widget->configure( -textvariable => $total_vars->[$row]->[$col] );
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
    my $row_header_widgets = $self->row_header_widgets;
    while ( my $var = shift @$row_header_text ) {
        $row_header_widgets->[$i]->configure( -textvariable => \$var );
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
    my $widget = $self->row_header_widgets->[$row];
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
        $widget = $self->totals_widgets->{$row}{$col};
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

sub totals_widgets {
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
    my $rows = $self->row_header_widgets;
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
    my $widgets = $self->totals_widgets;
    return $widgets->{$row}{$col};
}

sub num_totals_col {
    my $self = shift;
    my $cols = $self->totals_header_widgets;
    return scalar( @{$cols} );
}

sub num_totals_sub_col {
    my $self = shift;
    my $cols = $self->totals_sub_header_widgets;
    return scalar( @{$cols} );
}

1;

"""