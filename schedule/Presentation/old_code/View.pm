#!/usr/bin/perl
use strict;
use warnings;

package View;
use FindBin;
use lib "$FindBin::Bin/..";
use List::Util qw( min max );
use GUI::ViewTk;
use GUI::GuiBlockTk;
use GUI::ViewBaseTk;
use GUI::AssignBlockTk;
use Schedule::Undo;
use Schedule::Conflict;
use Schedule::Blocks;
use Export::DrawView;
use List::Util qw( min max );
use Presentation::AssignToResource; 
use UsefulClasses::AllScheduables;

=head1 NAME

View - describes the visual representation of a Schedule

=head1 VERSION

Version 6.00

=head1 SYNOPSIS

    use Schedule::Schedule;
    use GUI::SchedulerTk;
    use GUI::ViewsManager;
    use YAML;
    $YAML::LoadBlessed = 1;
    
    
    # ------------ Set up --------------------
    my $Schedule = Schedule->read_YAML($file) };
    my $gui = SchedulerTk->new();
    my $views_manager = ViewsManager->new( $gui, \$Dirtyflag, \$Schedule );
    my $teacher = $Schedule->Teachers->get_by_name("John","Doe");
        
    # ------------- Create and use view -------------
    my $view = View->new( $views_manager,$views_manager->gui->mw, $Schedule, $teacher );
        
    #... change the schedule... 
    
    $View->redraw;
    

=head1 DESCRIPTION

Describes a View

=head1 PROPERTIES

=cut

# =================================================================
# global and package variables
# =================================================================
my $Undo_number   = "";
my $Redo_number   = "";
my $Clicked_block = 0;
our @days         = @DrawView::days;
our %times        = %DrawView::times;
our $Earliest_time = min( keys %times );
our $Latest_time   = max( keys %times );
our $Max_id       = 0;

# =================================================================
# getters/setters
# =================================================================

=head2 schedule( [Schedule] )

Get/Set the schedule object

=cut 

sub schedule {
    my $self = shift;
    $self->{-schedule} = shift if @_;
    return $self->{-schedule};
}

=head2 gui( [ViewTk] )

Returns the gui object for this view

=cut 

sub gui {
    my $self = shift;
    $self->{-gui} = shift if @_;
    return $self->{-gui};
}

=head2 id()

Returns the unique id for this View object.

=cut

sub id {
    my $self = shift;
    return $self->{-id};
}

=head2 scheduable( [Teacher | Lab | Stream] ) 

Get/Set the Teacher, Lab or Stream associated to this View.

=cut

sub scheduable {
    my $self = shift;
    $self->{-obj} = shift if @_;
    return $self->{-obj};
}

=head2 type( [ "teacher" | "lab" | "stream" ] )

Get/Set the type of this View object.

=cut

sub type {
    my $self = shift;
    $self->{-type} = shift if @_;
    return $self->{-type};
}

=head2 blocks( [Blocks] ) 

Get/Set the Blocks of this View object. Pointer to an array of Block objects

=cut

sub blocks {
    my $self = shift;
    $self->{-blocks} = [] unless defined $self->{-blocks};
    $self->{-blocks} = shift if @_;
    return $self->{-blocks};
}

=head2 guiBlocks()

Get the GuiBlocks of this View object.

=cut

sub guiblocks {
    my $self = shift;
    return $self->{-guiblocks};
}

=head2 views_manager( [ViewsManager] ) 

Get/Set the views_manager of this View object.

=cut

sub views_manager {
    my $self = shift;
    $self->{-views_manager} = shift if @_;
    return $self->{-views_manager};
}


# =================================================================
# new
# =================================================================
=head1 PUBLIC METHODS

=head2 new( Tk::MainWindow, Schedule, (Teacher | Lab | Stream) ) 

creates a View object, draws the necessary GuiBlocks and returns the View object.

B<Parameters>

- views_manager => The ViewsManager object responsible for keeping track of
all of the views.

