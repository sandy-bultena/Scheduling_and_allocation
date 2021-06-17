use strict;
use warnings;

package GuiScheduleTk;
use FindBin;
use lib "$FindBin::Bin/..";
use SchedulerManagerTk;
my $mw;

sub new {
    my $class = shift;
    my $gui   = shift;
    my $self  = bless {};
    $self->{-maingui} = $gui;
    $self->main_window( $gui->mw );
    return $self;
}

sub mw {
    my $self = shift;
    return $self->{-mainWindow};
}

=head2 main_window ( [MainWindow] )

Get/sets the MainWindow for this GuiSchedule object.

=cut

sub main_window {
    my $self = shift;
    $self->{-mainWindow} = shift if @_;
    return $self->{-mainWindow};
}

=head2 add_button_refs ( \button, Teacher/Lab/Stream Object )

Adds a button reference to the hash of all button references and the 
Object it is associated to.

=cut

sub add_button_refs {
    my $self = shift;
    my $btn  = shift;
    my $obj  = shift;
    $self->{-buttonRefs} = {} unless $self->{-buttonRefs};

    # save
    $self->{-buttonRefs}->{$obj} = $btn;
    return $self;
}

=head2 _button_refs 

Returns a hash of all button hashes for this GuiSchedule object

=cut

sub _button_refs {
    my $self = shift;
    return $self->{-buttonRefs};
}

=head2 reset_button_refs 

Resets the hash of button references for this GuiSchedule object.

=cut

sub reset_button_refs {
    my $self = shift;
    $self->{-buttonRefs} = {};
}

sub set_button_colour {
    my $self          = shift;
    my $obj           = shift;
    my $view_conflict = shift;

    # get the button associated to the current teacher/lab/stream
    my $button_ptrs = $self->_button_refs;
    my $btn         = $button_ptrs->{$obj};

    # set button colour to conflict colour if there is a conflict
    my $colour = $SchedulerManagerTk::Colours->{ButtonBackground};
    if ($view_conflict) {
        $colour = Conflict->Colours->{$view_conflict} || 'red';
    }
    my $active = Colour->darken( 10, $colour );
    if ( $btn && $$btn ) {
        $$btn->configure( -background       => $colour,
                          -activebackground => $active );
    }
}

=head2 create_frame ( Frame, Type )

Populates frame with buttons for all Teachers, Labs or Streams depending on Type in alphabetical order.

=cut

sub create_buttons_for_frame {

    my $self         = shift;
    my $frame        = shift;
    my $view_choices = shift;
    my $command_sub  = shift || \&create_new_view;
    my $ordered      = $view_choices->named_scheduable_objs;
    my $type         = $view_choices->type;

    my $row = 0;
    my $col = 0;

    # determine how many buttons should be on one row
    my $arr_size = scalar @{$ordered};
    my $divisor  = 2;
    if ( $arr_size > 10 ) { $divisor = 4; }

    # for every view choice object
    foreach my $named_scheduable_obj (@$ordered) {
        my $name = $named_scheduable_obj->name;

        # create the command array reference including the GuiSchedule,
        # the Teacher/Lab/Stream, it's type
        my $command = [ $command_sub, $self, $named_scheduable_obj->object, $type ];

        # create the button on the frame
        my $btn = $frame->Button(
                                  -text    => $named_scheduable_obj->name,
                                  -command => $command
          )->grid(
                                          -row    => $row,
                                          -column => $col,
                                          -sticky => "nsew",
                                          -ipadx  => 30,
                                          -ipady  => 10
          );

        # pass the button reference the the event handler.
        push( @{$command}, \$btn );

        # add it to hash of button references
        $self->add_button_refs( \$btn, $named_scheduable_obj->object );

        $col++;

        # reset to next row
        if ( $col >= ( $arr_size / $divisor ) ) { $row++; $col = 0; }
    }

}


=head2 _close_view ( View )

Closes the selected View.

=cut

sub close_view {
    my $self = shift;
    my $view = shift;

    my $toplevel = $view->toplevel;

    $self->remove_view($view);
    $self->add_guischedule_to_views;
    $toplevel->destroy;
}


1
