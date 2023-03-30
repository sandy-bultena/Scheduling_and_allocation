"""A half hour time block used to select time slots on a view."""
from tkinter import Canvas


class AssignBlockTk:
    """Defines a 1/2 hour block of time within a view.

    You can find this time block by specifying the x/y canvas coordinates, or by the day, start and
    end time.

    The block can be coloured, or uncoloured."""
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
            start: Time that this gui block starts (real number)"""
        # Raise some sort of warning if view is None or absent.

        # ---------------------------------------------------------------
        # draw 1/2 the block
        # ---------------------------------------------------------------
        cn: Canvas = view.gui.canvas
        coords = view.gui.get_time_coords(day, start, 1/2)

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
        self.canvas = view.gui.canvas

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
        """Find the first block within assigned blocks that contains the canvas coords x & y.

        Parameters:
            x: canvas coordinates
            y: canvas coordinates
            assigned_blocks: array of AssignBlocks
        Returns:
            AssignBlock object if found, None otherwise"""
        if not assigned_blocks:
            return

        found: list[AssignBlockTk] = [b for b in assigned_blocks if b._at_canvas_coords(x,y)]
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

        # make sure we start from the left top towards the bottom right.
        if x1 > x2:
            tmp = x1
            x1 = x2
            x2 = tmp
        if y1 > y2:
            tmp = y1
            y1 = y2
            y2 = tmp

        return [b for b in assigned_blocks if b.x1 < x2 and b.x2 > x1 and b.y1 < y2 and b.y2 > y1]
    # endregion
