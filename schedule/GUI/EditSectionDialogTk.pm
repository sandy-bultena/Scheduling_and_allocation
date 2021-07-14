#!/usr/bin/perl
use strict;
use warnings;
# =================================================================
# Edit section dialog GUI
# -----------------------------------------------------------------
# INPUTS:
#   frame
#   course name
#   section id
#   section name
#
# METHODS:
#   Show - shows the dialog box
#
#   update_teacher_choices
#       inputs: hash of all teachers {teacher_id => teacher_name}
#               hash of teachers assigned to this section {teacher_id => teacher_name}
#
#   update_block_choices
#       inputs: hash of blocks assigned to this section {block_id => block_number}
#
#   update_stream_choices
#       inputs: hash of all streams {stream_id => stream_name}
#               hash of streams assigned to this section {stream_id => stream_number}
#
# RETURNS:
#   A string indicating what action was taken
#
# REQUIRED EVENT HANDLERS:
#   cb_remove_section_by_id             (section_id)
#   cb_change_section_name_by_id        (section_id, name)
#   cb_add_blocks_to_section            (section_id, array of block hours)
#   cb_remove_block_from_section        (section_id, block_id)
#   cb_edit_block                       (section_id, block_id)
#   cb_add_teacher_to_section           (section_id, teacher_id)
#   cb_remove_teacher_from_section      (section_id, teacher_id)
#   cb_add_stream_to_section            (section_id, stream_id)
#   cb_remove_stream_from_section       (section_id, stream_id)
#
# NOTES:
#   All changes occur when appropriate buttons are clicked.
#   The section name will be updated only when the dialog is closed.
# =================================================================

package EditSectionDialogTk;

my $Txt_stream;
my $Txt_stream_assigned;
my $Txt_teacher_assigned;
my $Txt_teacher;
my $Txt_section_name;
my $Txt_number_of_hours;
my $Txt_block;

my $Changed = "";

my $Edit_dialog;
__setup();

# ============================================================================
# constructor
# ============================================================================
sub new {
    my $class       = shift;
    my $frame       = shift;
    my $course_name = shift;
    my $section_id  = shift;
    $Txt_section_name   = shift;

    my $self = bless {};
    $self->section_id($section_id);
    $self->section_name($Txt_section_name);

    #--------------------------------------------------------
    # Defining Frames and widget names
    #--------------------------------------------------------

    $Edit_dialog = $frame->DialogBox(
        -title   => $course_name . ": Section " . $Txt_section_name,
        -buttons => [ 'Close', 'Delete' ]
    );

    my $top = $Edit_dialog->Subwidget("top");

    $self->_tk_top_frame($top);

    my $pad = 40;

    #--------------------------------------------------------
    # Section Name and hours
    #--------------------------------------------------------
    $top->Label( -text => "Section Name", -anchor => 'w' )
      ->grid( $top->Entry( -textvariable => \$Txt_section_name ),
        '-', '-', -sticky => "nsew" );

    $top->Label( -text => "Hours", -anchor => 'w' )->grid(
        $top->Entry( -textvariable => \$Txt_number_of_hours ),
        $top->Label( -text => "only used if there are no blocks" ),
        "-", -sticky => 'nsew'
    );

    $top->Label( -text => "" )->grid( -columnspan => 4 );

    #--------------------------------------------------------
    # Blocks
    #--------------------------------------------------------
    $self->_tk_block_dropdown(
        $top->JBrowseEntry(
            -variable => \$Txt_block,
            -state    => 'readonly',
            -width    => 12
        )->grid( -column => 1, -row => 2, -sticky => 'nsew', -ipadx => $pad )
    );
    my $entry_block = $self->_tk_block_dropdown->Subwidget("entry");
    $entry_block->configure( -disabledbackground => "white" );
    $entry_block->configure( -disabledforeground => "black" );

    $top->Label(
        -text   => "Block: ",
        -anchor => 'w'
    )->grid( -column => 0, -row => 2, -sticky => 'nsew' );

    $top->Button(
        -text    => "Add Block(s)",
        -command => [ \&_cmd_add_blocks, $self ]
    )->grid( -column => 2, -row => 3, -sticky => 'nsew', -columnspan => 2 );

    $top->Button(
        -text    => "Remove Block",
        -command => [ \&_cmd_remove_block, $self ],
    )->grid( -column => 3, -row => 2, -sticky => 'nsew' );

    $top->Button(
        -text    => "Edit Block",
        -command => [ \&_cmd_block_edit, $self ],
    )->grid( -column => 2, -row => 2, -sticky => 'nsew' );

    $self->_tk_block_status( $top->Label( -text => "" )
          ->grid( -column => 1, -row => 3, -sticky => 'nsew' ) );

    $top->Label( -text => "" )->grid( -columnspan => 4 );

    #--------------------------------------------------------
    # Teacher Add/REmove
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

    my $teach_add_btn = $top->Button(
        -text    => "Set to all blocks",
        -command => [ \&_cmd_add_teacher_to_all_blocks, $self ]
    );

    $top->Label(
        -text   => "Add Teacher: ",
        -anchor => 'w'
      )->grid( $self->_tk_teacher_dropdown,
        '-', $teach_add_btn, -sticky => 'nsew' );

    my $teach_remove_btn = $top->Button(
        -text    => "Remove from all blocks",
        -command => [ \&_cmd_remove_teacher_from_all_blocks, $self ],
    );

    $top->Label(
        -text   => "Remove Teacher: ",
        -anchor => 'w'
      )->grid( $self->_tk_teacher_assigned_dropdown,
        '-', $teach_remove_btn, -sticky => 'nsew' );

    $self->_tk_teacher_status(
        $top->Label( -text => "" )->grid( -columnspan => 4 ) );

    #--------------------------------------------------------
    # Stream Add/REmove
    #--------------------------------------------------------

    $self->_tk_stream_dropdown(
        $top->JBrowseEntry(
            -variable => \$Txt_stream,
            -state    => 'readonly',
            -width    => 12
        )
    );

    my $entry_stream = $self->_tk_stream_dropdown->Subwidget("entry");
    $entry_stream->configure( -disabledbackground => "white" );
    $entry_stream->configure( -disabledforeground => "black" );

    $self->_tk_stream_assigned_dropdown ( $top->JBrowseEntry(
        -variable => \$Txt_stream_assigned,
        -state    => 'readonly',
        -width    => 12
    ));

    my $entry_stream_assigned =
      $self->_tk_stream_assigned_dropdown->Subwidget("entry");
    $entry_stream_assigned->configure( -disabledbackground => "white" );
    $entry_stream_assigned->configure( -disabledforeground => "black" );

    my $stream_add_btn = $top->Button(
        -text    => "Add Stream",
        -command => [ \&_cmd_add_stream_to_section, $self ],
    );
    $top->Label(
        -text   => "Add Stream: ",
        -anchor => 'w'
      )->grid( $self->_tk_stream_dropdown,
        '-', $stream_add_btn, -sticky => 'nsew' );

    my $stream_remove_btn = $top->Button(
        -text    => "Remove Stream",
        -command => [ \&_cmd_remove_stream_from_section, $self ],
    );

    $top->Label(
        -text   => "Remove Stream: ",
        -anchor => 'w'
      )->grid( $self->_tk_stream_assigned_dropdown,
        '-', $stream_remove_btn, -sticky => 'nsew' );

    $self->_tk_stream_status(
        $top->Label( -text => "" )->grid( -columnspan => 4, -sticky => 'n' ) );

    my ( $columns, $rows ) = $top->gridSize();
    for ( my $i = 1 ; $i < $columns ; $i++ ) {
        $top->gridColumnconfigure( $i, -weight => 1 );
    }
    $top->gridRowconfigure( $rows - 1, -weight => 1 );

    $Edit_dialog->configure( -focus => $self->_tk_block_dropdown );

    return $self;
}

