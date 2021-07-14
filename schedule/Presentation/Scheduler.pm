#!/usr/bin/perl
use strict;
use warnings;

package Scheduler;

# ==================================================================
# This is the main entry point for the Scheduler Program
# ==================================================================

# uses MVP protocol, so the GUI must be implement the methods, etc
# defined in SchedulerManagerViewInterface.pm

# ==================================================================
# Required libraries
# ==================================================================
use FindBin;    # find which directory this executable is in
use lib "$FindBin::Bin/../";
use lib "$FindBin::Bin/../Library";
our $BinDir = "$FindBin::Bin/../";

use YAML;       # read / write YAML files
$YAML::LoadBlessed = 1;    # reads and process perl objects from the YAML file
use Cwd 'abs_path';        # get absolute path from relative path
use File::Basename;        # separate path into directory and filename

# libraries included with this source
use Schedule::Schedule;    # the Model (Schedule data)
use Export::PDF;           # write PDF schecdules
use Export::Latex;         # write Latex schedules
use Export::CSV;           # write CSV schedules
use GUI::SchedulerTk;      # gui code
use Presentation::ViewsManager;
use Presentation::DataEntry;
use Presentation::EditCourses;
use SharedData;
use GUI::FontsAndColoursTk;

# ==================================================================
# global vars
# ==================================================================
my $User_base_dir;
my $Preferences = {};
my $Schedule;                 # the current schedule
my $Current_schedule_file;    # will save to this file...
                              # ... when save is requested
my $Current_directory = $Preferences->{-current_dir} || $User_base_dir;
my $Filetypes = [ [ "Schedules", ".yaml" ], [ "All Files", "*" ] ];
my $Dirtyflag;
my $Gui;
my $Views_manager;

# ==================================================================
# external.  Defined in SharedData.pm
# ==================================================================
our %Pages_lookup;

# ==================================================================
# main
# ==================================================================
sub main {
    $Gui = SchedulerTk->new();

    foreach my $method (@Scheduler::SchedulerManagerGui_methods) {
        unless ( $Gui->can($method) ) {
            die("You gui class does not contain method ($method)");
        }
    }
    get_user_preferences();
    create_main_window();
    pre_process_stuff();
    $Gui->start_event_loop();
}

# ==================================================================
# user preferences saved in ini file (YAML format)
# ==================================================================
sub get_user_preferences {

    # where to find the ini file?
    if ( $^O =~ /darwin/i ) {    # Mac OS linux
        $User_base_dir = $ENV{"HOME"};
    }
    elsif ( $^O =~ /win/i ) {
        $User_base_dir = $ENV{"USERPROFILE"};
    }
    else {
        $User_base_dir = $ENV{"HOME"};
    }

    # read it already!
    read_ini();
}

# ==================================================================
# Create the mainWindow
# ==================================================================
sub create_main_window() {
    $Gui->create_main_window();
    my ( $toolbar_buttons, $button_properties, $menu ) = menu_info();
    $Gui->create_menu_and_toolbars( $toolbar_buttons, $button_properties,
        $menu );
    $Gui->create_front_page( $Preferences, \&open_schedule, \&new_schedule );
    $Gui->create_status_bar( \$Current_schedule_file );
}

# ==================================================================
# pre-process procedures
# ==================================================================
sub pre_process_stuff {
    $Gui->bind_dirty_flag( \$Dirtyflag );
    $Gui->define_notebook_tabs( \@Scheduler::Required_pages );

    $Gui->define_exit_callback( \&exit_schedule );

    # create the  (which shows all the schedule views etc.)
    $Views_manager = ViewsManager->new( $Gui, \$Dirtyflag, \$Schedule );
    $Gui->set_views_manager($Views_manager);
}

# ==================================================================
# read_ini
# ==================================================================
sub read_ini {

    if ( $User_base_dir && -e "$User_base_dir/.schedule" ) {
        local $/ = undef;
        open my $fh, "<", "$User_base_dir/.schedule" or return;
        eval { $Preferences = Load(<$fh>) };
        close $fh;
    }
}

# ==================================================================
# write_ini
# ==================================================================
sub write_ini {

    # open file
    open my $fh, ">", "$User_base_dir/.schedule" or return;

    # print YAML output
    $Preferences->{-current_dir}  = $Current_directory;
    $Preferences->{-current_file} = '';
    if ($Current_schedule_file) {
        $Preferences->{-current_file} = abs_path($Current_schedule_file);
    }
    eval { print $fh Dump($Preferences); };

    # finish up
    close $fh;
}

