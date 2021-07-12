#!/usr/bin/perl
use strict;
use warnings;

package AddSectionDialogTk;
my $MAX_SECTIONS = 100;
my $MAX_BLOCK    = 10;

my $number_of_sections = "";
my $number_of_blocks   = "";
my $inputframe;

#==========================================================
# Add Sections to a Course and add blocks to those sections.
#
# This code has three separate dialog boxes that are called
# one after the other.
# They are chained together, so at anytime, if Cancel is
# pressed on anyone of the dialog boxes, it treats it as
# if the whole thing has been canceled
#==========================================================

# ----------------------------------------------------------------------------
# new
# ----------------------------------------------------------------------------
sub new {
    my $class = shift;
    $inputframe = shift;
    my $course_id = shift;
    die "Cannot use AddSectionDialog without a valid course_id\n"
      unless $course_id;
    my $self = bless {}, $class;
    $self->course_id($course_id);

    return $self;
}

# ----------------------------------------------------------------------------
# Show the main dialog
# ----------------------------------------------------------------------------
sub Show {
    my $self            = shift;
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
        -validatecommand => \&is_integer,
        -invalidcommand  => sub { $inputframe->bell },
    )->pack( -fill => 'x', -padx => 5 );

    $db_num_sections->configure( -focus => $number_entry );

   my $answer = "";
    $answer = $db_num_sections->Show() || "Cancel";
    $answer = "Cancel" unless $answer;
    return $answer if $answer eq "Cancel";

    return $self->_process_the_sections();
}

# ----------------------------------------------------------------------------
# callback (when user says 'Ok')
# ----------------------------------------------------------------------------
sub cb_add_sections_with_blocks {
    print "defining add section with blocks: @_\n";
    my $self = shift;
    $self->{-add_section_with_blocks} = shift if @_;
    $self->{-add_section_with_blocks} =
      sub { print "<cb_add_section_with_blocks> Not implemented\n"; }
      unless $self->{-add_section_with_blocks};
    return $self->{-add_section_with_blocks};
}

# ----------------------------------------------------------------------------
# names of sections to add
# ----------------------------------------------------------------------------
sub section_names {
    my $self = shift;
    $self->{-section_names} = shift if @_;
    $self->{-section_names} = [] unless $self->{-section_names};
    return $self->{-section_names};
}

# ----------------------------------------------------------------------------
# hours per block to add to each section
# ----------------------------------------------------------------------------
sub block_hours {
    my $self = shift;
    $self->{-block_hours} = shift if @_;
    $self->{-block_hours} = [] unless $self->{-block_hours};
    return $self->{-block_hours};
}

# ----------------------------------------------------------------------------
# course_id
# ----------------------------------------------------------------------------
sub course_id {
    my $self = shift;
    $self->{-course_id} = shift if @_;
    return $self->{-course_id};
}

# ----------------------------------------------------------------------------
# process the sections
# ----------------------------------------------------------------------------
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
        push( @{ $self->section_names }, "" );
    }
    my $names = $self->section_names;

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
    return $answer if $answer eq 'Cancel';

    return $self->_process_blocks();
}

# ----------------------------------------------------------------------------
# process the blocks
# ----------------------------------------------------------------------------
sub _process_blocks {
    my $self = shift;

    my $db_num_blocks = $inputframe->DialogBox(
        -title          => 'How Many Blocks',
        -buttons        => [ 'Ok', 'Cancel' ],
        -default_button => 'Ok',
    );

    $db_num_blocks->add( 'Label', -text => "How Many Blocks? (MAX $MAX_BLOCK)" )
      ->pack;

    my $block_num_entry = $db_num_blocks->add(
        'Entry',
        -textvariable    => \$number_of_blocks,
        -validate        => 'key',
        -validatecommand => \&is_integer,
        -invalidcommand  => sub { $inputframe->bell },
        -width           => 20,
    )->pack( -fill => 'x' );
    my $answer = "";

    $db_num_blocks->configure( -focus => $block_num_entry );

    $answer = $db_num_blocks->Show() || "Cancel";
    return $answer if $answer eq 'Cancel';

    return $self->_process_block_hours();

}

# ----------------------------------------------------------------------------
# how many hours per block?
# ----------------------------------------------------------------------------
sub _process_block_hours {
    my $self = shift;
    $number_of_blocks = $MAX_BLOCK if $number_of_blocks > $MAX_BLOCK;

    if ($number_of_blocks) {
        my $db_block_hours = $inputframe->DialogBox(
            -title          => 'How Many Hours',
            -buttons        => [ 'Ok', 'Cancel' ],
            -default_button => 'Ok',
        );

        my $top = $db_block_hours->Subwidget("top");

        $top->Label( -text => "How Many Hours Per Block?" )
          ->grid( -columnspan => 2 );
        foreach my $i ( 1 ... $number_of_blocks ) {
            push @{ $self->block_hours }, "";
        }

        # stop the dialog box from executing the
        # default button press when hitting return
        $db_block_hours->bind( "<Return>", sub { } );

        my $first_entry;
        my $hrs   = $self->block_hours;
        my $index = 1;
        foreach my $hour (@$hrs) {
            my $label = $top->Label( -text => "Block $index" );
            my $entry = $top->Entry(
                -textvariable    => \$hour,
                -validate        => 'key',
                -validatecommand => \&is_number,
                -invalidcommand  => sub { $inputframe->bell },
            );
            $first_entry = $entry unless $first_entry;
            $label->grid( $entry, -sticky => 'new' );
            $entry->bind( "<Return>", sub { $entry->focusNext; } );
            $index++;
        }

        # layout
        my ( $col, $row ) = $top->gridSize();
        for ( my $i = 1 ; $i < $col ; $i++ ) {
            $top->gridColumnconfigure( $i, -weight => 1 );
        }
        $top->gridRowconfigure( $row - 1, -weight => 1 );

        my $answer = "";

        $db_block_hours->configure( -focus => $first_entry );

        # show dialog box
        $answer = $db_block_hours->Show() || "Cancel";
        return $answer if $answer eq 'Cancel';

        $self->cb_add_sections_with_blocks->(
            $self->course_id, $self->section_names, $self->block_hours
        );
        return "Ok";
    }
}

# =================================================================
# validate that number be entered in a entry box is a whole number
# (positive integer)
# =================================================================
sub is_integer {
    my $n = shift;
    return 1 if $n =~ /^(\s*\d+\s*|)$/;
    return 0;
}

# =================================================================
# validate that number be entered in a entry box is a real number
# (positive real number)
# =================================================================
sub is_number {
    my $n = shift;
    return 1 if $n =~ (/^(\s*\d*\.?\d*\s*|)$/);
    return 0;
}

1;
