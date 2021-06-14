use strict;
use warnings;

package SchedulerManagerTk;

# ============================================================================
# required third parth libraries
# ============================================================================
use FindBin;
use lib "$FindBin::Bin/";
use lib "$FindBin::Bin/Library";
our $BinDir = "$FindBin::Bin/";
use Tk;
use Tk::Table;
use Tk::Notebook;
use Tk::LabFrame;
use Tk::ROText;
use Tie::Watch;

# ============================================================================
# Libraries (shipped with this project)
# ============================================================================
use Tk::FindImages;
use Tk::InitGui;
use Tk::ToolBar;
use PerlLib::Colours;
use GuiSchedule::View;
use GuiSchedule::GuiSchedule;
use GuiSchedule::DataEntry;
use GuiSchedule::EditCourses;

# ============================================================================
# Package variables
# ============================================================================
our ( $Colours, $Fonts );

# ============================================================================
# Constants
# ============================================================================
my $Main_frame_height = 400;
my $Main_frame_width  = 800;
my $Welcome_width     = 600;
my $Welcome_height    = 600;

# ============================================================================
# Global vars
# ============================================================================

my %Pages;
my %OverviewPages;
my $Front_page_frame;
my $Schedule_ptr;
my $Dirty_flag_ptr;
my $Dirty_flag_text = "";
my $guiSchedule;
my $mw;

# ============================================================================
# new - returns an object,
# ... but it really saves no data, just makes
#     it a nice alias instead of SchedulerManagerTk::create_main_window()
# ============================================================================
sub new {
    my $class = shift;
    return bless {};
}

# ============================================================================
# create_main_window:
# ============================================================================
sub create_main_window {
    my $self = shift;

    # create the main window and frames
    $mw = MainWindow->new();
    $mw->Frame( -height => $Main_frame_height )->pack( -side => 'left' );
    $mw->geometry( $Welcome_height . "x" . $Welcome_width );

    # when clicking the 'x' in the corner of the window, call exit_schedule
    $mw->protocol( 'WM_DELETE_WINDOW', \&exit_schedule );

    # Gets and sets the colours and fonts
    ( $Colours, $Fonts ) = InitGui->set($mw);

    use Data::Dumper;
    print Dumper $Colours;

    # Hard code the colours
    $Colours = {
                 WorkspaceColour           => "#eeeeee",
                 WindowForeground          => "black",
                 SelectedBackground        => "#cdefff",
                 SelectedForeground        => "#0000ff",
                 DarkBackground            => "#cccccc",
                 ButtonBackground          => "#abcdef",
                 ButtonForeground          => "black",
                 ActiveBackground          => "#89abcd",
                 highlightbackground       => "#0000ff",
                 ButtonHighlightBackground => "#ff0000",
                 DataBackground            => "white",
                 DataForeground            => "black",
    };

    SetSystemColours( $mw, $Colours );
    $mw->configure( -bg => $Colours->{WorkspaceColour} );
    $self->{-mw} = $mw;
}

# ============================================================================
# create_menu_and_toolbars:
# - creates the menu and toolbars based on the information passed in by the
#   presenter.
# INPUTS:
#   buttons: a list pointer of buttons to create on the toolbar
#   actions: a hash pointer of: action_name
#                                           {code}->
#                                           {hint}->
#   menu:    a list of lists organizing actions into the menu bar
# ============================================================================

