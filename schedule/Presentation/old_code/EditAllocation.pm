#!/usr/bin/perl
use strict;
use warnings;

package EditAllocation;
use FindBin;
use Carp;
use lib "$FindBin::Bin/..";
use PerlLib::Colours;
use GUI::EditAllocationTk;
use CICalculator::CICalc;

# ============================================================================
# Create and manage the workloads
#
# - can edit courses, student numbers, teachers, and allocate hours to
#   each teacher.
#
# - calculates CI automatically
#
# INPUTS:
#   frame           - a gui object that can be used as a container
#   schedule_ptr    - a hash ptr. {semester => schedule}
#   dirty_ptr       - a reference to a scalar
#                       - a flag to indicate if the data has been modified since last saved
#
# METHODS:
#   draw
#
# ============================================================================
# NOTE: this module is dependent on functions in EditCourses
# ============================================================================

# =================================================================
# Class Variables
# =================================================================
our $Dirty_ptr;
our %Schedules;

# constants;
my $ValueKey   = "-value";
my $SectionKey = "-section";
my $CourseKey  = "-course";
my $TeacherKey = "-teacher";
my $CIKey      = "-CI";
my $CITotalKey = "-CI_total";
my $ReleaseKey = "-release";

# globals
my $Gui;
my @bound_data_vars;
my @bound_remaining_hours;
my $frame;

# =================================================================
# Constructor
# =================================================================
sub new {
    my $class = shift;
    $frame = shift;
    my $schedule_ref = shift;
    $Dirty_ptr = shift;

    my $self = bless {};
    %Schedules = (%$schedule_ref);

    $self->{-frame} = $frame;

    $self->draw($schedule_ref);

    return $self;
}

# ============================================================================
# draw - setup and create the interface
# ============================================================================
sub draw {
    my $self = shift;

    my $allocation_info = [];

    # ------------------------------------------------------------------------
    # Define required information by semester
    # ------------------------------------------------------------------------
    foreach my $semester ( $self->_semesters ) {

        # clear out previous data
        $self->_reset_teacher_hours($semester);
        $self->_reset_totals($semester);
        $self->_reset_unused_hours($semester);

        # courses by semester
        my $schedule = $Schedules{$semester};
        my @courses  = $Schedules{$semester}->courses->allocation_list;
        $self->_semester_courses( $semester, \@courses );

        # teachers by semester
        my @teachers =
          sort {
                 $a->firstname cmp $b->firstname
              || $a->lastname cmp $b->lastname
          } $Schedules{$semester}->all_teachers;
        $self->_semester_teachers( $semester, \@teachers );

        # sections by course by semester
        my @sections;
        foreach my $course (@courses) {
            my @new_sections =
              sort { $a->number cmp $b->number } $course->sections;
            push @sections, @new_sections;
        }
        $self->_semester_sections( $semester, \@sections );

        my @col_numbers = map { $_->number_of_sections } @courses;

        # save info
        push @$allocation_info,
          {
            -semester        => $semester,
            -courses         => \@courses,
            -rows            => scalar(@teachers),
            -columns_numbers => \@col_numbers,
            -totals_numbers  => [3]
          };
    }

    # ------------------------------------------------------------------------
    # create the gui, or redraw if already exists
    # ------------------------------------------------------------------------
    if ($Gui) {
        $Gui->redraw($allocation_info);
    }
    else {
        $Gui = EditAllocationTk->new( $frame, $allocation_info );
    }

    # ------------------------------------------------------------------------
    # define text binding and callback routines
    # ------------------------------------------------------------------------
    foreach my $semester ( $self->_semesters ) {

        # setup event handlers
        $Gui->set_cb_data_entry( $semester,
            sub { _cb_validate_number( $self, $semester, @_ ) } );
        $Gui->set_cb_process_data_change( $semester,
            sub { _cb_process_data_entry( $self, $semester, @_ ) } );
        $Gui->set_cb_bottom_row_ok(
            $semester,
            sub { my $remaining_number = shift || 0; return !$remaining_number }
        );

        # bind variables to AllocationGrid
        $self->_define_data_binding($semester);

        # update the CI
        $self->_update_all_CI($semester);

    }

}

