#!/usr/bin/perl
use strict;
use warnings;

# extension of the main package in SchedulerManager.pl
package Scheduler;

our @SchedulerManagerGui_methods = (
    qw(new create_main_window create_menu_and_toolbars create_front_page
      create_status_bar bind_dirty_flag define_exit_callback
      start_event_loop update_for_new_schedule_and_show_page show_error show_info choose_file
      choose_existing_file question wait_for_it stop_waiting show_info define_notebook_tabs
      set_views_manager)
);

package SharedRoutines;

sub get_all_scheduables {
    my $class = shift;
    my $schedule = shift;
    
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

    return [
             ScheduablesByType->new(
                               'teacher',       'Teacher View',
                               \@teacher_names, \@teacher_ordered
             ),
             ScheduablesByType->new( 'lab', 'Lab Views', \@lab_names, \@lab_ordered ),
             ScheduablesByType->new(
                               'stream',       'Stream Views',
                               \@stream_names, \@stream_ordered
             ),
    ];
}

sub valid_view_type {
    my $class = shift;
    my $type = shift;
    return 'teacher' if lc($type) eq 'teacher';
    return 'stream' if lc($type) eq 'stream';
    return 'lab' if lc($type) eq 'lab';
    die ("Invalid view type <$type>\n");
}



# ============================================================================
# ScheduablesByType class
# - defines the data for what views are available
# ... NOTE: A view is a visual representation of a schedule for a specific
#           teacher, lab or stream
# ============================================================================
package ScheduablesByType;

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

# ============================================================================
# class NamedObject
# - data struct that has a name for the object, and the object itself
# ============================================================================
package NamedObject;

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