sub create_menu_and_toolbars {
    my $self    = shift;
    my $buttons = shift;
    my $actions = shift;
    my $menu    = shift;

    my $image_dir = Tk::FindImages::get_image_dir();

    # ------------------------------------------------------------------------
    # create menu
    # ------------------------------------------------------------------------
    $mw->configure( -menu => my $menubar = $mw->Menu( -menuitems => $menu ) );

    # ------------------------------------------------------------------------
    # create toolbar
    # ------------------------------------------------------------------------
    my $toolbar = $mw->ToolBar( -buttonbg => $Colours->{WorkspaceColour},
                                -hoverbg  => $Colours->{ActiveBackground}, );

    # create all the buttons
    foreach my $button (@$buttons) {

        # if button not defined, insert a divider
        unless ($button) {
            $toolbar->bar();
            next;
        }

        # add button
        $toolbar->add(
                       -name     => $button,
                       -image    => "$image_dir/$button.gif",
                       -command  => $actions->{$button}{code},
                       -hint     => $actions->{$button}{hint},
                       -shortcut => $actions->{$button}{sc},
        );

    }

    # pack the toolbar
    $toolbar->pack( -side => 'top', -expand => 0, -fill => 'x' );

    # ------------------------------------------------------------------------
    # bind all of the accelerators
    # ------------------------------------------------------------------------
    $mw->bind( '<Control-Key-o>', $actions->{open}{code} );
    $mw->bind( '<Control-Key-s>', $actions->{save}{code} );
    $mw->bind( '<Control-Key-n>', $actions->{new}{code} );
    $mw->bind( '<Control-Key-e>', \&exit_schedule );

    # if darwin, also bind the 'command' key for MAC users
    if ( $^O =~ /darwin/ ) {
        $mw->bind( '<Meta-Key-o>', $actions->{open}{code} );
        $mw->bind( '<Meta-Key-s>', $actions->{save}{code} );
        $mw->bind( '<Meta-Key-n>', $actions->{new}{code} );
        $mw->bind( '<Meta-Key-e>', \&exit_schedule );
    }
}

# ==================================================================
# create_status_bar:
# - create a status bar for current filename, and for the
#   dirty pointer text
# INPUTS:
# - pointer to a scalar containing the current filename
# ==================================================================
sub create_status_bar {
    my $self                 = shift;
    my $current_filename_ptr = shift;

    # choose what colour to show 'dirty flag text' based on WorkspaceColour
    my $red;
    if ( Colour->isLight( $Colours->{WorkspaceColour} ) ) {
        $red = "#880000";
    }
    else {
        $red = "#ff0000";
    }

    # draw frame and labels for current filename and dirty flag
    my $status_frame = $mw->Frame(
                                   -borderwidth => 0,
                                   -relief      => 'flat',
    )->pack( -side => 'bottom', -expand => 0, -fill => 'x' );

    $status_frame->Label(
                          -textvariable => $current_filename_ptr,
                          -borderwidth  => 1,
                          -relief       => 'ridge',
    )->pack( -side => 'left', -expand => 1, -fill => 'x' );

    $status_frame->Label(
                          -textvariable => \$Dirty_flag_text,
                          -borderwidth  => 1,
                          -relief       => 'ridge',
                          -width        => 15,
                          -fg           => $red,
    )->pack( -side => 'right', -fill => 'x' );

}

# ============================================================================
# bind_schedule_and_dirty_flag
# - create access to the Schedule,
#   and its 'dirty_flag' (data changed since last save)
# ============================================================================
sub bind_schedule_and_dirty_flag {
    my $self = shift;
    $Schedule_ptr   = shift;
    $Dirty_flag_ptr = shift;

    # watch Dirty_flag and change the dirty_flag_text whenever
    # the dirty_flag changes
    my $dirty_watch = Tie::Watch->new(
        -variable => $Dirty_flag_ptr,
        -store    => sub {
            my $self = shift;
            if   ($$Dirty_flag_ptr) { $Dirty_flag_text = "NOT SAVED"; }
            else                    { $Dirty_flag_text = ""; }
            $self->Store();
          }

    );

}

