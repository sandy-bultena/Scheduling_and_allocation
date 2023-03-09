use strict;
use warnings;

package SchedulerTk;
use FindBin;
use lib "$FindBin::Bin/../";
use GUI::MainPageBaseTk;
use File::Basename;
use UsefulClasses::AllScheduables;

our @ISA = qw(MainPageBaseTk);

=head1 NAME

SchedulerTk - GUI code for the main application window 

Inherits from MainPageBaseTk

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

    # create the views_manager (which shows all the schedule views etc.)
    
    my $views_manager = ViewsManager->new( $gui, \$Dirtyflag, \$Schedule );
    $gui->set_views_manager($views_manager);

    $gui->start_event_loop();

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

=head2 set_views_manager

Sometimes this Tk class needs to access the views_manager.

This makes the views_manager available to this code

=cut

sub set_views_manager {
    my $self = shift;
    $views_manager = shift;
}

=cut

=head2 create_front_page

Creates the very first page that is shown to the user

=cut

sub create_front_page {
    my $self                   = shift;
    my $Preferences            = shift;
    my $open_schedule_callback = shift;
    my $new_schedule_callback  = shift;

    my $logo_file    = Tk::FindImages::get_logo();
    my $option_frame = $self->SUPER::create_front_page($logo_file);

    my $button_width    = 50;
    my $short_file_name = 25;

    # --------------------------------------------------------------
    # open previous schedule file option
    # --------------------------------------------------------------
    if ( $Preferences->{-current_file} && -e $Preferences->{-current_file} ) {

        # make sure name displayed is not too long
        my $file     = $Preferences->{-current_file};
        my $basename = basename($file);
        if ( length($basename) > $short_file_name ) {
            $basename = "(...) " . substr( $basename, -$short_file_name );
        }

        $option_frame->Button(
            -text        => "Open $basename",
            -justify     => 'right',
            -font        => $self->fonts->{big},
            -borderwidth => 0,
            -bg          => $self->colours->{DataBackground},
            -command =>
              [ $open_schedule_callback, $Preferences->{-current_file} ],
            -width  => $button_width,
            -height => 3,
        )->pack( -side => 'top', -fill => 'y', -expand => 0 );
    }

    # --------------------------------------------------------------
    # create new schedule file option
    # --------------------------------------------------------------
    $option_frame->Button(
        -text        => "Create NEW Schedule File",
        -font        => $self->fonts->{big},
        -borderwidth => 0,
        -bg          => $self->colours->{DataBackground},
        -command     => sub {
            $new_schedule_callback->();
        },
        -width  => $button_width,
        -height => 3,
    )->pack( -side => 'top', -fill => 'y', -expand => 0 );

    # --------------------------------------------------------------
    # open schedule file option
    # --------------------------------------------------------------
    $option_frame->Button(
        -text        => "Browse for Schedule File",
        -font        => $self->fonts->{big},
        -borderwidth => 0,
        -bg          => $self->colours->{DataBackground},
        -command     => $open_schedule_callback,
        -width       => $button_width,
        -height      => 3,
    )->pack( -side => 'top', -fill => 'y', -expand => 0 );

    $option_frame->Frame( -bg => $self->colours->{DataBackground} )->pack(
        -expand => 1,
        -fill   => 'both',
    );
}

=head2 update_for_new_schedule_and_show_page

Schedule has changed, so we need to update the view

=cut

sub update_for_new_schedule_and_show_page {
    my $self = shift;
    $views_manager->destroy_all();
    $self->SUPER::update_for_new_schedule_and_show_page(@_);
}

# ============================================================================

=head2 draw_view_choices

The ViewsManager can create schedule views for all teachers/labs etc.

The I<allowable> views depend on the schedules, so this function needs to
be called whenever the schedule changes.

Draws the buttons to access any of the available views

B<Parameters>

- default_tab => name of notebook tab to draw on

- all_view_choices => a list of schedulable objects (teachers/labs etc.)

- btn_callback => a function that will be called whenever the ViewsManager
is asked to create a view

=cut

{
    my $frame;

    sub draw_view_choices {
        my $self            = shift;
        my $default_tab     = shift;
        my $all_scheduables = shift;
        my $btn_callback    = shift || sub { return; };

        my $f = $self->_pages->{ lc($default_tab) };

        $views_manager->gui->reset_button_refs();

        $frame->destroy if $frame;

        $frame = $f->Frame->pack( -expand => 1, -fill => 'both' );

        foreach my $type ( AllScheduables->valid_types ) {
            my $view_choices_frame =
              $frame->LabFrame(
                -label => $all_scheduables->by_type($type)->title, )
              ->pack( -expand => 1, -fill => 'both' );

            my $view_choices_scrolled_frame =
              $view_choices_frame->Scrolled( 'Frame', -scrollbars => "osoe" )
              ->pack( -expand => 1, -fill => 'both' );

            $views_manager->gui->create_buttons_for_frame(
                $view_choices_scrolled_frame,
                $all_scheduables->by_type($type),
                $btn_callback
            );
        }

    }
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

        my $f = $self->_pages->{ lc($default_page) };

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
