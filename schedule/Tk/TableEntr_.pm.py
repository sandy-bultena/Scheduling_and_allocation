from tkinter import *
import tkinter as tk
from typing import Any
from os import path
import sys
from functools import partial

sys.path.append(path.dirname(path.dirname(__file__)))
from Tk.scrolled import Scrolled


class TableEntry(tk.Frame):
    """ Creates a TableEntry object, inside a frame """

    # ===================================================================
    # properties
    # ===================================================================
    @property
    def number_of_rows(self) -> int:
        """Gets and sets the number of rows in the table"""
        return self.cget("rows")

    @number_of_rows.setter
    def number_of_rows(self, rows: int):
        self.configure(rows=rows)

    @property
    def number_of_columns(self) -> int:
        """Gets and sets the number of columns in the table"""
        return self.cget("columns")

    @number_of_columns.setter
    def number_of_columns(self, columns: int):
        self.configure(columns=columns)

    # ===================================================================
    # Constructor
    # ===================================================================
    def __init__(self, parent: Any, **kwargs):
        tk.Frame.__init__(self, parent)
        self.rows = 0
        self.parent = parent
        self._cget = dict()
        self._title_widgets = list()
        self.frame = None

        # ---------------------------------------------------------------
        # where we keep lookup info (widget to cell, cell to widget)
        # ---------------------------------------------------------------
        self.__reverse_lookup = dict()
        self.__lookup = dict()

        self.__config_specs = {
            'bg_entry': self.__bg_entry,
            'rows': self.__set_rows,
            'columns': self.__set_columns,
            'titles': self.__set_titles,
            'disabled': self.__set_disabled,
            'delete': self.__set_delete_callback,
            'buttoncmd': self.__set_button_callback,
            'buttontext': self.__set_button_text,
            'colwidths': self.__set_column_widths,
            'defwidth': self.__set_default_width,
        }
        bg = self.winfo_toplevel().cget("bg")
        self._defaults = {
            "rows": 10,
            "bg_entry": "#ffffff",
            "columns": 10,
            "titles": list(),
            "colwidths": list(),
            "disabled": list(),
            "defwidth": 8,
            "width": 100,
            "height": 200,
            "relief": 'flat',
            "buttontext": "Go",
            "bg": bg,
            "delete": None,
            "buttoncmd": None,
        }
        self.__populate_the_frame(**kwargs)

    # ===================================================================
    # populate the frame
    # ===================================================================
    def __populate_the_frame(self, **kwargs):

        # ---------------------------------------------------------------
        # create a scrolled pane
        # ---------------------------------------------------------------
        scrolled_frame = Scrolled(self, "Frame", scrollbars="se", border=2, relief="flat")
        scrolled_frame.pack(side='left', fill='both')
        scrolled_frame.Subwidget('xscrollbar').configure(elementborderwidth=2, relief='ridge', width=12)
        scrolled_frame.Subwidget('yscrollbar').configure(elementborderwidth=2, relief='ridge', width=12)
        self.scrolled_frame = scrolled_frame
        self.frame = scrolled_frame.Subwidget("Frame")

        # ---------------------------------------------------------------
        # define the 'delete' image
        # ---------------------------------------------------------------
        image_dir = path.dirname(path.dirname(__file__)) + "/Images"
        # ex_photo = self.winfo_toplevel().Photo(format='gig',file=image_dir + "/ex.gif")

        # ---------------------------------------------------------------
        # configure this table entry & draw
        # ---------------------------------------------------------------
        to_configure = self._defaults.copy()
        to_configure.update(kwargs)
        self._configure(**to_configure)
        self.__draw()

    # ===================================================================
    # get widget in row/col
    # ===================================================================
    def get_widget(self, r, c) -> Entry:
        """get the widget in the row/col"""
        if (r, c) in self.__lookup:
            return self.__lookup[(r, c)]
        return None

    # ====================================================================================
    # find row and column position for given widget
    # ====================================================================================
    def find_pos(self, w: Any) -> (int, int):
        """find the row and column for a specific widget"""
        if w:
            return self.__reverse_lookup[w]

    # ===================================================================
    # draw the widgets, etc
    # ===================================================================
    def __draw(self):

        # create header row
        self.__create_header_row()

        # add rows
        for r in range(1, self.number_of_rows + 1):
            self.__add_empty_row(r)

        # calculate the width of the row, to set the pane width
        width_total = 0
        for c in range(self.number_of_columns + 1):
            w = self.get_widget(1, c)
            if w is not None:
                width_total += w.winfo_width() + 12

            if self.cget("buttoncmd"):
                width_total += 100

            width_total += 2 * self.cget("border")
            self.frame.configure(width=width_total)

    # ===================================================================
    # insert header_row
    # ===================================================================
    def __create_header_row(self):
        self._title_widgets.clear()
        titles = self.cget("titles")
        colwidths = self.cget("colwidths")

        # make sure lists are long enough
        while len(titles) < self.number_of_columns + 1:
            titles.append("")

        while len(colwidths) < self.number_of_columns + 1:
            colwidths.append(0)

        # add labels to the top row
        for c in range(1, self.number_of_columns + 1):
            colwidths[c - 1] = colwidths[c - 1] if colwidths[c - 1] else self.cget("defwidth")
            w = Label(self.frame, text=titles[c - 1], width=colwidths[c - 1])
            w.grid(column=c, sticky='nsew', row=0)
            self.__lookup[(0, c)] = w
            self.__reverse_lookup[w] = (0, c)

        self._configure(colwidths=colwidths)

    # ====================================================================================
    # add empty_row
    # ====================================================================================
    def __button_delete_cmd(self, row):
        if self.cget("buttoncmd"):
            data = self.__read_row(row)
            self.cget("buttoncmd")(data)

    def __add_empty_row(self, row):
        column_widths = self.cget("colwidths")
        columns_enabled_disabled = self.cget("disabled")

        # make sure lists are long enough
        while len(column_widths) < self.number_of_columns + 1:
            column_widths.append(0)
        while len(columns_enabled_disabled) < self.number_of_columns + 1:
            columns_enabled_disabled.append(0)

        # --------------------------------------------------------------------------------
        # add the row
        # --------------------------------------------------------------------------------

        # for each column, add an entry box
        for c in range(1, self.number_of_columns + 1):
            column_widths[c - 1] = column_widths[c - 1] if column_widths[c - 1] else self.cget("defwidth")

            # if there is something already there, delete it
            if (row, c) in self.__lookup:
                old = self.__lookup[(row, c)]
                if old:
                    old.destroy()

            # make entry widget
            w = Entry(self.scrolled_frame.Subwidget("Frame"),
                      width=column_widths[c - 1],
                      bg=self.cget("bg_entry"),
                      disabledforeground="black",
                      relief="flat",
                      )

            if columns_enabled_disabled[c - 1]:
                w.configure(state="disabled")

            w.grid(column=c, sticky="nsew", row=row)

            # key bindings for this entry widget
            w.bind("<Tab>", partial(self.__next_cell, self, w))
            w.bind("<Key-Return>", partial(self.__next_cell, self, w))
            w.bind("<Shift-Tab>", partial(self.__prev_cell, self, w))
            w.bind("<Key-Left>", partial(self.__prev_cell, self, w))
            w.bind("<Key-leftarrow>", partial(self.__prev_cell, self, w))
            w.bind("<Key-Up>", partial(self.__prev_row, self, w))
            w.bind("<Key-uparrow>", partial(self.__prev_row, self, w))
            w.bind("<Key-Down>", partial(self.__next_row, self, w))
            w.bind("<Key-downarrow>", partial(self.__next_row, self, w))
            w.bind("<Key-Right>", partial(self.__next_cell, self, w))
            w.bind("<Key-rightarrow>", partial(self.__next_cell, self, w))
            w.bind("<Button>", partial(self.__select_all, self, w))

            # I want my bindings to happen BEFORE the class bindings
            # w.bindtags( [ ($w.bindtags )[ 1, 0, 2, 3 ] ] );

            # save positional info
            self.__lookup[(row, c)] = w
            self.__reverse_lookup[w] = (row, c)

            # keep our row count up to date
            if row > self.number_of_rows:
                self.configure(rows=row)

            # add a `delete button` in the first column
            self.__put_delete(row)

            # if we have a row button, add that to the last column
            if self.cget("buttoncmd"):
                b = Button(self.frame,
                           text=self.cget("buttontext"),
                           command=partial(self.__button_delete_cmd, self, row, c)
                           )
                b.grid(column=self.number_of_columns + 1, sticky="nsew", row=row)

        # --------------------------------------------------------------------------------
        # adjust height of pane
        # --------------------------------------------------------------------------------
        height = 0
        for row in range(self.number_of_rows + 1):
            w = self.get_widget(row, 1)
            if not w:
                continue
            height += w.winfo_height()

        height += 2 * self.cget('border')
        height += self.scrolled_frame.Subwidget("xscrollbar").winfo_height()
        self.frame.configure(height=height)

    # ====================================================================================
    # put the "delete" button at the beginning of a row
    # ====================================================================================
    def __put_delete(self, row):
        bg = self.cget("bg")
        b = Button(self.frame,
                   text="del",
                   relief="flat",
                   command=partial(self.__delete_row, self, row),
                   highlightbackground=bg,
                   highlightcolor=bg,
                   bg=bg,
                   )
        b.grid(column=0, sticky="nsew", row=row)

        # save positional info
        self.__lookup[(row, 0)] = b
        self.__reverse_lookup[b] = (row, 0)

        # disable button?
        if self.__are_all_disabled():
            b.configure(state='disabled')

    # ====================================================================================
    # delete a row
    # ====================================================================================
    def __delete_row(self, row):
        if row == 0:
            return  # cannot delete the header row

        # run user supplied callback first
        delete_callback = self.cget("delete")
        if delete_callback:
            data = self.__read_row(row)
            delete_callback(data)

        # now remove the widgets and the row
        for c in range(0, self.number_of_columns + 1):
            w = self.get_widget(row, c)
            if w:
                self.__reverse_lookup.pop(w)
                self.__lookup.pop((row, c))
                w.destroy()

    # ====================================================================================
    # are all columns disabled?
    # ====================================================================================
    def __are_all_disabled(self) -> BooleanVar:
        disabled_columns = self.cget("disabled")
        flag = True
        for col in disabled_columns:
            flag = flag and col
        return flag

    # ====================================================================================
    # change focus to next cell (bound to Entry widgets)
    # ====================================================================================
    def __next_cell(self, w:Any, *args, **kwargs):
        self.__move_cell(w, 1, 0)

    def __prev_cell(self, w: Any, **kwargs):
        self.__move_cell(w, -1, 0)

    def __next_row(self, w: Any, **kwargs):
        self.__move_cell(w, 0, 1)

    def __prev_row(self, w: Any, **kwargs):
        self.__move_cell(w, 0, -1)

    def __move_cell(self, w: Entry, x_dir: int, y_dir: int):
        if self.__are_all_disabled:
            return

        w.selection_clear()

        (row, col) = self.find_pos(w)
        col = col + x_dir
        row = row + y_dir

        if col > self.number_of_columns:
            row = row + 1
            col = 1

        if col < 1:
            row = row - 1
            col = self.number_of_columns

        if row > self.number_of_rows:
            self.__add_empty_row(row)

        if row < 1:
            row = 1

        # set the focus, and move the scrollbars appropriately
        w2: Entry = self.get_widget(row, col)
        if w2:
            self.scrolled_frame.see(w2)
            self.update()
            w2.focus_get()
            w2.selection_range(0, 'end')

        # if we land on a disabled widget, keep moving
        disabled_list = self.cget("disabled")
        if disabled_list[col - 1]:
            w2 = self.get_widget(row, col)
            self.__move_cell(w2, x_dir, y_dir)

    # ====================================================================================
    # binding subroutine for <Button> on entry widget
    # ====================================================================================
    def __select_all(self, w: Entry, **kwargs):
        if w:
            w.focus()
            w.selection_clear()
            w.selection_range(0, 'end')

    # ====================================================================================
    # read row
    # ====================================================================================
    def __read_row(self, row):
        self.update()
        data = list()
        if row < 1:
            return data
        for c in range(1, self.number_of_columns + 1):
            w = self.get_widget(row, c)
            if w:
                data.append(w.get())
        return data

    # =================================================================================================
    # configure, cget, etc
    # =================================================================================================
    def _configure(self, **kwargs):
        """save the configuration into the _cget dictionary"""
        for k, v in kwargs.items():
            self._cget[k] = v

    def cget(self, option: str) -> Any:
        if option in self._cget:
            return self._cget[option]
        else:
            print(f"cget option is : {option}")
            return super().cget(option)

    def configure(self, **kwargs):
        for k, v in kwargs.items():
            if k in self._cget:
                self.__config_specs[k](v)
            else:
                pass
            #  super().configure(**{k: v})

    # =================================================================================================
    # Configuration routines
    # =================================================================================================
    def __apply_to_all_entry_widgets(self, func: callable):
        if self.number_of_columns and self.rows:
            for c in range(1, self.number_of_columns + 1):
                for r in range(1, self.number_of_rows + 1):
                    w = self.get_widget(r, c)
                    if w is not None:
                        func(w, r, c)

    def __bg_entry(self, colour):
        if colour is None:
            return self.cget('bg_entry')
        self._configure(colour=colour)
        self.__apply_to_all_entry_widgets(lambda w, r, c: w.configure(bg=colour))
        return self.cget("bg_entry")

    def __set_titles(self, title_list: list):
        if title_list is None:
            return self.cget('titles')
        while len(title_list) < self.number_of_columns:
            title_list.append("")
        self._configure(titles=title_list)
        self.__apply_to_all_entry_widgets(lambda w, r, c: w.configure(text=title_list[c - 1]))
        return self.cget('titles')

    def __set_disabled(self, column_disabled_list: list):
        if column_disabled_list is None:
            return self.cget("disabled")
        while len(column_disabled_list) < self.number_of_columns:
            column_disabled_list.append(0)
        self._configure(titles=column_disabled_list)

        def _disable_widget(w, r, c):
            if column_disabled_list[c - 1]:
                w.configure(state='disabled')
            else:
                w.configure(state='normal')

        self.__apply_to_all_entry_widgets(_disable_widget)
        return self.cget('disabled')

    def __set_column_widths(self, colwidths_list: list):
        if not colwidths_list:
            return self.cget("colwidths")
        self._configure(colwidths=colwidths_list)

        def _colwidths(w, r, c):
            width = colwidths_list[c - 1] or self.cget("defwidth") or 8
            w.configure(width=width)

        self.__apply_to_all_entry_widgets(_colwidths)
        return self.cget('colwidths')

    def __set_rows(self, rows: list):
        self._configure(rows=rows)
        return self.cget("rows")

    def __set_columns(self, columns: list):
        self._configure(columns=columns)
        return self.cget("columns")

    def __set_delete_callback(self, delete_callback: callable):
        self._configure(delete=delete_callback)
        return self.cget("delete")

    def __set_button_callback(self, button_callback: callable):
        self._configure(buttoncmd=button_callback)
        return self.cget("buttoncmd")

    def __set_button_text(self, button_text: str):
        self._configure(buttontext=button_text)
        return self.cget("buttontext")

    def __set_default_width(self, default_width: int):
        self._configure(defwidth=default_width)
        return self.cget("width")


def example():
    #    import Tk.TableEntr_.pm as te
    mw = Tk()
    frame = Frame(mw)
    frame.pack(expand=1, fill="both")

    titles = ["one", "two", "three"]
    col_widths = [10, 20, 5]
    de = TableEntry(frame, rows=3, columns=3, colwidths=col_widths)
    de.pack(side="top", expand=1, fill="both")
    mw.mainloop()

    """
    # ---------------------------------------------------------------
    # create the table entry object
    # ---------------------------------------------------------------
    my $de = $frame->TableEntry(
                                 -rows      => 1,
                                 -columns   => scalar(@$titles),
                                 -titles    => $titles,
                                 -colwidths => $col_widths,
                                 -delete    => [ $del_callback, $data_entry ],
    )->pack( -side => 'top', -expand => 1, -fill => 'both' );

    # disable the first columns, but not the rest
    my @disabled = (1);
    push @disabled, (0) x ( $de->columns - 1 );

    $de->configure( -disabled => \@disabled );

    # --------------------------------------------------------------------------
    # NOTE: If weird shit is happening, give up and use a 'Save' button
    # ... clicking the 'Delete' triggers a 'Leave'...
    # --------------------------------------------------------------------------

    """


example()
