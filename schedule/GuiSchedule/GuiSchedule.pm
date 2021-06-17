#!/usr/bin/perl
use strict;
use warnings;

package GuiSchedule;
use FindBin;
use lib "$FindBin::Bin/..";
use GuiSchedule::GuiBlocks;
use GuiSchedule::View;
use Schedule::Undo;
use GuiSchedule::GuiScheduleTk;

=head1 NAME

GuiSchedule - 

=head1 VERSION

Version 2.00

=head1 SYNOPSIS

    use Schedule::Schedule;
    use GuiSchedule::GuiSchedule
    use Tk;
    
    my $Dirtyflag   = 0;
    my $mw          = MainWindow->new();
    my $Schedule    = Schedule->read('myschedule_file.yaml');
    my $guiSchedule = GuiSchedule->new( $mw, \$Dirtyflag, \$Schedule );
    
    # create clickable buttons for every teacher in $Schedule
    $guiSchedule->create_frame( $mw, 'teacher' );
    
    #display a view (schedule) for a specific teacher
    my @all_teachers = $Schedule->all_teachers();
    my $teacher = $all_teachers[0];
    $guiSchedule->create_new_view($teacher,"teacher");   

=head1 DESCRIPTION

This class creates a button interface to access the all of the views,
and it manages those views.

Manages all the "undo" and "redo" of actions taken upon the views.

=head1 METHODS

=cut

# =================================================================
# Class Variables
# =================================================================
our $Max_id = 0;

# =================================================================
# new
# =================================================================

=head2 new ()

creates a GuiSchedule object

B<Parameters>

-mw => MainWindow to create new Views from

-dirtyFlag => Flag to know when the GuiSchedule has changed since last save

-schedule => where course-sections/teachers/labs/streams are defined 

B<Returns>

GuiSchedule object

=cut

# -------------------------------------------------------------------
# new
#--------------------------------------------------------------------
my $gui;

sub new {
    my $class      = shift;
    my $gui_main  = shift;
    my $dirtyFlag = shift;
    my $schedule  = shift;

    $gui = GuiScheduleTk->new($gui_main);

    my $self = {-gui=>$gui,-gui_main=>$gui_main};

    bless $self;
    $self->{-id} = $Max_id++;
    $self->dirty_flag($dirtyFlag);
    $self->schedule_ptr($schedule);

    return $self;
}
sub gui {
    my $self = shift;
    return $self->{-gui};
}

# =================================================================
# getters/setters
# =================================================================

=head2 id ()

Returns the unique id for this GuiSchedule object.

=cut

sub id {
    my $self = shift;
    return $self->{-id};
}

=head2 schedule_ptr ( [Schedule] )

Get/sets the Schedule for this GuiSchedule object.

=cut

sub schedule_ptr {
    my $self = shift;
    $self->{-schedule_ptr} = shift if @_;
    return $self->{-schedule_ptr};
}
sub schedule {
    my $self = shift;
    return ${$self->{-schedule_ptr}};
}

=head2 dirty_flag ( [DirtyFlag] )

Get/sets the DirtyFlag for this GuiSchedule object.

=cut

sub dirty_flag {
    my $self = shift;
    $self->{-dirty} = shift if @_;
    return $self->{-dirty};
}

=head2 set_dirty ( )

Sets the dirty flag for changes to Schedule.

=cut

sub set_dirty {
    my $self = shift;
    ${ $self->{-dirty} } = 1;
}

=head2 Undoes ( )

Get the Undoes of this GuiSchedule object.

=cut

sub undoes {
    my $self = shift;
        return @{ $self->{-undoes} };
}

=head2 Redoes ( )

Get the Redoes of this GuiSchedule object.

=cut

sub redoes {
    my $self = shift;
        return @{ $self->{-redoes} };
}

sub close_view {
    my $self = shift;
    my $view = shift;
    $gui->close_view($view);
}

=head2 undo ( )

Undo/Redo last action

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
        my $block = $self->_find_block_to_apply_undo_redo( $action, $target_obj );

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
    my $self         = shift;
    my $action       = shift;
    my $obj          = shift;
 
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

Add a Undo to the list of Undoes for this GuiSchedule object.

=cut

sub add_undo {
    my $self = shift;
    my $undo = shift;

    $self->{-undoes} = [] unless $self->{-undoes};
    push @{ $self->{-undoes} }, $undo;
    return $self;
}

=head2 add_redo ( Undo )

Add a Redo to the list of Redoes for this GuiSchedule object.

=cut

sub add_redo {
    my $self = shift;
    my $redo = shift;

    $self->{-redoes} = [] unless $self->{-redoes};
    push @{ $self->{-redoes} }, $redo;
    return $self;
}

=head2 add_guischedule_to_views ( )

Adds the current GuiSchedule object to all open Views.

=cut

sub add_guischedule_to_views {
    my $self      = shift;
    my $openViews = $self->views;
    foreach my $view ( values %$openViews ) {
        $view->guiSchedule($self);
    }
}

# =================================================================
# resetters/removers
# =================================================================

=head2 remove_view ( $view )

Remove a View from the list of Views for this GuiSchedule object

=cut

sub remove_view {
    my $self = shift;
    my $view = shift;
    delete $self->{-views}->{ $view->id };
    return $self;
}

=head2 remove_all_views ( )

Removes all Views associated with this GuiSchedule object.

=cut

