import pony.orm

from ..GUI.SchedulerTk import SchedulerTk
from ..Schedule.Schedule import Schedule
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


# ==================================================================
# read_ini
# ==================================================================
def read_ini():
    # NOTE: This function may no longer be necessary, since we aren't reading from YAML
    # files anymore.
    pass


# ==================================================================
# write_ini
# ==================================================================
def write_ini():
    # NOTE: Same with this one.
    pass


# ==================================================================
# define what goes in the menu and toolbar
# ==================================================================
def menu_info():
    # NOTE: Per Sandy's recommendation, I am skipping some aspects of this for now.

    # ----------------------------------------------------------
    # button names
    # ----------------------------------------------------------
    buttons = ['new', 'open', 'save']

    # ----------------------------------------------------------
    # actions with callback and hints
    # ----------------------------------------------------------
    actions: dict[str, dict[str]] = {
        'new': {
            'code': new_schedule,
            'hint': 'Create new Schedule File'
        },
        'open': {
            'code': open_schedule,
            'hint': 'Open Schedule File'
        },
        'save': {
            'code': save_schedule,
            'hint': 'Save Schedule File'
        }
    }

    # ----------------------------------------------------------
    # menu structure NOTE: SKIP FOR NOW
    # ----------------------------------------------------------
    menu: list[dict] = [{}]

    return buttons, actions, menu


# ==================================================================
# new_schedule
# ==================================================================
def new_schedule():
    # NOTE: Sandy left this to-do in the original Perl script: TODO: save previous schedule?
    global schedule, current_schedule_file
    schedule = Schedule()  # TODO: Change this to reflect what's in the db.
    current_schedule_file = None

    _schedule_file_changed(None)


# ==================================================================
# open_schedule
# ==================================================================
def open_schedule():
    # This is another one that will have to change.
    pass


# ==================================================================
# schedule file has changed
# ==================================================================
def _schedule_file_changed(file):
    # Another one with lots of changes to be made.
    global schedule
    if file and schedule:
        global current_schedule_file, current_directory
        current_schedule_file = file
        current_directory = file
        write_ini()


# ==================================================================
# save (as) schedule
# ==================================================================
def save_schedule():
    _save_schedule(False)


def save_as_schedule():
    _save_schedule(True)


def _save_schedule(save_as: bool):
    global schedule, gui
    gui: SchedulerTk
    schedule: Schedule

    if schedule is None:
        gui.show_error("Save Schedule", "There is no schedule to save!")
        return

    # get file to save to
    file: str
    global current_schedule_file
    if save_as or not current_schedule_file:
        file = gui.choose_file()
        # NOTE: This probably doesn't need to be implemented anymore.
        if not file:
            return
    else:
        file = current_schedule_file

    # Save to database.
    try:
        schedule.write_DB()
    except pony.orm.Error as err:
        gui.show_error("Save Schedule", f"Cannot save schedule:\nError: {err}")

    # save the current file for later use.
    # NOTE: We probably don't need these anymore.

    return


# ==================================================================
# save as CSV
# ==================================================================
def save_as_csv():
    pass


# ==================================================================
# update_choices_of_schedulable_views
# (what teachers/labs/streams) can we create schedules for?
# ==================================================================
def update_choices_of_schedulable_views():
    global views_manager
    btn_callback = views_manager.get_create_new_view_callback