- mw => Tk mainWindow

- schedule => where course-sections/teachers/labs/streams are defined

- scheduable => Teacher/Lab/Stream that the View is being made for

B<Returns>

View object

=cut

sub new {

    my $class             = shift;
    my $views_manager     = shift;
    my $mw                = shift;
    my $schedule          = shift;
    my $scheduable_object = shift;

    my $self = bless {};
    $self->{-id} = ++$Max_id;
    my $conflict_info = $self->_get_conflict_info();

    # ---------------------------------------------------------------
    # create the Gui
    # ---------------------------------------------------------------
    my $gui = ViewTk->new( $self, $mw, $conflict_info );

    # ---------------------------------------------------------------
    # this is what needs to be done to close the window
    # ---------------------------------------------------------------
    $gui->on_closing(sub{_cb_close_view($self)});
    
    # ---------------------------------------------------------------
    # type of view depends on which object it is for
    # ---------------------------------------------------------------
    my @blocks = $schedule->get_blocks_for_obj($scheduable_object);
    my $type   = $schedule->get_scheduable_object_type($scheduable_object);

    # ---------------------------------------------------------------
    # save some parameters
    # ---------------------------------------------------------------
    $self->gui($gui);
    $self->views_manager($views_manager);
    $self->blocks( \@blocks );
    $self->schedule($schedule);
    $self->type($type);
    $self->scheduable($scheduable_object);

    # ---------------------------------------------------------------
    # set the title
    # ---------------------------------------------------------------
    my $title;
    if ( $scheduable_object && $scheduable_object->isa('Teacher') ) {
        $self->gui->set_title(
                       uc( substr( $scheduable_object->firstname, 0, 1 ) ) . " "
                         . $scheduable_object->lastname );
    }
    elsif ($scheduable_object) {
        $self->gui->set_title( $scheduable_object->number );
    }

    # --------------------------------------------------------------
    # popup menu for guiblocks
    # ---------------------------------------------------------------
    my $named_scheduable_objects = $self->_get_named_scheduable_for_popup($type);
    $self->gui->setup_popup_menu( $self->type, $named_scheduable_objects,
                            \&_cb_toggle_movement, \&_cb_move_block_between_scheduable_objects );

    # ---------------------------------------------------------------
    # undo/redo
    # ---------------------------------------------------------------
    $self->gui->setup_undo_redo( \$Undo_number, \$Redo_number, \&_cb_undo_redo );

    # ---------------------------------------------------------------
    # refresh drawing - redrawing creates the guiblocks
    # ---------------------------------------------------------------
    $self->redraw();
    $self->schedule->calculate_conflicts;
    $self->update_for_conflicts( $self->type );

    # return object
    return $self;
}


=head2 redraw() 

Redraws the View with new GuiBlocks and their positions.

=cut

sub redraw {
    my $self         = shift;
    my $schedule = $self->schedule;
 
    # ---------------------------------------------------------------
    # draw the background, date/time stuff, etc
    # ---------------------------------------------------------------
    $self->gui->redraw();
    
    # ---------------------------------------------------------------
    # create and draw the gui blocks
    # ---------------------------------------------------------------

    # get blocks for this object
    my @blocks = $schedule->get_blocks_for_obj($self->scheduable);

    # remove all guiblocks stored in the View
    $self->_remove_all_guiblocks;

    # redraw all guiblocks
    foreach my $b (@blocks) {

        # this makes sure that synced blocks have the same time_start time
        $b->time_start( $b->time_start );
        $b->day( $b->day );

        my $guiblock = GuiBlock->new( $self->type, $self->gui, $b );

        $self->gui->bind_popup_menu($guiblock);
        $self->_add_guiblock($guiblock);
    }

    $self->blocks( \@blocks );
    $schedule->calculate_conflicts;
    $self->update_for_conflicts( $self->type );

    # ---------------------------------------------------------------
    # If this is a lab or teacher view, then add 'AssignBlocks'
    # to the view, and bind as necessary
    # ---------------------------------------------------------------
    $self->_setup_for_assignable_blocks();

    # ---------------------------------------------------------------
    # set colour for all buttons on main window, "Schedules" tab
    # ---------------------------------------------------------------
    $self->_set_view_button_colours();
    $self->views_manager->update_for_conflicts if $self->views_manager;

    # ---------------------------------------------------------------
    # bind events for each gui block
    # ---------------------------------------------------------------
    my $gbs = $self->guiblocks();

    foreach my $guiblock ( values %$gbs ) {

        my $block = $guiblock->block;

        # bind to allow block to move if clicked and dragged
        if ( $block->movable ) {
            $self->gui->set_bindings_for_dragging_guiblocks( $self,$guiblock,
                    \&_cb_guiblock_is_moving, \&_cb_guiblock_has_stopped_moving,
                    \&cb_update_after_moving_block );
        }

        # double click opens companion views
        $self->gui->bind_double_click( $self, $guiblock, \&_cb_open_companion_view );
    }
}

