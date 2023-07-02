from typing import *
from ..Tk.TableEntry import TableEntry
from dataclasses import dataclass
from tkinter import *
from ..Tk.InitGuiFontsAndColours import TkColours

"""
Basically a Tk::TableEntry object with some restrictions

The first column I<must> be a unique identifier for the corresponding data
object, and can not be edited.
"""


@dataclass
class DEColumnDescription:
    title: str
    width: int
    property: str


class DataEntryTk:

    def __init__(self,
                 parent: Frame,
                 delete_callback: Optional[Callable[[list], None]],
                 save_callback: Optional[Callable[[], None]],
                 colours: Optional[TkColours],
                 ):
        if colours is None:
            colours = TkColours()
        self.colours = colours
        self.delete_callback = delete_callback
        self.save_callback = save_callback
        self.frame = parent
        self.de: Optional[TableEntry] = None

    def initialize_columns(self, column_descriptions: list[DEColumnDescription]):

        titles: list[str] = list()
        column_widths: list[int] = list()
        for cd in column_descriptions:
            titles.append(cd.title)
            column_widths.append(cd.width)

        if self.de is not None:
            self.de.destroy()

        self.de = TableEntry(
            self.frame,
            rows=1,
            columns=len(column_descriptions),
            titles=titles,
            column_widths=column_widths,
            delete=self.delete_callback,
            colours=self.colours,
        )
        self.de.pack(side=TOP, expand=True, fill=BOTH)
        # --------------------------------------------------------------------------
        # NOTE: If weird shit is happening, give up and use a 'Save' button
        # ... clicking the 'Delete' triggers a 'Leave'...
        # --------------------------------------------------------------------------
        self.de.bind('<Leave>', self.save_callback)


        # disable the first columns, but not the rest
        disabled = [1]
        disabled.extend([0 for _ in range(1, self.de.number_of_columns)])
        self.de.configure(disabled=disabled)

    def refresh(self, data: list[list[Any]]):
        """
        refresh the data
        :param data: a list of lists (a 2-d array sort of)
        """
        self.de.clear_data()
        for row, row_data in enumerate(data):
            for col, cell_data in enumerate(row_data):
                self.de.put(row, col, str(cell_data))

        if self.de.number_of_rows <= len(data):
            self.de.add_empty_row()

        # stupid Tk won't update image unless I do this.  Oh well, at least it worked
        self.frame.focus_set()

    def get_all_data(self) -> list[list[str]]:
        """
        reads the data stored in teh TableEntry widget
        :return: a list of rows, which is a list of columns with the data
        """
        data: list = list()
        for row in range(self.de.number_of_rows):
            data.append(self.de.read_row(row))
        return data


"""
=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns

=head1 COPYRIGHT

Copyright (c) 2021, Jack Burns, Sandy Bultena, Ian Clement. 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut
"""
