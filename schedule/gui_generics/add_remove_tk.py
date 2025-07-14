"""
AddRemoveTk

Creates two list boxes where you can transfer items from one list to another, just by clicking on an item

"""
from tkinter import *
from typing import Callable, Any

from schedule.Tk import Scrolled
from functools import partial

class AddRemoveTk:
    def __init__(self, frame: Frame,
                 get_add_list: Callable[[],list],
                 get_remove_list: Callable[[], list],
                 to_add_function: Callable[[Any], None],
                 to_remove_function: Callable[[Any], None],
                 add_text="Add to",
                 remove_text="Remove from",
                 height = 10):
        """
        :param frame: the frame to put the widgets in
        :param get_add_list: function that returns the list for the 'add' side
        :param get_remove_list: function that returns the list for the 'remove' side
        :param to_add_function: function that deals with items that have been clicked on the 'add' side
        :param to_remove_function: function that deals with items that have been clicked on the 'remove' side
        :param add_text: text over the 'add' list
        :param remove_text: text over the 'remove' list
        """
        self.frame = frame
        self.to_add_function = to_add_function
        self.to_remove_function = to_remove_function
        self.add_text = add_text
        self.remove_text = remove_text
        self.add_listbox = None
        self.remove_listbox = None
        self.adds = []
        self.removes = []
        self.get_add_list = get_add_list
        self.get_remove_list = get_remove_list

        f = Frame(self.frame)
        f.grid(column=0, stick='nsew', row=0)
        Label(f, text=self.add_text).pack()
        sf = Frame(f)
        sf.pack(fill='both', expand=1)
        s: Scrolled = Scrolled(sf, 'Listbox', scrollbars='oe', height=height)
        self.add_listbox = s.widget
        self.add_listbox.configure(borderwidth="5", relief="sunken")
        s.widget.bind('<Button-1>', partial(self._cmd_click, 'add'))

        f = Frame(self.frame)
        f.grid(column=1, stick='nsew', row=0)
        Label(f, text=self.remove_text).pack()
        sf = Frame(f)
        sf.pack(fill='both', expand=1)
        s: Scrolled = Scrolled(sf, 'Listbox', scrollbars='oe', height=height)
        self.remove_listbox = s.widget
        self.remove_listbox.configure(borderwidth="5", relief="sunken")
        s.widget.bind('<Button-1>', partial(self._cmd_click, 'remove'))

        self.refresh()

    def _cmd_click(self, which: str, e: Event):
        if which == "add":
            widget = self.add_listbox
            index = widget.nearest(e.y)
            if index < len(self.adds):
                self.to_add_function(self.adds[index])
        else:
            widget = self.remove_listbox
            index = widget.nearest(e.y)
            if index < len(self.removes):
                self.to_remove_function(self.removes[index])
        self.refresh()

    def refresh(self):
        """updates the two list boxes"""
        self.adds = self.get_add_list()
        self.removes = self.get_remove_list()
        self.add_listbox.delete(0, "end")
        self.remove_listbox.delete(0, "end")
        for item in self.adds:
            self.add_listbox.insert("end", str(item))
        for item in self.removes:
            self.remove_listbox.insert("end", str(item))
