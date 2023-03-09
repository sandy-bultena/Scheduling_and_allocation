#!/usr/bin/perl
use strict;
use warnings;

# ============================================================================
# class NamedObject
# - data struct that has a name for the object, and the object itself
# ============================================================================
package NamedObject;
use FindBin;    # find which directory this executable is in
use lib "$FindBin::Bin/../";

sub new {
    my $class  = shift;
    my $name   = shift;
    my $object = shift;
    my $self   = { -name => $name, -obj => $object };
    return bless $self;
}

sub name {
    my $self = shift;
    $self->{-name} = shift if @_;
    return $self->{-name};
}

sub object {
    my $self = shift;
    $self->{-obj} = shift if @_;
    return $self->{-obj};
}

1;
