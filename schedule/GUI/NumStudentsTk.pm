#!/usr/bin/perl
use strict;
use warnings;

package NumStudentsTk;

use FindBin;
use Carp;
use Tk;
use lib "$FindBin::Bin/..";
use PerlLib::Colours;
use Tk::Dialog;
use Tk::Menu;
use Tk::LabEntry;
use Tk::Pane;

sub new {
    my $class  = shift;
    my $frame = shift;
    my $semesters = shift;
    
    my $self = bless {}, $class;
    my %panes = %{ $self->panes };
    my $col   = 0;

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
