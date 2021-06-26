use strict;
use warnings;

package SchedulerTk;

=head1 NAME

SchedulerTk - GUI code for the main application window 

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
# required third party libraries
# ============================================================================
use FindBin;
use lib "$FindBin::Bin/../";
use Tk;
use Tk::Table;
use Tk::Notebook;
use Tk::LabFrame;
use Tk::ROText;
use Tie::Watch;
use File::Basename;

# ============================================================================
# Libraries (shipped with this project)
# ============================================================================
use Tk::FindImages;
use Tk::ToolBar;
use PerlLib::Colours;
use GuiSchedule::EditCourses;

# ============================================================================
# Package variables
# ============================================================================
our $BinDir = "$FindBin::Bin/";

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
my $Dirty_flag_ptr;
my $Dirty_flag_text = "";
my $views_manager;
my $mw;
my $Notebook;
my $Required_notebook_tabs;
my $exit_callback;
my ( $Colours, $Fonts );


=head2 new

Instatiates the SchedulerTk object

=cut 

sub new {
    my $class = shift;
    return bless {};
}

=head2 start_event_loop:

Once everything is drawn, wait for an event to happen

Note that any code written after the event loop has started will not
execute until the event loop has ended (typically when the app is closing)

=cut

sub start_event_loop {
    MainLoop;
}

=head2 mw

Returns the Tk MainWindow object

=cut

sub mw {
    my $self = shift;
    return $self->{-mw};
}

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

=head2  bind_dirty_flag

Create access 'dirty_flag' (data changed since last save)

Watches the dirty_flag, and reacts accordingly when the dirty_flag changes

=cut

sub bind_dirty_flag {
    my $self = shift;
    $Dirty_flag_ptr = shift;

    # watch Dirty_flag and change the dirty_flag_text whenever
    # the dirty_flag changes
    Tie::Watch->new(
        -variable => $Dirty_flag_ptr,
        -store    => sub {
            my $self = shift;
            if   ($$Dirty_flag_ptr) { $Dirty_flag_text = "NOT SAVED"; }
            else                    { $Dirty_flag_text = ""; }
            $self->Store();
        }
    );

}

=head2 define_exit_callback

If the exit callback is defined, it will be executed just prior to the
call to "exit"

=cut

sub define_exit_callback {
    my $self = shift;
    $exit_callback = shift || sub { return };
}

# ============================================================================

=head1 METHODS TO CREATE THE GUI

=head2 create_main_window

Creates the main window

=cut

sub create_main_window {
    my $self = shift;

    # create the main window and frames
    $mw = MainWindow->new();
    $mw->Frame( -height => $Main_frame_height )->pack( -side => 'left' );
    $mw->geometry( $Welcome_height . "x" . $Welcome_width );

    # when clicking the 'x' in the corner of the window, call _exit_schedule
    $mw->protocol( 'WM_DELETE_WINDOW', \&_exit_schedule );

    # colours and fonts
    FontsAndColoursTk->setup($mw);
    $Fonts = FontsAndColoursTk->Fonts;
    $Colours = FontsAndColoursTk->Colours;

    $self->{-mw} = $mw;
}

=head2 create_menu_and_toolbars

Creates the menu and toolbars based on the information passed in by the
   presenter.
   
B<Parameters>

- buttons => a list of buttons to create on the toolbar

- actions => a hash of: 

=over

- action_name => a hash of:

=over

- code => callback if action is instegated (button press, etc)

- hint => text describing what the action is

=back

=back

- menu => a list of  lists organizing actions into a menu bar

Example: L<https://docstore.mik.ua/orelly/perl3/tk/ch12_02.htm>

    my $menu = [
        [
           cascade=>"Print", -tearoff=>0,
           -menuitems => [
              [
                 "command", "Print Hello",
                 -accelerator => "Ctrl-n",
                 -command     => sub {print "hello\n";},
              ],
              [
                 "command", "Say Goodbye",
                 -accelerator => "Ctrl-o",
                 -command     => sub {print "goodbye\n";},
              ],
        ],
        [
           cascade=>"Other", -tearoff=>0,
           -menuitems => [ ... ]
       ],
    ];


=cut 

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
    $mw->bind( '<Control-Key-e>', \&_exit_schedule );

    # if darwin, also bind the 'command' key for MAC users
    if ( $^O =~ /darwin/ ) {
        $mw->bind( '<Meta-Key-o>', $actions->{open}{code} );
        $mw->bind( '<Meta-Key-s>', $actions->{save}{code} );
        $mw->bind( '<Meta-Key-n>', $actions->{new}{code} );
        $mw->bind( '<Meta-Key-e>', \&_exit_schedule );
    }
}

=head2 create_status_bar

Create a status bar for current filename, and for the dirty pointer text

B<Parameters>

- current_filename_ptr => pointer to a scalar containing the current filename

=cut

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

=head2 create_front_page

Creates the very first page that is shown to the user

=cut

