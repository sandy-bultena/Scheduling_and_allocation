from tkinter import *

MOVABLE_TAG_NAME = "movable"


def main():
    mw: Tk = Tk()

    canvas: Canvas = Canvas(mw)
    canvas.pack(expand=1, fill='both')

    r1: int = canvas.create_rectangle(50, 50, 150, 150, fill='blue', tags=(MOVABLE_TAG_NAME, "obj1"))
    s1: int = canvas.create_text(100, 100, text="A", tags=(MOVABLE_TAG_NAME, "obj1"))
    r2: int = canvas.create_rectangle(70, 70, 170, 170, fill='red', tags=(MOVABLE_TAG_NAME, "obj2"))
    s2: int = canvas.create_text(120, 120, text="B", tags=(MOVABLE_TAG_NAME, "obj2"))

    canvas.tag_bind(MOVABLE_TAG_NAME, "<Button-1>", lambda e: select_gui_block_to_move(canvas, e))

    mw.mainloop()


def select_gui_block_to_move(canvas: Canvas, event: Event):
    obj: tuple[int, ...] = canvas.find_withtag('current')
    tags: tuple[str] = tuple(filter(lambda x: x != MOVABLE_TAG_NAME and x != 'current', canvas.gettags(obj[0])))
    canvas.tag_raise(tags, 'all')

    # unbind any previous binding for clicking and motion, just in case
    canvas.bind("<Motion>", "")
    canvas.bind("<ButtonRelease-1>", "")
    canvas.tag_bind(MOVABLE_TAG_NAME, "<Button-1>", "")

    # bind for mouse motion
    canvas.bind("<Motion>",
                lambda e: gui_block_is_moving(canvas, tags[0], event.x, event.y, e))

    # bind for release of mouse up
    canvas.bind("<ButtonRelease-1>", lambda e: gui_block_has_stopped_moving(canvas, tags[0], e))


def gui_block_is_moving(canvas, tag, x, y, event):
    # unbind moving while we process
    canvas.bind("<Motion>", "")

    # move the widget
    canvas.move(tag, event.x - x, event.y - y)

    # rebind for motion
    canvas.bind("<Motion>",
                lambda e: gui_block_is_moving(canvas, tag, event.x, event.y, e))


def gui_block_has_stopped_moving(canvas, tag, event):
    canvas.tag_bind(MOVABLE_TAG_NAME, "<Button-1>", lambda e: select_gui_block_to_move(canvas, e))
    canvas.bind("<Motion>", "")
    canvas.bind("<ButtonRelease-1>", "")


if __name__ == "__main__":
    main()

'''
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

    # this blocks is being controlled by the mouse
    $guiblock->is_controlled(1);

    # unbind any previous binding for clicking and motion,
    # just in case
    $self->canvas->CanvasBind( "<Motion>",          "" );
    $self->canvas->CanvasBind( "<ButtonRelease-1>", "" );

    # bind for mouse motion
    $cn->CanvasBind(
                     "<Motion>",
                     [
                        _gui_block_is_moving, $guiblock,
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
                        \&_gui_block_has_stopped_moving,
                        $self, $view, $guiblock
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

    # raise the blocks
    $guiblock->gui_view->canvas->raise( $guiblock->group );

    # where blocks needs to go
    my $desiredX = $xmouse - $xstart + $startingX;
    my $desiredY = $ymouse - $ystart + $startingY;

    # current x/y coordinates of rectangle
    my ( $curXpos, $curYpos ) = $cn->coords( $guiblock->rectangle );

    # check for valid move
    if ( defined $curXpos && defined $curYpos ) {

        # where blocks is moving to
        my $deltaX = $desiredX - $curXpos;
        my $deltaY = $desiredY - $curYpos;

        # move the guiblock
        $cn->move( $guiblock->group, $deltaX, $deltaY );
        $self->_refresh_gui;

        # set_default_fonts_and_colours the blocks new coordinates (time/day)
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

-guiblock => the gui blocks that has been moved

=cut

sub _gui_block_has_stopped_moving {
    my ( $cn, $self, $view, $guiblock, ) = @_;

    # it is ok now to process a click on the canvas
    $Clicked_block = 0;

    # unbind the motion on the guiblock
    $cn->CanvasBind( "<Motion>",          "" );
    $cn->CanvasBind( "<ButtonRelease-1>", "" );

    $guiblock->is_controlled(0);

    # let the view do what it needs to do once the blocks
    # has been dropped
    $self->{-after_release_cb}->( $view, $guiblock );

    # get_by_id the guiblocks new coordinates (closest day/time)
    my $blocks = $guiblock->blocks;
    my $coords =
      $self->get_time_coords( $blocks->day_number, $blocks->start_number,
                              $blocks->duration );

    # current x/y coordinates of rectangle
    my ( $curXpos, $curYpos ) = $cn->coords( $guiblock->rectangle );

    # move the guiblock to new position
    $cn->move(
               $guiblock->group,
               $coords->[0] - $curXpos,
               $coords->[1] - $curYpos
    );
    $self->_refresh_gui;

    # update everything that needs to be updated once the blocks data
    # is finalized
    $self->{-update_after_cb}->( $view, $blocks );
}

'''
