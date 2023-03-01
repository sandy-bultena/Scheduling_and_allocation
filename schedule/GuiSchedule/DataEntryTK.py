from tkinter import *
from tkinter import ttk

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

        #TODO: Pick up from here when the power comes back on.
        # self.de = self.frame.
        for title in self.titles:
            #TODO: Tkinter doesn't have an equivalent table widget. Figure something out.
            # This may present a solution: https://www.geeksforgeeks.org/create-table-using-tkinter/
            continue

    def refresh(self, data):
        pass

    def get_all_data(self):
        all_data = []

        # Loop over the rows & columns of the table to fill the array with all its data.
        
    