# ==================================================================
# create_front_page
# - creates the very fist page that is shown to the user
# ==================================================================
sub create_front_page {
    my $self                   = shift;
    my $Preferences            = shift;
    my $open_schedule_callback = shift;
    my $new_schedule_callback  = shift;

    my $button_width    = 50;
    my $short_file_name = 40;

    $Front_page_frame = $mw->Frame(
                                    -borderwidth => 10,
                                    -relief      => 'flat',
                                    -bg          => $Colours->{DataBackground},
    )->pack( -side => 'top', -expand => 1, -fill => 'both' );

    # --------------------------------------------------------------
    # logo
    # --------------------------------------------------------------

    # create an image object of the logo
    my $logo_file = Tk::FindImages::get_logo();
    my $image = $mw->Photo( -file => $logo_file );

    # frame and label
    my $labelImage =
      $Front_page_frame->Label(
                                '-image'     => $image,
                                -borderwidth => 5,
                                -relief      => 'flat'
      )->pack( -side => 'left', -expand => 0 );

    # --------------------------------------------------------------
    # frame for holding buttons for starting the scheduling tasks
    # --------------------------------------------------------------
    my $option_frame =
      $Front_page_frame->Frame(
                                -bg          => $Colours->{DataBackground},
                                -borderwidth => 10,
                                -relief      => 'flat'
      )->pack( -side => 'left', -expand => 1, -fill => 'both' );

    $option_frame->Frame( -background => $Colours->{DataBackground}, )
      ->pack( -expand => 1, -fill => 'both' );

    # --------------------------------------------------------------
    # open previous schedule file option
    # --------------------------------------------------------------
    if ( $Preferences->{-current_file} && -e $Preferences->{-current_file} ) {

        # make sure name displayed is not too long
        my $file = $Preferences->{-current_file};
        if ( length($file) > $short_file_name ) {
            $file = "(...) " . substr( $file, -$short_file_name );
        }

        $option_frame->Button(
            -text        => "Open $file",
            -font        => $Fonts->{big},
            -borderwidth => 0,
            -bg          => $Colours->{DataBackground},
            -command     => sub {
                $open_schedule_callback->( $Preferences->{-current_file} );
            },
            -width  => $button_width,
            -height => 3,
        )->pack( -side => 'top', -fill => 'y', -expand => 0 );
    }

    # --------------------------------------------------------------
    # create new schedule file option
    # --------------------------------------------------------------
    $option_frame->Button(
        -text        => "Create NEW Schedule File",
        -font        => $Fonts->{big},
        -borderwidth => 0,
        -bg          => $Colours->{DataBackground},
        -command     => sub {
            $new_schedule_callback->();
            $Front_page_frame->packForget();
            create_standard_page();
        },
        -width  => $button_width,
        -height => 3,
    )->pack( -side => 'top', -fill => 'y', -expand => 0 );

    # --------------------------------------------------------------
    # open schedule file option
    # --------------------------------------------------------------
    $option_frame->Button(
        -text        => "Browse for Schedule File",
        -font        => $Fonts->{big},
        -borderwidth => 0,
        -bg          => $Colours->{DataBackground},
        -command     => sub {
            $open_schedule_callback->();
        },
        -width  => $button_width,
        -height => 3,
    )->pack( -side => 'top', -fill => 'y', -expand => 0 );

    $option_frame->Frame( -bg => $Colours->{DataBackground} )->pack(
                                                                -expand => 1,
                                                                -fill => 'both',
    );
}

# ============================================================================
# choose_existing_file:
# - pick an existing file,
#
# INPUTS
# - initial directory to start searching
# - an array of arrays of filetypes to show.
#   Ex: [ [ "Schedules", ".yaml" ], [ "All Files", "*" ] ]
#
# RETURNS:
# - Selected file (if no file selected, returns an empty string
# ============================================================================

sub choose_existing_file {
    my $self              = shift;
    my $current_directory = shift;
    my $filetypes         = shift;
    my $file = $mw->getOpenFile( -initialdir => $current_directory,
                                 -filetypes  => $filetypes );
    return $file;
}

# ============================================================================
# show_error:
#
# INPUTS:
# - title
# - message to display
# ============================================================================
sub show_error {
    my $self    = shift;
    my $title   = shift;
    my $message = shift;
    $mw->messageBox(
                     -title   => $title,
                     -message => $message,
                     -type    => 'OK',
                     -icon    => 'error'
    );
}

