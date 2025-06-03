#!/usr/bin/perl
use strict;
use warnings;

package ViewBaseTk;
use FindBin;
use lib "$FindBin::Bin/..";
use Schedule::Conflict;
use Export::DrawView;
use List::Util qw( min max );
use Tk;

=head1 NAME

ViewBaseTk - Basic View with days/weeks printed on it

=head1 VERSION

Version 6.00

=head1 SYNOPSIS

    # Don't call this directly

=head1 DESCRIPTION

Base class for different types of schedule views

=head1 PUBLIC PROPERTIES

=cut

# =================================================================
# Class Variables
# =================================================================
our $Status_text      = "";
our $Immovable_colour = "#dddddd";

# =================================================================
# Public Properties
# =================================================================

=head2 mw ( [Tk::MainWindow] )

B<Gets/Sets>
a Tk MainWindow object

=cut

sub mw {
    my $self = shift;
    $self->{-mw} = shift if @_;
    return $self->{-mw};
}

=head2 popup_guiblock( [GuiBlock] )  

B<Gets/Sets> 
a guiblock object which is attached to the current popup menu

=cut

sub popup_guiblock {
    my $self = shift;
    $self->{-popup_guiblock} = shift if @_;
    return $self->{-popup_guiblock};
}

=head2 on_closing( [sub{}] ) 

B<Gets/Sets>
the callback method called when user clicks the 'X' button 
to close the window

=cut

sub on_closing {
    my $self = shift;
    $self->{-closing_callback} = shift if @_;

    if ( !defined $self->{-closing_callback} ) {
        $self->{-closing_callback} = sub {
            my $self = shift;
            $self->destroy();
          }
    }

    return $self->{-closing_callback};
}

=head2 canvas ( [Tk::Canvas] )

B<Gets/Sets> the canvas  of this View object.

=cut

sub canvas {
    my $self = shift;
    $self->{-canvas} = shift if @_;
    return $self->{-canvas};
}

=head2 current_scale 

Get/set the current scale of this View object.

=cut

sub current_scale {
    my $self = shift;
    $self->{-current_scale} = shift if @_;
    return $self->{-current_scale};
}

# =================================================================
# Public methods
# =================================================================

=head1 PUBLIC METHODS

=head2 new( Tk::MainWindow, conflict_info) 

creates a View object, does NOT draw the view.

B<Parameters>

- mw => Main Window

- conflict_info => a ptr to an array of hashes.  

Each hash has a key for the conflict text and the foreground and background colours

B<Returns>

ViewBaseTk object

=cut

sub new {
    my $class         = shift;
    my $mw            = shift;
    my $conflict_info = shift;

    my $self = {};
    bless $self, $class;
    $self->mw($mw);

    # ---------------------------------------------------------------
    # create a new toplevel window, add a canvas
    # ---------------------------------------------------------------
    my $tl = $mw->Toplevel;
    $tl->protocol( 'WM_DELETE_WINDOW', [ \&_close_view, $self ] );
    $tl->resizable( 0, 0 );

    # ---------------------------------------------------------------
    # Create bar at top to show colour coding of conflicts
    # ---------------------------------------------------------------
    my $f = $tl->Frame()->pack( -expand => 1, -fill => "x" );

    foreach my $c (@$conflict_info) {
        $f->Label(
                   -text       => $c->{-text},
                   -width      => 10,
                   -background => $c->{-bg},
                   -foreground => $c->{-fg},
        )->pack( -side => 'left', -expand => 1, -fill => "x" );
    }

    # ---------------------------------------------------------------
    # add canvas
    # ---------------------------------------------------------------
    my $cn = $tl->Canvas(
                          -height     => 700,
                          -width      => 700,
                          -background => "white"
    )->pack();

    # ---------------------------------------------------------------
    # create object
    # ---------------------------------------------------------------
    $self->canvas($cn);
    $self->_toplevel($tl);
    $self->_x_offset(1);
    $self->_y_offset(1);
    $self->_x_origin(0);
    $self->_y_origin(0);
    $self->_width_scale(100);
    $self->_horiz_scale(60);
    $self->current_scale(1);

    # ---------------------------------------------------------------
    # create scale menu
    # ---------------------------------------------------------------
    my $mainMenu = $mw->Menu();
    $tl->configure( -menu => $mainMenu );
    my $viewMenu =
      $mainMenu->cascade( -label => "View", -underline => 0, -tearoff => 0 );
    $viewMenu->command(
                        -label     => "50%",
                        -underline => 0,
                        -command   => [ \&_resize_view, $self, 0.50 ]
    );
    $viewMenu->command(
                        -label     => "75%",
                        -underline => 0,
                        -command   => [ \&_resize_view, $self, 0.75 ]
    );
    $viewMenu->command(
                        -label     => "100%",
                        -underline => 0,
                        -command   => [ \&_resize_view, $self, 1.00 ]
    );
    $self->_main_menu($mainMenu);

    # ---------------------------------------------------------------
    # if there is a popup menu defined, make sure you can make it
    # go away by clicking the toplevel (as opposed to the menu)
    # ---------------------------------------------------------------
    if ( my $pm = $self->_popup_menu ) {
        $tl->bind( '<1>', [ \&_unpostmenu, $self ] );
        $tl->bind( '<2>', [ \&_unpostmenu, $self ] );
    }

    # ---------------------------------------------------------------
    # create status bar
    # ---------------------------------------------------------------
    my $status;
    $self->_status_bar( $self->_create_status_bar($status) );

    # ---------------------------------------------------------------
    # return object
    # ---------------------------------------------------------------
    return $self;
}

