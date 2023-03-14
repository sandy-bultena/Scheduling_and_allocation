from __future__ import annotations
import sys
from dataclasses import dataclass, field
from os import path

sys.path.append(path.dirname(path.dirname(__file__)))
from Tk.scrolled import Scrolled

from tkinter import *
import PerlLib.Colour as Colour


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

                # function to validate and save the data when changed in the gui
                def validate(entry_input: str):
                    if entry_input.isdigit():
                        section.num_students = int(entry_input)
                        print(data)
                        return True
                    elif entry_input == "":
                        section.num_students = 0
                        print(data)
                        return True
                    else:
                        return False

                section.data_validate = validate
                course.sections.append(section)

    print_data(data)

    mw = Tk()
    frame = Frame(mw)
    frame.pack()
    gui=NumStudentsTk(frame, (sem.name for sem in data.semesters))
    gui.refresh(data)
    mw.mainloop()


def print_data(data):
    for semester in data.semesters:
        print(semester.name)
        for course in semester.courses:
            print(semester.name, course.name)
            for section in course.sections:
                print(semester.name, course.name,section.name, section.num_students)


class NumStudentsTk:
    """Displays all course/sections/student_numbers for each semester"""

    def __init__(self, frame, semesters: list[str]):
        """creates the Panes for each semester"""
        panes = dict()
        self.root = frame

        # make as many panes as there are semesters
        for col, semester in enumerate(semesters):
            f = Scrolled(
                self.root,
                "Frame",
                scrollbars=E,
                border=5,
                relief=FLAT,
            )
            f.grid(column=col, row=0, sticky="nsew")
            f.columnconfigure(col, weight=1);

            panes[semester] = f.widget
    #        Label(f,text=semester).pack()

        frame.rowconfigure(0, weight=1);
        self.panes = panes

    def refresh(self, data: NumStudentsData = None):
        """ Refreshes all the information"""
        if data is None: return

        # loop over semesters
        for col, semester in enumerate(data.semesters):
            pane = self.panes[semester.name]
            if pane is None: continue

            # loop over courses
            row = 0
            for course in sorted(semester.courses):
                Label(pane,
                      text=course.name,
                      anchor=W,
                      width=40
                      ).grid(column=col,row=row, columnspan=2, sticky='nsew')
                row = row + 1

                # for each section in a course
                for section in sorted(course.sections):
                    Label(pane,
                          width=4,
                          text=section.name,
                          anchor=E
                          ).grid(column=0, row=row, sticky="nsew")

                    reg = self.root.register(section.data_validate)
                    entry = Entry(pane,
                                  text=str(section.num_students),
                                  justify='right',
                                  validate='key',
                                  validatecommand=(reg, '%P'),
                                  invalidcommand=self.root.register(pane.bell),
                                  width=8
                                  )
                    entry.grid(column=1, row=row, sticky='nw')
                    # entry.bind("<Return>", entry.focusNext)
                    # entry.bind("FocisIn>", pane.see(entry))

                    row = row + 1


@dataclass
class NumStudentsDataSection:
    name: str
    num_students: int
    data_validate: callable = None

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
