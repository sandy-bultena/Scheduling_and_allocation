#!/usr/bin/perl
use strict;
use warnings;

package EditBlockDialogTk;

my $Txt_lab;
my $Txt_lab_assigned;
my $Txt_teacher_assigned;
my $Txt_teacher;
my $Txt_number_of_hours;
my $Txt_block;
my $Txt_block_duration;

my $Changed = "";

my $Edit_dialog;
__setup();

# ============================================================================
# new
# ============================================================================
sub new {
    my $class          = shift;
    my $frame          = shift;
    my $title          = shift;
    my $block_id       = shift;
    $Txt_block_duration = shift;
    my $self           = bless {}, $class;
    
    $self->block_duration($Txt_block_duration);
    $self->block_id($block_id);
    $self->_tk_top_frame($frame);

    #--------------------------------------------------------
    # Creating frames and widget names
    #--------------------------------------------------------
    $Edit_dialog = $frame->DialogBox(
        -title   => $title,
        -buttons => [ 'Close', 'Delete' ]
    );

    my $top = $Edit_dialog->Subwidget("top");

    #--------------------------------------------------------
    # Block Duration Entry
    #--------------------------------------------------------

    my $duration_entry = $top->Entry(
        -textvariable    => \$Txt_block_duration,
        -validate        => 'key',
        -validatecommand => \&_is_number,
        -invalidcommand  => sub { $frame->bell },
    );

    $top->Label(
        -text   => 'Block Duration: ',
        -anchor => 'w'
    )->grid( $duration_entry, '-', '-', -sticky => 'nsew' );

    $top->Label( -text => "" )->grid( -columnspan => 4 );

    #--------------------------------------------------------
    # Teacher Add/Remove
    #--------------------------------------------------------

    $self->_tk_teacher_dropdown(
        $top->JBrowseEntry(
            -variable => \$Txt_teacher,
            -state    => 'readonly',
            -width    => 12
        )
    );

    my $entry_teacher = $self->_tk_teacher_dropdown->Subwidget("entry");
    $entry_teacher->configure( -disabledbackground => "white" );
    $entry_teacher->configure( -disabledforeground => "black" );

    my $add_teacher_btn = $top->Button(
        -text    => "Add Teacher",
        -command => [ \&_cmd_add_teacher_to_block, $self ],
    );

    $top->Label(
        -text   => 'Add Teacher',
        -anchor => 'w'
      )->grid( $self->_tk_teacher_dropdown,
        '-', $add_teacher_btn, -sticky => 'nsew' );

    $self->_tk_teacher_assigned_dropdown(
        $top->JBrowseEntry(
            -variable => \$Txt_teacher_assigned,
            -state    => 'readonly',
            -width    => 12
        )
    );

    my $entry_teacher_entry =
      $self->_tk_teacher_assigned_dropdown->Subwidget("entry");
    $entry_teacher_entry->configure( -disabledbackground => "white" );
    $entry_teacher_entry->configure( -disabledforeground => "black" );

    my $remove_teacher_btn = $top->Button(
        -text    => "Remove Teacher",
        -command => [ \&_cmd_remove_teacher_from_block, $self ],
    );

    $top->Label(
        -text   => 'Remove Teacher',
        -anchor => 'w'
      )->grid( $self->_tk_teacher_assigned_dropdown,
        '-', $remove_teacher_btn, -sticky => 'nsew' );

    $self->_tk_teacher_status(
        $top->Label( -text => "" )->grid( -columnspan => 4 ) );

    #--------------------------------------------------------
    # Lab Add/Remove
    #--------------------------------------------------------

    # add
    $self->_tk_lab_dropdown(
        $top->JBrowseEntry(
            -variable => \$Txt_lab,
            -state    => 'readonly',
            -width    => 12
        )
    );

    my $labDropNEntry = $self->_tk_lab_dropdown->Subwidget("entry");
    $labDropNEntry->configure( -disabledbackground => "white" );
    $labDropNEntry->configure( -disabledforeground => "black" );

    my $add_lab_btn = $top->Button(
        -text    => "Add Lab",
        -command => [ \&_cmd_add_lab_to_block, $self ],
    );

    $top->Label(
        -text   => 'Add Lab',
        -anchor => 'w'
    )->grid( $self->_tk_lab_dropdown, '-', $add_lab_btn, -sticky => 'nsew' );

    # remove
    $self->_tk_lab_assigned_dropdown(
        $top->JBrowseEntry(
            -variable => \$Txt_lab_assigned,
            -state    => 'readonly',
            -width    => 12
        )
    );

    my $lab_entry_assigned =
      $self->_tk_lab_assigned_dropdown->Subwidget("entry");
    $lab_entry_assigned->configure( -disabledbackground => "white" );
    $lab_entry_assigned->configure( -disabledforeground => "black" );

    my $remove_lab_btn = $top->Button(
        -text    => "Remove Lab",
        -command => [ \&_cmd_remove_lab_from_block, $self ],
    );

    $top->Label(
        -text   => 'Remove Resource',
        -anchor => 'w'
    )->grid( $self->_tk_lab_assigned_dropdown, '-', $remove_lab_btn, -sticky => 'nsew' );

    $self->_tk_lab_status (
      $top->Label( -text => "" )->grid( -columnspan => 4, -sticky => 'n' ));

    #--------------------------------------------------------
    # layout
    #--------------------------------------------------------
    my ( $columns, $rows ) = $top->gridSize();
    for ( my $i = 1 ; $i < $columns ; $i++ ) {
        $top->gridColumnconfigure( $i, -weight => 1 );
    }
    $top->gridRowconfigure( $rows - 1, -weight => 1 );

    $Edit_dialog->configure( -focus => $duration_entry );
    return $self;

}
# ============================================================================
# Show Dialog box
# ============================================================================
sub Show {
    my $self = shift;

    my $answer = "continue";
    while ( $answer eq "continue" ) {
        $answer = $Edit_dialog->Show();
        return $self->_respond_to_dialog_closing($answer);
    }
}

