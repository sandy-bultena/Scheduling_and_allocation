#!/usr/bin/perl
use strict;
use warnings;

# extension of the main package in SchedulerManager.pl
package Scheduler;

our @Required_pages = (
    NoteBookPage->new( "Schedules", \&update_choices_of_schedule_views ),
    NoteBookPage->new( "Overview",  \&update_overview ),
    NoteBookPage->new( "Courses",    \&update_edit_courses ),
    NoteBookPage->new( "Teachers",  \&update_edit_teachers ),
    NoteBookPage->new( "Labs",      \&update_edit_labs ),
    NoteBookPage->new( "Streams",   \&update_edit_streams ),
);
our %Pages_lookup;
foreach my $page (@Required_pages) {
    $Pages_lookup{$page->name} = $page;
}

our @SchedulerManagerGui_methods = (
    qw(new create_main_window create_menu_and_toolbars create_front_page
      create_status_bar bind_schedule_and_dirty_flag define_exit_callback
      start_event_loop update_for_new_schedule_and_show_page show_error show_info choose_file
      choose_existing_file question wait_for_it stop_waiting show_info define_notebook_tabs
       set_gui_schedule)
);


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

1;