import os.path
from functools import partial
from typing import Callable

from .MainPageBaseTk import MainPageBaseTk
from ..Tk import FindImages
from tkinter import *

# ============================================================================
# Package variables
# ============================================================================
global views_manager
global mw


class SchedulerTk(MainPageBaseTk):
    """
    GUI Code for the main application window. Inherits from MainPageBaseTk.
    """
    CURRENT_FILE = 'current_file'

    # region ACCESS TO EXTERNAL DATA
    def set_views_manager(self, my_views_manager):
        """Sometimes this Tk class needs access to the views_manager.

        This method makes the views_manager available to this code."""
        global views_manager
        views_manager = my_views_manager

    def create_front_page(self, preferences: dict, open_schedule_callback: Callable,
                          new_schedule_callback: Callable):
        """Creates the very first page that is shown to the user."""
        logo_file = FindImages.get_logo()
        option_frame = super().create_front_page(logo_file)

        button_width = 50
        short_file_name = 25

        # --------------------------------------------------------------
        # open previous schedule file option
        # --------------------------------------------------------------
        if SchedulerTk.CURRENT_FILE in preferences.keys() \
                and os.path.isfile(preferences[SchedulerTk.CURRENT_FILE]):
            # make sure the name displayed is not too long
            file = preferences[SchedulerTk.CURRENT_FILE]
            basename = os.path.basename(file)
            if len(basename) > short_file_name:
                basename = basename[0:short_file_name] + "(...) "

            Button(
                option_frame,
                text=f"Open {basename}",
                justify=RIGHT,
                font=self.fonts['big'],
                borderwidth=0,
                bg=self.colours['DataBackground'],
                command=partial(
                    open_schedule_callback, preferences[SchedulerTk.CURRENT_FILE]
                ),
                width=button_width,
                height=3
            ).pack(side=TOP, fill=Y, expand=0)

        # --------------------------------------------------------------
        # create new schedule file option
        # --------------------------------------------------------------
        Button(
            option_frame,
            text="Create NEW Schedule File",
            font=self.fonts['big'],
            borderwidth=0,
            bg=self.colours['DataBackground'],
            command=new_schedule_callback,
            width=button_width,
            height=3
        ).pack(side=TOP, fill=Y, expand=0)

        # --------------------------------------------------------------
        # open schedule file option
        # --------------------------------------------------------------
        Button(
            option_frame,
            text="Browse for Schedule File",
            font=self.fonts['big'],
            borderwidth=0,
            bg=self.colours['DataBackground'],
            command=open_schedule_callback,
            width=button_width,
            height=3
        ).pack(side=TOP, fill=Y, expand=0)
        Frame(
            option_frame, bg=self.colours['DataBackground']
        ).pack(expand=1, fill=BOTH)

    def update_for_new_schedule_and_show_page(self, default_page_id):
        global views_manager
        # TODO: Determine if this is ViewsManager, or ViewsManagerTk.
        views_manager.destroy_all()
        super().update_for_new_schedule_and_show_page(default_page_id)
    # endregion
    def choose_existing_file(self, curr_dir, file_types):
        pass

    def choose_file(self, curr_dir, file_types):
        pass

