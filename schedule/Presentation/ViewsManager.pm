#!/usr/bin/perl
use strict;
use warnings;

package ViewsManager;
use FindBin;
use lib "$FindBin::Bin/..";
use Presentation::View;
use Schedule::Undo;
use GUI::ViewsManagerTk;
use UsefulClasses::AllScheduables;

=head1 NAME

ViewsManager - Manage all of the views (presentations of schedules) 

=head1 VERSION

Version 6.00

=head1 SYNOPSIS

    use Schedule::Schedule;
    use GUI::SchedulerTk;
    use GUI::ViewsManager;
    use YAML;
    $YAML::LoadBlessed = 1;
    
    my $Schedule = Schedule->read_YAML($file) };
    my $gui = SchedulerTk->new();
    my $views_manager = ViewsManager->new( $gui, \$Dirtyflag, \$Schedule );
    
    # get list of all possible views, with the appropriate call back function
    # to create a view, if needed
    my $btn_callback = $views_manager->get_create_new_view_callback;
    my $all_view_choices = $views_manager->get_all_scheduables();
    
    $views_manager->determine_button_colours($all_view_choices);

    # destroys any views that have been created
    $views_manager->destroy_all;
    
    #display a view (schedule) for a specific teacher
    $views_manager>create_new_view(undef, $teacher,"teacher");   

=head1 DESCRIPTION

This class creates a button interface to access the all of the schedule views,
and it manages those views.

Manages all the "undo" and "redo" of actions taken upon the views.

=head1 METHODS

=cut

# =================================================================
# Class Variables
# =================================================================
#TODO: our $Max_id = 0;

# =================================================================
# new
# =================================================================

=head2 new ()

creates a ViewsManager object

B<Parameters>

-gui_main => the gui that is used by whatever class invokes this class
             because we need to know the main_window etc.

-dirty_flag_ptr => Pointer to a flag that lets indicates if the schedule has 
              been changed since the last save

-schedule => where course-sections/teachers/labs/streams are defined 

B<Returns>

ViewsManager object

=cut

# -------------------------------------------------------------------
# new
#--------------------------------------------------------------------
my $gui;

sub new {
    my $class          = shift;
    my $gui_main       = shift;
    my $dirty_flag_ptr = shift;
    my $schedule       = shift;

    $gui = ViewsManagerTk->new($gui_main);

    my $self = { -gui => $gui, -gui_main => $gui_main };

    bless $self;

    #TODO:    $self->{-id}         = $Max_id++;
    $self->{-dirty_flag} = $dirty_flag_ptr;
    $self->_schedule_ptr($schedule);

    return $self;
}

=head2 gui 

Get/sets the gui that takes care of the GUI for this object.

=cut

sub gui {
    my $self = shift;
    return $self->{-gui};
}

# =================================================================
# getters/setters
# =================================================================

#TODO:
#=head2 id ()
#
#Returns the unique id for this ViewsManager object.
#
#=cut
#
#sub id {
#    my $self = shift;
#    return $self->{-id};
#}

sub _schedule_ptr {
    my $self = shift;
    $self->{-schedule_ptr} = shift if @_;
    return $self->{-schedule_ptr};
}

=head2 schedule 

Get/sets the Schedule for this ViewsManager object.

=cut

sub schedule {
    my $self = shift;
    return ${ $self->{-schedule_ptr} };
}

=head2 dirty_flag 

Get the dirty_flag for the schedule.

=cut

sub dirty_flag {
    my @caller = caller();
    my $self = shift;
    $self->{-dirty} = shift if @_;
    return $self->{-dirty};
}

=head2 set_dirty ( )

Sets the dirty flag for changes to the schedule.

=cut

sub set_dirty {
    my $self = shift;
    my $d = $self->{-dirty_flag};
    $$d = 1;
 }

# =================================================================
# Undo and redo
# =================================================================

=head2 Undoes ( )

Get the Undo objects of this ViewsManager object.

=cut

sub undoes {
    my $self = shift;
    return @{ $self->{-undoes} };
}

=head2 Redoes ( )

Get the Redoes of this ViewsManager object.

=cut