# =================================================================
# update
# =================================================================

=head2 update( Block )

Updates the position of any GuiBlocks, that have the same Block
as the currently moving GuiBlock.

B<Parameters>

- block => the Schedule::Block object that has been modified

=cut

sub update {
    my $self  = shift;
    my $block = shift;

    # go through each guiblock on the view
    if ( $self->guiblocks ) {
        foreach my $guiblock ( values %{ $self->guiblocks } ) {

            # race condition, no need to update the current moving block
            next if $guiblock->is_controlled;

            # guiblock's block is the same as moving block?
            if ( $guiblock->block->id == $block->id ) {
                $self->gui->move_block($guiblock);
            }
        }
    }
}

=head2 update_for_conflicts() 

Determines conflict status for all GuiBlocks on this View and colours 
them accordingly.

=cut

sub update_for_conflicts {
    my $self = shift;
    my $type = shift;
    unless ($type) {
        my @c = caller();
        print "Dieing from: @c\n";
        die("must specify a type");    ##### remove die later
    }
    my $guiblocks = $self->guiblocks;
   

    my $view_conflict = 0;

    # for every guiblock on this view
    foreach my $guiblock ( values %$guiblocks ) {

        $self->gui->colour_block( $guiblock, $type );

        # colour block by conflict only if it is moveable
        if ( $guiblock->block->moveable ) {

            # create conflict number for entire view
            $view_conflict = $view_conflict | $guiblock->block->is_conflicted;
        }
            
    }

    return $view_conflict;
}

=head2 close()

close the view

=cut

sub close {
    my $self = shift;
    $self->gui->destroy;
}


# =================================================================
# Callbacks (event handlers)
# =================================================================

=head1 CALLBACKS (Event Handlers?)

=head2 _cb_close_view( ViewsManager ) 

When the view is closed, need to let views_manager know.

B<Handles Event:> View is closed via the gui interface

=cut

sub _cb_close_view {
    my $self          = shift;
    my $views_manager = $self->views_manager;
    $views_manager->close_view($self);
}


=head2 _cb_undo_redo( "undo" | "redo" ) 

Lets the views_manager manage the undo/redo action

B<Handles Event:> Undo/Redo

B<Parameters>

- type => string, either 'undo' or 'redo'

=cut

sub _cb_undo_redo {
    my $self = shift;
    my $type = shift;

    $self->views_manager->undo($type);

    # set colour for all buttons on main window, "Schedules" tab
    $self->_set_view_button_colours();

    # update status bar
    $self->_set_status_undo_info;
}

=head2 _cb_assign_blocks( \@AssignedBlock )

Give the option of assigning these blocks to a resource 
(add to course, assign block to teacher/lab/stream)

B<Handles Event:> AssignBlock objects have been selected.

B<Parameters>

- chosen_blocks => a ptr to an array of AssignBlocks that have been 
                   selected by the user

