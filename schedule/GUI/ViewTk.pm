#!/usr/bin/perl
use strict;
use warnings;

package ViewTk;

our @ISA = qw(ViewBaseTk);

use Tk;

=head1 NAME

ViewTk - Gui code for the visual representation of a Schedule

=head1 VERSION

Version 6.00

=head1 DESCRIPTION

ViewTk is a gui interface for the View object.

B<Inherits from ViewBaseTk>

=head1 PROPERTIES

=cut

# ============================================================================
# Global variables
# ============================================================================
my $mw;
my $Clicked_block;
my $Select_colour = 'royalblue';
my $Selected_assign_block_completed_cb;

# ============================================================================
# properties
# ============================================================================

=head2 view( [View] )

B<Gets/Sets>

the View that is attached to this gui

=cut

sub view {
    my $self = shift;
    $self->{-view} = shift if @_;
    return $self->{-view};
}

# ============================================================================
# methods
# ============================================================================

=head1 METHODS

Note that the private methods start with an underscore "_"

=head2 new( View, Tk::MainWindow ) 

Creates a new ViewTk object

B<Parameters>

- view => The 'View' that is calling this function

- mw => The main Window (Tk main window)

=cut 

sub new {
    my $class = shift;
    my $view  = shift;
    $mw = shift;
    my $conflict_info = shift;

    my $self = $class->SUPER::new($mw, $conflict_info);
    $self->view($view);

    return $self;

}


=head2 setup_popup_menu( ("teacher" | "lab" | "stream"), 
        (Teacher | Lab | Stream), sub {}, sub {}, sub {})

Create a pop-up menu to be used when right-clicking a guiblock
 
Create the pop-up menu BEFORE drawing the blocks, so that it can be
bound to each block (done in $self->redraw)

B<Parameters>

- type => type of View (teacher/lab/stream)

- named_scheduables => all scheduable objects of this type

- toggle_movement_cb => callback routine to change a block from movable/unmovable

=over 

B<Inputs to Callback>

- View object

=back

- move_block_cb => callback routine if block is moved from one view to another

=over 

B<Inputs to Callback>

- View object

- Scheduable object (Teacher / Lab / Stream)

=back

=cut

sub setup_popup_menu {
    my $self               = shift;
    my $type               = shift;
    my $named_schedulables = shift;
    my $toggle_movement_cb = shift;
    my $move_block_cb      = shift;
    my $view               = $self->view;

    # create menu
    my $pm = $mw->Menu( -tearoff => 0 );

    # toggle block from movable to unmovable
    $pm->command( -label   => "Toggle Moveable/Fixed",
                  -command => [ $toggle_movement_cb, $view ], );

    # create sub menu
    my $mm = $pm->cascade( -label => 'Move Class to', -tearoff => 0 );

    foreach my $named_schedulable (@$named_schedulables) {
        $mm->command(
               -label   => $named_schedulable->name,
               -command => [ $move_block_cb, $view, $named_schedulable->object ]
        );
    }

    # save
    $self->_popup_menu($pm);
}


=head2 setup_undo_redo( \number, \number, sub {} )
 
Setup the gui to show undo/redo numbers, add actions to the main menu, and add 
shortcut keys

B<Parameters>

- undo_number_ptr => the address of the undo_number maintained by the View object

- redo_number_ptr => the address of the redo_number maintained by the View object

- callback => the callback function that does the undo or redo

=over

B<Inputs to Callback>

- type => a string, either 'undo' or 'redo'

=back

=cut