# ============================================================================
# define all the data and bind to Allocation Grid
# ============================================================================
sub _define_data_binding {
    my $self     = shift;
    my $semester = shift;

    # ------------------------------------------------------------------------
    # create arrays for storing the 'constant' information for the
    # AllocationGrid
    # ------------------------------------------------------------------------
    my @teachers_text =
      map { $_->firstname } @{ $self->_semester_teachers($semester) };

    my @courses_text =
      map { my $txt = $_->number; $txt =~ s/^\s*\d\d\d-//; $txt; }
      @{ $self->_semester_courses($semester) };
    my @courses_balloon =
      map { $_->name; } @{ $self->_semester_courses($semester) };

    my @sections_text =
      map { $_->number } @{ $self->_semester_sections($semester) };

    # ------------------------------------------------------------------------
    # data array and binding arrays
    # ------------------------------------------------------------------------

    # create arrays that have the data for hrs / teacher / section,
    # based on ROW/COL,
    # and create arrays for binding this information to the allocationGrid

    my $col = 0;

    # foreach course/section/teacher, holds the number of hours
    foreach my $course ( @{ $self->_semester_courses($semester) } ) {
        foreach
          my $section ( sort { $a->number cmp $b->number } $course->sections )
        {
            my $row = 0;
            foreach my $teacher ( @{ $self->_semester_teachers($semester) } ) {

                $self->_data_teacher_hours($semester)->[$row][$col] = {
                    $TeacherKey => $teacher,
                    $CourseKey  => $course,
                    $SectionKey => $section,
                    $ValueKey   => ""
                };

                $bound_data_vars[$row][$col] =
                  \$self->_data_teacher_hours($semester)
                  ->[$row][$col]{$ValueKey};

                # set the current hours based on info in the schedule
                if ( $section->has_teacher($teacher) ) {
                    $self->_data_teacher_hours($semester)
                      ->[$row][$col]{$ValueKey} =
                      $section->get_teacher_allocation($teacher);
                }

                $row++;

            }
            $col++;
        }
    }

    # ------------------------------------------------------------------------
    # CI, release, etc arrays and binding info
    # ------------------------------------------------------------------------

    # foreach teacher, release, CI for semester, and CI for year
    my @bound_totals;

    my $row = 0;
    foreach my $teacher ( @{ $self->_semester_teachers($semester) } ) {

        my $release = "";
        $release = sprintf( "%6.3f", $teacher->release ) if $teacher->release;

        my $CI = CICalc->new($teacher)->calculate( $Schedules{$semester} );

        my $info = {
            $TeacherKey => $teacher,
            $CIKey      => $CI,
            $CITotalKey => "",
            $ReleaseKey => $release,
        };

        $self->_data_totals($semester)->[$row] = $info;

        $bound_totals[$row][0] =
          \$self->_data_totals($semester)->[$row]->{$ReleaseKey};
        $bound_totals[$row][1] =
          \$self->_data_totals($semester)->[$row]->{$CIKey};
        $bound_totals[$row][2] =
          \$self->_data_totals($semester)->[$row]->{$CITotalKey};

        $row++;
    }

    # ------------------------------------------------------------------------
    # remaining hours to be allocated, arrays and binding
    # ------------------------------------------------------------------------

    # foreach course/section/teacher, holds the number of hours
    $col = 0;
    my $remaining_text = \"Avail Hrs";

    foreach my $course ( @{ $self->_semester_courses($semester) } ) {

        foreach
          my $section ( sort { $a->number cmp $b->number } $course->sections )
        {
            $self->_data_unused_hours($semester)->[$col] = {
                $SectionKey => $section,
                $ValueKey => "",   #$section->hours - $section->allocated_hours,
            };

            $bound_remaining_hours[$col] =
              \$self->_data_unused_hours($semester)->[$col]{$ValueKey};
            $col++;
        }
    }

    # ------------------------------------------------------------------------
    # set up the binding of the data to the gui elements in gui_grid
    # ------------------------------------------------------------------------
    $Gui->bind_data_to_grid(
        $semester,         \@courses_text,
        \@courses_balloon, \@sections_text,
        \@teachers_text,   \@bound_data_vars,
        [""], [qw(RT CI YEAR)],
        \@bound_totals, $remaining_text,
        \@bound_remaining_hours,
    );

}

# ============================================================================
# Update all the CI
# ============================================================================
sub _update_all_CI {
    my $self     = shift;
    my $semester = shift;
    my $totals   = $self->_data_totals($semester);
    my %all_semesters;

    # update for this semester only
    my $row = 0;
    foreach my $total (@$totals) {
        my $teacher = $total->{$TeacherKey};
        $total->{$CIKey} =
          CICalc->new($teacher)->calculate( $Schedules{$semester} );
        $all_semesters{"$teacher"} = $total->{$CIKey};
        $row++;
    }

    # update remaining hours for this semester only
    foreach my $remaining ( @{ $self->_data_unused_hours($semester) } ) {
        my $section = $remaining->{$SectionKey};
        $remaining->{$ValueKey} = $section->hours - $section->allocated_hours;
    }

    # get totals for all semesters
    foreach my $sem ( $self->_semesters ) {
        next if $sem eq $semester;
        my $tots = $self->_data_totals($sem);
        foreach my $tot (@$tots) {
            my $teacher = $tot->{$TeacherKey};
            $all_semesters{"$teacher"} += $tot->{$CIKey};
        }
    }

    # update the total CI on the grid
    foreach my $sem ( $self->_semesters ) {
        my $tots = $self->_data_totals($sem);
        foreach my $tot (@$tots) {
            my $teacher = $tot->{$TeacherKey};
            $tot->{$CITotalKey} = $all_semesters{"$teacher"};
        }
    }

}

# ============================================================================
# validate number callback routine
# - make sure it is a number
# - invalidate the CI calculations
# ============================================================================
sub _cb_validate_number {
    my $self       = shift;
    my $semester   = shift;
    my $row        = shift;
    my $col        = shift;
    my $totals     = $self->_data_totals($semester)->[$row];
    my $remainders = $self->_data_unused_hours($semester)->[$col];

    my $maybe_number = shift;

    if (   $maybe_number =~ /^\s*$/
        || $maybe_number =~ /^(\s*\d*)(\.?)(\d*\s*)$/ )
    {
        $totals->{$CIKey}        = "";
        $totals->{$CITotalKey}   = "";
        $remainders->{$ValueKey} = "";
        return 1;
    }
    return 0;
}

# ============================================================================
# User has entered data... process it (this is a callback routine)
# ============================================================================
sub _cb_process_data_entry {
    no warnings;
    my $self     = shift;
    my $semester = shift;
    my $row      = shift;
    my $col      = shift;

    my $remainders = $self->_data_unused_hours($semester)->[$col];
    my $data       = $self->_data_teacher_hours($semester)->[$row][$col];
    my $teacher    = $data->{$TeacherKey};
    my $section    = $data->{$SectionKey};
    my $hours      = $data->{$ValueKey};

    $section->set_teacher_allocation( $teacher, $hours );

    $self->_update_all_CI($semester);
    $self->_data_unused_hours($semester)->[$col]{$ValueKey} =
      $section->hours - $section->allocated_hours;

    $$Dirty_ptr = 1;
}

# ============================================================================
# bound data
# ============================================================================
my $data_semester_hash      = {};
my $totals_semester_hash    = {};
my $remaining_semester_hash = {};

sub _data_teacher_hours {
    my $self     = shift;
    my $semester = shift;
    $data_semester_hash->{$semester} = []
      unless $data_semester_hash->{$semester};

    return $data_semester_hash->{$semester};
}

sub _data_totals {
    my $self     = shift;
    my $semester = shift;
    $totals_semester_hash->{$semester} = []
      unless $totals_semester_hash->{$semester};
    return $totals_semester_hash->{$semester};
}

sub _data_unused_hours {
    my $self     = shift;
    my $semester = shift;
    $remaining_semester_hash->{$semester} = []
      unless $remaining_semester_hash->{$semester};
    return $remaining_semester_hash->{$semester};
}

sub _reset_teacher_hours {
    my $self     = shift;
    my $semester = shift;
    $data_semester_hash->{$semester} = [];
}

sub _reset_totals {
    my $self     = shift;
    my $semester = shift;
    $totals_semester_hash->{$semester} = [];
}

sub _reset_unused_hours {
    my $self     = shift;
    my $semester = shift;
    $remaining_semester_hash->{$semester} = [];
}

# ============================================================================
# Setters and Getters
# ============================================================================

sub _semester_courses {
    my $self     = shift;
    my $semester = shift;
    $self->{$semester}{-courses} = shift if @_;
    return $self->{$semester}{-courses};
}

sub _semester_teachers {
    my $self     = shift;
    my $semester = shift;
    $self->{$semester}{-teachers} = shift if @_;
    return $self->{$semester}{-teachers};
}

sub _semester_sections {
    my $self     = shift;
    my $semester = shift;
    $self->{$semester}{-sections} = shift if @_;
    return $self->{$semester}{-sections};
}

sub _semesters {
    my $self = shift;
    return ( sort keys %Schedules );
}

1;

