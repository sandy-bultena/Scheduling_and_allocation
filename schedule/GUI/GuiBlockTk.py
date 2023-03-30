from ..Export import DrawView
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
    def __init__(self, type: str, gui_view, block: Block, colour: str = ""):
        """Creates, draws and returns a GuiBlock object.

        Parameters:
            type: Type of view (teacher/lab/stream).
            gui_view: The GUI object associated with this view.
            block: The Block to turn into a GuiBlock.
            colour: The colour of the GuiBlock."""
        # get canvas from gui_view to draw on.
        canvas = gui_view.canvas

        # draw the block
        gui_objs = DrawView.draw_block(canvas, block, gui_view.get_scale_info(), type, colour)

        lines = gui_objs['lines']
        text = gui_objs['text']
        rectangle = gui_objs['rectangle']
        coords = gui_objs['coords']
        colour = gui_objs['colour']

        # Group rectangle and text to create a GuiBlock,
        # So that they both move as one on the UI.
        # NOTE: canvas.createGroup() doesn't exist in Tkinter. It's exclusive to Perl/Tk.
        # Plus, Sandy told us not to bother with it.

        # Create the object.
        self._id = GuiBlockTk.Max_id + 1
        self.block = block
        self.gui_view = gui_view
        self._coords = coords
        self.colour = colour
        self.rectangle = rectangle
        self.text = text
        self.is_controlled = False