sub setup_undo_redo {
    my $self            = shift;
    my $undo_number_ptr = shift;
    my $redo_number_ptr = shift;
    my $callback        = shift;
    my $tl              = $self->_toplevel;

    # ---------------------------------------------------------------
    # bind keys
    # ---------------------------------------------------------------
    $tl->bind( '<Control-KeyPress-z>' => sub {$callback->($self->view, 'undo' )} );
    $tl->bind( '<Meta-Key-z>'         => sub {$callback->($self->view, 'undo' )} );

    $tl->bind( '<Control-KeyPress-y>' => sub {$callback->($self->view, 'redo' )} );
    $tl->bind( '<Meta-Key-y>'         => sub {$callback->($self->view, 'redo' )} );

    # ---------------------------------------------------------------
    # add undo/redo to main menu
    # ---------------------------------------------------------------
    my $mainMenu = $self->_main_menu;
    $mainMenu->add(
                    'command',
                    -label   => "Undo",
                    -command => sub {$callback->($self->view, 'undo' )},
    );
    $mainMenu->add(
                    'command',
                    -label   => "Redo",
                    -command => sub {$callback->($self->view, 'redo' )},
    );

    # ---------------------------------------------------------------
    # add undo/redo to status_frame
    # ---------------------------------------------------------------
    my $status_frame = $self->_status_bar;
    $status_frame->Label(
                          -textvariable => $undo_number_ptr,
                          -borderwidth  => 1,
                          -relief       => 'ridge',
                          -width        => 15
    )->pack( -side => 'right', -fill => 'x' );

    $status_frame->Label(
                          -textvariable => $redo_number_ptr,
                          -borderwidth  => 1,
                          -relief       => 'ridge',
                          -width        => 15
    )->pack( -side => 'right', -fill => 'x' );

}

# ============================================================================
# Assign blocks
# ============================================================================

=head1 Assign Blocks Methods

=head2 setup_assign_blocks( \@AssignBlock, sub {}) 
 
Assign blocks are 1/2 hr sections that can be selected, and then, if desired,
used to create guiblocks.

B<Parameters>

assignable_blocks => ptr to array of assignable blocks that are available

callback => callback function called once a selection of assign_blocks is complete

=over

B<Inputs to Callback>

- a ptr to a list of AssignBlock objects

=back

=cut

sub setup_assign_blocks {
    my $self              = shift;
    my $assignable_blocks = shift;
    my $callback          = shift;

    # save for later
    $Selected_assign_block_completed_cb = $callback;

    # what we are drawing on
    my $cn = $self->canvas;

    #BINDS MOUSE 1 to the setup of AssignBlock selection, then calls a function
    #to bind the mouse movement
    $cn->CanvasBind(
        '<Button-1>',
        [
           sub {
               return if $Clicked_block;   # allow another event to take control
               my $cn = shift;
               my $x  = shift;
               my $y  = shift;

               # if mouse is not on an assignable block, bail out
               my $assblock = AssignBlock->find( $x, $y, $assignable_blocks );
               return unless $assblock;

               # get day of assignable block that was clicked
               my $day = $assblock->day();

               # set mouse_motion binding
               $self->_prepare_to_select_assign_blocks( $cn, $day, $x, $y,
                                                        $assignable_blocks );
           },
           Ev('x'),
           Ev('y')
        ]
    );

}

=head2 _prepare_to_select_assign_blocks( Tk::Canvas, day, x,y, \[AssignBlock...] ) 
  
Binds mouse movement for selecting AssignBlocks 

Binds mouse release for processing selected AssignBlocks

and we want to add (or subtract) any AssignBlocks if the
mouse passes over said blocks.

Once the mouse has been pressed (see setup_assign_blocks), the selection of 
'selectable'  AssignBlocks is limited to the day of the initial selection.


B<Parameters>

- cn => canvas object

- day => day of the first selection

- x1,y1 => canvas coordinates of the mouse when it was initially clicked

- all_blocks => ptr to array of all assignable blocks

=cut

sub _prepare_to_select_assign_blocks {
    my $self       = shift;
    my $cn         = shift;
    my $day        = shift;
    my $x1         = shift;
    my $y1         = shift;
    my $all_blocks = shift;

    my @selected_assigned_blocks;

    #Get a list of all the AssignBlocks associated with a given day
    my @day_blocks = grep { $_->day == $day } @$all_blocks;

    #Binds motion to a motion sub to handle the selection of multiple time slots
    #when moving mouse
    $cn->CanvasBind(
                     '<Motion>',
                     [
                        \&_selecting_assigned_blocks,
                        Ev('x'), Ev('y'), \$x1, \$y1,
                        \@selected_assigned_blocks, \@day_blocks,
                     ]
    );

    #Binds the release of Mouse 1 process the selection of AssignBlocks
    $cn->CanvasBind(
        '<ButtonRelease-1>',
        [
           sub {
               my $cn                       = shift;
               my $x                        = shift;
               my $y1                       = shift;
               my $y2                       = shift;
               my $selected_assigned_blocks = shift;

               #Unbind everything
               $cn->CanvasBind( '<Motion>',          sub { } );
               $cn->CanvasBind( '<ButtonRelease-1>', sub { } );

               my $something_to_do =
                 $selected_assigned_blocks && @$selected_assigned_blocks;
               return unless $something_to_do;

               $self->_selectedAssignBlocks( $cn, $selected_assigned_blocks );
           },
           $x1,
           $y1,
           Ev('y'),
           \@selected_assigned_blocks
        ]
    );
}