=cut

sub _cb_assign_blocks {
    my $self          = shift;
    my $chosen_blocks = shift;

    #Get the day and time of the chosen blocks
    my ( $day, $time_start, $duration ) =
      AssignBlockTk->get_day_start_duration($chosen_blocks);

    #create the menu to select the block to assign to the timeslot
    AssignToResource->new( $self->gui->mw, $self->schedule, $day,
                           $time_start, $duration, $self->scheduable);

    #redraw
    $self->redraw();
}

=head2 _cb_toggle_movement 
 
Toggles whether a Guiblock is moveable or not. 

B<Handles Event:> the toggle movable/unmovable on the popup menu 
has been clicked.

=cut

sub _cb_toggle_movement {
    my $self = shift;

    # get the block that was right_clicked
    return unless $self->gui->popup_guiblock();
    my $block = $self->gui->popup_guiblock()->block;

    # toggle movability
    if ( $block->movable() ) {
        $block->movable(0);
    }
    else {
        $block->movable(1);
    }

    # redraw, and set dirty flag
    $self->views_manager->redraw_all_views;
    my $views_manager = $self->views_manager;
    $self->views_manager->set_dirty( $views_manager->dirty_flag )
      if $views_manager;

}

=head2 _cb_move_block_between_scheduable_objects( Teacher | Lab | Stream )

Moves the selected class(es) from the original Views Teacher/Lab to 
the Teacher/Lab Object.

B<Handles Event:> the user has selected to move a block between
one selectable object and another via the popup_menu

B<Parameters>

- that_scheduable => target destination of the block

=cut

sub _cb_move_block_between_scheduable_objects {
    my ( $self, $that_scheduable ) = @_;
    my $this_scheduable = $self->scheduable;
    
    # get the gui block that the popup_menu was invoked on
    my $guiblock = $self->gui->popup_guiblock();
    
    # reassign teacher/lab to blocks
    if ( $self->type eq 'teacher' ) {
        $guiblock->block->remove_teacher($this_scheduable);
        $guiblock->block->assign_teacher($that_scheduable);
        $guiblock->block->section->remove_teacher($this_scheduable);
        $guiblock->block->section->assign_teacher($that_scheduable);
    }

    elsif ( $self->type eq 'lab' ) {
        $guiblock->block->remove_lab($this_scheduable);
        $guiblock->block->assign_lab($that_scheduable);
    }
    if ( $self->type eq 'stream' ) {
        $guiblock->block->section->remove_stream($this_scheduable);
        $guiblock->block->section->assign_stream($that_scheduable);
    }


    # there was a change, redraw all views
    my $undo = Undo->new(
                          $guiblock->block->id,  $guiblock->block->time_start,
                          $guiblock->block->day, $self->scheduable,
                          $self->type,           $that_scheduable
    );
    $self->views_manager->add_undo($undo);

    # new move, so reset redo
    $self->views_manager->remove_all_redoes;

    # update status bar
    $self->_set_status_undo_info;

    # set dirty flag, and redraw
    $self->views_manager->set_dirty;
    $self->views_manager->redraw_all_views;
}

=head2 _cb_guiblock_is_moving( GuiBlock )

Need to update all Views

B<Handles Event:> a guiblock is being dragged about by the user

B<Parameters>

- guiblock => guiblock that is moving 

=cut

sub _cb_guiblock_is_moving {
    my $self     = shift;
    my $guiblock = shift;

    # update same block on different views
    my $block         = $guiblock->block;
    my $views_manager = $self->views_manager;
    $views_manager->update_all_views($block);

    # is current block conflicting
    $self->schedule->calculate_conflicts;
    $self->gui->colour_block($guiblock);
}

=head2 _cb_open_companion_view( GuiBlock ) 

Based on the type of this view, will open another view which has this
block.

lab/stream -> teachers

teachers -> streams

B<Handles Event:> double-clicking on a guiblock

