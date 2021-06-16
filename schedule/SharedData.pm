#!/usr/bin/perl
use strict;
use warnings;

# extension of the main package in SchedulerManager.pl
package Scheduler;

our @Required_pages = (
                        NoteBookPage->new(
                                 "Schedules", \&update_choices_of_schedule_views
                        ),
                        NoteBookPage->new( "Overview", \&update_overview ),
                        NoteBookPage->new( "Courses",  \&update_edit_courses ),
                        NoteBookPage->new( "Teachers", \&update_edit_teachers ),
                        NoteBookPage->new( "Labs",     \&update_edit_labs ),
                        NoteBookPage->new( "Streams",  \&update_edit_streams ),
);
our %Pages_lookup;
foreach my $page (@Required_pages) {
    $Pages_lookup{ $page->name } = $page;
}

our @SchedulerManagerGui_methods = (
    qw(new create_main_window create_menu_and_toolbars create_front_page
      create_status_bar bind_schedule_and_dirty_flag define_exit_callback
      start_event_loop update_for_new_schedule_and_show_page show_error show_info choose_file
      choose_existing_file question wait_for_it stop_waiting show_info define_notebook_tabs
      set_gui_schedule)
);

# ============================================================================
# NoteBookPage class
# - defines notebook page info
# ============================================================================
package NoteBookPage;

sub new {
    my $class         = shift;
    my $name          = shift;
    my $event_handler = shift;
    my $self          = bless {};
    $self->name($name);
    $self->handler($event_handler);
    return $self;
}

sub name {
    my $self = shift;
    $self->{-name} = shift if @_;
    return $self->{-name};
}

sub handler {
    my $self = shift;
    $self->{-handler} = shift if @_;
    return $self->{-handler};
}

# ============================================================================
# ViewChoices class
# - defines the data for what views are available
# ... NOTE: A view is a visual representation of a schedule for a specific
#           teacher, lab or stream
# ============================================================================
package ViewChoices;

sub new {
    my $class = shift;
    my $type  = shift;    # what type of views are available?
    my $title = shift;    # title of this collection of view choices
    my $names = shift;    # array of names used for each $schedule_object
    my $schedule_objects = shift;

    # verify
    if ( $type !~ /^(teacher|lab|stream)$/ ) {
        die("You have specified an invalid type ($type) for a ViewChoice\n");
    }

    # make an ordered list of names=>$schedule_objects
    my @named_schedule_objects;
    foreach my $i ( 0 .. scalar(@$names) ) {
        push @named_schedule_objects,
          NamedObject->new( $names->[$i], $schedule_objects->[$i] );
    }

    my $self = {
                 -type                   => $type,
                 -title                  => $title,
                 -schedule_objects       => $schedule_objects,
                 -named_schedule_objects => \@named_schedule_objects,
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

sub named_schedule_objects {
    my $self = shift;
    return $self->{-title};
}

sub schedule_objects {
    my $self = shift;
    return $self->{-schedule_objects};
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
    return $self->{-object};
}

1;