=head2 _selecting_assigned_blocks( Tk::Canvas, x2,y2, x1,y1, \[AssignBlock,..], \[AssignBlock,..] )

Called when mouse is moving, and in the process of selecting AssignBlocks

B<Parameters>

- cn => canvas object

- x2,y2 => current position of mouse

- x1,y1 => position of mouse when first clicked

- selected_assigned_blocks => ptr to array of selected AssignBlocks 
                              (reset in this routine)

- day_blocks => ptr to list of AssignBlocks for the day (when the mouse was
                first clicked, the 'day' was calcuated)

=cut 

sub _selecting_assigned_blocks {
    my $cn                       = shift;
    my $x2                       = shift;
    my $y2                       = shift;
    my $x1                       = shift;
    my $y1                       = shift;
    my $selected_assigned_blocks = shift;
    my $day_blocks               = shift;

    #Temporarily unbind motion
    $cn->CanvasBind( '<Motion>', sub { } );

    #get the AssignBlocks currently under the selection window
    @$selected_assigned_blocks =
      AssignBlock->in_range( $$x1, $$y1, $x2, $y2, $day_blocks );

    #colour selection blue
    foreach my $blk (@$day_blocks) {
        $blk->unfill;
    }
    foreach my $blk (@$selected_assigned_blocks) {
        $blk->set_colour($Select_colour);
    }

    #rebind Motion
    $cn->CanvasBind(
                     '<Motion>',
                     [
                        \&_selecting_assigned_blocks,
                        Ev('x'), Ev('y'), $x1, $y1, $selected_assigned_blocks,
                        $day_blocks
                     ]
    );

}

=head2 _selectedAssignBlocks( Tk::Canvas, \[AssignBlock,..] )

Mouse is up, AssignBlocks have been selected.  Deal with it!

Calls the callback routine defined in setup_assign_blocks

B<Parameters> 

-cn => canvas object

-selected_assigned_blocks => ptr to array of selected AssignBlocks

=cut

sub _selectedAssignBlocks {
    my $self                     = shift;
    my $cn                       = shift;
    my $selected_assigned_blocks = shift;

    #Unbind everything
    $cn->CanvasBind( '<Motion>',          sub { } );
    $cn->CanvasBind( '<ButtonRelease-1>', sub { } );

    my $something_to_do =
      $selected_assigned_blocks && @$selected_assigned_blocks;
    return unless $something_to_do;

    $Selected_assign_block_completed_cb->($selected_assigned_blocks);
}

# ============================================================================
# Dragging Guiblocks around
# ============================================================================

=head1 Dragging Guiblocks Methods

=head2 set_bindings_for_dragging_guiblocks( View, GuiBlock, sub {}, sub {}, sub {})

Create the necessary binding to allow guiblocks to be grabbed from one
place and dropped into another place

B<Parameters>

- view => View object that called this routine

- giublock => What object are we going to bind the methods to? 

- moving_cb => callback to invoke while the guiblock is being moved

=over

B<Inputs to Callback>

- view => View Object

- guiblock => the original obj_to_bind_to

=back

- after_release_cb => callback to invoke when the dragging has stopped

=over 

B<Inputs to Callback>

- view => View Object

- guiblock => the original obj_to_bind_to

=back

- update_after_cb => callback to invoke when everything is finished and
                     maybe updates are required
                     
=over 

B<Inputs to Callback>

- view => View Object