# ============================================================================
# choose_file:
# - pick an existing file, or define your own
#
# INPUTS
# - initial directory to start searching
# - an array of arrays of filetypes to show.
#   Ex: [ [ "Schedules", ".yaml" ], [ "All Files", "*" ] ]
#
# RETURNS:
# - Selected file (if no file selected, returns an empty string)
# ============================================================================

sub choose_file {
    my $self              = shift;
    my $current_directory = shift;
    my $filetypes         = shift;
    my $file = $mw->getSaveFile( -initialdir => $current_directory,
                                 -filetypes  => $filetypes, );
    return $file;
}

# ============================================================================
# show_info:
# - show info to user
#
# INPUTS:
# - title
# - message to show user
# ============================================================================
sub show_info {
    my $self  = shift;
    my $title = shift;
    my $msg   = shift;
    $mw->messageBox(
                     -message => $msg,
                     -title   => $title,
                     -type    => 'OK',
                     -icon    => 'info'
    );
}

# ============================================================================
# question:
# - ask a user a question
#
# INPUTS:
# - title
# - msg
#
# RETURNS
# - a scalar (Yes|No|Cancel)
# ============================================================================
sub question {
    my $self  = shift;
    my $title = shift;
    my $msg   = shift;
    my $ans = $mw->messageBox(
                               -title   => $title,
                               -message => $msg,
                               -type    => 'YesNoCancel',
                               -icon    => 'question'
    );
    return $ans;
}

# ============================================================================
# wait_for_it:
# - asks user to please wait while something is in progress
#
# INPUTS:
# - title
# - message
#
# ============================================================================
# stop_waiting:
# - remove the wait message
# ============================================================================
{
    my $wait;

    sub wait_for_it {
        my $self  = shift;
        my $title = shift;
        my $msg   = shift;

        # ensure no 'previous waiting in progress'
        stop_waiting();

        # draw the window
        $wait = $mw->Toplevel();
        $wait->title($title);
        $wait->Label( -text => $msg, )->pack( -expand => 1, -fill => 'both' );

        #$wait->overrideredirect(1);
        $wait->geometry("300x450");
        $mw->update();
    }

    sub stop_waiting {
        $wait->destroy() if $wait;
        undef $wait;
    }
}
# ============================================================================
# start_event_loop:
# - once everything is drawn, wait for an event to happen
# ============================================================================
sub start_event_loop {
    MainLoop;
}

{
    my $Notebook;
    my $Required_notebook_tabs;

  # ============================================================================
  # define_notebook_tabs:
  # - define which tabs should be created in this application, and
  #   what functions should be called whenever a particular tab is opened
  # ============================================================================
    sub define_notebook_tabs {
        my $self = shift;
        $Required_notebook_tabs = shift;
    }

  # ============================================================================
  # get_notebook_page:
  # ============================================================================
    sub get_notebook_page {
        my $self = shift;
        my $page = shift;
        return $Pages{ lc($page) };
    }

  # ============================================================================
  # update_for_new_schedule:
  # - a new schedule has been read, reset the gui accordingly
  # ============================================================================
    sub update_for_new_schedule_and_show_page {
        my $self         = shift;
        my $default_page = shift;

        # remove any previous gui->views
        $guiSchedule->destroy_all;

        # if Notebook has already been created
        # (it is created in create_standard_page)
        if ($Notebook) {
            $Notebook->raise( lc($default_page) );
            draw_view_choices();
        }

        # Create the standard pages (notebooks, etc)
        else {
            $Front_page_frame->packForget();
            create_standard_page();
        }
    }

    # ==================================================================
    # create standard page
    # ==================================================================
    sub create_standard_page {

        my $Main_page_frame;

        # frame and label
        $Main_page_frame = $mw->Frame(
                                       -borderwidth => 1,
                                       -relief      => 'ridge',
        )->pack( -side => 'top', -expand => 1, -fill => 'both' );

        # create notebook
        $Notebook =
          $Main_page_frame->NoteBook()->pack( -expand => 1, -fill => 'both' );

        # View page
        die("Cannot work unless notebook tabs are defined")
          unless $Required_notebook_tabs;

        foreach my $page_info (@$Required_notebook_tabs) {
            my $lcname = lc( $page_info->name );
            $Pages{$lcname} =
              $Notebook->add(
                              $lcname,
                              -label    => $page_info->name,
                              -raisecmd => $page_info->handler
              );
        }

    }

}