B<Parameters>

- guiblock => the guiblock that was double clicked

=cut

sub _cb_open_companion_view {
    my ( $self, $guiblock ) = @_;
    my $type = $self->type;

    # TODO:  WTF?
    # ---------------------------------------------------------------
    # in lab or stream, open teacher schedules
    # no teacher schedules, then open other lab schedules
    # ---------------------------------------------------------------
    if ( $type eq 'lab' || $type eq 'stream' ) {

        my @teachers = $guiblock->block->teachers;
        if (@teachers) {
            $self->views_manager->create_view_containing_block( \@teachers,
                                                                $self->type );
        }
        else {
            my @labs = $guiblock->block->labs;
            $self->views_manager->create_view_containing_block( \@labs,
                                                  'teacher', $self->scheduable )
              if @labs;
        }
    }

    # ---------------------------------------------------------------
    # in teacher schedule, open lab schedules
    # no lab schedules, then open other teacher schedules
    # ---------------------------------------------------------------
    elsif ( $type eq 'teacher' ) {

        my @labs = $guiblock->block->labs;
        if (@labs) {
            $self->views_manager->create_view_containing_block( \@labs,
                                                                $self->type );
        }
        else {
            my @teachers = $guiblock->block->teachers;
            $self->views_manager->create_view_containing_block( \@teachers,
                                                      'lab', $self->scheduable )
              if @teachers;
        }
    }
}

=head2 _cb_guiblock_has_stopped_moving( GuiBlock ) 

Ensures that the guiblock is snapped to an appropriate location 
(i.e. start/end times must end on the hour or half-hour)

Updates undo/redo appropriately

B<Handles Event:> a guiblock has been placed into a new location

B<Parameters>

- guiblock - guiblock that has been moved

=cut

sub _cb_guiblock_has_stopped_moving {
    my ( $self, $guiblock ) = @_;

    my $undo =
      Undo->new( $guiblock->block->id, $guiblock->block->time_start,
                 $guiblock->block->day, $self->scheduable,
                 "Day/Time" );

    # set guiblocks new time and day
    $self->_snap_gui_block($guiblock);

    # don't create undo if moved to starting position
    if (    $undo->origin_start ne $guiblock->block->time_start
         || $undo->origin_day ne $guiblock->block->day )
    {

        # add change to undo
        $self->views_manager->add_undo($undo);

        # new move, so reset redo
        $self->views_manager->remove_all_redoes;

        # update status bar
        $self->_set_status_undo_info;
    }

}


=head2 cb_update_after_moving_block( Block )

Update all Views

Calculate conflicts and set button colours

Set dirty flag

B<Handles Event:> for when a guiblock has been dropped, and now it is time
to refresh everything

B<Parameters>

- block => the block that has been modified by moving a guiblock around

=cut

sub cb_update_after_moving_block {
    my $self  = shift;
    my $block = shift;

    # update all the views that have the block just moved to its new position
    my $views_manager = $self->views_manager;
    $views_manager->update_all_views($block);

    # calculate new conflicts and update other views to show these conflicts
    $self->schedule->calculate_conflicts;
    $views_manager->update_for_conflicts;
    $views_manager->set_dirty();

    # set colour for all buttons on main window, "Schedules" tab
    $self->_set_view_button_colours();
}


=head1 PRIVATE METHODS

=head2 _add_guiblock( GuiBlock )

Adds the GuiBlock to the list of GuiBlocks on the View. Returns the View object.

=cut

sub _add_guiblock {
    my $self     = shift;
    my $guiblock = shift;
    $self->{-guiblocks} = {} unless $self->{-guiblocks};

    # save
    $self->{-guiblocks}->{ $guiblock->id } = $guiblock;
    return $self;
}

=head2 _remove_all_guiblocks()

Remove all Guiblocks associated with this View.

=cut

sub _remove_all_guiblocks {
    my $self = shift;
    $self->{-guiblocks} = {};
    return $self;
}