- guiblock => the original obj_to_bind_to

=back

=cut

sub set_bindings_for_dragging_guiblocks {
    my $self     = shift;
    my $view     = shift;
    my $guiblock = shift;
    $self->{-moving_cb}        = shift || sub { return; };
    $self->{-after_release_cb} = shift || sub { return; };
    $self->{-update_after_cb}  = shift || sub { return; };

    # get the actual canvas objects that make up this object
    my $group_of_canvas_objs = $guiblock->group;

    $self->canvas->bind(
        $group_of_canvas_objs,    # objects to bind to
        "<1>",                    # bind event
        [                         # start of Tk::Callback
           \&_select_guiblock_to_move,    # function ptr
           $guiblock,                     # the object that was bound
           $self,                         # this ViewTk object
           $view,                         # the view object (View)
           Tk::Ev("x"),                   # the x-position of the mouse
           Tk::Ev("y"),                   # the y-position of the mouse
        ]
    );
}

=head2 _select_guiblock_to_move( GuiBlock, ViewTk, View, x,y )

Set up for drag and drop of GuiBlock. Binds motion and button release 
events to GuiBlock.

B<Parameters>

- guiblock => guiblock that we want to move

- self => this ViewTk object

- view => the View object that setup these functions

- xstart, ystart => x,y position of mouse when mouse was clicked

=cut

sub _select_guiblock_to_move {

    my ( $cn, $guiblock, $self, $view, $xstart, $ystart ) = @_;
    my ( $startingX, $startingY ) = $cn->coords( $guiblock->rectangle );

    # we are processing a click on a guiblock, so tell the
    # click event for the canvas not to do anything
    $Clicked_block = 1;

    # this block is being controlled by the mouse
    $guiblock->is_controlled(1);

    # unbind any previous binding for clicking and motion,
    # just in case
    $self->canvas->CanvasBind( "<Motion>",          "" );
    $self->canvas->CanvasBind( "<ButtonRelease-1>", "" );

    # bind for mouse motion
    $cn->CanvasBind(
                     "<Motion>",
                     [
                        \&_gui_block_is_moving, $guiblock,
                        $self,                  $view,
                        $xstart,                $ystart,
                        Tk::Ev("x"),            Tk::Ev("y"),
                        $startingX,             $startingY
                     ]
    );

    # bind for release of mouse up
    $cn->CanvasBind(
                     "<ButtonRelease-1>",
                     [
                        \&_gui_block_has_stopped_moving, $self,
                        $view,                           $guiblock
                     ]
    );
}

=head2 _gui_block_is_moving( Tk::Canvas, GuiBlock, ViewTk, x,y, x,y)

Moves the GuiBlock to the cursors current position on the View.

The guiblock is moving... need to update stuff as it is being moved

Invokes moving_cb callback (defined in set_bindings_for_dragging_guiblocks)

B<Parameters>

-cn => canvas object

-guiblock => the guiblock that is moving

-self => this ViewTk object

-xstart,ystart => initial mouse position when mouse was clicked

-startingX, startingY => current mouse position

=cut

sub _gui_block_is_moving {
    my (
         $cn,     $guiblock, $self,   $view,      $xstart,
         $ystart, $xmouse,   $ymouse, $startingX, $startingY
    ) = @_;

    # temporarily dis-able motion while we process stuff
    # (keeps execution cycles down)
    $cn->CanvasBind( "<Motion>", "" );

    # raise the block
   $guiblock->gui_view->canvas->raise( $guiblock->group );

    # where block needs to go
    my $desiredX = $xmouse - $xstart + $startingX;
    my $desiredY = $ymouse - $ystart + $startingY;

    # current x/y coordinates of rectangle
    my ( $curXpos, $curYpos ) = $cn->coords( $guiblock->rectangle );

    # check for valid move
    if ( defined $curXpos && defined $curYpos ) {

        # where block is moving to
        my $deltaX = $desiredX - $curXpos;
        my $deltaY = $desiredY - $curYpos;

        # move the guiblock
        $cn->move( $guiblock->group, $deltaX, $deltaY );
        $self->_refresh_gui;

        # set the blocks new coordinates (time/day)
        $self->_set_block_coords( $guiblock, $curXpos, $curYpos );

        $self->{-moving_cb}->( $view, $guiblock );
    }

    # ------------------------------------------------------------------------
    # rebind to the mouse movements
    # ------------------------------------------------------------------------

    # what if we had a mouse up while processing this code?
    # (1) handle the stopped moving functionality
    # (2) do NOT rebind the motion even handler

    unless ( $guiblock->is_controlled ) {
        _gui_block_has_stopped_moving( $cn, $self, $view, $guiblock );
    }

    # else - rebind the motion event handler
    else {
        $cn->CanvasBind(
                         "<Motion>",
                         [
                            \&_gui_block_is_moving, $guiblock,
                            $self,                  $view,
                            $xstart,                $ystart,
                            Tk::Ev("x"),            Tk::Ev("y"),
                            $startingX,             $startingY
                         ]
        );
    }

}

