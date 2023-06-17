# IN PROGRESS
import os.path
from functools import partial
from tkinter.ttk import Notebook
from typing import Callable

from Pmw.Pmw_2_1_1.lib.PmwScrolledFrame import ScrolledFrame

from .MainPageBaseTk import MainPageBaseTk
from ..Tk import FindImages
from tkinter import *

from ..Tk.scrolled import Scrolled
from ..UsefulClasses.AllScheduables import AllScheduables

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

    frame: Frame = None

    def draw_view_choices(self, default_tab: str, all_scheduables: AllScheduables,
                          btn_callback: Callable = lambda: None):
        """The ViewsManager can create schedule views for all teacher_ids/lab_ids etc.

        The allowable views depend on the schedules, so this function needs to be called whenever
        the schedule changes.

        Draws the buttons to access any of the available views.

        Parameters:
            default_tab: Name of notebook tab to draw on.
            all_scheduables: A list of schedulable objects (teacher_ids/lab_ids/etc.)
            btn_callback: A callback function called whenever the ViewsManager is asked to create a
            view."""
        f = self.pages[default_tab.lower()]

        views_manager.gui.reset_button_refs()

        # global frame
        if SchedulerTk.frame:
            SchedulerTk.frame.destroy()

        SchedulerTk.frame = Frame(f)
        SchedulerTk.frame.pack(expand=1, fill=BOTH)

        # TODO: View choice frames have positioning issues due to Scrolled's use of pack. Buttons are not centered.
        for type in all_scheduables.valid_types():
            view_choices_frame = LabelFrame(
                SchedulerTk.frame,
                text=all_scheduables.by_type(type).title)
            view_choices_frame.pack(expand=1, fill=BOTH)

            view_choices_scrolled_frame = Scrolled(view_choices_frame, 'Frame', scrollbars="osoe")
            # view_choices_scrolled_frame = ScrolledFrame(view_choices_frame)
            view_choices_scrolled_frame.pack(expand=1, fill=BOTH)

            # NOTE: Program was crashing inside this function call because
            # view_choices_scrolled_frame already has children managed by pack, while the
            # function is trying to add buttons managed by grid to view_choices_scrolled_frame.
            # Tcl doesn't like it when children of the same parent use different geometry managers.
            views_manager.gui.create_buttons_for_frame(
                view_choices_scrolled_frame,
                all_scheduables.by_type(type),
                btn_callback
            )

    tbox3: Scrolled = None
    tbox = None
    tbox2: Scrolled = None

    overview_notebook = None
    overview_pages: dict[str, Frame] = {}

    def draw_overview(self, default_page: str, course_text, teacher_text):
        """Writes the text overview of the schedule to the appropriate GUI object.

        Parameters:
            default_page: name of notebook tab to draw on.
            course_text: Text describing all the courses.
            teacher_text: Text describing all the teacher_ids' workloads."""
        f = self.pages[default_page.lower()]

        if not SchedulerTk.overview_notebook:
            SchedulerTk.overview_notebook = Notebook(f)
            SchedulerTk.overview_notebook.pack(expand=True, fill=BOTH)

            # NOTE: tkinter notebooks behave somewhat differently from PerlTk ones. They don't
            # create child Frames when the add() method is called; a child Frame must be created
            # first, and THEN it can be added to the Notebook using .add().
            course2 = Frame(SchedulerTk.overview_notebook)

            # Not entirely sure if this will work, just assigning the Frame itself to the
            # dictionary. In the original Perl,
            SchedulerTk.overview_notebook.add(course2, text="by Course")
            SchedulerTk.overview_pages['course2'] = course2

            teacher2 = Frame(SchedulerTk.overview_notebook)
            SchedulerTk.overview_notebook.add(teacher2, text="by Teacher")
            SchedulerTk.overview_pages['teacher2'] = teacher2
        SchedulerTk._actions_course(course_text)
        SchedulerTk._actions_teacher(teacher_text)

    # Draw Course Overview
    @staticmethod
    def _actions_course(text: str):
        f = SchedulerTk.overview_pages['course2']

        if not SchedulerTk.tbox2:
            SchedulerTk.tbox2 = Scrolled(
                f,
                'Text',
                height=20,
                width=50,
                scrollbars='se',
                state=DISABLED,
                wrap=NONE
            )
            SchedulerTk.tbox2.pack(expand=True, fill=BOTH)

        # Note: Not sure if this will work in tkinter.
        SchedulerTk.tbox2.widget.delete("1.0", "end")

        for txt in text:
            SchedulerTk.tbox2.widget.insert('end', txt)

    @staticmethod
    def _actions_teacher(text: str):
        f = SchedulerTk.overview_pages['teacher2']

        if not SchedulerTk.tbox3:
            SchedulerTk.tbox3 = Scrolled(
                f,
                "Text",
                height=20,
                width=50,
                scrollbars='se',
                wrap=NONE,
                state=DISABLED
            )
            SchedulerTk.tbox3.pack(expand=True, fill=BOTH)
        SchedulerTk.tbox3.widget.delete("1.0", "end")

        for txt in text:
            SchedulerTk.tbox3.widget.insert('end', txt)

    def choose_existing_file(self, curr_dir, file_types):
        pass

    def choose_file(self, curr_dir, file_types):
        pass