sub redoes {
    my $self = shift;
    return @{ $self->{-redoes} };
}

=head2 undo ( )

Undo/Redo last action

B<Parameters>

-type => "Day/Time" or anything else

=over 

=item * "Day/Time" is when the action occured for a specific 
schedulable object (i.e. a teacher/lab/stream)

=item * I<other> is when the action is applied to more than one
schedulable object (i.e. moving a course from one lab to another)
     
=back

=cut

sub undo {
    my $self = shift;
    my $type = shift;

    # ------------------------------------------------------------------------
    # get the undo/redo
    # ------------------------------------------------------------------------
    my $action;
    if ( $type eq 'undo' ) {
        my @undoes = $self->undoes;
        $action = pop @undoes;
    }
    else {
        my @redoes = $self->redoes;
        $action = pop @redoes;
    }
    return unless defined $action;

    # ------------------------------------------------------------------------
    # process action
    # ------------------------------------------------------------------------

    # Processing a simply change in either date/time within a single view
    # (no switching labs or teachers)

    if ( $action->move_type eq "Day/Time" ) {

        my $obj = $action->origin_obj;
        my $block = $self->_find_block_to_apply_undo_redo( $action, $obj );

        # --------------------------------------------------------------------
        # make new undo/redo object as necessary
        # --------------------------------------------------------------------
        my $redo_or_undo = Undo->new(
                                      $block->id,  $block->start,
                                      $block->day, $action->origin_obj,
                                      $action->move_type
        );

        if ( $type eq 'undo' ) {
            $self->add_redo($redo_or_undo);
            $self->remove_last_undo;
        }
        else {
            $self->add_undo($redo_or_undo);
            $self->remove_last_redo;
        }

        # --------------------------------------------------------------------
        # perform local undo/redo
        # --------------------------------------------------------------------
        $block->start( $action->origin_start );
        $block->day( $action->origin_day );

        # update all views to re-place blocks
        $self->redraw_all_views;
    }

    # ------------------------------------------------------------------------
    # moved a teacher from one course to another, or moved block from
    # one lab to a different lab
    # ------------------------------------------------------------------------
    else {

        my $original_obj = $action->origin_obj;
        my $target_obj   = $action->new_obj;
        my $block =
          $self->_find_block_to_apply_undo_redo( $action, $target_obj );

        # --------------------------------------------------------------------
        # make new undo/redo object as necessary
        # --------------------------------------------------------------------
        my $redo_or_undo = Undo->new(
                                      $action->block_id,  $block->start,
                                      $block->day,        $action->new_obj,
                                      $action->move_type, $action->origin_obj
        );
        if ( $type eq 'undo' ) {
            $self->add_redo($redo_or_undo);
            $self->remove_last_undo;
        }
        else {
            $self->add_undo($redo_or_undo);
            $self->remove_last_redo;
        }

        # reassign teacher/lab to block
        if ( $action->move_type eq 'teacher' ) {
            $block->remove_teacher($target_obj);
            $block->assign_teacher($original_obj);
            $block->section->remove_teacher($target_obj);
            $block->section->assign_teacher($original_obj);
        }
        elsif ( $action->move_type eq 'lab' ) {
            $block->remove_lab($target_obj);
            $block->assign_lab($original_obj);
        }

        # update all views to re-place blocks
        $self->redraw_all_views;
    }
}

sub _find_block_to_apply_undo_redo {
    my $self   = shift;
    my $action = shift;
    my $obj    = shift;

    my $block;
    my @blocks = $self->schedule->get_blocks_for_obj($obj);
    foreach my $b (@blocks) {
        if ( $b->id == $action->block_id ) {
            $block = $b;
            last;
        }
    }

    return $block;
}

=head2 add_undo ( Undo )

Add a Undo to the list of Undoes for this ViewsManager object.

=cut

sub add_undo {
    my $self = shift;
    my $undo = shift;

    $self->{-undoes} = [] unless $self->{-undoes};
    push @{ $self->{-undoes} }, $undo;
    return $self;
}

=head2 add_redo ( Undo )

Add a Redo to the list of Redoes for this ViewsManager object.

=cut