=head2 _gui_block_has_stopped_moving( Tk::Canvas, ViewTk, View, GuiBlock) 

Moves the GuiBlock to the cursors current position on the View and 
updates the Blocks time in the Schedule.

Invokes after_release_cb callback (defined in set_bindings_for_dragging_guiblocks)

Invokes update_after_cb callback (defined in set_bindings_for_dragging_guiblocks)

B<Parameters>

-cn => canvas object

-self => this ViewTk object

-view => the View object

-guiblock => the gui block that has been moved

=cut

sub _gui_block_has_stopped_moving {
    my ( $cn, $self, $view, $guiblock, ) = @_;

    # it is ok now to process a click on the canvas
    $Clicked_block = 0;

    # unbind the motion on the guiblock
    $cn->CanvasBind( "<Motion>",          "" );
    $cn->CanvasBind( "<ButtonRelease-1>", "" );

    $guiblock->is_controlled(0);

    # let the view do what it needs to do once the block
    # has been dropped
    $self->{-after_release_cb}->( $view, $guiblock );

    # get the guiblocks new coordinates (closest day/time)
    my $block = $guiblock->block;
    my $coords =
      $self->_get_time_coords( $block->day_number, $block->start_number,
                              $block->duration );

    # current x/y coordinates of rectangle
    my ( $curXpos, $curYpos ) = $cn->coords( $guiblock->rectangle );

    # move the guiblock to new position
    $cn->move(
               $guiblock->group,
               $coords->[0] - $curXpos,
               $coords->[1] - $curYpos
    );
    $self->_refresh_gui;

    # update everything that needs to be updated once the block data
    # is finalized
    $self->{-update_after_cb}->( $view, $block );
}

# ============================================================================
# Double clicking guiblock
# ============================================================================

=head1 Double Clicking Methods

=cut

{
    my $callback;

=head2 bind_double_click( View, GuiBlock, sub {} )

B<Parameters>

- view => the View object that called this methods

- guiblock => the guiblock that we want to bind the double click to

- callback => callback function that handles the double click 

=over

B<Inputs to Callback>

- view => View object

- guiblock => guiblock that was double clicked

=back

=cut

    sub bind_double_click {
        my $self     = shift;
        my $view     = shift;
        my $guiblock = shift;
        $callback = shift;

        # get the actual canvas objects that make up this object
        my $group_of_canvas_objs = $guiblock->group;
        $self->canvas->bind(
            $group_of_canvas_objs,
            "<Double-1>",
            [
               \&_was_double_clicked, $view, $guiblock,

            ]
        );
    }

=head2 _was_double_clicked( View, GuiBlock )

Invokes callback defined in bind_double_click

B<Parameters>

-view => View object

-guiblock => guiblock that was double clicked

=cut

    sub _was_double_clicked {
        my $cn       = shift;
        my $view     = shift;
        my $guiblock = shift;
        $callback->( $view, $guiblock );
    }
}

# =================================================================
# footer
# =================================================================

=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns - 2016

Sandy Bultena 2020 - Major Update

=head1 COPYRIGHT

Copyright (c) 2016, Jack Burns, Sandy Bultena, Ian Clement.

Copyright (c) 2021, Sandy Bultena 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut


1;
