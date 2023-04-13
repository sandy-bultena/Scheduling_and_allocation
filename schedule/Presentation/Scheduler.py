class Scheduler:
    """
    # ==================================================================
    # This is the main entry point for the Scheduler Program
    # ==================================================================

    # uses MVP protocol, so the GUI must be implement the methods, etc
    # defined in SchedulerManagerViewInterface.pm


    """
    # ==================================================================
    # global vars
    # ==================================================================
    # NOTE: Some of these class variables are probably unnecessary now.
    user_base_dir = None
    preferences = {}
    schedule = None
    current_schedule_file = ""
    current_directory = ""
    file_types = (("Schedules", ".yaml"), ("All Files", "*"))
    gui = None
    views_manager = None

    # ==================================================================
    # required Notebook pages
    # ==================================================================
    # NOTE: Come back to these later.
    required_pages = []

    pages_lookup = dict()

    # ==================================================================
    # main
    # ==================================================================
    @staticmethod
    def main():
        # TODO: Implement SchedulerTk.
        Scheduler.gui = SchedulerTk.new()
        pass