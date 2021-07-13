#!/usr/bin/perl
use strict;
use warnings;

package AddBlocksDialogTk;

use FindBin;
use Carp;
use lib "$FindBin::Bin/..";

my $MAX_BLOCK    = 10;
my $inputframe;
my $number_of_blocks;

# ----------------------------------------------------------------------------
# process the blocks
# ----------------------------------------------------------------------------
sub new {
    my $class = shift;
    $inputframe = shift;
    my $self = bless {}, $class;

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
    return undef if $answer eq 'Cancel';

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
        return undef if $answer eq 'Cancel'; 
               
        return $self->block_hours;
    }
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