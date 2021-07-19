use strict;
use warnings;

package AllocationManagerTk;
use FindBin;
use lib "$FindBin::Bin/../";
use GUI::MainPageBaseTk; 
use File::Basename;

our @ISA = qw(MainPageBaseTk);

=head1 NAME

AllocationManagerTk - GUI code for the main application window 

=head1 VERSION

Version 6.00

=head1 SYNOPSIS

    use GUI::SchedulerTk;
    my $gui = SchedulerTk->new();

    our @Required_pages = (
                        NoteBookPage->new( "Teachers", \&update_edit_teachers ),
                        NoteBookPage->new( "Streams",  \&update_edit_streams ),
    );
    
    # Create the mainWindow
    
    $gui->create_main_window();
    my ( $toolbar_buttons, $button_properties, $menu ) = menu_info();
    $gui->create_menu_and_toolbars( $toolbar_buttons, $button_properties, $menu );
    $gui->create_front_page( $Preferences, \&open_schedule, \&new_schedule );
    $gui->create_status_bar( \$Current_schedule_file );

    # pre-process procedures
    
    $gui->bind_dirty_flag( \$Dirtyflag );
    $gui->define_notebook_tabs( \@Required_pages );

    $gui->define_exit_callback( \&_exit_schedule );

=head1 METHODS 

=cut

# ============================================================================
# Package variables
# ============================================================================
our $BinDir = "$FindBin::Bin/";

my $views_manager;
my $mw;

# ============================================================================

=head1 ACCESS TO EXTERNAL DATA

=head2 create_status_bar

Create a status bar for current filename, and for the dirty pointer text

B<Parameters>

- current_filename_ptr => pointer to a scalar containing the current filename

=cut

=head2 create_front_page

Creates the very first page that is shown to the user

=cut

sub create_front_page {
    my $self                   = shift;
    my $Preferences            = shift;
    my $semesters = shift;
    my $open_schedules_callback = shift;
    my $new_schedule_callback  = shift;
    my $open_schedule_callback = shift;

use Data::Dumper;print Dumper $Preferences;
    my $logo_file = Tk::FindImages::get_allocation_logo();
    my $option_frame = $self->SUPER::create_front_page($logo_file);

    my $button_width    = 50;
    my $short_file_name = 25;

    # --------------------------------------------------------------
    # create "open previous allocation files"" button
    # --------------------------------------------------------------

    # do all the files stored in the 'ini' file still exist?
    my $flag = 1;    # true
    foreach my $semester (@$semesters) {
        $flag = 0
          unless $Preferences->{ "-current_$semester" . "_file" }
          && -e $Preferences->{ "-current_$semester" . "_file" };
    }

        my %files = ();
        my %short_files = ();
    
    # yes, all files stored in ini file still exists, 
    # make button
    if ($flag) {


        foreach my $semester (@$semesters) {

            $files{$semester} =
              $Preferences->{ "-current_$semester" . "_file" };

            # make sure displayed names are not too long
            if ( defined $files{$semester}
                && length( $files{$semester} ) > $short_file_name )
            {
                $short_files{$semester} =
                  "(...) " . substr( $files{$semester}, -$short_file_name );
            }

        }

        # make button for opening all files
        my $text = "Open";
        foreach my $semester (@$semesters) { $text .= "\n$short_files{$semester}"; }
        $option_frame->Button(
            -text        => $text,
            -font        => $self->fonts->{big},
            -borderwidth => 0,
            -bg          => $self->colours->{DataBackground},
            -command     => [$open_schedules_callback,\%files], 
            -width  => $button_width,
            -height => 6,
        )->pack( -side => 'top', -fill => 'y', -expand => 0 );

    }

    # --------------------------------------------------------------
    # create new allocation files
    # --------------------------------------------------------------
    foreach my $semester (@$semesters) {
        $option_frame->Button(
            -text        => "Create NEW $semester Schedule File",
            -font        => $self->fonts->{big},
            -borderwidth => 0,
            -bg          => $self->colours->{DataBackground},
            -command     => [$new_schedule_callback, $semester],
            -width  => $button_width,
            -height => 3,
        )->pack( -side => 'top', -fill => 'y', -expand => 0 );
    }

    # --------------------------------------------------------------
    # open schedule file
    # --------------------------------------------------------------

    foreach my $semester (@$semesters) {
        $option_frame->Button(
            -text        => "Browse for $semester Schedule File",
            -font        => $self->fonts->{big},
            -borderwidth => 0,
            -bg          => $self->colours->{DataBackground},
            -command     => [ $open_schedule_callback, $semester ],
            -width       => $button_width,
            -height      => 3,
        )->pack( -side => 'top', -fill => 'y', -expand => 0 );

    }
    $option_frame->Frame( -bg => $self->colours->{DataBackground} )->pack(
        -expand => 1,
        -fill   => 'both',
    );
}

sub update_for_new_schedule_and_show_page {
    print "update_for_new_schedule\n";
    my $self =shift;
    $self->SUPER::update_for_new_schedule_and_show_page(@_);
}

=head2 draw_overview

Writes the text overview of the schedule to the appropriate gui object

B<Parameters>

- default_tab => name of notebook tab to draw on

- course_text => text describing all the courses

- teacher_text => text describing all the teachers workloads

=cut

{
    my $tbox3;
    my $tbox;
    my $tbox2;

    my $OverviewNotebook;
    my %OverviewPages;

    sub draw_overview {
        my $self         = shift;
        my $default_page = shift;
        my $course_text  = shift;
        my $teacher_text = shift;

        my $f = $self->pages->{ lc($default_page) };

        unless ($OverviewNotebook) {
            $OverviewNotebook =
              $f->NoteBook()->pack( -expand => 1, -fill => 'both' );

            $OverviewPages{'course2'} = $OverviewNotebook->add(
                'course2',
                -label => 'by Course',

            );

            $OverviewPages{'teacher2'} =
              $OverviewNotebook->add( 'teacher2', -label => 'by Teacher', );

        }
        _actions_course($course_text);
        _actions_teacher($teacher_text);

    }

    # Draw Course Overview
    sub _actions_course {
        my $text = shift;
        my $f    = $OverviewPages{'course2'};

        unless ($tbox2) {
            $tbox2 = $f->Scrolled(
                'ROText',
                -height     => 20,
                -width      => 50,
                -scrollbars => 'osoe',
                -wrap       => 'none'
            )->pack( -expand => 1, -fill => 'both' );
        }

        $tbox2->delete( "1.0", 'end' );

        foreach my $txt (@$text) {
            $tbox2->insert( 'end', $txt );
        }

    }

    sub _actions_teacher {
        my $text = shift;
        my $f    = $OverviewPages{'teacher2'};

        unless ($tbox3) {
            $tbox3 = $f->Scrolled(
                'ROText',
                -height     => 20,
                -width      => 50,
                -scrollbars => 'osoe',
                -wrap       => 'none'
            )->pack( -expand => 1, -fill => 'both' );
        }
        $tbox3->delete( "1.0", 'end' );

        foreach my $txt (@$text) {
            $tbox3->insert( 'end', $txt );
        }

    }
}

1;
