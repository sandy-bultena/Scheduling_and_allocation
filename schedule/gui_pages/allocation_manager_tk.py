# COMPLETED
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
    "fall_file_open",
    "fall_file_new",
    "fall_file_open_previous",
    "fall_file_open_previous",
    "winter_file_open",
    "winter_file_new",
    "winter_file_open_previous",
    "winter_file_open_previous",
    "exit",
]

MAIN_PAGE_EVENT_HANDLERS: dict[EVENT_HANDLER_NAMES, Callable[[], None]] = {}
for event_name in get_args(EVENT_HANDLER_NAMES):
    MAIN_PAGE_EVENT_HANDLERS[event_name] = lambda: print(f"'selected. {event_name}")


def set_main_page_event_handler(name: EVENT_HANDLER_NAMES, handler: Callable[[], None]):
    MAIN_PAGE_EVENT_HANDLERS[name] = handler

# ============================================================================
# class: AllocationManagerTk
# ============================================================================
class AllocationManagerTk(MainPageBaseTk):

    # ========================================================================
    # constructor
    # ========================================================================
    def __init__(self, title: str, preferences: Preferences, bin_dir: str):
        """
        create object - starts with welcome page displayed
        :param title: Sir, Ma'am, Her Royal Highness
        :param preferences: what d'ya want, what d'ya really really want?
        :param bin_dir: the directory that the logo for this app is located
        """
        self.preferences: Preferences = preferences
        self.previous_file_button: Optional[Button] = None
        self._schedule_filename = ""

        super().__init__(title, preferences)
        MainPageBaseTk.bin_dir = bin_dir
        self._fall_previous_file: StringVar = StringVar(value="None")  # bound to previous_file_button
        self._winter_previous_file: StringVar = StringVar(value="None")  # bound to previous_file_button


    # ========================================================================
    # override exit event
    # ========================================================================
    def _exit_schedule(self, *_):
        self.exit_schedule()

    def exit_schedule(self):
        MAIN_PAGE_EVENT_HANDLERS["exit"]()
        super()._exit_schedule()

    def create_welcome_page(self, preferences, semesters_, open_schedules_callback, select_schedule_callback):
        """Creates the very first page that is shown to the user."""
        option_frame = super().create_welcome_page_base()

        # divide frame into two, so that we have fall and winter choices
        right_frame = Frame
#         global semesters, open_button
#         semesters = semesters_
#
#         logo_file = FindImages.get_allocation_logo()
#         option_frame = super().create_welcome_page_base(logo_file)
#
#         button_width = 100  # double Perl version
#
#         disabled_colour = Colour.string(self.colours['DataBackground'])
#         if Colour.is_light(disabled_colour):
#             disabled_colour = Colour.darken(disabled_colour, 20)
#         else:
#             Colour.lighten(disabled_colour, 20)
#
#         # --------------------------------------------------------------
#         # selected files
#         # --------------------------------------------------------------
#         Label(option_frame, text="Selected Schedules", font=self.fonts['bigbold'], bg=self.colours['DataBackground'])\
#             .pack(side='top', fill='x', expand=0)
#
#         for semester in semesters:
#             if semester not in short_scheds:
#                 short_scheds[semester] = StringVar()
#
#             Label(option_frame, textvariable=short_scheds[semester], bg=self.colours['DataBackground'])\
#                 .pack(side='top', fill='x', expand=0)
#
#         Label(option_frame, text='\n', font=self.fonts['bigbold'], bg=self.colours['DataBackground'])\
#             .pack(side='top', fill='x', expand=0)
#
#         # --------------------------------------------------------------
#         # choose schedules
#         # --------------------------------------------------------------
#         (choose_frame := Frame(option_frame)).pack(side='top', fill='x', expand=0)
#
#         for i, semester in enumerate(semesters):
#             Label(choose_frame, text=semester.capitalize() + ":",
#                   bg=self.colours['DataBackground'], font=self.fonts['bold'])\
#                 .grid(row=i, column=0, sticky='nsew', columnspan=2)
#
#             def _open_button(_semester):
#                 sched = select_schedule_callback(_semester)
#                 if sched:
#                     _set_file(_semester, sched.number, sched.descr)
#
#             Button(choose_frame, text='Open Schedule', font=self.fonts['normal'], borderwidth=0, height=3,
#                    bg=self.colours['DataBackground'], command=partial(_open_button, semester))\
#                 .grid(row=i, column=2, columnspan=2, sticky='nsew')
#
#         # --------------------------------------------------------
#         # gui layout commands
#         # --------------------------------------------------------
#         columns, rows = choose_frame.grid_size()
#         for i in range(columns):
#             choose_frame.grid_columnconfigure(i, weight=1)
#         choose_frame.grid_rowconfigure(rows - 1, weight=1)
#
#         Frame(option_frame, bg=self.colours['DataBackground']).pack(expand=0, fill='x')
#
#         # --------------------------------------------------------------
#         # make button for opening selected schedules
#         # --------------------------------------------------------------
#         text = 'Open Selected Schedules'
#         open_button = Button(option_frame,
#                              text=text,
#                              font=self.fonts['big'],
#                              borderwidth=0,
#                              bg=self.colours['DataBackground'],
#                              command=open_schedules_callback,
#                              width=button_width,
#                              height=3,
#                              disabledforeground=disabled_colour)
#         open_button.pack(side='top', fill='x', expand=0)
#
#         # --------------------------------------------------------------
#         # set_default_fonts_and_colours selected schedules to those in the preference file
#         # --------------------------------------------------------------
#         for semester in semesters:
#             _set_file(semester, preferences.get_by_id(f'current_{semester}_id'), preferences.get_by_id(f'current_{semester}_name'))
#
#
# def _set_file(semester, schedule_id, schedule_name):
#     if schedule_id is None or schedule_name is None:
#         _all_files_chosen()
#         return
#     if semester not in short_scheds:
#         short_scheds[semester] = StringVar()
#
#     schedules[semester] = schedule_id
#     # limit to the last 30 or fewer characters
#     display = schedule_name[-short_sched_name:len(schedule_name)]
#     if len(schedule_name) > short_sched_name:
#         display = f"(...) {display}"
#     short_scheds[semester].set(display)
#
#     _all_files_chosen()
#
#
# def _all_files_chosen():
#     enable_flag = "normal"
#     for semester in semesters:
#         if semester not in schedules:
#             enable_flag = 'disabled'
#     open_button.configure(state=enable_flag)
