#!/usr/bin/perl
use strict;
use warnings;

package DataEntry;
use FindBin;
use Carp;
use lib "$FindBin::Bin/..";
use GUI::DataEntryTk; 

=head1 NAME

DataEntry - provides methods/objects for entering teachers/labs/etc data  

=head1 VERSION

Version 6.00

=head1 SYNOPSIS

    use Schedule::Schedule;
    use Presentation::ViewsManager;
    use GUI::DataEntryTk;
    
    my $Dirtyflag   = 0;
    my $mw          = MainWindow->new();
    my $Schedule = Schedule->read_YAML('myschedule_file.yaml');
    my $views_manager = ViewsManager->new( $mw, \$Dirtyflag, \$Schedule );
    
    # create a data entry list
    # NOTE: requires $views_manager just so that it can update
    #       the views if data has changed (via the dirty flag)
    
    my $de = DataEntry->new( $mw, $Schedule->teachers, 
                    $Schedule, \$Dirtyflag, $views_manager );

=head1 DESCRIPTION

A generic data entry widget

=head1 PUBLIC PROPERTIES

=cut

# =================================================================
# Class Variables
# =================================================================
our $Max_id = 0;
my @Delete_queue;
my $views_manager;
my $room_index = 1;
my $id_index   = 0;

# =================================================================
# Properties
# =================================================================

=head2 gui 

Gets/Sets DataEntryTk object

=cut 

sub gui {
    my $self = shift;
    $self->{-gui} = shift if @_;
    return $self->{-gui};
}

=head2 schedule 

Gets/Sets Schedule object

=cut 
sub schedule {
    my $self = shift;
    $self->{-schedule} = shift if @_;
    return $self->{-schedule};
}


=head2 dirty

Sets the dirty_flag pointer (has the schedule been changed since the last save?)

=cut 
sub dirty {
    my $self = shift;
    ${$self->_dirty_ptr} = shift if @_;
    return ${$self->_dirty_ptr};
}

sub _dirty_ptr {
    my $self = shift;
    $self->{-dirty_ptr} = shift if @_;
    return $self->{-dirty_ptr};
}

=head2 type 

Gets Scheduable type (teacher|lab|stream)

=cut 
sub type {
    my $self = shift;
    return $self->schedule->get_scheduable_object_type(
                                                   $self->scheduable_list_obj );
}

=head2 scheduable_class 

Gets Schedulable class name ( Teacher | Lab | Stream )

=cut 
sub scheduable_class {
    my $self = shift;
    my $type = $self->type;
    my $class = ucfirst($type);
}

=head2 schedule_list_obj 

Gets/Sets the object containing the list of scheduable objects
(Teachers | Labs | Streams)

=cut 
sub scheduable_list_obj {
    my $self = shift;
    $self->{-list_obj} = shift if @_;
    return $self->{-list_obj};
}

=head2 col_titles

Gets/Sets the titles for each individual column

=cut 
sub col_titles {
    my $self = shift;
    $self->{-col_titles} = shift if @_;
    return $self->{-col_titles};
}

=head2 col_widths

Gets/Sets the widths required for each individual column

=cut 
sub col_widths {
    my $self = shift;
    $self->{-col_widths} = shift if @_;
    return $self->{-col_widths};
}

# =================================================================
# new
# =================================================================
=head1 PUBLIC METHODS

=head2 new ()

creates the basic Data Entry (simple matrix)

B<Inputs>

=over

=item * Tk frame where to draw data entry widgets

=item * Scheduable Collection object (Teachers | Labs | Streams)

=item * the schedule object

=item * reference to the dirty pointer

=item * views_manager - the object that manages the views

=back

B<Returns>

data entry object

=cut

# ===================================================================
# new
# ===================================================================
sub new {
    my $class               = shift;  # class
    my $frame               = shift;  # frame where new GUI stuff is attached to
    my $scheduable_list_obj = shift;  # (teachers, labs, streams, etc)
    my $schedule            = shift;  # the actual schedule object
    my $dirty_ptr           = shift;  # has the data changed
    $views_manager = shift;           # the object containing all GUI stuff

    undef @Delete_queue;

    my $self = bless {}, $class;
    $self->_dirty_ptr($dirty_ptr);
    $self->scheduable_list_obj($scheduable_list_obj);
    $self->schedule($schedule);

    # ---------------------------------------------------------------
    # get objects to process?
    # ---------------------------------------------------------------
    my @objs = $scheduable_list_obj->list;
    my $rows = scalar(@objs);

    # ---------------------------------------------------------------
    # what are the columns?
    # ---------------------------------------------------------------
    my @methods;
    my @titles;
    my @disabled;
    my @widths;
    my $sortby;
    my $delete_sub = sub { };
    my $de;

    if ( $self->type eq 'teacher' ) {
        push @methods, qw(id firstname lastname release);
        push @titles, ( 'id', 'first name', 'last name', 'RT' );
        push @widths, qw(4 20 20 8);
        $sortby = 'lastname';
    }

    if ( $self->type eq 'lab' ) {
        push @methods, qw(id number descr);
        push @titles, ( 'id', 'room', 'description' );
        push @widths, qw(4 7 40 );
        $sortby = 'number';
    }

    if ( $self->type eq 'stream' ) {
        push @methods, qw(id number descr);
        push @titles, ( 'id', 'number', 'description' );
        push @widths, qw(4 10 40 );
        $sortby = 'number';
    }

    $self->_col_sortby($sortby);
    $self->_col_methods( \@methods );
    $self->col_titles( \@titles );
    $self->col_widths( \@widths );

    # ---------------------------------------------------------------
    # create the table entry object
    # ---------------------------------------------------------------
    my $gui = DataEntryTk->new( $self, $frame, \&_cb_delete_obj, \&_cb_save );
    $self->gui($gui);

    my $row = $self->refresh;

    return $self;
}

