# COMPLETED
import os.path
import tkinter

from typing import Callable, Optional, Literal, get_args

from ..Utilities.Preferences import Preferences

from .main_pages_tk import MainPageBaseTk
import tkinter as tk
from tkinter import ttk
from schedule.model.enums import SemesterType

BUTTON_WIDTH = 25
MAX_LEN_OF_DISPLAYED_FILENAME = 25

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
    "go",
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
    def __init__(self, title: str, preferences: Preferences = None, bin_dir: str = "."):
        """
        create object - starts with welcome page displayed
        :param title: Sir, Ma'am, Her Royal Highness
        :param preferences: what d'ya want, what d'ya really really want?
        :param bin_dir: the directory that the logo for this app is located
        """
        print("inside AllocationManagerTk")
        self.preferences: Preferences = preferences
        self.previous_file_buttons: dict[SemesterType, Optional[tk.Button]] = {
            SemesterType.fall: None,
            SemesterType.winter: None,
        }

        super().__init__(title, preferences)
        MainPageBaseTk.bin_dir = bin_dir

        self._previous_files: dict[SemesterType, tk.StringVar] = {
            SemesterType.fall: tk.StringVar(value="None"),
            SemesterType.winter: tk.StringVar(value="None")
        }
        self._schedule_filenames: dict[SemesterType, Optional[tk.StringVar]] = {
            SemesterType.fall: tk.StringVar(value='Create New'),
            SemesterType.winter: tk.StringVar(value="Create New"),
        }

    @property
    def previous_file_fall(self):
        return self._previous_files[SemesterType.fall].get()

    @previous_file_fall.setter
    def previous_file_fall(self, value):
        self._configure_previous_file(SemesterType.fall, value)

    @property
    def previous_file_winter(self):
        return self._previous_files[SemesterType.winter].get()

    @previous_file_winter.setter
    def previous_file_winter(self, value):
        self._configure_previous_file(SemesterType.winter, value)

    @property
    def schedule_filename_fall(self):
        return self._schedule_filenames[SemesterType.fall].get()

    @schedule_filename_fall.setter
    def schedule_filename_fall(self, value: str):
        if value is not None and value != "":
            value = os.path.abspath(value)
            if len(value) > MAX_LEN_OF_DISPLAYED_FILENAME:
                value = "... " + value[len(value) - MAX_LEN_OF_DISPLAYED_FILENAME:]
            self._schedule_filenames[SemesterType.fall].set(value)
        else:
            self._schedule_filenames[SemesterType.fall].set(value="Create New")


    @property
    def schedule_filename_winter(self):
        return self._schedule_filenames[SemesterType.winter].get()

    @schedule_filename_winter.setter
    def schedule_filename_winter(self, value: str):
        if value is not None and value != "":
            value = os.path.abspath(value)
            if len(value) > MAX_LEN_OF_DISPLAYED_FILENAME:
                value = "... " + value[len(value) - MAX_LEN_OF_DISPLAYED_FILENAME:]
            self._schedule_filenames[SemesterType.winter].set(value)
        else:
            self._schedule_filenames[SemesterType.winter].set(value="Create New")

    def _configure_previous_file(self, semester, value):
        if value is not None and value != "":
            basename = os.path.basename(str(value))
            if len(basename) > MAX_LEN_OF_DISPLAYED_FILENAME:
                basename = "..." + basename[len(basename) - MAX_LEN_OF_DISPLAYED_FILENAME:]
            self._previous_files[semester].set(basename)
        else:
            self._previous_files[semester].set(value="None")

        try:
            if self._previous_files[semester] != "None":
                self.previous_file_buttons[semester].configure(state='normal')
            else:
                self.previous_file_buttons[semester].configure(state='disabled')
        except tk.TclError:
            pass

    # ========================================================================
    # override exit event
    # ========================================================================
    def _exit_schedule(self, *_):
        self.exit_schedule()

    def exit_schedule(self):
        MAIN_PAGE_EVENT_HANDLERS["exit"]()
        super()._exit_schedule()

    def create_welcome_page(self):
        """Creates the very first page that is shown to the user."""
        option_frame = super().create_welcome_page_base()

        # divide frame into two, so that we have fall and winter choices
        option_frames: dict[SemesterType, tk.LabelFrame] = {
            SemesterType.fall: tk.LabelFrame(option_frame,text=SemesterType.fall.name,font=self.fonts.big),
            SemesterType.winter: tk.LabelFrame(option_frame,text=SemesterType.winter.name, font=self.fonts.big)
        }
        option_frames[SemesterType.fall].grid(row=0, padx=10,pady=10)
        option_frames[SemesterType.winter].grid(row=1, padx=10, pady=10)

        for semester in SemesterType.fall, SemesterType.winter:
            # --------------------------------------------------------------
            # open previous schedule file buttons
            # -------------------------------------------------------------
            self.previous_file_buttons[semester]= tk.Button(
                option_frames[semester],
                justify="right",
                font=self.fonts.big,
                borderwidth=2,
                background=self.colours.ButtonBackground,
                foreground=self.colours.ButtonForeground,
                command=MAIN_PAGE_EVENT_HANDLERS[semester.name+"_file_open_previous"],
                width=BUTTON_WIDTH,
                height=2,
                textvariable=self._previous_files[semester],
                state='disabled'
            )
            self.previous_file_buttons[semester].pack(side="top", fill="y", expand=0, padx=5, pady=5)

            # --------------------------------------------------------------
            # open schedule file option
            # --------------------------------------------------------------
            tk.Button(
                option_frames[semester],
                text=f"Browse",
                font=self.fonts.big,
                borderwidth=2,
                background=self.colours.ButtonBackground,
                foreground=self.colours.ButtonForeground,
                command=MAIN_PAGE_EVENT_HANDLERS[semester.name+"_file_open"],
                width=BUTTON_WIDTH,
                height=2
            ).pack(side="top", fill="y", expand=0, padx=5, pady=5)

            # --------------------------------------------------------------
            # selected file
            # --------------------------------------------------------------
            frame = tk.Frame(option_frames[semester])
            frame.pack(side="top",fill="y", expand=0, padx=5, pady=5)
            label = tk.Label(frame,text="selected file")
            entry = tk.Entry(frame, textvariable=self._schedule_filenames[semester],
                             state="disabled", )
            label.pack(side="top")
            entry.pack(side="top",expand=1, fill="y")

        # --------------------------------------------------------------
        # go
        # --------------------------------------------------------------
        tk.Button(option_frame, text="Go", font=self.fonts.big, padx=20,pady=5,
                  command=MAIN_PAGE_EVENT_HANDLERS['go']).grid(
            row=2, sticky='ew'
        )




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
