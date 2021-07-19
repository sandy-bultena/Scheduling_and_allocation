#!/usr/bin/perl
use strict;
use warnings;

package AllocationManager;

# ==================================================================
# Entry point for the Gui Allocation Management Tool
# ==================================================================
use FindBin;    # find which directory this executable is in
use lib "$FindBin::Bin/../";
use lib "$FindBin::Bin/../Library";
our $BinDir = "$FindBin::Bin/../";
use Schedule::Schedule;
use Presentation::EditCourses;
use GuiSchedule::NumStudents;
use Presentation::EditAllocation;
use GUI::AllocationManagerTk;
use PerlLib::Colours;
use Presentation::DataEntry;
use UsefulClasses::NoteBookPageInfo;

use YAML;
$YAML::LoadBlessed = 1;    # default changed in YAML 1.30

use Cwd 'abs_path';
use File::Basename;

# ==================================================================
# global vars
# ==================================================================
my @Semesters = (qw(fall winter));
my %Schedules = (                    # the current schedule
    fall   => '',
    winter => ''
);
my %Current_schedule_file = (    # will save to this file when save is requested
    fall   => '',
    winter => '',
);

my $Dirtyflag;
my $Gui;

my @Required_pages;
my %Pages_lookup;

my $User_base_dir;
my $Preferences = {};
my $Current_schedule_file;    # will save to this file...
                              # ... when save is requested
my $Current_directory = $Preferences->{-current_dir} || $User_base_dir;
my $Filetypes = [ [ "Schedules", ".yaml" ], [ "All Files", "*" ] ];

# ==================================================================
# main
# ==================================================================
sub main {
    $Gui = AllocationManagerTk->new();

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
    $Gui->create_front_page( $Preferences, \@Semesters, \&open_schedules,
        $Current_directory, $Filetypes );
    $Gui->create_status_bar( \$Current_schedule_file );
}

# ==================================================================
# pre-process procedures
# ==================================================================
sub pre_process_stuff {

    $Gui->bind_dirty_flag( \$Dirtyflag );

    define_notebook_pages();
    $Gui->define_notebook_tabs( \@Required_pages );

    $Gui->define_exit_callback( \&exit_schedule );

}

# ==================================================================
# required Notebook pages
# ==================================================================
sub define_notebook_pages {

    @Required_pages = (
        NoteBookPageInfo->new( "Allocation", sub { draw_allocation() } ),
        NoteBookPageInfo->new( "Student Numbers", \&update_overview ),
    );

    # one page for each semester
    my %sub_notebook;
    foreach my $semester (@Semesters) {
        my $label = ucfirst($semester);
        $sub_notebook{$semester} = [];
        push @Required_pages, NoteBookPageInfo->new(
            $label,
            sub {
                update_edit_courses($semester);
                update_edit_teachers($semester);
            },
            $sub_notebook{$semester},
        );
    }

    # Semester Courses and Teachers
    foreach my $semester (@Semesters) {
        my $label = ucfirst($semester);

        push @{ $sub_notebook{$semester} },
          my $c = NoteBookPageInfo->new( "$label Courses",
            sub { update_edit_courses($semester); } );

        push @{ $sub_notebook{$semester} },
          my $t = NoteBookPageInfo->new( "$label Teachers",
            sub { update_edit_teachers($semester) } );

        $Pages_lookup{"$label Courses"}  = $c;
        $Pages_lookup{"$label Teachers"} = $t;
    }

    foreach my $page (@Required_pages) {
        $Pages_lookup{ $page->name } = $page;
    }
}