# =================================================================
# refresh the tables
# =================================================================
=head2 refresh

B<Parameters>

- list_obj => Scheduable Collection object (Teachers | Labs | Streams )

=cut
sub refresh {
    my $self     = shift;
    my $list_obj = shift;

    $self->scheduable_list_obj($list_obj) if $list_obj;

    my $objs   = $self->scheduable_list_obj->list;
    my $sortby = $self->_col_sortby;

    # create a 2-d array of data that needs to be displayed
    my @data;
    foreach my $obj ( sort { $a->$sortby cmp $b->$sortby } @$objs ) {
        my @row;
        foreach my $method ( @{ $self->_col_methods } ) {
            push @row, $obj->$method();
        }
        push @data, \@row;
    }

    # refresh the gui
    $self->gui->refresh( \@data );

    undef @Delete_queue;

}

# =================================================================
# Save updated data
# =================================================================
my $currently_saving = 0;

=head1 CALLBACKS (EVENT HANDLERS)

=head2 _cb_save

save any changes that the user entered in the gui form

=cut
sub _cb_save {

    # get inputs
    my $self     = shift;
    my $schedule = $self->schedule;

    my $dirty_flag = 0;

    # get data from gui object
    my $all_data = $self->gui->get_all_data();
    
    # just in case saving is already in process, wait before continuing
    return if $currently_saving > 2;  # too much at once
    sleep(1) if $currently_saving;
    $currently_saving++;

    # read data from data object
    foreach my $row ( @$all_data) {
        my @data = @$row;

        # if this is an empty row, do nothing
        next if @data == grep { !$_ } @data;

        # --------------------------------------------------------------------
        # if this row has an ID, then we need to update the
        # corresponding object
        # --------------------------------------------------------------------
        if ( defined $data[$id_index] && !( $data[$id_index] eq '' ) ) {

            no strict 'refs';
            my $scheduable_list_obj = $self->{-list_obj};
            my $o = $scheduable_list_obj->get( $data[$id_index] );

            # loop over each method used to get info about this object
            my $col = 1;
            foreach my $method ( @{ $self->_col_methods } ) {
                no warnings;

               # set dirty flag if new data is not the same as the currently set
               # property
                $dirty_flag++ if $o->$method() ne $data[ $col - 1 ];

                # set the property to the data
                eval {$o->$method($data[$col-1]);};

                $col++;
            }
        }

        # --------------------------------------------------------------------
        # if this row does not have an ID, then we need to create
        # corresponding object
        # --------------------------------------------------------------------
        else {
            my $scheduable_list_obj = $self->{-list_obj};

            # create parameters to pass to new
            my %parms;
            my $col = 1;
            foreach my $method ( @{ $self->_col_methods } ) {
                $parms{ '-' . $method } = $data[ $col - 1 ];
                $col++;
            }

            # create new object and add to the list
            my $new;
            eval {
                $new = $self->scheduable_class->new(%parms);
                $scheduable_list_obj->add($new);
            };

            # No errors?
            if ( $new && !$@ ) {
                $dirty_flag++;
            }

        }
    }

    # ------------------------------------------------------------------------
    # go through delete queue and apply changes
    # ------------------------------------------------------------------------
    while ( my $d = shift @Delete_queue ) {

        no strict 'refs';
        my $scheduable_list_obj = shift @$d;
        my $o                   = shift @$d;

        if ($o) {
            $dirty_flag++;
            if ( $self->type eq 'teacher' ) {
                $schedule->remove_teacher($o);
            }
            elsif ( $self->type eq 'stream' ) {
                $schedule->remove_stream($o);
            }
            elsif ( $self->type eq 'lab' ) {
                $schedule->remove_lab($o);
            }

        }
    }

    # if there have been changes, set global dirty flag, and do what is necessary
    $self->_set_dirty() if $dirty_flag;
    $currently_saving = 0;
    
}

# =================================================================
# delete object
# =================================================================
=head2 _cb_delete_obj

save delete requests, to be processed later

=cut
sub _cb_delete_obj {
    my $self = shift;
    my $data = shift;

    # create a queue so that we can delete the objects
    # when the new info is saved

    my $obj = $self->scheduable_list_obj->get( $data->[$id_index] );
    push @Delete_queue, [ $self->scheduable_list_obj, $obj ] if $obj;
}

# =================================================================
# set dirty flag
# =================================================================
=head1 PRIVATE PROPERTIES AND METHODS

=head2 _col_methods

Gets/Sets the methods required to get or set the property for each column

=cut 
sub _col_methods {
    my $self = shift;
    $self->{-col_methods} = shift if @_;
    return $self->{-col_methods};
}

=head2 _col_sortby

Gets/Sets the method which gets the property which tells 
us how to sort the individual objects

=cut 
sub _col_sortby {
    my $self = shift;
    $self->{-col_sortby} = shift if @_;
    return $self->{-col_sortby};
}

=head2 _set_dirty

Data has changed, process accordingly

=cut
sub _set_dirty {
    my $self = shift;
    $self->dirty(1);
    $self->refresh ;
    $views_manager->redraw_all_views if $views_manager;
}

# =================================================================
# footer
# =================================================================

=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns

=head1 COPYRIGHT

Copyright (c) 2020, Jack Burns, Sandy Bultena, Ian Clement. 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut

1;

