#!/usr/bin/perl
use strict;
use warnings;

package NoteBookPageInfo;

sub new {
    my $class         = shift;
    my $name          = shift;
    my $event_handler = shift;
    my $self          = bless {};
    my $subpages = shift;
    $self->name($name);
    $self->handler($event_handler);
    $self->subpages($subpages);
    return $self;
}

sub name {
    my $self = shift;
    $self->{-name} = shift if @_;
    return $self->{-name};
}

sub subpages {
    my $self = shift;
    $self->{-subpages} = shift if @_;
    return $self->{-subpages};
}

sub handler {
    my $self = shift;
    $self->{-handler} = shift if @_;
    return $self->{-handler};
}

sub id {
    my $self = shift;
    my $label = $self->name;
    $label = lc($label);
    $label =~ s/\s/_/g;
    return $label;
}



1;