# ============================================================================
# Show the dialog box
# ============================================================================
sub Show() {
    my $self = shift;

    #--------------------------------------------------------
    # show dialog box
    #--------------------------------------------------------
    my $answer = "continue";
    while ( $answer eq "continue" ) {
        $answer = $Edit_dialog->Show();
        return $self->_respond_to_dialog_closing($answer);
    }
}

# ============================================================================
# update block choices
# ============================================================================
sub update_block_choices {
    my $self          = shift;
    my $choices_block = shift;

    $self->_choices_block($choices_block);
    $self->_tk_block_dropdown->configure( -choices => $choices_block );
    $self->_tk_block_dropdown->update;
    $Txt_block = "";

}

# ============================================================================
# update stream choices
# ============================================================================
sub update_stream_choices {
    my $self                    = shift;
    my $choices_stream          = shift;
    my $choices_stream_assigned = shift;

    $self->_choices_stream($choices_stream);
    $self->_tk_stream_dropdown->configure( -choices => $choices_stream );
    $self->_tk_stream_dropdown->update;
    $Txt_stream = "";

    $self->_choices_stream_assigned($choices_stream_assigned);
    $self->_tk_stream_assigned_dropdown->configure(
        -choices => $choices_stream_assigned );
    $self->_tk_stream_assigned_dropdown->update;
    $Txt_stream_assigned = "";
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
# add blocks
# ============================================================================
sub _cmd_add_blocks {
    my $self = shift;
        my $block_hours = AddBlocksDialogTk->new($self->_tk_top_frame);

    if (  $block_hours) {
        $self->cb_add_blocks_to_section->($self->section_id,$block_hours);
        $self->_tk_block_status->configure( -text => "Block(s) Added" );
        $self->_tk_top_frame->bell;
    }
    else {
        $self->_tk_block_status->configure( -text => "" );
    }
    $self->_tk_block_status->update;
}

# ============================================================================
# add stream to section
# ============================================================================
sub _cmd_add_stream_to_section {
    my $self = shift;
    return unless $Txt_stream;
    my $id = __get_id( $self->_choices_stream, $Txt_stream );
    $self->cb_add_stream_to_section->( $self->section_id, $id );

    $Txt_stream = "";
    $self->_tk_stream_status->configure( -text => "Stream Added" );
    $self->_tk_stream_status->update;
    $self->_tk_stream_status->bell;
    $Changed = "Section Modified";
}

# ============================================================================
# set teacher to all blocks
# ============================================================================
sub _cmd_add_teacher_to_all_blocks {
    my $self = shift;
    return unless $Txt_teacher;
    my $id = __get_id( $self->_choices_teacher, $Txt_teacher );
    $self->cb_add_teacher_to_section->( $self->section_id, $id );

    $Txt_teacher = "";
    $self->_tk_teacher_status->configure( -text => "Teacher Added" );
    $self->_tk_teacher_status->bell;
    $self->_tk_teacher_status->update;
    $Changed = "Section Modified";
}

# ============================================================================
# block edit
# ============================================================================

sub _cmd_block_edit {
        my $self = shift;
    return unless $Txt_block;
    my $id = __get_id( $self->_choices_block, $Txt_block );
    $self->cb_edit_block->($self->section_id,$id);
    
}

# ============================================================================
# remove block
# ============================================================================
sub _cmd_remove_block {
    my $self = shift;
    return unless $Txt_block;

    my $id = __get_id( $self->_choices_block, $Txt_block );
    $self->cb_remove_block_from_section->($self->section_id,$id);

    $self->_tk_block_dropdown->bell;
    $self->_tk_block_status->configure( -text => "Block Removed" );
    $self->_tk_block_status->bell;
    $Changed = "Section Modified";
}

# ============================================================================
# remove stream from section
# ============================================================================
sub _cmd_remove_stream_from_section {
    my $self = shift;
    return unless $Txt_stream_assigned;
    my $id = __get_id( $self->_choices_stream_assigned, $Txt_stream_assigned );
    $self->cb_remove_stream_from_section->( $self->section_id, $id );

    $Txt_stream_assigned = "";
    $self->_tk_stream_status->configure( -text => "Stream Removed" );
    $self->_tk_stream_status->update;
    $self->_tk_stream_status->bell;
    $Changed = "Section Modified";
}

# ============================================================================
# remove teacher from all blocks (remove teacher from section)
# ============================================================================
sub _cmd_remove_teacher_from_all_blocks {
   my $self = shift;
    return unless $Txt_teacher_assigned;
    my $id =
      __get_id( $self->_choices_teacher_assigned, $Txt_teacher_assigned );
    $self->cb_remove_teacher_from_section->( $self->section_id, $id );

    $Txt_teacher_assigned = "";
    $self->_tk_teacher_status->configure( -text => "Teacher Removed" );
    $self->_tk_teacher_status->bell;
    $self->_tk_teacher_status->update;
    $Changed = "Section Modified";
}

# ============================================================================
# dialog closing, time to button up (ha ha)
# ============================================================================
sub _respond_to_dialog_closing {
    my $self   = shift;
    my $answer = shift || '';

    if ( $answer eq 'Delete' ) {

        my $sure = $self->_tk_top_frame->DialogBox(
            -title   => "Delete?",
            -buttons => [ 'Yes', 'NO' ]
        );

        $sure->Label( -text => "Are you Sure You\nWant To Delete?" )->pack;

        my $answer2 = $sure->Show();
        $answer2 = "NO" unless $answer2;
        return "continue" if $answer2 eq "NO";
        $self->cb_remove_section_by_id->( $self->section_id );
        return 'Section Deleted';

    }
    if ( $self->section_name ne $Txt_section_name ) {
        $self->cb_change_section_name_by_id->(
            $self->section_id, $Txt_section_name
        );
    }
    return $Changed;
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

      __create_setters_and_getters(
          -category   => "section",
          -properties => [qw(id name)],
          -default    => ""
      );

      __create_setters_and_getters(
          -category   => "_choices",
          -properties => [
              qw(stream_assigned stream teacher_assigned teacher
                section block)
          ],
          -default => ""
      );

      # ------------------------------------------------------------------------
      # getters and setters for callback routines
      # ------------------------------------------------------------------------
      my @callbacks = (
          qw(remove_section_by_id change_section_name_by_id edit_block 
            add_stream_to_section remove_stream_from_section remove_teacher_from_section
            add_teacher_to_section add_block_to_section remove_block_from_section
            add_blocks_to_section )
      );
      __create_setters_and_getters(
          -category   => "cb",
          -properties => \@callbacks,
          -default    => sub { print "Caller: caller()\n\n\n", die }
      );

      # ------------------------------------------------------------------------
      # Defining widget getters and setters
      # ------------------------------------------------------------------------
      my @widgets = (
          qw(top_frame block_status block_dropdown teacher_dropdown teacher_assigned_dropdown teacher_status
            stream_dropdown stream_assigned_dropdown stream_status)
      );
      __create_setters_and_getters(
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
sub __create_setters_and_getters {

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
