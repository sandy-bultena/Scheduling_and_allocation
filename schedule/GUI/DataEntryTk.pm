#!/usr/bin/perl
use strict;
use warnings;

package DataEntryTk;

use FindBin;
use lib "$FindBin::Bin/..";
use Tk::TableEntry;

=head1 NAME

DataEntryTk - Enter data object  

=head1 VERSION

Version 6.00

=head1 DESCRIPTION

Basically a Tk::TableEntry object with some restrictions

=head2 Notes

The first column I<must> be a unique identifier for the corresponding data
object, and can not be edited.

=head1 PUBLIC METHODS

=cut

sub new {
    my $class         = shift;
    my $data_entry    = shift;
    my $frame         = shift;
    my $del_callback  = shift;
    my $save_callback = shift;

    my $titles     = $data_entry->col_titles;
    my $col_widths = $data_entry->col_widths;

    my $self = {};
    bless $self, $class;

    # ---------------------------------------------------------------
    # create the table entry object
    # ---------------------------------------------------------------
    my $de = $frame->TableEntry(
                                 -rows      => 1,
                                 -columns   => scalar(@$titles),
                                 -titles    => $titles,
                                 -colwidths => $col_widths,
                                 -delete    => [ $del_callback, $data_entry ],
    )->pack( -side => 'top', -expand => 1, -fill => 'both' );

    # disable the first columns, but not the rest
    my @disabled = (1);
    push @disabled, (0) x ( $de->columns - 1 );

    $de->configure( -disabled => \@disabled );

    # --------------------------------------------------------------------------
    # NOTE: If weird shit is happening, give up and use a 'Save' button
    # ... clicking the 'Delete' triggers a 'Leave'...
    # --------------------------------------------------------------------------
    $de->bind( '<Leave>', sub { $save_callback->($data_entry) } );

    # --------------------------------------------------------------------------
    # create the object
    # --------------------------------------------------------------------------
    $self->_table($de);

    return $self;

}

=head2 refresh

B<Parameters>

- data => a pointer to a 2d array containing all of the data

=cut

sub refresh {
    my $self = shift;
    my $data = shift;

    my $de = $self->_table;

    my $row = 1;
    foreach my $line (@$data) {
        my $col = 1;
        foreach my $col_data (@$line) {
            $de->put( $row, $col, $col_data );
            $col++;
        }
        $row++;
    }
    $de->add_empty_row($row);

}

=head2 get_all_data

B<Returns>

a pointer to a 2d array containing all of the data

=cut

sub get_all_data {
    my $self = shift;

    my @all_data;
    foreach my $r ( 1 .. $self->_table->rows ) {
        my @data = $self->_table->read_row($r);
        push @all_data, \@data;
    }

    return \@all_data;
}

sub _table {
    my $self = shift;
    $self->{-de} = shift if @_;
    return $self->{-de};
}

=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns

=head1 COPYRIGHT

Copyright (c) 2021, Jack Burns, Sandy Bultena, Ian Clement. 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut

1;