=head2 set_title( string )

Sets the title of the toplevel widget

B<Parameters>

- title => text used as the title for the window

=cut

sub set_title {
    my $self  = shift;
    my $title = shift || "";
    my $tl    = $self->_toplevel();
    $tl->title($title);
}

=head2 bind_popup_menu( GuiBlock ) 

Draws the GuiBlock onto the view
Binds a popup menu if one is defined

B<Parameters>

- guiblock => object where the popup menu is being bound to

=cut

sub bind_popup_menu {
    my $self     = shift;
    my $guiblock = shift;

    # menu bound to individual gui-blocks
    $self->canvas->bind( $guiblock->group, '<3>',
                         [ \&_postmenu, $self, Ev('X'), Ev('Y'), $guiblock ] );

    return $guiblock;
}

=head2 draw_background() 

Draws the Schedule timetable on the View canvas.

=cut

sub draw_background {
    my $self = shift;
    DrawView->draw_background( $self->canvas, $self->get_scale_info );
    return;
}

=head2 unset_popup_guiblock ()

No block has a popup menu, so unset popup_guiblock

=cut

sub unset_popup_guiblock {
    my $self = shift;
    undef $self->{-popup_guiblock};
    return;
}

=head2 move_block( GuiBlock )

Moves the gui block to the appropriate place, based on the 
blocks new day and time

B<Parameters>

- guiblock => the gui block to move

=cut

sub move_block {
    my $self     = shift;
    my $guiblock = shift;
    my $block    = $guiblock->block;

    # get new coordinates of block
    my $coords =
      $self->get_time_coords( $block->day_number, $block->start_number,
                              $block->duration );

    # get current x/y of the guiblock
    my ( $curXpos, $curYpos ) =
      $guiblock->gui_view->canvas->coords( $guiblock->rectangle );

    # bring the guiblock to the front, passes over others
    $guiblock->gui_view->canvas->raise( $guiblock->group );

    # move guiblock to new position
    $guiblock->gui_view->canvas->move(
                                       $guiblock->group,
                                       $coords->[0] - $curXpos,
                                       $coords->[1] - $curYpos
    );

}

=head2 colour_block( GuiBlock )

Colours the block according to conflicts

B<Parameters>

- guiblock => the guiblock that will be coloured

- type => the type of scheduable object that this guiblock is attached to 
(Teacher/Lab/Stream)

=cut 

sub colour_block {
    my $self     = shift;
    my $guiblock = shift;
    my $type     = shift;
    my $conflict =
      Conflict->most_severe( $guiblock->block->is_conflicted, $type );

    # if the block is unmovable, then grey it out, and do not change
    # its colour even if there is a conflict
    unless ( $guiblock->block->moveable ) {
        $guiblock->change_colour($Immovable_colour);
        return;
    }

    # else ...

    # change the colour of the block to the most important conflict
    if ($conflict) {
        $guiblock->change_colour( Conflict->Colours->{$conflict} );
    }

    # no conflict found, reset back to default colour
    else {
        $guiblock->change_colour( $guiblock->colour );
    }
}

=head2 redraw() 

Redraws the View with new GuiBlocks and their positions.

=cut