sub create_front_page {
    my $self                   = shift;
    my $Preferences            = shift;
    my $open_schedule_callback = shift;
    my $new_schedule_callback  = shift;

    my $button_width    = 50;
    my $short_file_name = 25;

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
        my $file     = $Preferences->{-current_file};
        my $basename = basename($file);
        if ( length($basename) > $short_file_name ) {
            $basename =
              "(...) " . substr( $basename, -$short_file_name );
        }

        $option_frame->Button(
            -text        => "Open $basename",
            -justify     => 'right',
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
            _create_standard_page();
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
            $open_schedule_callback->( $Preferences->{-current_file} );
        },
        -width  => $button_width,
        -height => 3,
    )->pack( -side => 'top', -fill => 'y', -expand => 0 );

    $option_frame->Frame( -bg => $Colours->{DataBackground} )->pack(
                                                                -expand => 1,
                                                                -fill => 'both',
    );
}

sub _create_standard_page {
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

=head2 define_notebook_tabs

Define which tabs should be created in this application, and
what functions should be called whenever a particular tab is opened

=B<Parameters>
    
- a list of NoteBookPage objects, defining the name of the page, and the function
that is called when this page is brought to focus (raised)

=cut

sub define_notebook_tabs {
    my $self = shift;
    $Required_notebook_tabs = shift;
}

=head2 get_notebook_page (page_name)

=cut

sub get_notebook_page {
    my $self = shift;
    my $page = shift;
    return $Pages{ lc($page) };
}

# ============================================================================

=head1 METHODS FOR RESPONDING TO CHANGES

=head2 update_for_new_schedule_and_show_page:

A new schedule has been read, reset the gui accordingly

=cut

sub update_for_new_schedule_and_show_page {
    my $self         = shift;
    my $default_page = shift;

    # remove any previous gui->views
    $views_manager->destroy_all;

    # if Notebook has already been created
    # (it is created in _create_standard_page)
    if ($Notebook) {
        $Notebook->raise( lc($default_page) );

        # the raisecmd isn't invoked if the page is already being shown
        # ... hack to get the callback routine to be called regardless
        my $tk_callback = $Notebook->pagecget( lc($default_page), -raisecmd );
        my @tk_callback_array = @$tk_callback;
        my $cmd               = shift @tk_callback_array;
        $cmd->(@tk_callback_array);

        # not sure how to call the raisecmd for the page directly
        # $Pages{ lc($default_page) }->Callback(-raisecmd);
        # $Notebook->Callback(lc($default_page),-raisecmd);
    }

    # Create the standard pages (notebooks, etc)
    else {
        $Front_page_frame->packForget();
        _create_standard_page();
    }

}

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
        my $self             = shift;
        my $default_tab      = shift;
        my $all_scheduables = shift || [];
        my $btn_callback     = shift || sub { return; };

        my $f = $Pages{ lc($default_tab) };

        $views_manager->gui->reset_button_refs();

        $frame->destroy if $frame;

        $frame = $f->Frame->pack( -expand => 1, -fill => 'both' );

        foreach my $scheduables_by_type (@$all_scheduables) {
            my $view_choices_frame =
              $frame->LabFrame( -label => $scheduables_by_type->title, )
              ->pack( -expand => 1, -fill => 'both' );

            my $view_choices_scrolled_frame =
              $view_choices_frame->Scrolled( 'Frame', -scrollbars => "osoe" )
              ->pack( -expand => 1, -fill => 'both' );

            $views_manager->gui->create_buttons_for_frame(
                   $view_choices_scrolled_frame, $scheduables_by_type, $btn_callback );
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
        _draw_overview_course($course_text);
        _draw_overview_teacher($teacher_text);

    }

}

{
    my $tbox;

    # Draw Course Overview
    sub _draw_overview_course {
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

# Draw Teacher Overview

{
    my $tbox;

    sub _draw_overview_teacher {
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

# ============================================================================

=head1 STANDARD GUI DIALOG BOXES

=head2 choose_existing_file:

Pick an existing file,

B<Parameters>

- current_directory => initial directory to start searching

- filetypes => an array of arrays of filetypes to show.

Ex: C<[ [ "Schedules", ".yaml" ], [ "All Files", "*" ] ]>

B<Returns>

Selected file (if no file selected, Returns an empty string

=cut

sub choose_existing_file {
    my $self              = shift;
    my $current_directory = shift;
    my $filetypes         = shift;
    my $file = $mw->getOpenFile( -initialdir => $current_directory,
                                 -filetypes  => $filetypes );
    return $file;
}

=head2 show_error

B<Parameters>

- title

- message to display

=cut

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

=head2 choose_file:

Pick an existing file, or define your own

B<Parameters>

- initial directory to start searching

- an array of arrays of filetypes to show.

Example: C<[ [ "Schedules", ".yaml" ], [ "All Files", "*" ] ]>

B<Returns>

Selected file (if no file selected, returns an empty string)

=cut

sub choose_file {
    my $self              = shift;
    my $current_directory = shift;
    my $filetypes         = shift;
    my $file = $mw->getSaveFile( -initialdir => $current_directory,
                                 -filetypes  => $filetypes, );
    return $file;
}

=head2 show_info

Show info to user

B<Parameters>

- title
- message to show user

=cut

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

=head2 question:

Ask a user a question

B<Parameters>

- title

- msg => question to ask the user

B<Returns>

- a scalar (Yes|No|Cancel)

=cut

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

=head2 wait_for_it

Asks user to please wait while something is in progress

B<Parameters>

- title

- message

=head2 stop_waiting:

Remove the wait message

=cut

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

# ==================================================================
# _exit_schedule
# ==================================================================
sub _exit_schedule {
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

1;
