#!/usr/bin/perl
use strict;
use warnings;

# =================================================================
# Edit Allocation
# -----------------------------------------------------------------
# INPUTS:
#   frame
#   rows            - number of rows in the grid
#   col_merge       - array of numbers, where each item is used to
#                     represent a group of columns (affects colouring)
#   totals_merge    - array of numbers, where each item is used to
#                     represent a group of columns in the 'totals'
#                     section
#   fonts           - hash of fonts,
#                     required: small
#   allocation_info - array of hashes (one for each semester) of the following:
#       -rows
#       -columns_numbers
#       -totals_numbers
#
# METHODS:
#   redraw                  (allocation_info)   # useful if info has changed
#   set_cb_data_entry       (semesters, event_handler)
#   set_cb_process_entry    (semester, event_handler)
#   set_cb_bottom_row_ok    (semester, event_handler)
#   bind_data_to_grid       (
#                               semester,
#                               courses_text,
#                               courses_balloon,
#                               sections_text,
#                               teachers_text,
#                               bound_data_vars,
#                               bottom_row_header,
#                               totals_txt,
#                               bound_totals,
#                               remaining_text,
#                               bound_remaining_hours
#                           )
#
# RETURNS:
#   - none -
#
# REQUIRED EVENT HANDLERS:
#   For each semester (used by AllocationGrid):
#       cb_data_entry              (row, col, proposed_new_text)->bool
#       cb_process_data_change     (row, col)
#       cb_bottom_row_ok           (text_of_entry_widget)->bool
# =================================================================

package EditAllocationTk;
use FindBin;
use lib "$FindBin::Bin/..";
use Carp;
use Tk;
use Tk::Dialog;
use Tk::Menu;
use Tk::LabEntry;
use Tk::Pane;
use GUI::AllocationGridTk;
use GUI::FontsAndColoursTk;

my $Fonts = FontsAndColoursTk->Fonts;
my $frame;

sub new {
    my $class = shift;
    $frame = shift;
    my $allocation_info = shift;
    my $self = bless {}, $class;
    $self->{-frame} = $frame;

    $Fonts = FontsAndColoursTk->Fonts;
    my $yscroll;

    $yscroll = $self->{-frame}->Scrollbar( -orient => 'vertical' )
      ->pack( -side => 'right', -fill => 'y' );
    $self->{-scrolledframe} = $self->{-frame}->Pane( -sticky => 'nsew' )
      ->pack( -side => 'top', -expand => 1, -fill => 'both' );

    # manage the scrollbar?
    $yscroll->configure(
        -command => sub {
            $self->{-scrolledframe}->yview(@_);
        }
    );
    $self->{-scrolledframe}->configure(
        -yscrollcommand => sub {
            my (@args) = @_;
            $yscroll->set(@args);
        },
    );

    $self->redraw($allocation_info);
    return $self;
}

sub redraw {
    my $self            = shift;
    my $allocation_info = shift;
    my $panes           = $self->_panes;

    foreach my $semester_info (@$allocation_info) {
        my $semester = $semester_info->{-semester};

        # ----------------------------------------------------------------
        # create an allocation grid for this semester,
        # if and only if it is different than the previous grid drawn
        # ----------------------------------------------------------------
        unless (
            $self->gui_grid($semester)
            && !$self->_has_grid_size_changed(
                $semester,
                $semester_info->{-rows},
                $semester_info->{-columns_numbers},
                $semester_info->{-totals_numbers},
            )
          )
        {
            my $semester = $semester_info->{-semester};

            # make new frame if if does not already exist
            unless ( $panes->{$semester} ) {
                $panes->{$semester} =
                  $self->{-scrolledframe}->Pane( -sticky => "nsew" );
            }

            # make and replace existing grid
            if ( $self->gui_grid($semester) ) {
                $self->gui_grid($semester)->delete();
            }
            my $grid = AllocationGridTk->new(
                $panes->{$semester},
                $semester_info->{-rows},
                $semester_info->{-columns_numbers},
                $semester_info->{-totals_numbers},
                $Fonts,
            );

            # save info for later
            $self->gui_grid( $semester, $grid );
            $self->num_rows( $semester, $semester_info->{-rows} );
            $self->sub_section_numbers( $semester,
                $semester_info->{-columns_numbers} );
            $self->total_numbers( $semester,
                $semester_info->{-totals_numbers} );

        }
    }

    # ------------------------------------------------------------------------
    # layout the top widgets via grid manager
    # ------------------------------------------------------------------------
    # now that the grids are drawn, display the semester
    # ... thought this would be faster, it wasn't (sniff, sniff)
    my $row = 0;
    foreach my $semester_info (@$allocation_info) {

        my $semester = $semester_info->{-semester};
        if ( $panes->{$semester} ) {
            $panes->{$semester}
              ->grid( -row => $row, -sticky => 'nswe', -column => 0 );
            $self->{-scrolledframe}->gridRowconfigure( $row, -weight => 0 );
            $row++;
        }

    }
    $self->{-scrolledframe}->gridColumnconfigure( 0, -weight => 1 );

}

