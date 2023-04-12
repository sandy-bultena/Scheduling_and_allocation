"""Create or assign Time Blocks to various resources."""
from ..GUI.AssignToResourceTk import AssignToResourceTk
from ..Schedule.Lab import Lab
from ..Schedule.Schedule import Schedule
from ..Schedule.Stream import Stream
from ..Schedule.Teacher import Teacher

# ===================================================================
# globals
# ===================================================================
global course
global section
global block
global teacher
global lab
global gui


class AssignToResource:
    """Create or assign Time Blocks to various resources.

    Called with a date/time/duration of a block, as well as a Teacher/Lab.

    Allows the user to assign this block to a Course and Section,
    or to create a new block.

    or to assign an existing block to Course and Section."""
    # =================================================================
    # Class/Global Variables
    # =================================================================
    global schedule
    global mw
    global Type
    Day_name = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday"
    }

    # ===================================================================
    # Constructor
    # ===================================================================
    def __init__(self, mw, schedule: Schedule, day: int, start, duration, schedulable):
        """Creates and manages a gui that will allow the user to assign a block to various
        resources.

        Parameters:
            mw: The main GUI window.
            schedule: Schedule object.
            day: new Block information
            start: new Block information
            duration: new Block information
            schedulable: Teacher or Lab (nothing will happen if this is a Stream object)."""
        global Type
        Type = schedule.get_view_type_of_object(schedulable)
        if Type == Lab:
            global lab
            lab = schedulable
        elif Type == Teacher:
            global teacher
            teacher = schedulable
        elif Type == Stream or Type is None:
            return

        # ------------------------------------
        # Create Dialog Box
        # ------------------------------------
        title = "Assign Block to " + Type
        block_text = f"{AssignToResource.Day_name[day]} at " \
                     f"{_hours_to_string(start)} for {duration} hour(s)"

        global gui
        gui = AssignToResourceTk(Type) # TODO: Implement this class.
        gui.draw(mw, title, block_text)

        # ------------------------------------
        # open dialog
        # ------------------------------------
        if schedule:
            _open_dialog()

    # ============================================================================
    # OpenDialog
    # ============================================================================
    def _open_dialog(self):
        # ------------------------------------
        # setup event handlers
        # ------------------------------------
        global gui

        pass

