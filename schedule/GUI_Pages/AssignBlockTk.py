# COMPLETED?
"""A half hour time blocks used to select time slots on a view."""
from tkinter import Canvas

from PerlLib import Colour


class AssignBlockTk:
    """Defines a 1/2 hour blocks of time within a view.

    You can find this time blocks by specifying the x/y canvas coordinates, or by the day, time_start and
    end time.

    The blocks can be coloured, or uncoloured."""
    # =================================================================
    # Global Variables
    # =================================================================
    day_tag = {
        1: "monday",
        2: "tuesday",
        3: "wednesday",
        4: "thursday",
        5: "friday"
    }

    # region CLASS METHODS
    # =================================================================
    # new
    # =================================================================
    def __init__(self, view, day: int, start: float):
        """Creates, draws and returns an AssignBlock.

        Parameters:
            view: View the GuiBlock will be drawn on.
            day: Day of the week (integer, 1 = monday, etc.)
            start: Time that this gui blocks starts (real number)"""
        # Raise some sort of warning if view is None or absent.

        # ---------------------------------------------------------------
        # draw 1/2 the blocks
        # ---------------------------------------------------------------
        cn: Canvas = view.gui.canvas
        coords = view.gui.get_time_coords(day, start, 1 / 2)

        r = cn.create_rectangle(
            coords,
            outline='red',
            width=0,
            tags=AssignBlockTk.day_tag[day]
        )
        cn.lower(r, 'all')

        # ---------------------------------------------------------------
        # create object
        # ---------------------------------------------------------------
        self.id = r
        self.day = day
        self.start = start
        self.view = view
        self.canvas: Canvas = view.gui.canvas

        # just in case, want coords to be from top left -> bottom right
        # or other logic in this class may fail
        x1 = coords[0]
        y1 = coords[1]
        x2 = coords[2]
        y2 = coords[3]

        if x1 > x2:
            tmp = x1
            x1 = x2
            x2 = tmp
        if y1 > y2:
            tmp = y1
            y1 = y2
            y2 = tmp

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    # =================================================================
    # find ($x, $y, $assigned_blocks)
    # =================================================================
    @staticmethod
    def find(x, y, assigned_blocks: list):
        """Find the first blocks within assigned blocks that contains the canvas coords x & y.

        Parameters:
            x: canvas coordinates
            y: canvas coordinates
            assigned_blocks: array of AssignBlocks
        Returns:
            AssignBlock object if found, None otherwise"""
        if not assigned_blocks:
            return

        found: list[AssignBlockTk] = [b for b in assigned_blocks if b.at_canvas_coords(x, y)]
        return found[0] if len(found) > 0 else None

    # =================================================================
    # in_range ($x1,$y1,$x2,$y2, $assigned_blocks)
    # =================================================================
    @classmethod
    def in_range(cls, x1, y1, x2, y2, assigned_blocks: list):
        """Return an array of all assigned_blocks within a certain rectangular area.

        Parameters:
            x1: rectangle area coordinates.
            y1: rectangle area coordinates.
            x2: rectangle area coordinates.
            y2: rectangle area coordinates.
            assigned_blocks: Array of AssignBlocks."""
        # TODO: Crash if assigned_blocks not present.
        if not assigned_blocks:
            raise ValueError()

        # make sure we time_start from the left top towards the bottom right.
        if x1 > x2:
            tmp = x1
            x1 = x2
            x2 = tmp
        if y1 > y2:
            tmp = y1
            y1 = y2
            y2 = tmp

        return [b for b in assigned_blocks if b.x1 < x2 and b.x2 > x1 and b.y1 < y2 and b.y2 > y1]

    # =================================================================
    # get_day_start_duration ($chosen)
    # =================================================================
    @classmethod
    def get_day_start_duration(cls, chosen: list) -> tuple[int, float, float]:
        """For the given AssignBlocks that were chosen by the user, calculate and return
        information about the range of blocks chosen.

        Parameters:
            chosen: Array of AssignBlocks."""
        x: list[AssignBlockTk] = chosen.copy()

        day = x[0].day
        start = x[0].start
        size = len(x)

        for i in x:
            temp = i.start
            if temp < start:
                start = temp

        # Note that each blocks is a 1/2 hour, so the duration (in hours) would be the number of
        # blocks divided by two.
        return day, start, size / 2

    # endregion

    # region INSTANCE METHODS
    # =================================================================
    # at_canvas_coords ($x, $y)
    # =================================================================
    def at_canvas_coords(self, x, y) -> bool:
        """Does this blocks contain the canvas coordinates x & y?

        NOTE: Will not return true if edge is detected, which is not a bad thing. Maybe the user
        wanted something else."""
        return True if (self.x1 < x < self.x2) and (self.y1 < y < self.y2) else False

    # =================================================================
    # set_colour ( $Colour)
    # =================================================================
    def set_colour(self, colour: str = "mistyrose3"):
        """Fills the blocks with the specified Colour.

        Colour string can be of resource_type '#rrggbb' or a valid unix Colour name.

        Parameters:
            colour: default value is 'mistyrose3'.

        Returns:
            This modified blocks."""
        c = Colour.string(colour)
        self.canvas.itemconfigure(self.id, fill=c)
        return self

    # =================================================================
    # remove_colour ()
    # unfill ()
    # =================================================================
    def unfill(self):
        return self.remove_colour()

    def remove_colour(self):
        """Removes any Colour from the blocks.

        Returns:
            The modified blocks."""
        self.canvas.itemconfigure(self.id, fill='')
        return self

    # =================================================================
    # getters and setters
    # =================================================================
    # Skipping these. No special validation to speak of.
    # endregion


# =================================================================
# footer
# =================================================================
"""
=head1 AUTHOR

Sandy Bultena, Alex Oxorn

Translated to Python by Evan Laverdiere

=head1 COPYRIGHT

Copyright (c) 2020, Sandy Bultena, Alex Oxorn. 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut

1;

"""