sub redraw {
    my $self = shift;
    my $cn;
    eval { $cn = $self->canvas; };
    return if @!;
    my $current_scale = $self->current_scale;

    # remove everything on canvas
    $cn->delete('all');

    # redraw background (things that don't change, like time, etc)
    $self->draw_background;

    # remove any binding to the canvas itself
    $self->canvas->CanvasBind( "<1>",               "" );
    $self->canvas->CanvasBind( "<B1-Motion>",       "" );
    $self->canvas->CanvasBind( "<ButtonRelease-1>", "" );

}

=head2 get_scale_info() 

Returns a hash with the following values:

=over

=item * -xoff => x offset

=item * -yoff => y offset

=item * -xorg => x origin

=item * -yorg => y origin

=item * -xscl => x scale

=item * -yscl => y scale

=item * -scale => current scaling

=back

=cut

sub get_scale_info {
    my $self = shift;

    return {
             -xoff  => $self->_x_offset,
             -yoff  => $self->_y_offset,
             -xorg  => $self->_x_origin,
             -yorg  => $self->_y_origin,
             -xscl  => $self->_width_scale,
             -yscl  => $self->_horiz_scale,
             -scale => $self->current_scale,
    };
}

=head2 get_time_coords( day, start, duration )

Converts the times into X and Y coordinates and returns them

B<Parameters>

day => the day

start => the start time of the block

duration => number of hours for this block

=cut

sub get_time_coords {
    my $self     = shift;
    my $day      = shift;
    my $time_start    = shift;
    my $duration = shift;

    my $scl = $self->get_scale_info();
    my @coords = DrawView->get_coords( $day, $time_start, $duration, $scl );

    if (wantarray) {
        return @coords;
    }
    else {
        [@coords];
    }
}

=head2 destroy()

Close/destroy the gui window

=cut

sub destroy {
    my $self     = shift;
    my $toplevel = $self->_toplevel;
    $toplevel->destroy;
}

# =================================================================
# Private Properties
# =================================================================

=head1 Private Properties

=head2 _main_menu 

Get/set the main menu at top of View

=cut

sub _main_menu {
    my $self = shift;
    $self->{-main_menu} = shift if @_;
    return $self->{-main_menu};
}

=head2 _status_bar  

Get/set the status bar at the bottom the of View

=cut

sub _status_bar {
    my $self = shift;
    $self->{-status_bar} = shift if @_;
    return $self->{-status_bar};
}

=head2 _toplevel 

Get/set the toplevel of this View object.

=cut

sub _toplevel {
    my $self = shift;
    $self->{-toplevel} = shift if @_;
    return $self->{-toplevel};
}

=head2 _popup_menu 

Get/set the popup menu for this guiblock

=cut

sub _popup_menu {
    my $self = shift;
    $self->{-popup} = shift if @_;
    return $self->{-popup};
}

=head2 _x_offset 

Get/set the _x_offset of this View object.

=cut

sub _x_offset {
    my $self = shift;
    $self->{-x_offset} = shift if @_;
    return $self->{-x_offset};
}

=head2 _y_offset 

Get/set the _y_offset of this View object.

=cut

sub _y_offset {
    my $self = shift;
    $self->{-y_offset} = shift if @_;
    return $self->{-y_offset};
}

=head2 _x_origin 

Get/set the _x_origin of this View object.

=cut

sub _x_origin {
    my $self = shift;
    $self->{-x_origin} = shift if @_;
    return $self->{-x_origin};
}

=head2 _y_origin 

Get/set the _y_origin of this View object.

=cut

sub _y_origin {
    my $self = shift;
    $self->{-y_origin} = shift if @_;
    return $self->{-y_origin};
}

=head2 _width_scale 

Get/set the width scale of this View object.

=cut

sub _width_scale {
    my $self = shift;
    $self->{-width_scale} = shift if @_;
    return $self->{-width_scale};
}

=head2 _horiz_scale 

Get/set the horizontal scale of this View object.

=cut

sub _horiz_scale {
    my $self = shift;
    $self->{-horiz_scale} = shift if @_;
    return $self->{-horiz_scale};
}

# =================================================================
# Private Methods
# =================================================================

=head1 Private Methods

=head2 _resize_view( number )

B<Parameters>

- scale => scale that the view will be resized to.

Resizes the View to the new Scale

=cut