# ==================================================================
# define what goes in the menu and toolbar
# ==================================================================
sub menu_info {

    # ----------------------------------------------------------
    # button names
    # ----------------------------------------------------------
    my @buttons = ( 'new', 'open', 'CSVimport', 'save', );

    # ----------------------------------------------------------
    # actions with callback and hints
    # ----------------------------------------------------------
    my %actions = (
        new => {
            code => \&new_schedule,
            hint => 'Create new Schedule File',
        },
        open => {
            code => \&open_schedule,
            hint => 'Open Schedule File',
        },
        CSVimport => {
            code => \&import_schedule,
            hint => 'Import Schedule from CSV'
        },
        CSVexport => {
            code => \&save_as_csv,
            hint => 'Save entire schedule as a CSV'
        },
        pdf_teachers => {
            code => [ \&print_views, 'PDF', 'teacher' ],
            hint => 'Print to pdf of Teacher Schedules',
        },
        pdf_streams => {
            code => [ \&print_views, 'PDF', 'stream' ],
            hint => 'Print to pdf of Stream Schedules',
        },
        pdf_labs => {
            code => [ \&print_views, 'PDF', 'lab' ],
            hint => 'Print to pdf of Lab Schedules',
        },
        pdf_text => {
            code => [ \&print_views, 'PDF', 'text' ],
            hint => 'Text output of schedules (good for registrar)',
        },
        latex_teachers => {
            code => [ \&print_views, 'Latex', 'teacher' ],
            hint => 'Print to pdf of Teacher Schedules',
        },
        latex_streams => {
            code => [ \&print_views, 'Latex', 'stream' ],
            hint => 'Print to pdf of Stream Schedules',
        },
        latex_labs => {
            code => [ \&print_views, 'Latex', 'lab' ],
            hint => 'Print to pdf of Lab Schedules',
        },
        latex_text => {
            code => [ \&print_views, 'Latex', 'text' ],
            hint => 'Text output of schedules (good for registrar)',
        },
        save => {
            code => \&save_schedule,
            hint => "Save Schedule File",
        },
    );

    # ----------------------------------------------------------
    # menu structure
    # ----------------------------------------------------------
    my $menu = [
        [
            qw/cascade File -tearoff 0 -menuitems/,
            [
                [
                    "command", "~New",
                    -accelerator => "Ctrl-n",
                    -command     => $actions{new}{code},
                ],
                [
                    "command", "~Open",
                    -accelerator => "Ctrl-o",
                    -command     => $actions{open}{code}
                ],
                [
                    "command", "~Import CSV", -command => $actions{import}{code}
                ],
                'separator',
                [
                    "command", "~Save",
                    -accelerator => "Ctrl-s",
                    -command     => $actions{save}{code}
                ],
                [ "command", "Save As", -command => \&save_as_schedule ],
                [
                    "command", "Save As CSV",
                    -command => $actions{CSVexport}{code}
                ],
                'separator',
                [
                    "command", "~Exit",
                    -accelerator => "Ctrl-e",
                    -command     => \&exit_schedule
                ],

            ],
        ],
        [
            qw/cascade Print -tearoff 0 /,
            -menuitems => [
                [
                    qw/cascade PDF -tearoff 0/,
                    -menuitems => [
                        [
                            "command",
                            "Teacher Schedules",
                            -command => $actions{pdf_teachers}{code},
                        ],
                        [
                            "command",
                            "Lab Schedules",
                            -command => $actions{pdf_labs}{code},
                        ],
                        [
                            "command",
                            "Stream Schedules",
                            -command => $actions{pdf_streams}{code},
                        ],
                        'separator',
                        [
                            "command", "Text Output",
                            -command => $actions{pdf_text}{code},
                        ],
                    ],
                ],
                [
                    qw/cascade Latex -tearoff 0/,
                    -menuitems => [
                        [
                            "command",
                            "Teacher Schedules",
                            -command => $actions{latex_teachers}{code},
                        ],
                        [
                            "command",
                            "Lab Schedules",
                            -command => $actions{latex_labs}{code},
                        ],
                        [
                            "command",
                            "Stream Schedules",
                            -command => $actions{latex_streams}{code},
                        ],
                        'separator',
                        [
                            "command", "Text Output",
                            -command => $actions{latex_text}{code},
                        ],
                    ],
                ],
                [
                    qw/cascade CSV -tearoff 0/,
                    -menuitems => [
                        [
                            "command",
                            "Save schedule as CSV",
                            -command => $actions{CSVexport}{code},
                        ],
                    ],
                ],
            ],
        ],
    ];

    return \@buttons, \%actions, $menu;

}

# ==================================================================
# new_schedule
# ==================================================================
sub new_schedule {

    # TODO: save previous schedule?
    $Schedule = Schedule->new();
    undef $Current_schedule_file;

    _schedule_file_changed(undef);

}