# ============================================================================
# has the grid size changed since last time we created it?
# ============================================================================
sub _has_grid_size_changed {
    my $self     = shift;
    my $semester = shift;
    my $rows     = shift;
    my $col_nums = shift;
    my $tot_nums = shift;

    # number of rows that have changed?
    return 1 unless $rows == $self->num_rows($semester);

    # foreach course, is the number of courses the same,
    # is the number of sections per course the same?

    return 1
      unless scalar(@$col_nums) ==
      scalar( @{ $self->sub_section_numbers($semester) } );

    foreach my $sec ( 0 .. scalar(@$col_nums) - 1 ) {
        return 1
          unless $col_nums->[$sec] ==
          $self->sub_section_numbers($semester)->[$sec];
    }
    return 1
      unless scalar(@$tot_nums) ==
      scalar( @{ $self->total_numbers($semester) } );

    foreach my $total_secs ( 0 .. scalar(@$tot_nums) - 1 ) {
        return 1
          unless $tot_nums->[$total_secs] ==
          $self->total_numbers($semester)->[$total_secs];
    }
    return;
}

# ============================================================================
# set the allocation grid cb_data_entry callback for specified semester
# ============================================================================
sub set_cb_data_entry {
    my $self          = shift;
    my $semester      = shift;
    my $event_handler = shift;
    $self->gui_grid($semester)->cb_data_entry($event_handler);
}

# ============================================================================
# set the allocation grid cb_process_data_change callback for specified semester
# ============================================================================
sub set_cb_process_data_change {
    my $self          = shift;
    my $semester      = shift;
    my $event_handler = shift;
    $self->gui_grid($semester)->cb_process_data_change($event_handler);
}

# ============================================================================
# set the allocation grid cb_bottom_row_ok callback for specified semester
# ============================================================================
sub set_cb_bottom_row_ok {
    my $self          = shift;
    my $semester      = shift;
    my $event_handler = shift;
    $self->gui_grid($semester)->cb_bottom_row_ok($event_handler);
}

# ============================================================================
# bind all the data to the various AllocationGrid entry widgets
# ============================================================================
sub bind_data_to_grid {
    my $self                  = shift;
    my $semester              = shift;
    my $courses_text          = shift;
    my $courses_balloon       = shift;
    my $sections_text         = shift;
    my $teachers_text         = shift;
    my $bound_data_vars       = shift;
    my $totals_header         = shift;
    my $totals_txt            = shift;
    my $bound_totals          = shift;
    my $remaining_text        = shift;
    my $bound_remaining_hours = shift;

    $self->gui_grid($semester)->populate(
        $courses_text,  $courses_balloon, $sections_text,
        $teachers_text, $bound_data_vars, $totals_header,
        $totals_txt,    $bound_totals,    $remaining_text,
        $bound_remaining_hours,
      )

}

sub _panes {
    my $self = shift;
    $self->{-panes} = {} unless $self->{-panes};
    $self->{-panes} = shift if @_;
    return $self->{-panes};
}

# ============================================================================
# returns the AllocationGrid for the specific semester
# ============================================================================
sub gui_grid {
    my $self     = shift;
    my $semester = shift;
    $self->{$semester}->{-gui_grid} = shift if @_;
    return $self->{$semester}->{-gui_grid};
}

# ============================================================================
# number of rows for the allocation grid for specific semester
# ============================================================================
sub num_rows {
    my $self     = shift;
    my $semester = shift;
    $self->{$semester}->{-num_rows} = shift if @_;
    return $self->{$semester}->{-num_rows};
}

# ============================================================================
# number of section numbers for each course for the allocation grid for specific semester
# ============================================================================
sub sub_section_numbers {
    my $self     = shift;
    my $semester = shift;
    $self->{$semester}->{-sub_numbers} = shift if @_;
    return $self->{$semester}->{-sub_numbers};
}

# ============================================================================
# number of sub_sections for the 'totals' heading
# for the allocation grid for specific semester
# ============================================================================
sub total_numbers {
    my $self     = shift;
    my $semester = shift;
    $self->{$semester}->{-total_numbers} = shift if @_;
    return $self->{$semester}->{-total_numbers};
}

1;