sub add_redo {
    my $self = shift;
    my $redo = shift;

    $self->{-redoes} = [] unless $self->{-redoes};
    push @{ $self->{-redoes} }, $redo;
    return $self;
}

=head2 remove_last_undo ( )

Remove last undo

=cut

sub remove_last_undo {
    my $self = shift;
    pop @{ $self->{-undoes} };
    return $self;
}

=head2 remove_last_redo ( )

Remove last redo

=cut

sub remove_last_redo {
    my $self = shift;
    pop @{ $self->{-redoes} };
    return $self;
}

=head2 remove_all_undoes ( )

Removes all Undoes associated with this ViewsManager object.

=cut

sub remove_all_undoes {
    my $self = shift;
    $self->{-undoes} = [];
    return $self;
}

=head2 remove_all_redoes ( )

Removes all Redoes associated with this ViewsManager object.

=cut

sub remove_all_redoes {
    my $self = shift;
    $self->{-redoes} = [];
    return $self;
}

# ============================================================================
# house keeping
# ============================================================================

=head2 add_manager_to_views ( )

Making sure the views have access to the view manager

=cut

sub add_manager_to_views {
    my $self      = shift;
    my $openViews = $self->views;
    foreach my $view ( values %$openViews ) {
        $view->views_manager($self);
    }
}

# =================================================================
# keeping track of the views
# =================================================================

=head2 close_view ($view)

Close the gui window, and remove view from list of 'open' views

=cut

sub close_view {
    my $self = shift;
    my $view = shift;
    
    $view->close();
    $self->_remove_view($view);
    delete $self->{-views}->{ $view->id };
    return $self;
}

sub _remove_view {
    my $self = shift;
    my $view = shift;
    delete $self->{-views}->{ $view->id };
    return $self;
}

=head2 destroy_all ( )

Closes all open Views.

=cut

sub destroy_all {
    my $self      = shift;
    my $openViews = $self->views;

    foreach my $view ( values %$openViews ) {
        $self->close_view($view);
    }
    $self->remove_all_undoes;
    $self->remove_all_redoes;
}

=head2 is_open 

Checks if the View corresponding to the button pressed by user is open.

B<Parameters>

- id => the id of the view that you want to check on

- type => the type of view that you want to check

B<Returns> 

- the View object if View is open, else 0.

=cut

sub is_open {
    my $self = shift;
    my $id   = shift;
    my $type = shift;

    my $openViews = $self->views;
    foreach my $view ( values %$openViews ) {
        if ( $view->type eq $type ) {
            if ( $view->scheduable->id == $id ) { return $view; }
        }
    }

    return 0;
}

=head2 views ( )

Get the Views of this ViewsManager object.

=cut

sub views {
    my $self = shift;
    return $self->{-views};
}

=head2 add_view 

Add a View to the list of Views for this ViewsManager object.

B<Parameters> 

- view object

=cut

sub add_view {
    my $self = shift;
    my $view = shift;
    $self->{-views} = {} unless $self->{-views};

    # save
    $self->{-views}->{ $view->id } = $view;
    return $self;
}

# =================================================================
# updater the views
# =================================================================

=head2 update_all_views 

Updates the position of the current moving GuiBlock across all open Views.

<Parameters>

- gui block object (TODO: is this a gui block or a just a regular block?)

=cut

sub update_all_views {
    my $self      = shift;
    my $block     = shift;
    my $openViews = $self->views;

    # go through all currently open views
    foreach my $view ( values %$openViews ) {

        # update the guiblocks on the view
        $view->update($block);
    }
}

=head2 redraw_all_views ( )

Redraw all open Views with new GuiBlocks (if any).

=cut

sub redraw_all_views {
    my $self      = shift;
    my $openViews = $self->views;

    foreach my $view ( values %$openViews ) {
        $view->redraw;
    }
}

=head2 update_for_conflicts

Goes through all open Views and updates their GuiBlocks for any new Conflicts.

=cut

sub update_for_conflicts {
    my $self      = shift;
    my $openViews = $self->views;

    foreach my $view ( values %$openViews ) {
        $view->update_for_conflicts( $view->type );
    }
}

=head get_all_scheduables 