# ==================================================================
# open_schedule
# ==================================================================
sub open_schedule {

    my $file = shift;

    # get file to open
    unless ( $file && -e $file ) {
        $file = "";
        $file = $Gui->choose_existing_file( $Current_directory, $Filetypes );
    }

    # if user has chosen file...
    if ($file) {

        # get YAML input of file
        eval { $Schedule = Schedule->read_YAML($file) };
        if ( $@ || !$Schedule ) {
            $Gui->show_error( 'Read Schedule',
                "Cannot read schedule\nERROR:$@" );
            undef $file;
        }
    }

    # if schedule successfully read, then
    _schedule_file_changed($file);
}

# ==================================================================
# import_schedule from CSV
# ==================================================================
sub import_schedule {
    my $file = shift;

    # get file to open
    unless ( $file && -e $file ) {
        $file = "";
        $file =
          $Gui->choose_existing_file( $Current_directory,
            [ [ 'Comma Separated Value', '.csv' ], [ 'All', '*' ] ] );
    }

    # if user has chosen file...
    if ($file) {

        # get CSV input of file
        eval { $Schedule = CSV->import_csv($file) };
        if ( $@ || !$Schedule ) {
            $Gui->show_error( 'Read Schedule', "Cannot read CSV\nERROR:$@" );
            undef $file;
        }
    }

    # if schedule successfully read, then
    _schedule_file_changed($file);
}

# ==================================================================
# schedule file has changed
# ==================================================================
sub _schedule_file_changed {
    my $file = shift;

    if ( $file && $Schedule ) {
        $Current_schedule_file = abs_path($file);
        $Current_directory     = dirname($file);
        write_ini();
    }

    # update for new schedule
    $Gui->update_for_new_schedule_and_show_page(
        $Scheduler::Pages_lookup{Schedules}->name );

    $Dirtyflag = 0;
    return;
}

# ==================================================================
# save (as) schedule
# ==================================================================
sub save_schedule {
    _save_schedule(0);
}

sub save_as_schedule {
    _save_schedule(1);
}

sub _save_schedule {
    my $save_as = shift;

    # There is no schedule to save!
    unless ($Schedule) {
        $Gui->show_error( "Save Schedule", "There is no schedule to save!" );
        return;
    }

    # get file to save to
    my $file;
    if ( $save_as || !$Current_schedule_file ) {
        $file = $Gui->choose_file( $Current_directory, $Filetypes );

        return unless $file;
    }
    else {
        $file = $Current_schedule_file;
    }

    # save YAML output of file
    eval { $Schedule->write_YAML($file) };
    if ($@) {
        $Gui->show_error( 'Save Schedule', "Cannot save schedule\nERROR:$@" );
        return;
    }

    # save the current file info for later use
    $Current_schedule_file = abs_path($file);
    $Current_directory     = dirname($file);
    $Dirtyflag             = 0;
    write_ini();
    return;

}

# ==================================================================
# save as CSV
# ==================================================================

sub save_as_csv {

    unless ($Schedule) {
        $Gui->show_error( 'Save Schedule', 'There is no schedule to save!' );
    }
    my $file = $Gui->choose_file( $Current_directory,
        [ [ 'Comma Separated Value', '.csv' ], [ 'All', '*' ] ] );
    return unless $file;

    # if the user didn't provide the .csv extension
    $file .= ".csv" if ( $file !~ /\.csv$/ );

    my $csv = CSV->new( -output_file => $file, -schedule => $Schedule );
    $csv->export();
    $Gui->show_info( "Export", "File $file was created" );

}

# ==================================================================
# update_choices_of_schedulable_views
# (what teachers/labs/streams) can we create schedules for?
# ==================================================================

sub update_choices_of_schedulable_views {

    my $btn_callback     = $Views_manager->get_create_new_view_callback;
    my $all_view_choices = $Views_manager->get_all_scheduables();
    my $page_name        = $Scheduler::Pages_lookup{Schedules}->name;
    $Gui->draw_view_choices( $page_name, $all_view_choices, $btn_callback );

    $Views_manager->determine_button_colours($all_view_choices);
}

