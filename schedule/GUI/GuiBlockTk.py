from .ViewTk import ViewTk
from ..Export import DrawView
from ..PerlLib import Colour
from ..Schedule.Block import Block


class GuiBlockTk:
    """GuiBlock - describes the visual representation of a Block."""
    # =================================================================
    # Class Variables
    # =================================================================
    Max_id = 0
    Edge = 5

    # =================================================================
    # new
    # =================================================================
    def __init__(self, type: str, gui_view: ViewTk, block: Block, colour: str = ""):
        """Creates, draws and returns a GuiBlock object.

        Parameters:
            type: Type of view (teacher/lab/stream).
            gui_view: The GUI object associated with this view.
            block: The Block to turn into a GuiBlock.
            colour: The colour of the GuiBlock."""
        # get canvas from gui_view to draw on.
        canvas = gui_view.canvas

        # draw the block
        gui_objs = DrawView.draw_block(canvas, block, gui_view.get_scale_info(), type, colour,
                                       block_tag=GuiBlockTk.Max_id + 1)

        lines: list[int] = gui_objs['lines']
        text: int = gui_objs['text']
        rectangle: int = gui_objs['rectangle']
        coords = gui_objs['coords']
        colour = gui_objs['colour']

        # Group rectangle and text to create a GuiBlock,
        # So that they both move as one on the UI.
        # NOTE: canvas.createGroup() doesn't exist in Tkinter. It's exclusive to Perl/Tk.
        # Plus, Sandy told us not to bother with drag-and-drop functionality.
        # Still, we need it for the change_colour function...
        # NOTE: I think Sandy said something about a tkinter Group function. However, this seems
        # to come from a different package altogether based on the email she showed me.
        group = (
            # canvas.find_withtag(f"rectangle_block_{GuiBlockTk.Max_id + 1}"),
            # canvas.find_withtag(f"text_block_{GuiBlockTk.Max_id + 1}"),
            # canvas.find_withtag(f"lines_block_{GuiBlockTk.Max_id + 1}")
            rectangle, text, lines
        )

        # Create the object.
        GuiBlockTk.Max_id += 1
        self._id = GuiBlockTk.Max_id
        self.block = block
        self.gui_view = gui_view
        self._coords = coords
        self.rectangle = rectangle
        self.colour = colour
        self.text = text
        self.group = group
        self.group_tag = f"block_{self._id}"
        self.is_controlled = False

    # =================================================================
    # change the colour of the guiblock
    # =================================================================
    def change_colour(self, colour: str):
        """Change the colour of the GuiBlock (including text and shading).

        Parameters:
            colour: A string specifying a valid colour (name or #rrggbb acceptable)."""
        colour = Colour.string(colour)

        cn = self.gui_view.canvas

        (light, dark, textcolour) = DrawView.get_colour_shades(colour)

        try:
            (rect, text, lines) = self.group
            cn.itemconfigure(rect, fill=colour, outline=colour)
            cn.itemconfigure(text, fill=textcolour)

            for i in range(len(lines)):
                cn.itemconfigure(lines[i * 2], fill=dark[i])
                cn.itemconfigure(lines[i * 2 + 1], fill=light[i])

        except IndexError:
            print("FAILED CHANGE COLOUR\n")

    # =================================================================
    # getters/setters
    # =================================================================
    # Skipping most of these except for Colour, as that's the only one with special validation.
    @property
    def colour(self):
        """Gets/sets the colour for this GuiBlock."""
        return self._colour

    @colour.setter
    def colour(self, value: str):
        self._colour = value
        canvas = self.gui_view.canvas
        rectangle = self.rectangle
        canvas.itemconfigure(rectangle, fill=self._colour)

    @property
    def id(self) -> int:
        """Returns the unique id for this GuiBlock object."""
        return self._id

# =================================================================
# footer
# =================================================================
"""
=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns

Rewritten for Python by Evan Laverdiere

=head1 COPYRIGHT

Copyright (c) 2016, Jack Burns, Sandy Bultena, Ian Clement. 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut

1;

"""