#!/usr/bin/perl
use strict;
use warnings;

package AllScheduables;

use FindBin;    # find which directory this executable is in
use lib "$FindBin::Bin/../";
use UsefulClasses::ScheduablesByType;

sub new {
    my $class    = shift;
    my $schedule = shift;
    my $self     = bless {}, $class;

    # get teacher info
    my @teacher_array = $schedule->all_teachers;
    my @teacher_ordered = sort { $a->lastname cmp $b->lastname } @teacher_array;
    my @teacher_names;
    foreach my $obj (@teacher_ordered) {
        my $name = uc( substr( $obj->firstname, 0, 1 ) ) . " " . $obj->lastname;
        push @teacher_names, $name;
    }

    # get lab info
    my @lab_array = $schedule->all_labs;
    my @lab_ordered = sort { $a->number cmp $b->number } @lab_array;
    my @lab_names;
    foreach my $obj (@lab_ordered) {
        push @lab_names, $obj->number;
    }

    # get stream info
    my @stream_array = $schedule->all_streams;
    my @stream_ordered = sort { $a->number cmp $b->number } @stream_array;
    my @stream_names;
    foreach my $obj (@stream_ordered) {
        push @stream_names, $obj->number;
    }

    $self->teachers(
        ScheduablesByType->new(
            'teacher', 'Teacher View', \@teacher_names, \@teacher_ordered
        )
    );
    $self->labs(
        ScheduablesByType->new(
            'lab', 'Lab Views', \@lab_names, \@lab_ordered
        )
    );
    $self->streams(
        ScheduablesByType->new(
            'stream', 'Stream Views', \@stream_names, \@stream_ordered
        )
    );
    return $self;
}

sub by_type {
    my $self = shift;
    my $type = shift;
    return $self->teachers if $type eq 'teacher';
    return $self->labs     if $type eq 'lab';
    return $self->streams  if $type eq 'stream';
}

sub teachers {
    my $self = shift;
    $self->{-teachers} = shift if @_;
    return $self->{-teachers};
}

sub labs {
    my $self = shift;
    $self->{-labs} = shift if @_;
    return $self->{-labs};
}

sub streams {
    my $self = shift;
    $self->{-streams} = shift if @_;
    return $self->{-streams};
}

sub valid_types {
    return ( 'teacher', 'stream', 'lab' );
}

sub valid_view_type {
    my $self = shift;
    my $type = shift;
    return 'teacher' if lc($type) eq 'teacher';
    return 'stream'  if lc($type) eq 'stream';
    return 'lab'     if lc($type) eq 'lab';
    die("Invalid view type <$type>\n");
}
1;