# ============================================================================
# respond to dialog closing
# ============================================================================
sub _respond_to_dialog_closing {
    my $self = shift;
    my $answer = shift;
 
     if ( $answer eq 'Delete' ) {

        my $sure = $self->_tk_top_frame->DialogBox(
            -title   => "Delete?",
            -buttons => [ 'Yes', 'NO' ]
        );

        $sure->Label( -text => "Are you Sure You\nWant To Delete?" )->pack;

        my $answer2 = $sure->Show();
        $answer2 = "NO" unless $answer2;
        return "continue" if $answer2 eq "NO";
        $self->cb_remove_block_by_id->( $self->block_id );
        return 'Block Deleted';

    }
    if ( $self->block_duration ne $Txt_block_duration ) {
        $self->cb_change_block_duration->(
            $self->block_id, $Txt_block_duration
        );
    }
    return $Changed;
}

# ============================================================================
# update teacher choices
# ============================================================================
sub update_teacher_choices {
    my $self                     = shift;
    my $choices_teacher          = shift;
    my $choices_teacher_assigned = shift;

    $self->_choices_teacher($choices_teacher);
    $self->_tk_teacher_dropdown->configure( -choices => $choices_teacher );
    $self->_tk_teacher_dropdown->update;
    $Txt_teacher = "";

    $self->_tk_teacher_assigned_dropdown->configure(
        -choices => $choices_teacher_assigned );
    $self->_choices_teacher_assigned($choices_teacher_assigned);
    $self->_tk_teacher_assigned_dropdown->update;
    $Txt_teacher_assigned = "";
}

# ============================================================================
# update lab choices
# ============================================================================
sub update_lab_choices {
    my $self                    = shift;
    my $choices_lab          = shift;
    my $choices_lab_assigned = shift;

    $self->_choices_lab($choices_lab);
    $self->_tk_lab_dropdown->configure( -choices => $choices_lab );
    $self->_tk_lab_dropdown->update;
    $Txt_lab = "";

    $self->_choices_lab_assigned($choices_lab_assigned);
    $self->_tk_lab_assigned_dropdown->configure(
        -choices => $choices_lab_assigned );
    $self->_tk_lab_assigned_dropdown->update;
    $Txt_lab_assigned = "";
}


# ============================================================================
# add teacher to block
# ============================================================================
sub _cmd_add_teacher_to_block {
    my $self = shift;
    return unless $Txt_teacher;
    my $id = __get_id( $self->_choices_teacher, $Txt_teacher );
    $self->cb_add_teacher_to_block->( $self->block_id, $id );

    $Txt_teacher = "";
    $self->_tk_teacher_status->configure( -text => "Teacher Added" );
    $self->_tk_teacher_status->bell;
    $self->_tk_teacher_status->update;
    $Changed = "Block Modified";
}

