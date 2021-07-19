#!/usr/bin/perl
use strict;
use warnings;

# ============================================================================
# ScheduablesByType class
# - defines the data for what views are available
# ... NOTE: A view is a visual representation of a schedule for a specific
#           teacher, lab or stream
# ============================================================================
package ScheduablesByType;
use FindBin;    # find which directory this executable is in
use lib "$FindBin::Bin/../";
use UsefulClasses::NamedObjects;

sub new {
    my $class           = shift;
    my $type            = shift; # what type of scheduables are these?
    my $title           = shift; # title of this collection of scheduables
    my $names           = shift; # array of names used for each $schedule_object
    my $scheduable_objs = shift;

    # verify
    if ( $type !~ /^(teacher|lab|stream)$/ ) {
        die("You have specified an invalid type ($type) for a ViewChoice\n");
    }

    # make an ordered list of names=>$scheduable_objs
    my @named_scheduable_objs;
    foreach my $i ( 0 .. scalar(@$names) - 1 ) {
        push @named_scheduable_objs,
          NamedObject->new( $names->[$i], $scheduable_objs->[$i] );
    }

    my $self = {
        -type                  => $type,
        -title                 => $title,
        -scheduable_objs       => $scheduable_objs,
        -named_scheduable_objs => \@named_scheduable_objs,
    };
    return bless $self;
}

sub type {
    my $self = shift;
    return $self->{-type};
}

sub title {
    my $self = shift;
    return $self->{-title};
}

sub named_scheduable_objs {
    my $self = shift;
    return $self->{-named_scheduable_objs};
}

sub scheduable_objs {
    my $self = shift;
    return $self->{-scheduable_objs};
}

1;
