#!/usr/bin/perl
use strict;
use warnings;

# =================================================================
# Add sections dialog GUI
# -----------------------------------------------------------------
# Add Sections to a Course and add blocks to those sections.
# -----------------------------------------------------------------
# Inputs:
#   frame
# Returns:
#   An array of section names
#   An array of hours for each block
#   - undef if Cancelled
# Required Event Handlers:
#   -none-
# =================================================================

package AddSectionDialogTk;

use FindBin;
use Carp;
use lib "$FindBin::Bin/..";
use GUI::AddBlocksDialogTk;

my $MAX_SECTIONS = 100;

my $number_of_sections = "";
my $inputframe;

# =================================================================
# new
# =================================================================
sub new {
    my $class = shift;
    $inputframe = shift;
    my $self = bless {}, $class;
    my $number_of_sections = "";

    # ------------------------------------------------------------------------
    # Show the main dialog
    # ------------------------------------------------------------------------
    my $db_num_sections = $inputframe->DialogBox(
        -title   => 'How Many Sections',
        -buttons => [ 'Ok', 'Cancel' ],
    );
    $db_num_sections->add( 'Label',
        -text => "How Many Sections? (MAX $MAX_SECTIONS)" )->pack( -padx => 5 );

    my $number_entry = $db_num_sections->add(
        'Entry',
        -textvariable    => \$number_of_sections,
        -validate        => 'key',
        -validatecommand => \&_is_integer,
        -invalidcommand  => sub { $inputframe->bell },
    )->pack( -fill => 'x', -padx => 5 );

    $db_num_sections->configure( -focus => $number_entry );

    my $answer = "";
    $answer = $db_num_sections->Show() || "Cancel";
    $answer = "Cancel" unless $answer;
    return undef if $answer eq "Cancel";

    return $self->_process_the_sections();
}

# =================================================================
# validate that number be entered in a entry box is a whole number
# (positive integer)
# =================================================================
sub _is_integer {
    my $n = shift;
    return 1 if $n =~ /^(\s*\d+\s*|)$/;
    return 0;
}

# =================================================================
# process the sections
# =================================================================
sub _process_the_sections {
    my $self = shift;

    $number_of_sections = $MAX_SECTIONS if $number_of_sections > $MAX_SECTIONS;

    my $db_name_the_sections = $inputframe->DialogBox(
        -title   => 'Name The Sections',
        -buttons => [ 'Ok', 'Cancel' ],
    );

    # stop the dialog box from executing the default
    # button press when hitting return
    $db_name_the_sections->bind( "<Return>", sub { } );

    my $top = $db_name_the_sections->Subwidget("top");

    # frame for all the section entry boxes
    my $scrolledframe = $top->Scrolled(
        'Pane',
        -scrollbars => 'oe',
        -width      => 300,
        -height     => 300,
        -sticky     => 'nsew',
    )->pack( -expand => 1, -fill => 'both' );

    $scrolledframe->Label( -text => "Name the Sections (OPTIONAL)" )
      ->pack( -side => 'top' );
    foreach my $i ( 1 ... $number_of_sections ) {
        push( @{ $self->_section_names }, "" );
    }

    my $names = $self->_section_names;

    # create the entry boxes
    my $first_entry_box;
    foreach my $name (@$names) {

        my $x =
          $scrolledframe->Frame()->pack( -fill => 'x', -padx => 5, -pady => 5 );

        my $y = $x->Entry( -textvariable => \$name )->pack(
            -side   => 'left',
            -expand => 1,
            -fill   => 'x'
        );
        $y->bind( "<Return>",  sub { $y->focusNext; } );
        $y->bind( "<FocusIn>", sub { $scrolledframe->see($y) } );

        $first_entry_box = $y unless $first_entry_box;
    }

    # layout
    $scrolledframe->Label( -text => "", )
      ->pack( -expand => 1, -fill => 'both' );

    $db_name_the_sections->configure( -focus => $first_entry_box );

    # show the dialog box
    my $answer = "";
    $answer = $db_name_the_sections->Show() || $answer;
    return undef if $answer eq 'Cancel';

    my $new_blocks = AddBlocksDialogTk->new($inputframe);
    return $self->_section_names, $new_blocks;
}

# =================================================================
# names of sections to add
# =================================================================
sub _section_names {
    my $self = shift;
    $self->{-section_names} = shift if @_;
    $self->{-section_names} = [] unless $self->{-section_names};
    return $self->{-section_names};
}

1;