sub remove_all_views {
    my $self = shift;
    $self->{-views} = {};
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

Removes all Undoes associated with this GuiSchedule object.

=cut

sub remove_all_undoes {
    my $self = shift;
    $self->{-undoes} = [];
    return $self;
}

=head2 remove_all_redoes ( )

Removes all Redoes associated with this GuiSchedule object.

=cut

sub remove_all_redoes {
    my $self = shift;
    $self->{-redoes} = [];
    return $self;
}

=head2 destroy_all ( )

Closes all open Views.

=cut

sub destroy_all {
    my $self = shift;
    my $openViews = $self->views;

    foreach my $view ( values %$openViews ) {
        $self->close_view($view);
    }
    $self->remove_all_undoes;
    $self->remove_all_redoes;
}


# =================================================================
# updaters
# =================================================================

=head2 update_all_views ( Block )

Updates the position of the current moving GuiBlock across all open Views.

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

=head2 update_for_conflicts ( )

Goes through all open Views and updates their GuiBlocks for any new Conflicts.

=cut

sub update_for_conflicts {
    my $self      = shift;
    my $openViews = $self->views;

    foreach my $view ( values %$openViews ) {
        $view->update_for_conflicts( $view->type );
    }
}

sub get_view_choices {
    my $self = shift;
    
        # get teacher/lab/stream info
    my @teacher_array = $self->schedule->all_teachers;
    my @teacher_ordered = sort { $a->lastname cmp $b->lastname } @teacher_array;
    my @teacher_names;
    foreach my $obj (@teacher_ordered) {
        my $name = uc( substr( $obj->firstname, 0, 1 ) ) . " " . $obj->lastname;
        push @teacher_names, $name;
    }

    my @lab_array = $self->schedule->all_labs;
    my @lab_ordered = sort { $a->number cmp $b->number } @lab_array;
    my @lab_names;
    foreach my $obj (@lab_ordered) {
        push @lab_names, $obj->number;
    }

    my @stream_array = $self->schedule->all_streams;
    my @stream_ordered = sort { $a->number cmp $b->number } @stream_array;
    my @stream_names;
    foreach my $obj (@stream_ordered) {
        push @stream_names, $obj->number;
    }

    return [
                         ViewChoices->new(
                                           'teacher',       'Teacher View',
                                           \@teacher_names, \@teacher_ordered
                         ),
                         ViewChoices->new(
                                  'lab', 'Lab Views', \@lab_names, \@lab_ordered
                         ),
                         ViewChoices->new(
                                           'stream',       'Stream Views',
                                           \@stream_names, \@stream_ordered
                         ),
    ];
}

=head2 determine_button_colours ( Array of Teachers/Labs/Streams, Type of Object ) 

Finds the highest conflict for each teacher/lab/stream in the array and sets 
the colour of the button accordingly.

=cut

sub determine_button_colours {

    my $self         = shift;
    my $view_choices = shift || $self->get_view_choices();

    foreach my $view_choice (@$view_choices) {
        my $scheduable_objs = $view_choice->scheduable_objs;
        my $type                 = $view_choice->type;

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
# creators
# =================================================================

=head2 create_view ( Array Pointer, Type )

Preparation function for creating a new View when double clicking on a GuiBlock.

=cut

sub create_view {
    my $self    = shift;
    my $schedulable_objs = shift;
    my $type    = shift;
    my $ob      = shift;
    my $obj_id  = $ob->id if $ob;

    if   ( $type eq 'teacher' ) { $type = 'lab'; }
    else                        { $type = 'teacher'; }

    foreach my $scheduable_obj (@$schedulable_objs) {
        unless ( defined($obj_id) && $obj_id == $scheduable_obj->id ) {
            $self->create_new_view( undef, $scheduable_obj, $type);
        }
    }
}

=head2 create_new_view ( Teacher/Lab/Stream Object, Type, Button Pointer )

Creates a new View for the selected Teacher, Lab or Stream, depending on the object. 
If View is already open, the View for that object is brought to front.

Button Pointer is only used in debug mode

=cut

sub create_new_view {
    my $self    = shift;
    shift;  # when Tk calls this, it adds an extra object that we don't care about
    my $scheduable_obj     = shift;
    my $type    = shift;

    my $open         = $self->is_open( $scheduable_obj->id, $type );

    if ( not $open ) {
        my $view = View->new( $gui, $self->schedule, $scheduable_obj );

        $self->add_view($view);
        $self->add_guischedule_to_views;
    }
    else {
        $open->toplevel->raise;
        $open->toplevel->focus;
    }
}

sub get_callback_for_buttons {
    my $self = shift;
    return sub {create_new_view($self, @_);}
}

=head2 is_open ( Teacher/Lab/Stream ID, object type )

Checks if the View corresponding to the button pressed by user is open.
Returns the View object if View is open, else 0.

=cut

sub is_open {
    my $self = shift;
    my $id   = shift;
    my $type = shift;

    my $openViews = $self->views;
    foreach my $view ( values %$openViews ) {
        if ( $view->type eq $type ) {
            if ( $view->obj->id == $id ) { return $view; }
        }
    }

    return 0;
}

=head2 views ( )

Get the Views of this GuiSchedule object.

=cut

sub views {
    my $self = shift;
    return $self->{-views};
}

=head2 add_view ( View )

Add a View to the list of Views for this GuiSchedule object.

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