sub _resize_view {
    my $self  = shift;
    my $scale = shift;

    # get height and width of toplevel
    my $window_height = $self->_toplevel->height;
    my $window_width  = $self->_toplevel->width;

    # get height and width of canvas
    my @heights       = $self->canvas->configure( -height );
    my $canvas_height = $heights[-1];
    my @widths        = $self->canvas->configure( -width );
    my $canvas_width  = $widths[-1];

    # get current scaling sizes
    my $x_origin      = $self->_x_origin;
    my $y_origin      = $self->_y_origin;
    my $horiz_scale   = $self->_horiz_scale;
    my $width_scale   = $self->_width_scale;
    my $current_scale = $self->current_scale;

    # reset scales back to default value
    $x_origin      /= $current_scale;
    $y_origin      /= $current_scale;
    $width_scale   /= $current_scale;
    $horiz_scale   /= $current_scale;
    $window_height /= $current_scale;
    $window_width  /= $current_scale;
    $canvas_height /= $current_scale;
    $canvas_width  /= $current_scale;

    $current_scale = $scale;

    # set scales to new size
    $x_origin      *= $scale;
    $y_origin      *= $scale;
    $width_scale   *= $scale;
    $horiz_scale   *= $scale;
    $window_height *= $scale;
    $window_width  *= $scale;
    $canvas_height *= $scale;
    $canvas_width  *= $scale;

    # set the new scaling sizes
    $self->_x_origin($x_origin);
    $self->_y_origin($y_origin);
    $self->_horiz_scale($horiz_scale);
    $self->_width_scale($width_scale);
    $self->current_scale($current_scale);

    # set height and width of canvas and toplevel
    $self->canvas->configure( -width  => $canvas_width,
                              -height => $canvas_height );
    $self->_toplevel->configure( -width  => int($window_width),
                                 -height => int($window_height) );

    # now that you have changed sizes etc, redraw
    $self->redraw();

}

=head2 _refresh_gui()

Forces the graphics to update

=cut

sub _refresh_gui {
    my $self = shift;
    $self->{-mw}->update;
}

=head2 _create_status_bar ()
 
Status bar at the bottom of each View to show current movement type. 

=cut

sub _create_status_bar {
    my $self = shift;

    return if $self->_status_bar;

    my $status_frame =
      $self->_toplevel->Frame(
                               -borderwidth => 0,
                               -relief      => 'flat',
      )->pack( -side => 'bottom', -expand => 0, -fill => 'x' );

    $status_frame->Label(
                          -textvariable => \$Status_text,
                          -borderwidth  => 1,
                          -relief       => 'ridge',
    )->pack( -side => 'left', -expand => 1, -fill => 'x' );

    return $status_frame;
}

=head2 _postmenu( Tk::Canvas, ViewBaseTk, x,y, GuiBlock )

Posts (shows) the popup menu at location X,Y

B<Parameters>

- c => Tk::Canvas object

- self => this ViewBaseTk object

- x,y => the x,y position of the mouse

- guiblock => the guiblock associated with the popup menu 

=cut

sub _postmenu {
    ( my $c, my $self, my $x, my $y, my $guiblock ) = @_;

    if ( my $m = $self->_popup_menu ) {
        $self->popup_guiblock($guiblock);
        $m->post( $x, $y ) if $m;
    }
}

=head2 _unpostmenu( Tk::Canvas, ViewBaseTk )

Removes the Context Menu.

B<Parameters>

- c => Tk::Canvas object

- self => this ViewBaseTk object

=cut

sub _unpostmenu {
    my ( $c, $self ) = @_;
    if ( my $m = $self->_popup_menu ) {
        $m->unpost;
    }
    $self->unset_popup_guiblock();
}

=head2 _close_view() 

Close the current View.

=cut

sub _close_view {
    my $self = shift;
    $self->on_closing->();
}

=head2 _set_block_coords( GuiBlock,  x,y, scale_number)

Converts the X and Y coordinates into times and sets the time to the Block associated with the guiblock

B<Parameters>

- guiblock => the guiblock that was moved

- x,y => the x,y position of the block

- scl => the scale information

=cut

sub _set_block_coords {
    my $self     = shift;
    my $guiblock = shift;
    my $x        = shift;
    my $y        = shift;
    my $scl      = $self->get_scale_info;

    return unless $guiblock;

    my ( $day, $time, $duration ) =
      DrawView->coords_to_day_time_duration( $x, $y, $y, $scl );
    $guiblock->block->day_number($day);
    $guiblock->block->start_number($time);
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
