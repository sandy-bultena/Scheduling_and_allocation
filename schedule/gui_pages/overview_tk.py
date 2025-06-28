from tkinter import *
from tkinter import ttk
from ..Tk.Scrolled import Scrolled


class OverviewTk:
    """ write a text overview of schedule, 2 modes.. teacher/course"""

    def __init__(self, parent: Frame):
        """
        create the notebook pages for the overview
        :param parent: parent frame
        """

        # --------------------------------------------------------------------
        # create the gui widgets
        # --------------------------------------------------------------------
        overview_notebook = ttk.Notebook(parent)
        overview_notebook.pack(expand=True, fill=BOTH)

        course_overview_frame = Frame(overview_notebook)
        overview_notebook.add(course_overview_frame, text="by Course")

        teacher_overview_frame = Frame(overview_notebook)
        overview_notebook.add(teacher_overview_frame, text="by Teacher")

        s: Scrolled = Scrolled(
            course_overview_frame,
            'Text',
            height=20,
            width=50,
            scrollbars='se',
            wrap=NONE
        )
        s.pack(expand=True, fill=BOTH)
        self.overview_course_textbox = s.widget

        s: Scrolled = Scrolled(
            teacher_overview_frame,
            'Text',
            height=20,
            width=50,
            scrollbars='se',
            wrap=NONE,
        )
        s.pack(expand=True, fill=BOTH)
        self.overview_teacher_textbox = s.widget

    def refresh(self, course_text: tuple[str, ...], teacher_text: tuple[str, ...]):
        """
        Writes the text overview of the schedule to the appropriate GUI_Pages object.
        :param course_text: Text describing all the courses.
        :param teacher_text: Text describing all the teacher_ids' workloads.
        """

        # --------------------------------------------------------------------
        # write info into appropriate text boxes
        # --------------------------------------------------------------------
        self.overview_teacher_textbox.config(state=NORMAL)
        self.overview_course_textbox.config(state=NORMAL)
        self.overview_teacher_textbox.delete("1.0", "end")
        for txt in teacher_text:
            self.overview_teacher_textbox.insert('end', txt + "\n")

        self.overview_course_textbox.delete("1.0", "end")
        for txt in course_text:
            self.overview_course_textbox.insert('end', txt + "\n")

        # make text boxes read-only
        self.overview_teacher_textbox.config(state=DISABLED)
        self.overview_course_textbox.config(state=DISABLED)