# ============================================================================
# remove teacher from block
# ============================================================================
sub _cmd_remove_teacher_from_block {
   my $self = shift;
    return unless $Txt_teacher_assigned;
    my $id =
      __get_id( $self->_choices_teacher_assigned, $Txt_teacher_assigned );
    $self->cb_remove_teacher_from_block->( $self->block_id, $id );

    $Txt_teacher_assigned = "";
    $self->_tk_teacher_status->configure( -text => "Teacher Removed" );
    $self->_tk_teacher_status->bell;
    $self->_tk_teacher_status->update;
    $Changed = "Block Modified";

}

# ============================================================================
# add lab to block
# ============================================================================
sub _cmd_add_lab_to_block {
    my $self = shift;
    return unless $Txt_lab;
    my $id = __get_id( $self->_choices_lab, $Txt_lab );
    $self->cb_add_lab_to_block->( $self->block_id, $id );

    $Txt_lab = "";
    $self->_tk_lab_status->configure( -text => "Lab Added" );
    $self->_tk_lab_status->bell;
    $self->_tk_lab_status->update;
    $Changed = "Block Modified";
}

# ============================================================================
# remove lab from block
# ============================================================================
sub _cmd_remove_lab_from_block {
   my $self = shift;
    return unless $Txt_lab_assigned;
    my $id =
      __get_id( $self->_choices_lab_assigned, $Txt_lab_assigned );
    $self->cb_remove_lab_from_block->( $self->block_id, $id );

    $Txt_lab_assigned = "";
    $self->_tk_lab_status->configure( -text => "Lab Removed" );
    $self->_tk_lab_status->bell;
    $self->_tk_lab_status->update;
    $Changed = "Block Modified";
}

# =================================================================
# validate that number be entered in a entry box is a real number
# (positive real number)
# =================================================================
sub _is_number {
	my $n = shift;
	return 1 if $n =~ (/^(\s*\d*\.?\d*\s*|)$/);
	return 0;
}

# ----------------------------------------------------------------------------
# get id from hash used in JEntry boxes
# ----------------------------------------------------------------------------
sub __get_id {
      my $hash    = shift;
      my $name    = shift;
      my %reverse = reverse %$hash;
      return $reverse{$name};
}

# ============================================================================
# setup getters and setters
# ============================================================================
sub __setup {

    # ------------------------------------------------------------------------
    # setter/getters for various properties
    # ------------------------------------------------------------------------

    _create_setters_and_getters(
        -category   => "block",
        -properties => [qw(id duration)],
        -default    => ""
    );

    _create_setters_and_getters(
        -category   => "_choices",
        -properties => [
            qw(lab_assigned lab teacher_assigned teacher)
        ],
        -default => ""
    );

    # ------------------------------------------------------------------------
    # getters and setters for callback routines
    # ------------------------------------------------------------------------
    my @callbacks = (
        qw(remove_block_by_id change_block_duration
          add_lab_to_block remove_lab_from_block remove_teacher_from_block
          add_teacher_to_block )
    );
    _create_setters_and_getters(
        -category   => "cb",
        -properties => \@callbacks,
        -default    => sub { print "Caller: caller()\n\n\n", die }
    );

    # ------------------------------------------------------------------------
    # Defining widget getters and setters
    # ------------------------------------------------------------------------
    my @widgets = (
        qw(top_frame block_status block_dropdown teacher_dropdown teacher_assigned_dropdown teacher_status
          lab_dropdown lab_assigned_dropdown lab_status)
    );
    _create_setters_and_getters(
        -category   => "_tk",
        -properties => \@widgets,
        -default    => undef
    );

}

# ============================================================================
# getters and setters
# - creates two subs for each property
# 1) cat_property
# 2) cat_property_ptr
# ============================================================================
sub _create_setters_and_getters {

    my %stuff   = @_;
    my $cat     = $stuff{-category};
    my $props   = $stuff{-properties};
    my $default = $stuff{-default};

    foreach my $prop (@$props) {
        no strict 'refs';

        # create simple getter and setter
        *{ $cat . "_" . $prop } = sub {
            my $self = shift;
            $self->{ $cat . "_" . $prop } = shift if @_;
            return $self->{ $cat . "_" . $prop } || $default;
        };
    }
}
1;
