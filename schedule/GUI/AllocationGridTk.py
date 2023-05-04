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
row_col_indicator_colour = Colour.lighten("cdefab", 5)
totals_header_colour     = Colour.string("lemonchiffon")
totals_colour            = Colour.lighten(totals_header_colour, 5)
fg_colour                = "black"
bg_colour                = "white"
needs_update_colour      = Colour.string("mistyrose")
not_ok_colour            = needs_update_colour

# width of the data entry; Perl includes a comment about making if configurable in the future
width = 5


class AllocationGridTk:
    def __init__(self, frame: Frame, rows,
                 col_merge, totals_merge, fonts,
                 cb_data_entry = lambda *_, **__: True,
                 cb_process_data_change = lambda *_, **__: True,
                 cb_bottom_row_ok = lambda *_, **__: True):
        self.cb_data_entry = cb_data_entry
        self.cb_process_data_change = cb_process_data_change
        self.cb_bottom_row_ok = cb_bottom_row_ok

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
        for w in frame.pack_slaves():
            w.destroy()

        # ------------------------------------------------------------------------
        # make a 2x3 grid with frames for
        # blank   | header | blank
        # teacher | data   | totals
        # ------------------------------------------------------------------------
        display = Scrolled(frame, 'Frame')
        pane = display.widget
        display.pack(side='top', expand=1, fill='both')

        # make the frames
        self.header_frame = Scrolled(pane, 'Frame', 's')
        self.header_frame.forget()
        self.row_frame = Scrolled(pane, 'Frame')
        self.row_frame.forget()
        self.data_frame = Scrolled(pane, 'Frame', 's')
        self.data_frame.forget()
        self.totals_frame = Frame(pane)
        self.totals_header_frame = Frame(pane)
        self.bottom_header_frame = Scrolled(pane, 'Frame')
        self.bottom_header_frame.forget()
        self.bottom_frame = Scrolled(pane, 'Frame', 's')
        self.bottom_frame.forget()

        # configure the layout
        self.header_frame.grid(row=0, column=1, sticky='nsew', pady=2)
        self.row_frame.grid(row=1, column=0, sticky='nsew', padx=3)
        self.data_frame.grid(row=1, column=1, sticky='nsew')
        self.totals_frame.grid(row=1, column=2, sticky='nsew', padx=3)
        self.totals_header_frame.grid(row=0, column=2, padx=3, pady=2)
        self.bottom_header_frame.grid(row=2, column=0, sticky='nsew', padx=3, pady=2)
        self.bottom_frame.grid(row=2, column=1, sticky='nsew', pady=2)

        pane.grid_columnconfigure(0, weight=0)
        pane.grid_columnconfigure(1, weight=5)
        pane.grid_columnconfigure(2, weight=0)

        scroll_options = {'relief': 'flat', 'activerelief': 'flat'}
        display.vertical_scrollbar.configure(**scroll_options)
        self.header_frame.horizontal_scrollbar.configure(**scroll_options)
        self.data_frame.horizontal_scrollbar.configure(**scroll_options)
        self.bottom_frame.horizontal_scrollbar.configure(**scroll_options)

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
        self.entry_widgets: list[list[Entry]] = []
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
    def make_header_columns(self, col_merge):
        prop = self.entry_props.copy()
        prop['disabledbackground'] = header_colour1
        prop['state'] = 'disabled'

        # merged header
        for i, header in enumerate(list(col_merge)):
            # frame to hold the merged header, and the subheadings
            mini_frame = Frame(self.header_frame.widget)
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
            for sub_section in range(1, len(header)):
                # widget
                prop = self.entry_props.copy()
                prop['disabledbackground'] = header_colour1
                se = Entry(self.bottom_frame.widget, **prop, state='disabled', validate='key')
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
        se = Entry(self.bottom_header_frame.widget, **prop, state='disabled')

        # keep these widgets so that they can be configured later
        self.bottom_header_widgets.append(se)

    # ============================================================================
    # row titles
    # ============================================================================
    def make_row_titles(self, rows):
        prop = self.entry_props.copy()
        prop['width'] = 12
        for _ in range(rows):
            re = Entry(self.row_frame.widget, **prop, state='disabled')
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
                    self.totals_widgets.get(row, {})[col] = de
                    col += 1

    # ============================================================================
    # data grid
    # ============================================================================
    def make_data_grid(self, rows, col_merge):
        def validate(r, c, n, w):
            widget = self.data_frame.nametowidget(w)
            widget.configure(bg=needs_update_colour)
            return self.cb_data_entry([r, c, n])  # what is the point of this?

        for row in range(rows):
            (df1 := Frame(self.data_frame.widget)).pack(side='top', expand=1, fill='x')

            # foreach header
            col = 0
            for header in col_merge:
                # subsections
                for subsection in header:

                    # data entry box
                    de = Entry(df1, **self.entry_props, validate='key')
                    de.configure(validatecommand=(de.register(partial(validate, row, col)), '%P', '%W'))
                    de.configure(invalidcommand=de.register(df1.bell))
                    de.pack(side='left')

                    # save row/column with dataentry, and vice-versa
                    self.entry_widgets[row][col] = de
                    self.widgets_row_col[de] = [row, col]

                    # set colour in column to make it easier to read
                    colour = de.cget('bg')
                    if header % 2:
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

                    de.bind("<FocusIn>", partial(self.focus_changed, 'focusIn', row_col_indicator_colour))
                    de.bind("<FocusOut>", partial(self.focus_changed, 'focusOut', row_col_indicator_colour))
                    de.bindtags([*de.bindtags(), 1, 0, 2, 3])

                    col += 1

    # ============================================================================
    # populate: assign text variables to each of the entry widgets
    # ============================================================================
    def populate(self, header_text: list[StringVar], balloon_text: list[str],
                 sub_header_text: list[StringVar], row_header_text: list[StringVar],
                 data_vars: list[list[StringVar]], total_header_texts: list[StringVar],
                 total_sub_texts: list[StringVar], total_vars: list[list[StringVar]],
                 bottom_header_text: StringVar, bottom_row_vars: list[StringVar]):
        balloon_text = list(balloon_text)

        # bottom row
        self.bottom_header_widgets[0].configure(textvariable=bottom_header_text)

        for c, bw in enumerate(self.bottom_widgets):
            bw.configure(textvariable=bottom_row_vars[c])

        # the totals header
        for col in range(self.num_totals_col):
            self.totals_header_widgets[col].configure(textvariable=total_header_texts[col])

        # the totals sub header
        for col in range(self.num_totals_sub_col):
            self.totals_sub_header_widgets[col].configure(textvariable=total_sub_texts[col])

            # the totals data
            for row in range(self.num_rows):
                widget = self.get_totals_widget(row, col)
                if widget:
                    widget.configure(textvariable=total_vars[row][col])

        # the data grid
        for col in range(self.num_cols):
            for row in range(self.num_rows):
                widget = self.get_widget(row, col)

                # note... want the widget colour to go back to what it was,
                # even if the data has changed
                bg = widget.cget('bg')
                widget.configure(textvariable=data_vars[row][col])
                widget.configure(bg=bg)

        # the header data
        i = 0
        for ht in header_text:
            self.header_widgets[i].configure(textvariable=ht)
            Hovertip(self.header_widgets[i], balloon_text[i])
            i += 1

        # the sub header data
        i = 0
        for sht in sub_header_text:
            if len(self.sub_header_widgets) > i:
                self.sub_header_widgets[i].configure(textvariable=sht)
                i += 1
            else:
                break

        # the row header
        i = 0
        for rht in row_header_text:
            self.row_header_widgets[i].configure(textvariable=rht)
            i += 1

    # ============================================================================
    # navigation routines
    # ============================================================================
    def _move(self, where, ev):
        w: Entry = ev.widget

        w.selection_clear()
        row, col = self.get_row_col(w)

        old_row = row
        old_col = col

        if where == 'nextRow':
            row = min(max(row+1, 0), self.num_rows - 1)
        elif where == 'prevRow':
            row = min(max(row-1, 0), self.num_rows - 1)
        elif where == 'nextCell':
            row = min(max(col+1, 0), self.num_rows - 1)
        elif where == 'prevCell':
            row = min(max(col-1, 0), self.num_rows - 1)

        e = self.get_widget(row, col)
        self.set_focus(e)

        # forces Tk to not continue applying any binding routines after this
        return "break"

    # ----------------------------------------------------------------------------
    # what to do when the widget gets the focus
    # ----------------------------------------------------------------------------
    def set_focus(self, e):
        r, c = self.get_row_col(e)
        self.header_frame.see(e)
        self.data_frame.see(e)
        self.bottom_frame.see(self.bottom_widgets[c])
        e.focus()

    # ----------------------------------------------------------------------------
    # focus has changed - indicate what row/col we are on, callback process change
    # ----------------------------------------------------------------------------
    def focus_changed(self, inout, colour, e):
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
            e = self.get_widget(r, c)
            e.configure(bg=col_colour)

        # set colours for cols (data)
        for col in range(self.num_cols):
            e = self.get_widget(r, c)
            col_colour = Colour.add(dcolour, self.column_colours.get(col))
            e.configure(bg=col_colour)

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
        return tuple(self.widgets_row_col.get(widget, []))

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
