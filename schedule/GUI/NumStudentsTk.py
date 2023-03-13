import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__)))
from Tk.scrolled import Scrolled

from tkinter import *
import PerlLib.Colour as Colour




class NumStudentsTk:
    def __init__(self, frame, semesters: [str]):
        """displays the number of students per course, per valid semester"""
        panes = dict()

        # make as many panes as there are semesters
        for col, semester in enumerate(semesters):
            panes[semester.name] = Scrolled(
                self.frame,
                scrollbars=E,
                border=5,
                relief=FLAT,
            )
            panes[semester.name].grid(colum=col, row=0, sticky="nsew")
            frame.gridColumnconfigure(col, weight=1);

        frame.gridRowconfigure(0, weight=1);
        self.panes = panes

    # @student_info:
    #  [
    #   { semester=semester_name,
    #     course =
    #     { short_description=
    #       { section_number =
    #         { student_number = number
    #           validate = function
    #         }
    #        }
    #      }
    #     }
    #    }
    #  ]
    def refresh(self, student_info=None):
        if student_info is None: return

        # loop over semesters
        for info_by_semester in student_info:
            pane = self.panes[info_by_semester["semester"]]
            if pane is None: continue

            # loop over courses
            for row, course_descr in enumerate(sorted(info_by_semester["courses"],key=info_by_semester["courses"].key)):
                Label(pane,
                      text=course_descr,
                      anchor=W,
                      width=40
                      ).grid("-","-","-",sticky='nsew')

                # for each section in a course


    """
sub refresh {

            foreach my $section_descr ( sort keys %$info_by_course )
            {
                my $info_by_section = $info_by_course->{$section_descr};
                $pane->Label(
                    -width  => 4,
                    -text   => $section_descr,
                    -anchor => 'e',
                )->grid( -column => 0, -row => $row, -sticky => 'nsew' );

                my $e = $pane->Entry(
                    -textvariable => $info_by_section->{-student_number},
                    -justify  => 'right',
                    -validate => 'key',
                    -validatecommand => $info_by_section->{-validate_sub},
                    -invalidcommand => sub { $pane->bell },
                    -width          => 8,
                  )->grid(
                    -column => 1,
                    -row    => $row,
                    -sticky => 'nw'
                  );
                $e->bind( "<Return>",  sub { $e->focusNext; } );
                $e->bind( "<FocusIn>", sub { $pane->see($e) } );

                $row++;
            }

        }

    }
}


1;

    """
