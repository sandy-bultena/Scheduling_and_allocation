import os.path

from typing import Callable, Optional, Literal, get_args

from ..Utilities.Preferences import Preferences

from .main_pages_tk import MainPageBaseTk
from tkinter import *
from tkinter import ttk

BUTTON_WIDTH = 50
MAX_LEN_OF_DISPLAYED_FILENAME = 60

# ============================================================================
# event handlers
# ============================================================================

EVENT_HANDLER_NAMES = Literal[
    "file_open",
    "file_new",
    "file_open_previous",
    "file_exit",
    "semester_change"
]
MAIN_PAGE_EVENT_HANDLERS: dict[EVENT_HANDLER_NAMES, Callable[[], None]] = {}
for event_name in get_args(EVENT_HANDLER_NAMES):
    MAIN_PAGE_EVENT_HANDLERS[event_name] = lambda: print(f"'selected. {event_name}")


def set_main_page_event_handler(name: EVENT_HANDLER_NAMES, handler: Callable[[], None]):
    MAIN_PAGE_EVENT_HANDLERS[name] = handler


# ============================================================================
# class: SchedulerTk
# ============================================================================
class SchedulerTk(MainPageBaseTk):
    """
    GUI_Pages Code for the main Scheduling application window. Inherits from MainPageBaseTk.
    """
    # ========================================================================
    # class variables
    # ========================================================================
    _overview_notebook: Optional[ttk.Notebook] = None
    _overview_teacher_textbox: Optional[Text] = None
    _overview_course_textbox: Optional[Text] = None

    # ========================================================================
    # constructor
    # ========================================================================
    def __init__(self, title: str, preferences: Preferences, bin_dir: str):
        self.preferences: Preferences = preferences
        self.previous_file_button: Optional[Button] = None
        self._schedule_filename = ""

        super().__init__(title, preferences)
        MainPageBaseTk.bin_dir = bin_dir
        self._current_semester: StringVar = StringVar()  # bound to semester_frame radio buttons
        self._previous_file: StringVar = StringVar(value="None")  # bound to previous_file_button

    @property
    def current_semester(self):
        return self._current_semester.get()

    @current_semester.setter
    def current_semester(self, value):
        self._current_semester.set(value)

    @property
    def previous_file(self):
        return self._previous_file.get()

    @previous_file.setter
    def previous_file(self, value):
        if value is not None and value != "":
            basename = os.path.basename(value)
            if len(basename) > MAX_LEN_OF_DISPLAYED_FILENAME:
                basename = "..." + basename[len(basename) - MAX_LEN_OF_DISPLAYED_FILENAME:]
            self._previous_file.set(basename)
        else:
            self._previous_file.set("None")

    @property
    def schedule_filename(self):
        return self._schedule_filename

    @schedule_filename.setter
    def schedule_filename(self, value: str):
        self._schedule_filename = value
        if value is not None and value != "":
            value = os.path.abspath(value)
            if len(value) > MAX_LEN_OF_DISPLAYED_FILENAME:
                value = "... " + value[len(value) - MAX_LEN_OF_DISPLAYED_FILENAME:]
        self.status_bar_file_info = value

    # ========================================================================
    # override exit event
    # ========================================================================
    def _exit_schedule(self, *_):
        self.exit_schedule()

    def exit_schedule(self):
        MAIN_PAGE_EVENT_HANDLERS["file_exit"]()
        super()._exit_schedule()

    # ========================================================================
    # create front page
    # ========================================================================
    def create_front_page(self, semester):
        """Creates the very first page that is shown to the user."""
        option_frame = super().create_front_page_base()

        # --------------------------------------------------------------
        # which semester?
        # --------------------------------------------------------------
        self._current_semester.set(str(semester))
        semester_frame = Frame(option_frame)
        semester_frame.pack(side=TOP, fill=Y, expand=1)
        radio_fall = Radiobutton(semester_frame, text='Fall', variable=self._current_semester, value='fall')
        radio_winter = Radiobutton(semester_frame, text='Winter', variable=self._current_semester, value='winter')

        radio_fall.grid(row=0, column=0)
        radio_winter.grid(row=0, column=1)

        # place a watch on changing bound variables
        self._current_semester.trace('w', MAIN_PAGE_EVENT_HANDLERS["semester_change"])

        def _previous_file_change_event(*_):
            if self._previous_file != "None":
                self.previous_file_button.configure(state='normal')
            else:
                self.previous_file_button.configure(state='disabled')

        self._previous_file.trace('w', _previous_file_change_event)

        # --------------------------------------------------------------
        # open previous schedule file buttons
        # -------------------------------------------------------------
        self.previous_file_button = Button(
            option_frame,
            justify=RIGHT,
            font=self.fonts.big,
            borderwidth=0,
            background=self.colours.ButtonBackground,
            foreground=self.colours.ButtonForeground,
            command=MAIN_PAGE_EVENT_HANDLERS["file_open_previous"],
            width=BUTTON_WIDTH,
            height=3,
            textvariable=self._previous_file
        )
        self.previous_file_button.pack(side=TOP, fill=Y, expand=0)

        # --------------------------------------------------------------
        # create new schedule file option
        # --------------------------------------------------------------
        Button(
            option_frame,
            text="Create NEW Schedule File",
            font=self.fonts.big,
            borderwidth=0,
            background=self.colours.ButtonBackground,
            foreground=self.colours.ButtonForeground,
            command=MAIN_PAGE_EVENT_HANDLERS["file_new"],
            width=BUTTON_WIDTH,
            height=3
        ).pack(side=TOP, fill=Y, expand=0)

        # --------------------------------------------------------------
        # open schedule file option
        # --------------------------------------------------------------
        Button(
            option_frame,
            text="Browse for Schedule File",
            font=self.fonts.big,
            borderwidth=0,
            background=self.colours.ButtonBackground,
            foreground=self.colours.ButtonForeground,
            command=MAIN_PAGE_EVENT_HANDLERS["file_open"],
            width=BUTTON_WIDTH,
            height=3
        ).pack(side=TOP, fill=Y, expand=0)

        # a growable and shrinkable frame which makes resizing look better
        Frame(
            option_frame, background=self.colours.DataBackground
        ).pack(expand=1, fill=BOTH)

        # --------------------------------------------------------------
        # update the current file and/or button
        # --------------------------------------------------------------
        MAIN_PAGE_EVENT_HANDLERS["semester_change"]()

    # ========================================================================
    # semester has changed, so update semester and update current file
    # ========================================================================

    # def set_views_manager(self, my_views_manager):
    #     """Defines the code that manages the view"""
    #     self.views_manager = my_views_manager
    #
    # def update_for_new_schedule_and_show_page(self, default_page_id):
    #     global views_manager
    #     # TODO: Determine if this is ViewsManager, or ViewsManagerTk.
    #     views_manager.destroy_all()
    #     super().update_for_new_schedule_and_show_page(default_page_id)
    #
    # # endregion
    #
    # def draw_view_choices(self, default_tab: str, all_resources: AllResources,
    #                       btn_callback: Callable = lambda: None):
    #     """The ViewsManager can create schedule views for all teacher_ids/lab_ids etc.
    #
    #     The allowable views depend on the schedules, so this function needs to be called whenever
    #     the schedule changes.
    #
    #     Draws the buttons to access any of the available views.
    #
    #     Parameters:
    #         default_tab: Name of _notebook tab to draw on.
    #         all_resources: A list of resource_type objects (teacher_ids/lab_ids/etc.)
    #         btn_callback: A callback function called whenever the ViewsManager is asked to create a
    #         view."""
    #     f = self.pages[default_tab.lower()]
    #
    #     views_manager.gui.reset_button_refs()
    #
    #     # global frame
    #     if SchedulerTk.frame:
    #         SchedulerTk.frame.destroy()
    #
    #     SchedulerTk.frame = Frame(f)
    #     SchedulerTk.frame.pack(expand=1, fill=BOTH)
    #
    #     # TODO: View choice frames have positioning issues due to Scrolled's use of pack. Buttons are not centered.
    #     for resource_type in all_resources.valid_types():
    #         view_choices_frame = LabelFrame(
    #             SchedulerTk.frame,
    #             text=all_resources.by_type(resource_type).title)
    #         view_choices_frame.pack(expand=1, fill=BOTH)
    #
    #         view_choices_scrolled_frame = Scrolled(view_choices_frame, 'Frame', scrollbars="osoe")
    #         # view_choices_scrolled_frame = ScrolledFrame(view_choices_frame)
    #         view_choices_scrolled_frame.pack(expand=1, fill=BOTH)
    #
    #         # NOTE: Program was crashing inside this function call because
    #         # view_choices_scrolled_frame already has children managed by pack, while the
    #         # function is trying to add buttons managed by grid to view_choices_scrolled_frame.
    #         # Tcl doesn't like it when children of the same notebook use different geometry managers.
    #         views_manager.gui.create_buttons_for_frame(
    #             view_choices_scrolled_frame,
    #             all_resources.by_type(resource_type),
    #             btn_callback
    #         )
    #
    # tbox3: Scrolled = None
    # tbox = None
    # tbox2: Scrolled = None
    #
    # _overview_notebook = None
    # overview_pages: dict[str, Frame] = {}
    #
    def get_gui_container(self, page_name: str) -> Optional[Frame]:
        return self.dict_of_frames.get(page_name.lower())
