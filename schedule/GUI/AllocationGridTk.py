# IN PROGRESS
from PerlLib import Colour
from tkinter import Entry, Frame, StringVar
from Tk.scrolled import Scrolled
from functools import partial
from idlelib.tooltip import Hovertip


# ============================================================================
# globals
# ============================================================================

# fonts

header_colour1           = "#abcdef"
header_colour2           = Colour.lighten(header_colour1, 5)
very_light_grey          = "#eeeeee"
row_col_indicator_colour = Colour.lighten("#cdefab", 5)
totals_header_colour     = Colour.string("lemonchiffon")
totals_colour            = Colour.lighten(totals_header_colour, 5)
fg_colour                = "black"
bg_colour                = "white"
needs_update_colour      = Colour.string("mistyrose")
not_ok_colour            = needs_update_colour

# width of the data entry; Perl includes a comment about making if configurable in the future
width = 5


class AllocationGridTk:
    def __init__(self, frame: Scrolled, rows,
                 col_merge, totals_merge, fonts,
                 cb_data_entry = lambda *_, **__: True,
                 cb_process_data_change = lambda *_, **__: True,
                 cb_bottom_row_ok = lambda *_, **__: True):
        self.cb_data_entry = cb_data_entry
        self.cb_process_data_change = cb_process_data_change
        self.cb_bottom_row_ok = cb_bottom_row_ok

        # if any of these are map objects, they can only be converted to a list once
        # so convert them now and pass the lists directly to methods
        col_merge = list(col_merge)
        totals_merge = list(totals_merge)

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
        for w in frame.widget.pack_slaves():
            w.destroy()

        # ------------------------------------------------------------------------
        # make a 2x3 grid with frames for
        # blank   | header | blank
        # teacher | data   | totals
        # ------------------------------------------------------------------------
        pane = Frame(frame.widget)
        pane.pack(expand=1, fill='both')

        pane.configure(bg='pink')

        # make the frames
        # TODO: Verify if center_col causes alignment issues w/ rest of table
        # If it does, revert to what the Perl ver did, creating a scrollbar and binding to
        # all three objects
        self.center_col = Scrolled(pane, 'Frame', scrollbars='s')
        self.center_col.forget()
        self.center_col.configure(bg='lime')
        self.header_frame = Frame(self.center_col.widget)
        self.row_frame = Frame(pane)
        self.row_frame.configure(bg='red')
        self.data_frame = Frame(self.center_col.widget)
        self.totals_frame = Frame(pane)
        self.totals_frame.configure(bg='blue')
        self.totals_header_frame = Frame(pane)
        self.totals_header_frame.configure(bg='green')
        self.bottom_header_frame = Frame(pane)
        self.bottom_header_frame.configure(bg='yellow')
        self.bottom_frame = Frame(self.center_col.widget)
        self.bottom_frame.configure(bg='purple')

        pane.grid_columnconfigure(0, weight=0)
        pane.grid_columnconfigure(1, weight=5)
        pane.grid_columnconfigure(2, weight=0)

        self.header_frame.grid(row=0, column=0, sticky='nsew', pady=2)
        self.data_frame.grid(row=1, column=0, sticky='nsew')
        self.bottom_frame.grid(row=2, column=0, sticky='nsew', pady=2)

        # configure the layout
        self.center_col.grid(row=0, column=1, rowspan=3, sticky='nsew')
        self.totals_header_frame.grid(row=0, column=2, padx=3, pady=2)
        self.row_frame.grid(row=1, column=0, sticky='nsew', padx=3)
        self.totals_frame.grid(row=1, column=2, sticky='nsew', padx=3)
        self.bottom_header_frame.grid(row=2, column=0, sticky='nsew', padx=3, pady=2)

        scroll_options = {'relief': 'flat', 'activerelief': 'flat'}
        frame.vertical_scrollbar.configure(**scroll_options)
        self.center_col.horizontal_scrollbar.configure(**scroll_options)

        # ------------------------------------------------------------------------
        # make the other stuff
        # ------------------------------------------------------------------------
        self.header_widgets: list[Entry] = []
        self.sub_header_widgets: list[Entry] = []
        self.bottom_widgets: list[Entry] = []
        self.bottom_header_widgets: list[Entry] = []
        self.row_header_widgets: list[Entry] = []
        self.totals_header_widgets: list[Entry] = []
        self.totals_sub_header_widgets: list[Entry] = []
        self.totals_widgets: dict[int, dict[int, Entry]] = dict()
        self.entry_widgets: dict[int, dict[int, Entry]] = dict()
        self.widgets_row_col: dict[Entry, list[int, int]] = dict()
        self.column_colours: dict[int, str] = dict()

        self.make_header_columns(col_merge)
        self.make_row_titles(rows)
        self.make_data_grid(rows, col_merge)
        self.make_total_grid(rows, totals_merge)
        self.make_bottom_header()
        self.make_bottom(col_merge)

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
            mini_frame = Frame(self.header_frame)
            mini_frame.pack(side='left')

            # widget
            me = Entry(mini_frame, **prop)
            me.pack(side='top', expand=0, fill='both')

            # change colour every second merged header
            if i % 2:
                me.configure(disabledbackground=header_colour2)

            # keep these widgets so that they can be configured later
            self.header_widgets.append(me)

            # --------------------------------------------------------------------
            # subsections
            # --------------------------------------------------------------------
            for sub_section in range(1, header()):
                # frame within the mini-frame, so we can stack 'left'
                (hf2 := Frame(mini_frame)).pack(side='left')

                # widget
                (se := Entry(hf2, **prop)).pack(side='left')

                # change colour every second merged header
                if i % 2:
                    se.configure(disabledbackground=header_colour2)

                # keep these widgets so that they can be configured later
                self.sub_header_widgets.append(se)

    # ============================================================================
    # bottom row
    # ============================================================================
    def make_bottom(self, col_merge):
        def validate(n, w):
            if self.cb_bottom_row_ok(n):
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
                se = Entry(self.bottom_frame, **prop, state='disabled', validate='key')
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
        se = Entry(self.bottom_header_frame, **prop, state='disabled')

        # keep these widgets so that they can be configured later
        self.bottom_header_widgets.append(se)

    # ============================================================================
    # row titles
    # ============================================================================
    def make_row_titles(self, rows):
        prop = self.entry_props.copy()
        prop['width'] = 12
        for _ in range(rows):
            re = Entry(self.row_frame, **prop, state='disabled')
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
            (mini_frame := Frame(self.totals_header_frame)).pack(side='left')

            # widget
            (me := Entry(mini_frame, **prop)).pack(side='top', expand=0, fill='both')

            # keep these widgets so that they can be configured later
            self.totals_header_widgets.append(me)

            for sub_section in range(1, header):
                # frame within the mini-frame so we can stack left
                (hf2 := Frame(mini_frame)).pack(side='left')

                # widget
                (se := Entry(hf2, **prop)).pack(side='left')

                # keep these widgets so that they can be configured later
                self.totals_sub_header_widgets.append(se)

        for row in range(rows):
            (df1 := Frame(self.totals_frame)).pack(side='top', expand=1, fill='x')

            # foreach header
            col = 0
            for header in range(len(totals_merge)):
                # subsections
                for _ in range(1, totals_merge[header]):
                    # data entry box
                    (de := Entry(df1, **prop)).pack(side='left')

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
            return self.cb_data_entry([r, c, n])  # what is the point of this?

        for row in range(rows):
            (df1 := Frame(self.data_frame)).pack(side='top', expand=1, fill='x')

            # foreach header
            col = 0
            for i, header in enumerate(col_merge):
                # subsections
                for subsection in range(header()):

                    # data entry box
                    de = Entry(df1, **self.entry_props, validate='key')
                    de.configure(validatecommand=(de.register(partial(validate, row, col)), '%P', '%W'))
                    de.configure(invalidcommand=de.register(df1.bell))
                    de.pack(side='left')

                    # save row/column with dataentry, and vice-versa
                    if row not in self.entry_widgets:
                        self.entry_widgets[row] = {}
                    self.entry_widgets[row][col] = de
                    self.widgets_row_col[de] = [row, col]

                    # set colour in column to make it easier to read
                    colour = de.cget('bg')
                    if i % 2:
                        colour = very_light_grey
                    self.column_colours[col] = colour
                    de.configure(bg=colour)

                    # set bindings for navigation
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
        self.bottom_header_widgets[0].configure(textvariable=StringVar(value=bottom_header_text))

        for c, bw in enumerate(self.bottom_widgets):
            bw.configure(textvariable=StringVar(value=bottom_row_vars[c]))

        # the totals header
        for col in range(self.num_totals_col):
            self.totals_header_widgets[col].configure(textvariable=StringVar(value=total_header_texts[col]))

        # the totals sub header
        for col in range(self.num_totals_sub_col):
            self.totals_sub_header_widgets[col].configure(textvariable=StringVar(value=total_sub_texts[col]))

            # the totals data
            for row in range(self.num_rows):
                widget = self.get_totals_widget(row, col)
                if widget:
                    widget.configure(textvariable=StringVar(value=total_vars[row][col]))

        # the data grid
        for col in range(self.num_cols):
            for row in range(self.num_rows):
                widget = self.get_widget(row, col)

                # note... want the widget colour to go back to what it was,
                # even if the data has changed
                bg = widget.cget('bg')
                widget.configure(textvariable=StringVar(value=data_vars[row][col]))
                widget.configure(bg=bg)

        # the header data
        i = 0
        for ht in header_text:
            self.header_widgets[i].configure(textvariable=StringVar(value=ht))
            Hovertip(self.header_widgets[i], balloon_text[i])
            i += 1

        # the sub header data
        i = 0
        for sht in sub_header_text:
            if len(self.sub_header_widgets) > i:
                self.sub_header_widgets[i].configure(textvariable=StringVar(value=sht))
                i += 1
            else:
                break

        # the row header
        i = 0
        for rht in row_header_text:
            self.row_header_widgets[i].configure(textvariable=StringVar(value=rht))
            i += 1

    # ============================================================================
    # navigation routines
    # ============================================================================
    def _move(self, where, ev):
        w: Entry = ev.widget

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
        w: Entry = e.widget
        if inout == "focusIn":
            w.selection_range(0, 'end')
        else:
            w.selection_clear()

        # set data colour and totals colour
        dcolour = colour or bg_colour
        tcolour = colour

        # are we processing a 'data change'?
        original_colour = w.cget('bg')
        data_changed = original_colour == needs_update_colour and inout == 'focusOut'

        # get the widget
        r, c = self.get_row_col(w)

        # set colours for rows (data)
        col_colour = Colour.add(dcolour, self.column_colours.get(c))
        for row in range(self.num_rows):
            wid = self.get_widget(row, c)
            wid.configure(bg=col_colour)

        # set colours for cols (data)
        for col in range(self.num_cols):
            wid = self.get_widget(r, col)
            col_colour = Colour.add(dcolour, self.column_colours.get(col))
            wid.configure(bg=col_colour)

        # set colour for row header
        widget = self.row_header_widgets[r]
        widget.configure(disabledbackground=dcolour)

        # set colours for totals row
        if tcolour:
            tcolour = Colour.add(tcolour, totals_colour)
        else:
            tcolour = totals_colour

        for col in range(self.num_totals_sub_col):
            widget = self.totals_widgets[r][col]
            widget.configure(disabledbackground=tcolour)

        # callback (only if data has changed) (indicated by the current colour)
        if data_changed:
            self.cb_process_data_change(r, c)

    def widgets_row(self, row):
        widgets = []
        for col in range(self.num_cols):
            widgets.append(self.entry_widgets[row][col])
        return widgets

    def widgets_col(self, col) -> list[Entry]:
        widgets = []
        for row in range(self.num_rows):
            widgets.append(self.entry_widgets[row][col])
        return widgets

    def get_widget(self, row, col):
        return self.entry_widgets[row][col]

    def get_row_col(self, widget: Entry) -> tuple[int, int]:
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