=head2 _setup_for_assignable_blocks()

Find all 1/2 blocks and turn them into AssignBlocks

=cut

sub _setup_for_assignable_blocks {
    my $self = shift;
    my $type = $self->type;
    
    # don't do this for 'stream' types
    return unless lc($type) eq 'lab' || lc($type) eq 'teacher';

    #Loop through each half hour time slot,
    # and create and draw AsignBlock for each
    my @assignable_blocks;
    foreach my $day ( 1 ... 5 ) {
        foreach my $time_start ( $Earliest_time * 2 ... ( $Latest_time * 2 ) - 1 ) {
            push @assignable_blocks,
              AssignBlockTk->new( $self, $day, $time_start / 2 );
        }
    }

    $self->gui->setup_assign_blocks( \@assignable_blocks, \&_cb_assign_blocks );
}


=head2 _get_conflict_info()

What types of conflicts are there?  What colours should they be?

=cut

sub _get_conflict_info {
    my $self = shift;

    my @conflict_info;

    foreach my $c ( Conflict::TIME_TEACHER, Conflict::TIME,
                    Conflict::LUNCH, Conflict::MINIMUM_DAYS,
                    Conflict::AVAILABILITY
      )
    {
        my $bg = Colour->new( Conflict->Colours->{$c} );
        my $fg = Colour->new("white");
        $fg = Colour->new("black") if $bg->isLight;
        my $text = Conflict->get_description($c);
        push @conflict_info, { -bg => $bg->string, -fg => $fg->string, -text => $text };
    }
    return \@conflict_info;

}

=head2 _get_named_scheduable_for_popup( "teacher" | "lab" | "stream" )

For this view, find all scheduable objects that are the same type as
this view, but not including the scheduable associated with this view

B<Parameters> 

- type => type of scheduable object (Teacher/Lab/Stream)

B<Returns>

ptr to array of NamedObjects, with the object being a Teacher/Lab/Stream

=cut

sub _get_named_scheduable_for_popup {
    my $self = shift;
    my $type = shift;

    # get all scheduables
    my $all_scheduables = AllScheduables->new( $self->schedule );

    # get only the scheduables that match the type of this view
    my $scheduables_by_type = $all_scheduables->by_type($type);
 
    # remove the scheduable object that is associated with this view
    my @named_schedulable_objects =
      grep { $_->object->id != $self->scheduable->id }
      @{$scheduables_by_type->named_scheduable_objs};

    return \@named_schedulable_objects;
    
}

=head2 _set_view_button_colours() 
    
In the main window, in the schedules tab, there are buttons that
are used to call up the various Schedule Views.  

This function
will colour those buttons according to the maximum conflict
for that given view    
    
=cut

sub _set_view_button_colours {
    my $self = shift;

    if ( $self->views_manager ) {
        $self->views_manager->determine_button_colours();
    }

}

=head2 _set_status_undo_info() 

Writes info to status bar about undo/redo status

=cut

sub _set_status_undo_info {
    my $self = shift;
    $Undo_number = scalar $self->views_manager->undoes . " undoes left";

    $Redo_number = scalar $self->views_manager->redoes . " redoes left";

}


=head2 _snap_gui_block( GuiBlock )

Takes the guiblock and forces it to be located on the nearest 
day and 1/2 hour boundary

B<Parameters>

- guiblock => guiblock that is being moved

=cut

sub _snap_gui_block {
    my $self     = shift;
    my $guiblock = shift;
    if ($guiblock) {
        $guiblock->block->snap_to_day( 1, scalar(@days) );
        $guiblock->block->snap_to_time( min( keys %times ),
                                        max( keys %times ) );
    }
}




=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns - 2016

Sandy Bultena 2020

Updat

=head1 COPYRIGHT

Copyright (c) 2016, Jack Burns, Sandy Bultena, Ian Clement.

Copyright (c) 2021, Sandy Bultena 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut

1;
