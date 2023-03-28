use strict;
use warnings;

package AllocationManagerTk;
use FindBin;
use lib "$FindBin::Bin/../";
use GUI::MainPageBaseTk;
use File::Basename;
use PerlLib::Colour;

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

# ============================================================================
# Global variables
# ============================================================================
my $open_button;            # button used to open selected files
my %files           = ();   # hash of all selected files
my %short_files     = ();   # hash of all selected files (short name)
my $short_file_name = 30;   # max length of filename displayed to user
my $Semesters;              # ptr to array of semesters


# ============================================================================

=head1 METHODS

=head2 create_front_page

Creates the very first page that is shown to the user

=cut

sub create_front_page {
    my $self        = shift;
    my $Preferences = shift;
    $Semesters = shift;
    my $open_schedules_callback = shift;
    my $current_directory = shift;
    my $filetypes         = shift;

    my $logo_file    = Tk::FindImages::get_allocation_logo();
    my $option_frame = $self->SUPER::create_front_page($logo_file);

    my $button_width = 50;
    
    my $disabled_colour = Colour->new($self->colours->{DataBackground});
    if ($disabled_colour->isLight()) {
        $disabled_colour = $disabled_colour->darken(20);
    }
    else {
        $disabled_colour = $disabled_colour->lighten(20);
    }

    # --------------------------------------------------------------
    # selected files
    # --------------------------------------------------------------
    $option_frame->Label(
        -text => "Selected_files",
        -font => $self->fonts->{bigbold},
        -bg   => $self->colours->{DataBackground}
    )->pack( -side => 'top', -fill => 'x', -expand => 0 );

    foreach my $semester (@$Semesters) {
        $option_frame->Label(
            -textvariable => \$short_files{$semester},
            -bg           => $self->colours->{DataBackground},
        )->pack( -side => 'top', -fill => 'x', -expand => 0 );
    }
    $option_frame->Label(
        -text => "\n",
        -font => $self->fonts->{bigbold},
        -bg   => $self->colours->{DataBackground}
    )->pack( -side => 'top', -fill => 'x', -expand => 0 );

    # --------------------------------------------------------------
    # choose files
    # --------------------------------------------------------------
    my $choose_frame = $option_frame->Frame()
      ->pack( -side => "top", -fill => 'x', -expand => 0 );

    foreach my $semester (@$Semesters) {

        # --------------------------------------------------------------
        # create new allocation files
        # --------------------------------------------------------------
        $choose_frame->Label(
            -text  => ucfirst($semester) . ": ",
            -anchor => "e",
            -bg    => $self->colours->{DataBackground}
          )->grid(
            $choose_frame->Button(
                -text        => "New",
                -font        => $self->fonts->{normal},
                -borderwidth => 0,
                -bg          => $self->colours->{DataBackground},
                -command     => [ \&_set_file, $semester, '-new-' ],
                -height      => 3,
            ),

            # --------------------------------------------------------------
            # open schedule file
            # --------------------------------------------------------------
            $choose_frame->Button(
                -text        => "Browse",
                -font        => $self->fonts->{normal},
                -borderwidth => 0,
                -bg          => $self->colours->{DataBackground},
                -command     => sub {
                    my $file = $self->choose_existing_file( $current_directory,
                        $filetypes );
                        _set_file($semester,$file);
                },
                -height => 3,
            ),
            -sticky => 'nsew'
          );

    }

    #--------------------------------------------------------
    # gui layout commands
    #--------------------------------------------------------

    my ( $columns, $rows ) = $choose_frame->gridSize();
    for ( my $i = 0 ; $i < $columns ; $i++ ) {
        $choose_frame->gridColumnconfigure( $i, -weight => 1 );
    }
    $choose_frame->gridRowconfigure( $rows - 1, -weight => 1 );

    $option_frame->Frame( -bg => $self->colours->{DataBackground} )->pack(
        -expand => 0,
        -fill   => 'x',
    );

    # --------------------------------------------------------------
    # make button for opening selected files
    # --------------------------------------------------------------
    my $text = "Open Selected Files";
    $open_button = $option_frame->Button(
        -text               => $text,
        -font               => $self->fonts->{big},
        -borderwidth        => 0,
        -bg                 => $self->colours->{DataBackground},
        -command            => [ $open_schedules_callback, \%files ],
        -width              => $button_width,
        -height             => 3,
        -disabledforeground => $disabled_colour,
    )->pack( -side => 'top', -fill => 'x', -expand => 0 );

    # --------------------------------------------------------------
    # set selected files to those in the preference file
    # --------------------------------------------------------------
    foreach my $semester (@$Semesters) {
        _set_file( $semester,
            $Preferences->{ "-current_$semester" . "_file" } );
    }

}

# ============================================================================
# a file has been chosen.  Adjust gui as appropriate
# ============================================================================
sub _set_file {
    my $semester = shift;
    my $file = shift || '';

    undef $files{$semester};
    undef $short_files{$semester};
    my $basename = basename($file);

    if ( -e $file || $basename eq '-new-' ) {
        $files{$semester} = $file;
        if ( length($basename) > $short_file_name ) {
            $short_files{$semester} =
              "(...) " . substr( $basename, -$short_file_name );
        }
        else {
            $short_files{$semester} = $basename;
        }
    }
    _all_files_chosen();
}

# ============================================================================
# disable or enable the 'open' button depending if all semester files 
# have been chosen
# ============================================================================
sub _all_files_chosen {
    my $enable_flag = "normal";
    foreach my $semester (@$Semesters) {
        $enable_flag = "disabled" unless defined $files{$semester};
    }
    $open_button->configure( -state => $enable_flag );
}


1;
