"""
This is the central control for launching any or all of the Views
(the things that allow you to move blocks around)

For each schedule item view, there will be:
* A button to open the view for that schedule item
* The button colour will reflect the Conflict status for that schedule item
    * Due to the inability to change the background colour of a button on a MAC, we will use
      borders around our button to indicate the various colour statuses of our scheduled items

"""
from __future__ import annotations

import platform
from functools import partial
from tkinter import *
from typing import Callable

from schedule.Tk import Scrolled
from schedule.Utilities import Colour
from schedule.gui_generics.block_colours import RESOURCE_COLOURS
from schedule.model.enums import ConflictType, ResourceType
from schedule.Tk import InitGuiFontsAndColours as fac



class ViewsControllerTk:
    colours: fac.TkColours = fac.colours
    Fonts: fac.TkFonts = fac.fonts

    def __init__(self, parent: Frame, resources:dict[ResourceType,list], btn_callback: Callable):
        """
        Initialize this manager
        :param parent: where to put the gui objects
        """
        # remove anything that was already in the frame
        for widget in parent.winfo_children():
            widget.destroy()


        self.parent = parent

        if self.Fonts is None:
            self.Fonts = fac.TkFonts(parent.winfo_toplevel())
        scrolled_frame = Scrolled(parent, "Frame").widget

        self._button_refs: dict[str, Button] = {}

        Label(scrolled_frame,text="Edit Class Times for ...", font=self.Fonts.big, anchor='center').pack(expand=1,fill='both', pady=20)
        for resource_type in (ResourceType.teacher, ResourceType.lab, ResourceType.stream):
            l_frame = LabelFrame(scrolled_frame, text=resource_type.name)
            l_frame.pack(expand=1,fill='both', padx=5,pady=15)

            for index,resource in enumerate(resources[resource_type]):
                row = int(index/4)
                col = index-row*4
                command = partial(btn_callback, resource)
                self._button_refs[resource.number] = Button(l_frame, text=str(resource), highlightthickness=4, command=command, width=15)
                self._button_refs[resource.number].grid(column = col, row=row, sticky='nsew',ipadx=20, ipady=10, padx=2, pady=2)

        mw = self.parent.winfo_toplevel()
        mw.update_idletasks()
        current_height = mw.winfo_height()
        w = min(mw.winfo_reqwidth(), mw.winfo_screenwidth()-50)
        mw.geometry(f"{w}x{current_height}")

    def set_button_colour(self, button_id: str, resource_type, view_conflict: ConflictType = None):
        """
        Sets the colour according to the conflict resource_type
        :param resource_type:
        :param button_id:
        :param view_conflict: conflict for the view associated with this button
        :return:
        """
        btn = self._button_refs.get(button_id, None)
        if btn is None:
            return

        # change the background colour of the button
        # ... (doesn't work on MAC) so also change the background colour of the highlighted area

        colour_highlight = self.parent.cget("background")
        colour = RESOURCE_COLOURS.get(resource_type, self.colours.ButtonBackground)
        active_colour = self.colours.ActiveBackground

        if view_conflict != ConflictType.NONE:
            colour = ConflictType.colours().get(view_conflict,'grey')
            active_colour = Colour.darken(colour, 10)

        if platform.system() == "Darwin":
            colour_highlight = colour
        btn.configure(background=colour, activebackground=active_colour,
                      highlightbackground=colour_highlight)

