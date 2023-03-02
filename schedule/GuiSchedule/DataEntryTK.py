from builtins import function
from tkinter import *
from tkinter import ttk
from schedule.Tk.TableEntry import TableEntry

'''
package DataEntryTk;

use FindBin;
use lib "$FindBin::Bin/..";
use Tk::TableEntry;

=head1 NAME
DataEntryTk - Enter data object  

=head1 VERSION
Version 6.00

=head1 DESCRIPTION
Basically a Tk::TableEntry object with some restrictions

=head2 Notes
The first column I<must> be a unique identifier for the corresponding data
object, and can not be edited.
=head1 PUBLIC METHODS
'''


class DataEntryTK:
    def __init__(self, data_entry, frame: Frame, del_callback: function, save_callback: function):
        self.data_entry = data_entry
        self.frame = frame
        self.del_callback = del_callback
        self.save_callback = save_callback

        self.titles = data_entry.col_titles
        self.col_widths = data_entry.col_widths

        # TODO: Tkinter doesn't have an equivalent table widget. Figure something out.
        # This may present a solution: https://www.geeksforgeeks.org/create-table-using-tkinter/
        # NOTE: Above solution does work, but TableEntry is a custom widget Sandy made.
        # continue
        for r in range(len(self.data_entry.schedulable_list_obj.list()) + 1):
            for c in range(len(self.titles)):
                if r == 0:
                    e = Label(self.frame, width=self.col_widths[c], text=self.titles[c])
        self.de = TableEntry(
            self.frame,
            columns=len(self.titles),
            titles=self.titles,
            colwidths=self.col_widths,
            delete=[self.del_callback, self.data_entry]
        )
        self.de.pack(side='top', expand=1, fill="both")

    def refresh(self, data):
        pass

    def get_all_data(self):
        all_data = []

        # Loop over the rows & columns of the table to fill the array with all its data.
