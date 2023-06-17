import pony.orm
from pony.orm import Database
from __future__ import annotations

from .ViewsManager import ViewsManager
from ..GUI.SchedulerTk import SchedulerTk
from ..GuiSchedule.ScenarioSelector import ScenarioSelector
from ..GuiSchedule.ScheduleSelector import ScheduleSelector
from ..Schedule.Schedule import Schedule
from ..Schedule.database.PonyDatabaseConnection import define_database, Scenario
from ..Schedule.database.db_constants import PROVIDER, DB_NAME, CREATE_DB
from ..UsefulClasses.NoteBookPageInfo import NoteBookPageInfo
from .globals import *

from ..Presentation.MenuItem import MenuItem, MenuType, ToolbarItem

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
gui: SchedulerTk
global views_manager
views_manager: ViewsManager
db: Database = None
scenario: Scenario | None = None

# ==================================================================
# required Notebook pages
# ==================================================================
# NOTE: Come back to these later.
required_pages: list[NoteBookPageInfo]
# required_pages = [
#     NoteBookPageInfo("Schedules", update_choices_of_schedulable_views),
#     NoteBookPageInfo("Overview", update_overview),
#     NoteBookPageInfo("Courses", update_edit_courses),
#     NoteBookPageInfo("Teachers", update_edit_teachers),
#     NoteBookPageInfo("Labs", update_edit_labs),
#     NoteBookPageInfo("Streams", update_edit_streams)
# ]

pages_lookup: dict[str, NoteBookPageInfo]  # = dict([(p.name, p) for p in required_pages])


# ==================================================================
# main
# ==================================================================
def main():
    global gui
    gui = SchedulerTk()

    global required_pages, pages_lookup
    required_pages = [
        NoteBookPageInfo("Schedules", update_choices_of_schedulable_views),
        NoteBookPageInfo("Overview", update_overview),
        NoteBookPageInfo("Courses", update_edit_courses),
        NoteBookPageInfo("Teachers", update_edit_teachers),
        NoteBookPageInfo("Labs", update_edit_labs),
        NoteBookPageInfo("Streams", update_edit_streams)
    ]
    pages_lookup = dict([(p.name, p) for p in required_pages])

    # SANDY COMMENT:  It was just a way to verify that the gui class has the correct
    #                 methods, as perl does not have abstract classes
    # NOTE: I have no idea where this comes from. Commenting it out for now.
    # for method in Scheduler.SchedulerManagerGui_methods:
    #     if not hasattr(gui, method):
    #         raise ValueError(f"Your GUI class does not contain the method {method}")

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
    gui.create_main_window()

    (toolbar_buttons, button_properties, menu) = __menu_and_toolbar_info()
    gui.create_menu_and_toolbars(toolbar_buttons, button_properties, menu)
    gui.create_front_page(preferences, open_schedule, new_schedule)
    gui.create_status_bar()


