from __future__ import annotations
import sys
from dataclasses import dataclass, field
from os import path

sys.path.append(path.dirname(path.dirname(__file__)))
from Tk.scrolled import Scrolled
from tkinter import *


"""
Display and update student numbers for a set of semesters/courses/sectons

Inputs: 
    frame  -> the frame where you want this form to be inserted
    data: NumStudentsData -> the data to be displayed (see example for how to construct the data)

Notes:
    will insert scrollbars
     
def example():
    # setting up the data
    data = NumStudentsData()
    for semester_name in ("fall", "winter"):
        semester = NumStudentsDataSemester(name=semester_name)
        data.semesters.append(semester)
        for course_name in ("abc", "def", "ghi", "jkl"):
            course = NumStudentsDataCourse(name=course_name)
            semester.courses.append(course)
            for section_name in ("1", "2"):
                section = NumStudentsDataSection(name=section_name, num_students=10)
                section.data_validate = validate_factory(data, section)
                course.sections.append(section)

    mw = Tk()
    frame = Frame(mw, bg='blue', border=4, relief=RIDGE)
    frame.pack(expand=1, fill=BOTH)
    NumStudentsTk(frame, data)
    mw.mainloop()


def validate_factory(data, section):
    def validate(entry_input: str):
        if entry_input.isdigit():
            section.num_students = int(entry_input)
            return True
        elif entry_input == "":
            section.num_students = 0
            return True
        else:
            return False

    return validate

"""


# #################################################################################################
# Class to allow users to update student numbers for each section in each course for each semester
# #################################################################################################
class NumStudentsTk:
    """Displays and allows updates for all course/sections/student_numbers for each semester"""

    # ============================================================================================
    # constructor
    # ============================================================================================
    def __init__(self, frame, data: NumStudentsData = None):
        """creates the Panes for each semester"""

        panes = dict()
        self.root = frame

        # ----------------------------------------------------------------------------------------
        # make as many panes as there are semesters
        # ----------------------------------------------------------------------------------------
        for col, semester in enumerate(data.semesters):
            # set up the weight for each column
            frame.columnconfigure(col, weight=1);

            f = Scrolled(
                self.root,
                "Frame",
                scrollbars=E,
                border=5,
                relief=FLAT,
            )
            f.grid(column=col, row=0, sticky="nsew")
            panes[semester.name] = f

        frame.rowconfigure(0, weight=1);
        self.panes = panes

        # ----------------------------------------------------------------------------------------
        # put data into widget
        # ----------------------------------------------------------------------------------------
        self.refresh(data)

    # ============================================================================================
    # refresh - update the info (assumes same number of semesters!
    # ============================================================================================
    def refresh(self, data: NumStudentsData = None):
        """ Refreshes all the information"""

        if data is None: return

        # ----------------------------------------------------------------------------------------
        # loop over semesters
        # ----------------------------------------------------------------------------------------
        for col, semester in enumerate(data.semesters):
            pane = self.panes[semester.name].widget
            if pane is None: break

            # layout
            pane.columnconfigure(1, weight=2);
            pane.columnconfigure(0, weight=1);

            # ----------------------------------------------------------------------------------------
            # remove all widgets in the semester pane
            # ----------------------------------------------------------------------------------------
            for w in pane.winfo_children():
                w.destroy()

            # ----------------------------------------------------------------------------------------
            # add titles to the panes
            # ----------------------------------------------------------------------------------------
            Label(pane,
                  text=semester.name,
                  anchor='center',
                  ).grid(column=0, row=0, columnspan=2, sticky='nsew')

            # ----------------------------------------------------------------------------------------
            # loop over courses
            # ----------------------------------------------------------------------------------------
            row = 1
            for course in sorted(semester.courses):
                Label(pane,
                      text=course.name,
                      anchor=W,
                      width=40
                      ).grid(column=0, row=row, columnspan=2, sticky='nsew')
                row = row + 1

                # ----------------------------------------------------------------------------------------
                # for each section in a course
                # ----------------------------------------------------------------------------------------
                for section in sorted(course.sections):
                    Label(pane,
                          width=4,
                          text=section.name,
                          anchor=E,
                          ).grid(column=0, row=row, sticky="nsew")

                    reg = self.root.register(section.data_validate)
                    tv = StringVar(value=section.num_students)
                    entry = Entry(pane,
                                  justify='right',
                                  validate='key',
                                  textvariable=tv,
                                  validatecommand=(reg, '%P'),
                                  invalidcommand=self.root.register(pane.bell),
                                  width=8
                                  )
                    entry.grid(column=1, row=row, sticky='nw')

                    # ----------------------------------------------------------------------------------------
                    # bind <Return> to go to the next entry widget
                    # bind <FocusIn> to automatically scroll so you can see the widget
                    # ----------------------------------------------------------------------------------------
                    entry.bind("<Return>", lambda e: e.widget.tk_focusNext().focus())
                    entry.bind("<FocusIn>", lambda e, p=self.panes[semester.name]: p.see_widget(e.widget))
                    row = row + 1


# ============================================================================================================
# Data classes to define the structure of data expected by this form
# ============================================================================================================

@dataclass
class NumStudentsDataSection:
    name: str
    num_students: int
    data_validate: callable # a function that validates the input into an entry widget

    def __lt__(self, obj):
        return self.name < obj.name


@dataclass
class NumStudentsDataCourse:
    name: str
    sections: list[NumStudentsDataSection] = field(default_factory=list)

    def __lt__(self, obj):
        return self.name < obj.name


@dataclass
class NumStudentsDataSemester:
    name: str
    courses: list[NumStudentsDataCourse] = field(default_factory=list)


@dataclass
class NumStudentsData:
    semesters: list[NumStudentsDataSemester] = field(default_factory=list)


if __name__ == "__main__":
    example()