# ==================================================================
# define what goes in the menu and toolbar
# ==================================================================
sub menu_info {

    # ----------------------------------------------------------
    # button names
    # ----------------------------------------------------------
    my @buttons =
      ( 'new_fall', 'new_winter', 'open_fall', 'open_winter', 'save', );

    # ----------------------------------------------------------
    # what actions are associated with the menu items
    # ----------------------------------------------------------
    my %actions = (
        new_fall => {
            cb => [ \&new_schedules, 'fall' ],
            hn => 'Create new fall File',
        },
        new_winter => {
            cb => [ \&new_schedules, 'winter' ],
            hn => 'Create new winter Files',
        },
        open_fall => {
            cb => [ \&_open_schedule, "fall" ],
            hn => 'Open Fall Schedule File',
        },
        open_winter => {
            cb => [ \&_open_schedule, "winter" ],
            hn => 'Open Winter Schedule File',
        },
        save => {
            cb => \&save_schedule,
            hn => "Save Schedule Files",
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
                    "command", "New Fall",
                    -accelerator => "Ctrl-n",
                    -command     => $actions{new_fall}{cb},
                ],
                [
                    "command", "New Winter",
                    -accelerator => "Ctrl-n",
                    -command     => $actions{new_winter}{cb},
                ],
                [
                    "command", "Open Fall",
                    -accelerator => "Ctrl-o",
                    -command     => $actions{open_fall}{cb}
                ],
                [
                    "command", "Open Winter",
                    -accelerator => "Ctrl-o",
                    -command     => $actions{open_winter}{cb}
                ],
                'separator',
                [
                    "command", "~Save",
                    -accelerator => "Ctrl-s",
                    -command     => $actions{save}{cb}
                ],
                [ "command", "Save As", -command => \&save_as_schedule ],
                'separator',
                [
                    "command", "~Exit",
                    -accelerator => "Ctrl-e",
                    -command     => \&exit_schedule
                ],

            ],
        ],
    ];

    return \@buttons, \%actions, $menu;

}

# ==================================================================
# front_page_done (time to make standard page)
# ==================================================================
sub front_page_done {
    my $flag = 1;
    foreach my $semester (@Semesters) {
        $flag = 0 unless $Schedules{$semester};
    }
    if ($flag) {
        $Gui->update_for_new_schedule_and_show_page();
        $Dirtyflag = 0;
    }
}

# ==================================================================
# new_schedule
# ==================================================================
sub new_schedules {

    my $semester = shift;
    $Schedules{$semester} = Schedule->new();
    undef $Current_schedule_file{$semester};
    $Dirtyflag = 1;
    front_page_done();

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

    # --------------------------------------------------------------
    # There is no schedule to save!
    # --------------------------------------------------------------
    foreach my $semester (@Semesters) {
        unless ( $Schedules{$semester} ) {
            $Gui->show_error( "Save Schedule",
                "Missing allocation file for $semester" );
            return;
        }
    }

    my %files = ();

    foreach my $semester (@Semesters) {

        # ----------------------------------------------------------
        # get files to save to (if save (as) has been requested)
        # ----------------------------------------------------------
        if ( $save_as || !$Current_schedule_file{$semester} ) {
            $files{$semester} =
              $Gui->choose_file( $Current_directory, $Filetypes );

            # if cancel has been pressed
            return unless $files{$semester};
        }

        # ----------------------------------------------------------
        # or use current file name
        # ----------------------------------------------------------
        else {
            $files{$semester} = $Current_schedule_file{$semester};
        }

        # ----------------------------------------------------------
        # save YAML output of file
        # ----------------------------------------------------------
        eval { $Schedules{$semester}->write_YAML( $files{$semester} ) };
        if ($@) {
            $Gui->show_error( "Save Schedule",
                "Cannot save schedule\nERROR:$@" );
            return;
        }

        # ----------------------------------------------------------
        # save the current file info for later use
        # ----------------------------------------------------------
        $Current_directory = dirname( $files{$semester} );
        $Current_schedule_file{$semester} = abs_path( $files{$semester} );
    }

    # save the current file info for later use
    write_ini();

    return;

}

# ==================================================================
# open pre-defined schedules
# ==================================================================
sub open_schedules {
    my $files = shift;

    foreach my $semester (@Semesters) {
        if ( $files->{$semester} eq '-new-' ) {
            new_schedule($semester);
        }
        else {
            _open_schedule( $semester, $files->{$semester} );
        }
    }
}