# ==================================================================
# pre-process procedures
# ==================================================================
def pre_process_stuff():
    global gui
    gui.bind_dirty_flag()
    gui.define_notebook_tabs(required_pages)

    gui.define_exit_callback(exit_schedule)

    # Create the view manager (which shows all the schedule views, etc.)
    global views_manager, schedule
    # TODO: Implement ViewsManager class.
    views_manager = ViewsManager(gui, is_data_dirty(), schedule)
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
def __menu_and_toolbar_info() -> (list[str], list[ToolbarItem], list[MenuItem]):
    menu = list()

    # -----------------------------------------------------------------------------------------
    # File menu
    # -----------------------------------------------------------------------------------------
    file_menu = MenuItem(name='file', menu_type=MenuType.Cascade, label='File')
    file_menu.add_child(MenuItem(name='new', menu_type=MenuType.Command, label='New', accelerator='Ctrl-n',
                                 command=lambda *_: print("'File/New' selected")))
    file_menu.add_child(MenuItem(name='open', menu_type=MenuType.Command, label='Open', accelerator='Ctrl-o',
                                 command=lambda *_: print("'File/Open' selected")))

    file_menu.add_child(MenuItem(menu_type=MenuType.Separator))

    file_menu.add_child(MenuItem(name='save', menu_type=MenuType.Command, label='Save', accelerator='Ctrl-s',
                                 underline=0,
                                 command=lambda *_: print("'File/Save' selected")))
    file_menu.add_child(MenuItem(name='save_as', menu_type=MenuType.Command, label='Save As',
                                 command=lambda *_: print("'File/Save As' selected")))

    file_menu.add_child(MenuItem(menu_type=MenuType.Separator))

    file_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Exit', accelerator='Ctrl-e',
                                 command=lambda *_: print("'File/Exit' selected")))

    # -----------------------------------------------------------------------------------------
    # Print menu
    # -----------------------------------------------------------------------------------------
    print_menu = MenuItem(name='print', menu_type=MenuType.Cascade, label='Print')
    pdf_menu = MenuItem(menu_type=MenuType.Cascade, label='PDF')
    latex_menu = MenuItem(menu_type=MenuType.Cascade, label='Latex')
    print_menu.add_child(pdf_menu)
    print_menu.add_child(latex_menu)

    # pdf sub-menu
    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Teacher Schedules',
                                command=lambda *_: print("'Print/Teacher Schedules' selected")))
    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Lab Schedules',
                                command=lambda *_: print("'Print/Lab Schedules' selected")))
    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Stream Schedules',
                                command=lambda *_: print("'Print/Stream Schedules' selected")))

    pdf_menu.add_child(MenuItem(menu_type=MenuType.Separator))

    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Text Output',
                                command=lambda *_: print("'Print/Text Output' selected")))

    # latex sub menu
    latex_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Teacher Schedules',
                                  command=lambda *_: print("'Print/Teacher Schedules' selected")))
    latex_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Lab Schedules',
                                  command=lambda *_: print("'Print/Lab Schedules' selected")))
    latex_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Stream Schedules',
                                  command=lambda *_: print("'Print/Stream Schedules' selected")))

    latex_menu.add_child(MenuItem(menu_type=MenuType.Separator))

    latex_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Text Output',
                                  command=lambda *_: print("'Print/Text Output' selected")))

    # -----------------------------------------------------------------------------------------
    # toolbar
    # -----------------------------------------------------------------------------------------
    toolbar_info = dict()
    toolbar_info['new'] = ToolbarItem(command=MenuItem.all_menu_items['new'], hint='Create new Schedule File')
    toolbar_info['open'] = ToolbarItem(command=MenuItem.all_menu_items['open'], hint='Open Schedule File')
    toolbar_info['save'] = ToolbarItem(command=MenuItem.all_menu_items['save'], hint='Save Schedule File')
    toolbar_order = ['new', 'open', 'save']

    # return list of top level menu items
    menu.append(file_menu)
    menu.append(print_menu)
    return toolbar_order, toolbar_info, menu


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

    # For the moment, we'll connect to the database. In the future, this will need to be decoupled.
    global db

    if not db:
        if PROVIDER == "sqlite":
            # If it's SQLite, connect to the database.
            db = define_database(provider=PROVIDER, filename=DB_NAME, create_db=CREATE_DB)
        elif PROVIDER == "mysql":
            # Otherwise, connect to the remote MySQL database. NOTE: Come back to this later.
            pass

    def get_scenario(current_scen, selected_scen):
        current_scen = selected_scen
        return current_scen

    # Are we opening a local SQLite database, or connecting to a remote MySQL one?
    if PROVIDER == "sqlite":
        global scenario

        def get_scenario(func):
            global scenario
            scenario = func()
            print(f"In the callback, the scenario is {scenario}.")

        # Open a ScenarioSelector window.
        ScenarioSelector(parent=gui.mw, db=db, two=False, callback=get_scenario)
        # NOTE: The lines of code below don't run until the main window of the app is closed.
        # We'll need to pass in something else to be the ScenarioSelector's parent.
        print(f"The scenario is {scenario}")
        gui.show_info("Scenario", f"The selected scenario is {scenario}.")

        if not scenario or len(scenario) != 1 or scenario[0] is None:
            gui.show_error("INVALID SELECTION", "Incorrect number of Scenarios picked. "
                                                "Please select 1.")
        else:
            global schedule

            def get_schedule(func):
                global schedule
                schedule = func()
                print(f"Retrieved the following object from function: {schedule}")

            ScheduleSelector(parent=gui.mw, db=db, scenario=scenario[0], callback=get_schedule)
            gui.show_info("SCHEDULE SELECTED", f"Successfully selected a Schedule: {schedule}")

            # If the schedule was successfully read, then
            views_manager.schedule = schedule
            _schedule_file_changed(None)

    elif PROVIDER == "mysql":
        # Otherwise, open the login window. NOTE: Come back to this later.
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

    gui.update_for_new_schedule_and_show_page(
        pages_lookup['Schedules'].id
    )


# ==================================================================
# save (as) schedule
# ==================================================================
def save_schedule():
    _save_schedule(False)


def save_as_schedule():
    _save_schedule(True)


def _save_schedule(save_as: bool):
    global schedule, gui

    if schedule is None:
        gui.show_error("Save Schedule", "There is no schedule to save!")
        return

    # get_by_id file to save to
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
# (what teacher_ids/lab_ids/stream_ids) can we create schedules for?
# ==================================================================
def update_choices_of_schedulable_views():
    global views_manager, gui
    btn_callback = views_manager.get_create_new_view_callback
    all_view_choices = views_manager.get_all_scheduables()
    page_name = pages_lookup['Schedules'].name
    gui.draw_view_choices(page_name, all_view_choices, btn_callback)

    views_manager.determine_button_colours()


# ==================================================================
# update_overview
# A text representation of the schedules
# ==================================================================
def update_overview():
    pass


# ==================================================================
# update_edit_teachers
# - A page where teacher_ids can be added/modified or deleted
# ==================================================================
def update_edit_teachers():
    pass


# ==================================================================
# update_edit_streams
# - A page where stream_ids can be added/modified or deleted
# ==================================================================
def update_edit_streams():
    pass


# ==================================================================
# update_edit_labs
# - A page where lab_ids can be added/modified or deleted
# ==================================================================
def update_edit_labs():
    pass


# ==================================================================
# draw_edit_courses
# - A page where courses can be added/modified or deleted
# ==================================================================
def update_edit_courses():
    pass


# ==================================================================
# print_views
# - print the schedule 'views'
# - type defines the output type, PDF, Latex
# ==================================================================
def print_views(print_type, type):
    global gui
    # --------------------------------------------------------------
    # no schedule yet
    # --------------------------------------------------------------

    if not schedule:
        gui.show_error("Export", "Cannot export - There is no schedule")

    # --------------------------------------------------------------
    # cannot print if the schedule is not saved
    # --------------------------------------------------------------
    if is_data_dirty():
        ans = gui.question(
            "Unsaved Changes",
            "There are unsaved changes.\nDo you want to save them?"
        )
        if ans:
            save_schedule()
        else:
            return

    # --------------------------------------------------------------
    # define base file name
    # --------------------------------------------------------------
    # NOTE: Come back to this later.
    pass


# ==================================================================
# exit_schedule
# ==================================================================
def exit_schedule():
    global gui
    if is_data_dirty():
        answer = gui.question("Save Schedule", "Do you want to save changes?")
        if answer == "Yes":
            save_schedule()
        elif answer == "Cancel":
            return
    write_ini()
