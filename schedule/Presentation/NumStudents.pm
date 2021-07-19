#!/usr/bin/perl
use strict;
use warnings;

# TODO: Change the status bar to be able to include two files
# TODO: Fall/Winter sub-Notebooks

package NumStudents;
use FindBin;
use lib "$FindBin::Bin/..";
use GUI::NumStudentsTk;

=head1 NAME

NumStudents - provides methods/objects for entering number of students per section 

=head1 VERSION

Version 1.00

=head1 SYNOPSIS


=head1 DESCRIPTION

Dialog for entering student numbers foreach section

=head1 METHODS

=cut

# =================================================================
# Class Variables
# =================================================================
our $Dirty_ptr;
our %Schedules;
my $Gui;

# =================================================================
# new
# =================================================================
sub new {
    my $class        = shift;
    my $self         = bless {};
    my $frame        = shift;
    my $schedule_ref = shift;
    $Dirty_ptr = shift;
    %Schedules = (%$schedule_ref);

    $self->{-frame} = $frame;
    $self->refresh($schedule_ref);
    return $self;
}

sub refresh {
    my $self         = shift;
    my $schedule_ref = shift;
    
    %Schedules = (%$schedule_ref);
    my @semesters = ( sort keys %Schedules );

    $Gui = NumStudentsTk->new( $self->{-frame}, \@semesters );
    my %sections = ();

    my @student_info;

    foreach my $semester ( @semesters) {
        my $schedule = $Schedules{$semester};
        
        my $info_by_semester = {-semester=>$semester,-courses=>{}};
        push @student_info,$info_by_semester;

        my @courses =
          grep { $_->needs_allocation } $schedule->all_courses();

        my $row = 0;
        foreach my $course (@courses) {

            $info_by_semester->{-courses}
              ->{ $course->short_description } = {};
            
            foreach my $section ( sort { $a->number cmp $b->number }
                $course->sections )
            {
                my $student_number = $section->num_students;
                $info_by_semester->{-courses}
                  ->{ $course->short_description }
                  ->{ $section->number } = {
                    -student_number => \$student_number,
                    -validate_sub   => [ \&validate, $section ]
                  };
            }
        }
    }
    $Gui->refresh(\@student_info);
}

# =================================================================
# validate that number be entered in a entry box is a real number
# (positive real number)
# =================================================================
sub validate {
    no warnings;
    my $section = shift;
    my $n       = shift;
    $n = 0 unless $n;
    if ( $n =~ /^(\s*\d*\s*)$/ ) {
        $section->num_students($n);
        $$Dirty_ptr = 1;
        return 1;
    }
    return 0;
}

1;

