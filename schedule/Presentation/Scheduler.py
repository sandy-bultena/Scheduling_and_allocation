from ..GUI.SchedulerTk import SchedulerTk
from ..UsefulClasses.NoteBookPageInfo import NoteBookPageInfo

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
global gui
views_manager = None

# ==================================================================
# required Notebook pages
# ==================================================================
# NOTE: Come back to these later.
required_pages = [
    NoteBookPageInfo("Schedules", update_choices_of_schedulable_views),
    NoteBookPageInfo("Overview", update_overview),
    NoteBookPageInfo("Courses", update_edit_courses),
    NoteBookPageInfo("Teachers", update_edit_teachers),
    NoteBookPageInfo("Labs", update_edit_labs),
    NoteBookPageInfo("Streams", update_edit_streams)
]

pages_lookup: dict[str, NoteBookPageInfo] = dict([(p.name, p) for p in required_pages])


# ==================================================================
# main
# ==================================================================
def main():
    global gui
    gui = SchedulerTk()

    # NOTE: I have no idea where this comes from.
    for method in Scheduler.SchedulerManagerGui_methods:
        if not hasattr(gui, method):
            raise ValueError(f"Your GUI class does not contain the method {method}")

    get_user_preferences()
    create_main_window()
    pre_process_stuff()
    gui.start_event_loop()


# ==================================================================
# user preferences saved in ini file (YAML format)
# ==================================================================
# NOTE: This will have to change significantly to look through the database instead.
def get_user_preferences():
    pass


# ==================================================================
# Create the mainWindow
# ==================================================================
def create_main_window():
    global gui, preferences
    gui: SchedulerTk
    gui.create_main_window()

    (toolbar_buttons, button_properties, menu) = menu_info()
    gui.create_menu_and_toolbars(toolbar_buttons, button_properties, menu)
    gui.create_front_page(preferences, open_schedule, new_schedule)
    gui.create_status_bar()


# ==================================================================
# pre-process procedures
# ==================================================================
def pre_process_stuff():
    global gui
    gui: SchedulerTk
    gui.bind_dirty_flag()
    gui.define_notebook_tabs(required_pages)

    gui.define_exit_callback(exit_schedule)

    # Create the view manager (which shows all the schedule views, etc.)
    global views_manager, schedule
    # TODO: Implement ViewsManager class.
    views_manager = ViewsManager(gui, schedule)
    gui.set_views_manager(views_manager)
