
import os.path
from functools import partial

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
    "file_open_from_main_page",
    "file_open_previous_from_main_page",
    "go",
    "exit",
]

MAIN_PAGE_EVENT_HANDLERS: dict[EVENT_HANDLER_NAMES, Callable[[SemesterType], None]] = {}

for event_name in get_args(EVENT_HANDLER_NAMES):
    MAIN_PAGE_EVENT_HANDLERS[event_name] = lambda x: print(f"'selected. {event_name}")


def set_main_page_event_handler(name: EVENT_HANDLER_NAMES, handler: Callable[[SemesterType], None]):
    MAIN_PAGE_EVENT_HANDLERS[name] = handler

# ============================================================================
# class: AllocationManagerTk
# ============================================================================
class AllocationManagerTk(MainPageBaseTk):

    # ----------------------------------------------------------------------------------------------------------------
    # constructor
    # ----------------------------------------------------------------------------------------------------------------
    def __init__(self, title: str, preferences: Preferences = None, bin_dir: str = "."):
        """
        create object - starts with welcome page displayed
        :param title: Sir, Ma'am, Her Royal Highness
        :param preferences: what d'ya want, d'ya really really want?
        :param bin_dir: the directory that the logo for this app is located
        """
        self.preferences: Preferences = preferences
        self.previous_file_buttons: dict[SemesterType, Optional[tk.Button]] = {s: None for s in SemesterType}

        super().__init__(title, preferences)
        MainPageBaseTk.bin_dir = bin_dir

        self._previous_files: dict[SemesterType, tk.StringVar] = {s: tk.StringVar(value="None") for s in SemesterType}

        self._schedule_filenames: dict[SemesterType, Optional[tk.StringVar]] = {
            s: tk.StringVar(value="Create New") for s in SemesterType}

    # ----------------------------------------------------------------------------------------------------------------
    # setting the previous file
    # ----------------------------------------------------------------------------------------------------------------
    def previous_file(self, semester=SemesterType.any, value:str=None) -> str:
        """
        the previous file is saved as a Tk StringVar, and used on a button
        :param semester:
        :param value:
        :return: the current value of the Tk StringVar
        """
        if value is not None:
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
        return self._previous_files[semester].get()


    # ----------------------------------------------------------------------------------------------------------------
    # setting the schedule filename
    # ----------------------------------------------------------------------------------------------------------------
    def schedule_filename(self, semester:SemesterType = SemesterType.any, value:str =""):
        """
        the schedule file is saved as a Tk StringVar, and is trimmed down to a smaller size if necessary
        :param semester:
        :param value:
        :return: the current value of the Tk StringVar
        """
        if value is not None and value != "":
            value = os.path.abspath(value)
            if len(value) > MAX_LEN_OF_DISPLAYED_FILENAME:
                value = "... " + value[len(value) - MAX_LEN_OF_DISPLAYED_FILENAME:]
            self._schedule_filenames[semester].set(value)
        else:
            self._schedule_filenames[semester].set(value="Create New")
        return self._schedule_filenames[semester].get()

    # ----------------------------------------------------------------------------------------------------------------
    # override exit event
    # ----------------------------------------------------------------------------------------------------------------
    def _exit_schedule(self, *_):
        self.exit_schedule()

    def exit_schedule(self):
        MAIN_PAGE_EVENT_HANDLERS["exit"]()
        super()._exit_schedule()

    # ----------------------------------------------------------------------------------------------------------------
    # create welcome page
    # ----------------------------------------------------------------------------------------------------------------
    def create_welcome_page(self, valid_semesters:list[SemesterType]):
        """
        Creates the very first page that is shown to the user
        :param valid_semesters:
        """
        option_frame = super().create_welcome_page_base()

        # divide frame into semesters
        option_frames: dict[SemesterType, tk.LabelFrame] = {}
        for row,semester in enumerate(valid_semesters):
            option_frames[semester] = tk.LabelFrame(option_frame,text=semester.name,font=self.fonts.big)
            option_frames[semester].grid(row=row, padx=10,pady=10)

        for semester in valid_semesters:

            # open previous schedule file buttons
            self.previous_file_buttons[semester]= tk.Button(
                option_frames[semester],
                justify="right",
                font=self.fonts.big,
                borderwidth=2,
                background=self.colours.ButtonBackground,
                foreground=self.colours.ButtonForeground,
                command=partial(MAIN_PAGE_EVENT_HANDLERS["file_open_previous_from_main_page"],semester),
                width=BUTTON_WIDTH,
                height=2,
                textvariable=self._previous_files[semester],
                state='disabled'
            )
            self.previous_file_buttons[semester].pack(side="top", fill="y", expand=0, padx=5, pady=5)

            # open schedule file option
            tk.Button(
                option_frames[semester],
                text=f"Browse",
                font=self.fonts.big,
                borderwidth=2,
                background=self.colours.ButtonBackground,
                foreground=self.colours.ButtonForeground,
                command=partial(MAIN_PAGE_EVENT_HANDLERS["file_open_from_main_page"],semester),
                width=BUTTON_WIDTH,
                height=2
            ).pack(side="top", fill="y", expand=0, padx=5, pady=5)

            # selected file
            frame = tk.Frame(option_frames[semester])
            frame.pack(side="top",fill="y", expand=0, padx=5, pady=5)
            label = tk.Label(frame,text="selected file")
            entry = tk.Entry(frame, textvariable=self._schedule_filenames[semester],
                             state="disabled", )
            label.pack(side="top")
            entry.pack(side="top",expand=1, fill="y")

        # go
        tk.Button(option_frame, text="Go", font=self.fonts.big, padx=20,pady=5,
                  command=partial(MAIN_PAGE_EVENT_HANDLERS['go'],SemesterType.any)).grid(
            row=2, sticky='ew'
        )