# ==================================================================
# update_overview
# A text representation of the schedules
# ==================================================================
sub update_overview {

    # ------------------------------------------------------------------------
    # course info
    # ------------------------------------------------------------------------
    my @course_text;
    if ($Schedule) {
        unless ( $Schedule->all_courses ) {
            push @course_text, 'No courses defined in this schedule';
        }
        else {
            foreach my $c ( sort { $a->number cmp $b->number }
                $Schedule->all_courses )
            {
                push @course_text, $c;
            }
        }
    }
    else {
        push @course_text, 'There is no schedule, please open one';
    }

    # ------------------------------------------------------------------------
    # teacher info
    # ------------------------------------------------------------------------

    my @teacher_text;

    # if schedule, show info
    if ($Schedule) {
        unless ( $Schedule->all_teachers ) {
            push @teacher_text, 'No teachers defined in this schedule';
        }
        else {
            foreach my $t ( sort { lc( $a->lastname ) cmp lc( $b->lastname ) }
                $Schedule->all_teachers )
            {
                push @teacher_text, $Schedule->teacher_details($t);
            }
        }
    }
    else {
        push @teacher_text, 'There is no schedule, please open one';
    }

    $Gui->draw_overview( "Overview", \@course_text, \@teacher_text );

}

# ==================================================================
# update_edit_teachers
# - A page where teachers can be added/modified or deleted
# ==================================================================
{
    my $de;
    {

        sub update_edit_teachers {

            my $notebook_page =
              $Gui->get_notebook_page(
                $Scheduler::Pages_lookup{Teachers}->name );
            if ($de) {
                $de->refresh( $Schedule->teachers );
            }
            else {
                $de = DataEntry->new( $notebook_page, $Schedule->teachers,
                    $Schedule, \$Dirtyflag, $Views_manager );
            }
        }
    }
}

# ==================================================================
# draw_edit_streams
# - A page where streams can be added/modified or deleted
# ==================================================================
{
    my $de;

    sub update_edit_streams {

        my $f =
          $Gui->get_notebook_page( $Scheduler::Pages_lookup{Streams}->name );
        if ($de) {
            $de->refresh( $Schedule->streams );
        }
        else {
            $de =
              DataEntry->new( $f, $Schedule->streams, $Schedule, \$Dirtyflag,
                $Views_manager );
        }
    }

}

# ==================================================================
# update_edit_labs
# - A page where labs can be added/modified or deleted
# ==================================================================
{
    my $de;
    {

        sub update_edit_labs {

            my $f =
              $Gui->get_notebook_page( $Scheduler::Pages_lookup{Labs}->name );
            if ($de) {
                $de->refresh( $Schedule->labs );
            }
            else {
                $de = $de =
                  DataEntry->new( $f, $Schedule->labs, $Schedule, \$Dirtyflag,
                    $Views_manager );
            }

        }
    }
}

# ==================================================================
# draw_edit_courses
# - A page where courses can be added/modified or deleted
# ==================================================================
sub update_edit_courses {
    my $self = shift;
    my $f = $Gui->get_notebook_page( $Scheduler::Pages_lookup{Courses}->name );
    EditCourses->new( $f, $Schedule, \$Dirtyflag, $Views_manager );
}

# ==================================================================
# print_views
# - print the schedule 'views'
# - type defines the output type, PDF, Latex
# ==================================================================

sub print_views {
    my $print_type = shift;
    my $type       = shift;

    # --------------------------------------------------------------
    # no schedule yet
    # --------------------------------------------------------------
    unless ($Schedule) {
        $Gui->show_error( "Export", "Cannot export - There is no schedule" );
    }

    # --------------------------------------------------------------
    # cannot print if the schedule is not saved
    # --------------------------------------------------------------
    if ($Dirtyflag) {
        my $ans = $Gui->question( "Unsaved Changes",
            "There are unsaved changes\n" . "Do you want to save them?" );
        if ( $ans eq 'Yes' ) {
            save_schedule();
        }
        else {
            return;
        }
    }

    # --------------------------------------------------------------
    # define base file name
    # --------------------------------------------------------------
    my $file = $Current_schedule_file;
    $file =~ s/\.yaml$//;
    $Gui->wait_for_it( "Printing", "Please wait while we process the files" );

    # -------------------------------------------------------------------
    # text overview
    # -------------------------------------------------------------------
    if ( lc($type) eq "text" ) {
        $print_type->newReport( $Schedule, $file . "_text" );
    }

    # -------------------------------------------------------------------
    # views
    # -------------------------------------------------------------------
    else {
        my @objs;

        @objs = $Schedule->all_teachers() if lc($type) eq "teacher";
        @objs = $Schedule->all_streams()  if lc($type) eq "stream";
        @objs = $Schedule->all_labs()     if lc($type) eq "lab";

        foreach my $obj (@objs) {
            $print_type->newView( $Schedule, $obj, $file . "_$type" . " $obj" );
        }
    }

    $Gui->stop_waiting();
    $Gui->show_info( "Export", "$type $print_type views created\n$file*.pdf" );

    return;
}

# ==================================================================
# exit_schedule
# ==================================================================
sub exit_schedule {
    save_schedule();
    write_ini();
}

1;
