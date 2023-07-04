# IN PROGRESS
import os.path

from typing import Callable, Optional
from ..UsefulClasses.Preferences import Preferences

from .MainPageBaseTk import MainPageBaseTk
from tkinter import *
from tkinter import ttk

BUTTON_WIDTH = 50
MAX_LEN_OF_DISPLAYED_FILENAME = 25


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
    def __init__(self, title: str, preferences: Preferences):
        self.preferences: Preferences = preferences
        self.current_file: Optional[str] = None
        self.current_file_button: Optional[Button] = None

        super().__init__(title, preferences)
        self.current_semester: StringVar = StringVar()

    # ========================================================================
    # create front page
    # ========================================================================
    def create_front_page(self, open_schedule_callback: Callable[[str], None],
                          new_schedule_callback: Callable[[], None]):

        self._open_schedule_callback = open_schedule_callback
        self._new_schedule_callback = new_schedule_callback

        """Creates the very first page that is shown to the user."""
        option_frame = super().create_front_page_base()

        # --------------------------------------------------------------
        # which semester?
        # --------------------------------------------------------------
        semester_str = self.preferences.semester()
        self.current_semester.set(semester_str)
        radio_frame = Frame(option_frame)
        radio_frame.pack(side=TOP, fill=Y, expand=1)
        radio_fall = Radiobutton(radio_frame, text='Fall', variable=self.current_semester, value='fall')
        radio_winter = Radiobutton(radio_frame, text='Winter', variable=self.current_semester, value='winter')

        radio_fall.grid(row=0, column=0)
        radio_winter.grid(row=0, column=1)

        self.current_file = self.preferences.current_file()
        self.current_semester.trace('w', self._semester_change_event)

        # --------------------------------------------------------------
        # open previous schedule file buttons
        # -------------------------------------------------------------
        self.current_file_button = Button(
            option_frame,
            justify=RIGHT,
            font=self.fonts.big,
            borderwidth=0,
            bg=self.colours.DataBackground,
            command=self._open_schedule,
            width=BUTTON_WIDTH,
            height=3
        )
        self.current_file_button.pack(side=TOP, fill=Y, expand=0)

        # --------------------------------------------------------------
        # create new schedule file option
        # --------------------------------------------------------------
        Button(
            option_frame,
            text="Create NEW Schedule File",
            font=self.fonts.big,
            borderwidth=0,
            bg=self.colours.DataBackground,
            command=self._new_schedule_callback,
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
            bg=self.colours.DataBackground,
            command=self.select_file,
            width=BUTTON_WIDTH,
            height=3
        ).pack(side=TOP, fill=Y, expand=0)

        # a growable and shrinkable frame which makes resizing look better
        Frame(
            option_frame, bg=self.colours.DataBackground
        ).pack(expand=1, fill=BOTH)

        # --------------------------------------------------------------
        # update the current file and/or button
        # --------------------------------------------------------------
        self._semester_change_event()

    # ========================================================================
    # semester has changed, so update semester and update current file
    # ========================================================================
    def _semester_change_event(self, *_):

        # update semester and current file
        self.preferences.semester(self.current_semester.get())
        self.current_file = self.preferences.current_file()

        # update the button that opens the last previous file
        if self.current_file_button is not None:
            if self.current_file is not None:
                basename = os.path.basename(self.current_file)
                if len(basename) > MAX_LEN_OF_DISPLAYED_FILENAME:
                    basename = basename[0:MAX_LEN_OF_DISPLAYED_FILENAME] + ". . ."
                self.current_file_button.configure(state='normal', text=basename)
            else:
                self.current_file_button.configure(state='disabled', text='')

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
    # def draw_view_choices(self, default_tab: str, all_scheduables: AllScheduables,
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
    #         all_scheduables: A list of schedulable objects (teacher_ids/lab_ids/etc.)
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
    #     for type in all_scheduables.valid_types():
    #         view_choices_frame = LabelFrame(
    #             SchedulerTk.frame,
    #             text=all_scheduables.by_type(type).title)
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
    #             all_scheduables.by_type(type),
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

