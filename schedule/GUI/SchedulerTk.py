from .MainPageBaseTk import MainPageBaseTk


class SchedulerTk(MainPageBaseTk):
    """
    GUI Code for the main application window. Inherits from MainPageBaseTk.
    """

    # ============================================================================
    # Package variables
    # ============================================================================
    views_manager = None
    mw = None

    # region ACCESS TO EXTERNAL DATA
    def set_views_manager(self, views_manager):
        """Sometimes this Tk class needs access to the views_manager.

        This method makes the views_manager available to this code."""

    # endregion
    def choose_existing_file(self, curr_dir, file_types):
        pass

    def choose_file(self, curr_dir, file_types):
        pass