Gets a list of all scheduable objects and organizes them by type (teacher/lab/stream)
with a list of the schedulable objects, the names to be displayed in the gui, etc.

B<Returns>

An array of ScheduablesByType (see SharedData.pm)

=cut

sub get_all_scheduables {
    my $self = shift;
    return AllScheduables->new($self->schedule);
}

=head2 determine_button_colours 

Finds the highest conflict for each teacher/lab/stream in the array and sets 
the colour of the button accordingly.

B<Parameters>

- a list of the view_choices

=cut

sub determine_button_colours {

    my $self = shift;
    my $all_view_choices = shift || $self->get_all_scheduables();

    foreach my $type (AllScheduables->valid_types) {
        my $scheduable_objs = $all_view_choices->by_type($type)->scheduable_objs;

        # calculate conflicts
        $self->schedule->calculate_conflicts;

        my @blocks;

        # for every teacher, lab, stream schedule
        foreach my $scheduable_obj (@$scheduable_objs) {
            @blocks = $self->schedule->get_blocks_for_obj($scheduable_obj);

            # what is this view's conflict? start with 0
            my $view_conflict = 0;

            # for every block
            foreach my $block (@blocks) {
                $view_conflict =
                  Conflict->most_severe( $view_conflict | $block->is_conflicted,
                                         $type );
                last if $view_conflict == $Conflict::Sorted_Conflicts[0];
            }

            $gui->set_button_colour( $scheduable_obj, $view_conflict );

        }
    }
}

# =================================================================
# callbacks used by View objects
# =================================================================

=head2 create_view_containing_block 

B<Used as a callback function for View objects>

B<Parameters>

=over

=item * scheduable_objs 

A list of objects (teachers/labs/streams) where a 
schedule can be created for them, and so a view is created for each of these
objects

=item * type of view to draw (teacher/lab/stream)

=item * block object

=back 

Find a scheduable object(s) in the given list, and if the given block object
is also part of that specific schedule, then create a new view.

TODO:  Clarify what the hell this is doing, once we are working on the View.pm file 

=cut

sub create_view_containing_block {
    my $self             = shift;
    my $schedulable_objs = shift;
    my $type             = shift;
    my $ob               = shift;

    my $obj_id = $ob->id if $ob;

    if   ( $type eq 'teacher' ) { $type = 'lab'; }
    else                        { $type = 'teacher'; }

    foreach my $scheduable_obj (@$schedulable_objs) {
        unless ( defined($obj_id) && $obj_id == $scheduable_obj->id ) {
            $self->create_new_view( undef, $scheduable_obj, $type );
        }
    }
}

=head2 create_new_view 

B<Used as a callback function for View objects>

Creates a new View for the selected Teacher, Lab or Stream , depending on the 
scheduable object. 

If the View is already open, the View for that object is brought to front.

B<Parameters>

=over

=item * undef

Because this is used as a callback function, it inserts a
parameter that we don't care about.  If calling this function directly, just
use C<undef> as the first parameter.

=item * scheduable_obj - an object that can have a schedule (teacher/lab/stream)

=item * type - type of view to show (teacher/lab/stream)

=cut

sub create_new_view {
    my $self           = shift;
    my $undef          = shift;
    my $scheduable_obj = shift;
    my $type           = shift;

    my $open = $self->is_open( $scheduable_obj->id, $type );

    if ( not $open ) {
        my $view = View->new( $self,$gui->mw, $self->schedule, $scheduable_obj );
        $self->add_view($view);
        $self->add_manager_to_views;
    }
    else {
        # TODO: Should have a View method for this instead of View->gui
        $open->gui->_toplevel->raise;
        $open->gui->_toplevel->focus;
    }
}

=head2 get_create_new_view_callback

Creates a callback function from C<create_new_view>
that includes this object as the first parameter.

B<Returns>

The new callback function

=cut

sub get_create_new_view_callback {
    my $self = shift;
    return sub { create_new_view( $self, @_ ); }
}

# =================================================================
# footer
# =================================================================

=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns

=head1 COPYRIGHT

Copyright (c) 2016, Jack Burns, Sandy Bultena, Ian Clement. 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut

1;
