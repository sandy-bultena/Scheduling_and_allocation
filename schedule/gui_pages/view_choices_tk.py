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
from schedule.model.enums import ConflictType, ResourceType
from schedule.Tk import InitGuiFontsAndColours as fac



class ViewChoicesTk:
    """
            my $self            = shift;
        my $default_tab     = shift;
        my $all_scheduables = shift;
        my $btn_callback    = shift || sub { return; };

        my $f = $self->_pages->{ lc($default_tab) };

        $views_manager->gui->reset_button_refs();

        $frame->destroy if $frame;

        $frame = $f->Frame->pack( -expand => 1, -fill => 'both' );

        foreach my $resource_type ( AllScheduables->valid_types ) {
            my $view_choices_frame =
              $frame->LabFrame(
                -label => $all_scheduables->by_type($resource_type)->title, )
              ->pack( -expand => 1, -fill => 'both' );

            my $view_choices_scrolled_frame =
              $view_choices_frame->Scrolled( 'Frame', -scrollbars => "osoe" )
              ->pack( -expand => 1, -fill => 'both' );

            $views_manager->gui->create_buttons_for_frame(
                $view_choices_scrolled_frame,
                $all_scheduables->by_type($resource_type),
                $btn_callback
            );
        }

    }

    """
    colours: fac.TkColours = fac.colours
    Fonts: fac.TkFonts = fac.fonts

    def __init__(self, frame: Frame, resources:dict[ResourceType,list], btn_callback: Callable):
        """
        Initialize this manager
        :param frame: where to put the gui objects
        """

        if self.Fonts is None:
            self.Fonts = fac.TkFonts(frame.winfo_toplevel())

        self.frame = frame
        self._button_refs: dict[str, Button] = {}

        Label(frame,text="Edit Class Times for ...", font=self.Fonts.big, anchor='center').pack(expand=1,fill='both')

        for resource_type in (ResourceType.teacher, ResourceType.lab, ResourceType.stream):
            l_frame = LabelFrame(text=resource_type.name)
            l_frame.pack(expand=1,fill='both', padx=5,pady=15)

            r_frame = Scrolled(l_frame, "Frame").widget
            r_frame.pack(expand=1, fill='both')

            for index,resource in enumerate(resources[resource_type]):
                row = int(index/4)
                col = index-row*4
                command = partial(btn_callback, resource)
                self._button_refs[resource.number] = Button(r_frame, text=str(resource), highlightthickness=10, command=command, width=15)
                self._button_refs[resource.number].grid(column = col, row=row, sticky='nsew',ipadx=20, ipady=20, padx=2, pady=2)



    def set_button_colour(self, button_id: str, view_conflict: ConflictType = None):
        """
        Sets the colour according to the conflict resource_type
        :param button_id:
        :param view_conflict: conflict for the view associated with this button
        :return:
        """

        btn = self._button_refs.get(button_id, None)
        if btn is None:
            return

        # change the background colour of the button
        # ... (doesn't work on MAC) so also change the background colour of the highlighted area
        colour_highlight = self.frame.cget("background")
        colour = self.colours.ButtonBackground
        active_colour = self.colours.ActiveBackground
        if view_conflict is not None:
            colour = ConflictType.colours()[view_conflict]
            active_colour = Colour.darken(colour, 10)
            if platform.system() == "Darwin":
                colour_highlight = colour
        btn.configure(background=colour, activebackground=active_colour,
                      highlightbackground=colour_highlight)

