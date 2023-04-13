"""ViewsManager - Manage all of the views (presentations of schedules)"""
from ..GUI.ViewsManagerTk import ViewsManagerTk
from ..Schedule.Schedule import Schedule


class ViewsManager:
    """This class creates a button interface to access all of the schedule views,
    and it manages those views.

    Manages all the 'undo' and 'redo' of actions taken upon the views."""

    # =================================================================
    # Class Variables
    # =================================================================
    max_id = 0

    # =================================================================
    # new
    # =================================================================
    def __int__(self, gui_main, dirty_flag_ptr, schedule: Schedule):
        """Creates a ViewsManager object.

        Parameters:
            gui_main: The gui that is used by whatever class invokes this class, because we need to know the main_window etc.
            dirty_flag_ptr: Pointer to a flag that indicates if the schedule has been changed since the last save.
            schedule: Where course-sections/teachers/labs/streams are defined."""
        gui = ViewsManagerTk(gui_main)
        self.gui = gui
        self.gui_main = gui_main
        ViewsManager.max_id += 1
        self.id = ViewsManager.max_id
        self.dirty_flag = dirty_flag_ptr  # NOTE: Replace this w/ call to the globals object?
        self.schedule = schedule