sub set_gui_schedule {
    my $self = shift;
    $guiSchedule = shift;
}

# ==================================================================
# draw_view_choices
# ==================================================================
{
    my $frame;

    sub draw_view_choices {
        my $self        = shift;
        my $default_tab = shift;
        my $info_ptr    = shift;

        my $f = $Pages{ lc($default_tab) };

        $guiSchedule->reset_button_refs();

        $frame->destroy if $frame;

        $frame = $f->Frame->pack( -expand => 1, -fill => 'both' );

        foreach my $frame_info (@$info_ptr) {
            my $view =
              $frame->LabFrame( -label => $frame_info->[1], )
              ->pack( -expand => 1, -fill => 'both' );

            my $view2 =
              $view->Scrolled( 'Frame', -scrollbars => "osoe" )
              ->pack( -expand => 1, -fill => 'both' );

            $guiSchedule->create_frame( $view2, $frame_info );
        }

    }
}

# ==================================================================
# draw_overview
# ==================================================================

{
    my $OverviewNotebook;

    sub draw_overview {
        my $self         = shift;
        my $default_page = shift;
        my $course_text  = shift;
        my $teacher_text = shift;

        my $f = $Pages{ lc($default_page) };

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
        draw_overview_course($course_text);
        draw_overview_teacher($teacher_text);

    }

}

# ==================================================================
# exit_schedule
# ==================================================================
{
    my $exit_callback;

    sub define_exit_callback {
        my $self = shift;
        $exit_callback = shift || sub { return };
    }

    sub exit_schedule {
        my $self = shift;

        if ($$Dirty_flag_ptr) {
            my $ans = $mw->messageBox(
                                       -title   => 'Unsaved Changes',
                                       -message => "There are unsaved changes\n"
                                         . "Do you want to save them?",
                                       -type => 'YesNoCancel',
                                       -icon => 'question'
            );
            if ( $ans eq 'Yes' ) {
                $exit_callback->();
            }
            elsif ( $ans eq 'Cancel' ) {
                return;
            }
        }

        $mw->destroy();
        exit();
    }
}

# ============================================================
# Draw Course Overview
# ============================================================

{
    my $tbox;

    sub draw_overview_course {
        my $text = shift;
        my $f    = $OverviewPages{'course2'};

        unless ($tbox) {
            $tbox = $f->Scrolled(
                                  'ROText',
                                  -height     => 20,
                                  -width      => 50,
                                  -scrollbars => 'osoe',
                                  -wrap       => 'none'
            )->pack( -expand => 1, -fill => 'both' );
        }

        $tbox->delete( "1.0", 'end' );

        foreach my $txt (@$text) {
            $tbox->insert( 'end', $txt );
        }

    }
}

# ==================================================================
# Draw Teacher Overview
# ==================================================================

{
    my $tbox;

    sub draw_overview_teacher {
        my $text = shift;
        my $f    = $OverviewPages{'teacher2'};

        unless ($tbox) {
            $tbox = $f->Scrolled(
                                  'ROText',
                                  -height     => 20,
                                  -width      => 50,
                                  -scrollbars => 'osoe',
                                  -wrap       => 'none'
            )->pack( -expand => 1, -fill => 'both' );
        }
        $tbox->delete( "1.0", 'end' );

        foreach my $txt (@$text) {
            $tbox->insert( 'end', $txt );
        }

    }
}

1;
