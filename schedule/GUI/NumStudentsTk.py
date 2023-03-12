import sys
from os import path
sys.path.append(path.dirname(path.dirname(__file__)))

from tkinter import *
import PerlLib.Colour as Colour


class NumStudentsTk:
    def __init__(self, frame, semesters: [str]):
        self.panes = dict()
        self.frame = frame

        # make as many panes as there are semesters
        for semester in semesters:
            panes[semester] =

    """

sub new {
#ADDING A SCROLLBAR
myscrollbar=Scrollbar(frame,orient="vertical")
myscrollbar.pack(side="right",fill="y")
#Add Entry Widgets
Label(frame, text= "Username").pack()
username= Entry(frame, width= 20)
username.pack()


    # make as many panes as there are semesters
    foreach my $semester ( sort @$semesters ) {
        if ( $panes{$semester} ) {
            $panes{$semester}->destroy;
        }

        $panes{$semester} = $frame->Scrolled(
            "Frame",
            -scrollbars => 'oe',
            -border     => 5,
            -relief     => 'flat',
        )->grid( -column => $col, -row => 0, -sticky => 'nsew' );
        $frame->gridColumnconfigure( $col, -weight => 1 );
        $col++;
    }
    $frame->gridRowconfigure( 0, -weight => 1 );
    $self->panes( \%panes );
    return $self;
}

sub panes {
    my $self = shift;
    $self->{-panes} = {} unless $self->{-panes};
    $self->{-panes} = shift if @_;
    return $self->{-panes};
}

sub refresh {
    my $self         = shift;
    my $student_info = shift;

    foreach my $info_by_semester ( @$student_info ) {
        my $pane     = $self->panes->{$info_by_semester->{-semester}};
        next unless $pane;

        my $row = 0;
        foreach my $course_descr (sort keys %{$info_by_semester->{-courses}}) {
            my $info_by_course = $info_by_semester->{-courses}->{$course_descr};
            $pane->Label(
                -text   => $course_descr,
                -anchor => 'w',
                -width  => 40,
            )->grid( '-', "-", '-', -sticky => 'nsew' );
            $row++;

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