# ==================================================================
# open_schedule
# ==================================================================
sub _open_schedule {

    my $semester = shift;
    my $file     = shift;

    # get file to open
    unless ( $file && -e $file ) {
        $file = "";
        $file = $Gui->choose_existing_file( $Current_directory, $Filetypes );
    }

    # if user has chosen file...
    if ($file) {

        # get YAML input of file
        eval { $Schedules{$semester} = Schedule->read_YAML($file) };
        if ( $@ || !$Schedules{$semester} ) {
            $Gui->show_error( 'Read Schedule',
                "Cannot read schedule\nERROR:$@" );
            undef $file;
        }
    }

    # if schedule successfully read, then
    if ( $file && $Schedules{$semester} ) {
        $Current_schedule_file{$semester} = abs_path($file);
        $Current_directory = dirname($file);
        write_ini();
    }

    front_page_done();
    return;
}

# ==================================================================
# exit_schedule
# ==================================================================
sub exit_schedule {

    if ($Dirtyflag) {
        my $answer = $Gui->question( "Save Schedule",
            "Do you want to save your changes?" );
        save_schedule() if $answer eq 'Yes';
        return if $answer eq 'Cancel';
    }
    write_ini();
    CORE::exit();

}

# ==================================================================
# read_ini
# ==================================================================
sub read_ini {

    if ( $User_base_dir && -e "$User_base_dir/.allocation" ) {
        local $/ = undef;
        open my $fh, "<", "$User_base_dir/.allocation" or return;
        eval { $Preferences = Load(<$fh>) };
        close $fh;
    }
    $Current_directory = $Preferences->{-current_dir} || $User_base_dir;
}

# ==================================================================
# write_ini
# ==================================================================
sub write_ini {

    # open file
    open my $fh, ">", "$User_base_dir/.allocation" or return;

    # print YAML output
    $Preferences->{-current_dir}  = $Current_directory;
    $Preferences->{-current_file} = '';
    foreach my $semester (@Semesters) {
        if ( $Current_schedule_file{$semester} ) {
            $Preferences->{ "-current_$semester" . "_file" } =
              abs_path( $Current_schedule_file{$semester} );
        }
    }
    eval { print $fh Dump($Preferences); };

    # finish up
    close $fh;
}

# ==================================================================
# update_edit_teachers
# ==================================================================

{
    my %de;

    sub update_edit_teachers {
        my $semester = shift;
        die("update_edit_courses did not specify a semester\n")
          unless $semester;

        my $label         = ucfirst($semester);
        my $notebook_page = $Pages_lookup{"$label Teachers"}->id;

        my $f = $Gui->get_notebook_page($notebook_page);

        if ( $de{$semester} ) {
            $de{$semester}->refresh( $Schedules{$semester}->teachers );
        }
        else {
            $de{$semester} =
              DataEntry->new( $f, $Schedules{$semester}->teachers,
                $Schedules{$semester}, \$Dirtyflag, undef );
        }
    }

}

# ==================================================================
# update_student_numbers
# ==================================================================

{
    my $de;

    sub update_student_numbers {
        my $notebook_page = $Pages_lookup{"Student_Numbers"}->id;
        my $f             = $Gui->get_notebook_page($notebook_page);

        if ($de) {
            $de->refresh( \%Schedules );
        }
        else {
            $de = NumStudents->new( $f, \%Schedules, \$Dirtyflag );
        }
    }
}

# ==================================================================
# update_edit_courses
# ==================================================================
sub update_edit_courses {
 
    my $semester = shift;
    my $label    = ucfirst($semester);
    die("update_edit_courses did not specify a semester\n")
      unless $semester;
      
    eval {
        my $f = $Gui->get_notebook_page( $Pages_lookup{"$label Courses"}->id );
        EditCourses->new( $f, $Schedules{$semester}, \$Dirtyflag, undef );
    };
}

# ==================================================================
# draw_allocation
# ==================================================================
{
    my $de;

    sub draw_allocation {
        my $f = $Gui->get_notebook_page( $Pages_lookup{"Allocation"}->id );
        unless ($de) {
            $de = EditAllocation->new( $f, \%Schedules, \$Dirtyflag );
        }
        else {
            $de->draw();
        }
    }

}

1;
