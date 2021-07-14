#!/usr/bin/perl
use strict;
use warnings;

# =================================================================
# Edit course dialog GUI
# -----------------------------------------------------------------
# INPUTS:
#   frame
#   course id
#   course number
#   course name
#   needs allocation flag
#
# METHODS:
#   Show - shows the dialog box
#
#   update_teacher_choices
#       inputs: hash of all teachers {teacher_id => teacher_name}
#               hash of teachers assigned to this course {teacher_id => teacher_name}
#
#   update_section_choices
#       inputs: hash of sections assigned to this course {section_id => section_number}
#
#   update_stream_choices
#       inputs: hash of all streams {stream_id => stream_name}
#               hash of streams assigned to this course {stream_id => stream_number}
#
# RETURNS:
#   A string indicating what action was taken
#
# REQUIRED EVENT HANDLERS:
#   cb_set_allocation               (bool)
#   cb_remove_course_by_id          (course_id)
#   cb_change_course_name_by_id     (course_id, name)
#   cb_change_course_number_by_id   (course_id, number)
#   cb_is_course_num_unique         (new course number)
#   cb_edit_section                 (course_id, section_id)
#   cb_edit_section                 (course_id) # create new section before editing
#   cb_add_sections_with_blocks     (course_id, array or section names, array of block hours)
#   cb_add_teacher_to_course        (course_id, teacher_id)
#   cb_remove_teacher_from_course   (course_id, teacher_id)
#   cb_add_stream_to_course         (course_id, stream_id)
#   cb_remove_stream_from_course    (course_id, stream_id)
#
# NOTES:
#   All changes occur when appropriate buttons are clicked.
#   The course number and name will be updated only when the dialog is closed.
# =================================================================

package EditCourseDialogTk;
use FindBin;
use Carp;
use lib "$FindBin::Bin/..";

use GUI::AddSectionDialogTk;

# =================================================================
# variables bound to entry boxes
# =================================================================
my $Txt_course_number;
my $Txt_course_name;
my $Txt_stream;
my $Txt_stream_assigned;
my $Txt_teacher_assigned;
my $Txt_teacher;
my $Txt_section;
my $Bool_needs_allocation;

# =================================================================
# global
# =================================================================
my $Edit_dialog;

__setup();

# =================================================================
# constructor
# =================================================================
sub new {
    my $class     = shift;
    my $frame     = shift;
    my $course_id = shift;
    $Txt_course_number     = shift;
    $Txt_course_name       = shift;
    $Bool_needs_allocation = shift;

    my $self = bless {};
    $self->course_id($course_id);
    $self->course_number($Txt_course_number);
    $self->course_name($Txt_course_name);

    #---------------------------------------------------
    # Creating Frames and defining widget variable names
    #---------------------------------------------------
    $Edit_dialog = $frame->DialogBox(
        -title   => "Edit " . $Txt_course_name,
        -buttons => [ 'Close', 'Delete' ],
    );
    $self->_tk_top_frame( $Edit_dialog->Subwidget("top") );
    $self->_tk_close_btn( $Edit_dialog->Subwidget("B_Close") );

    my $pad = 40;

    #-----------------------------------------
    # Course number and name entry entry
    #-----------------------------------------

    # Course # Entry widget
    $self->_tk_entry_course_number(
        $Edit_dialog->Entry(
            -textvariable    => \$Txt_course_number,
            -validate        => 'key',
            -validatecommand => [ \&_cmd_validate_course_number, $self ],
        )
    );
    _cmd_validate_course_number( $self, $Txt_course_number );

    $self->_tk_top_frame->Label( -text => "Course Number", -anchor => 'w' )
      ->grid( $self->_tk_entry_course_number, '-', '-', -sticky => "nsew" );

    # course description entry widget
    $self->_tk_top_frame->Label( -text => "Course Name", -anchor => 'w' )
      ->grid( $Edit_dialog->Entry( -textvariable => \$Txt_course_name, ),
        '-', '-', -sticky => "nsew" );

    #-----------------------------------------
    # allocation and scheduling
    #-----------------------------------------
    my $row      = 3;
    my $alloc_cb = $self->_tk_top_frame->Checkbutton(
        -text        => "Needs Allocation? ",
        -variable    => \$Bool_needs_allocation,
        -indicatoron => 1,
        -selectcolor => 'blue',
        -command     => [ $self->cb_set_allocation, \$Bool_needs_allocation ],
    )->grid( -column => 1, -sticky => 'nsew', -row => $row );

    $row++;

    #-----------------------------------------
    # blank space
    #-----------------------------------------
    $self->_tk_top_frame->Label( -text => "" )
      ->grid( -columnspan => 4, -row => $row, -sticky => "nsew" );
    $row++;

    #-----------------------------------------
    # Section Add/Remove/Edit
    #-----------------------------------------

    # browse entry course sections
    $self->_tk_section_dropdown(
        $self->_tk_top_frame->JBrowseEntry(
            -variable => \$Txt_section,
            -state    => 'readonly',
            -width    => 12
          )->grid(
            -row    => $row,
            -column => 1,
            -ipadx  => $pad,
            -sticky => "nsew"
          )
    );

    my $entry_section = $self->_tk_section_dropdown->Subwidget("entry");
    $entry_section->configure( -disabledbackground => "white" );
    $entry_section->configure( -disabledforeground => "black" );

    # buttons to manipulate sections
    $self->_tk_top_frame->Button(
        -text    => "Advanced Add Section",
        -command => [ \&_cmd_add_section_advanced, $self ]
    )->grid( -row => $row, -column => 3, -sticky => "nsew" );

    $self->_tk_top_frame->Button(
        -text    => "Add Section(s)",
        -command => [ \&_cmd_add_section, $self ]
    )->grid( -row => $row, -column => 2, -sticky => "nsew" );

    $self->_tk_top_frame->Label( -text => "Sections:", -anchor => 'w' )
      ->grid( -row => $row, -column => 0, -sticky => "nsew" );

    my $btn_remove_section = $self->_tk_top_frame->Button(
        -text    => "Remove Section",
        -command => [ \&_cmd_remove_section, $self ]
    );

    my $btn_section_edit = $self->_tk_top_frame->Button(
        -text    => "Edit Section",
        -command => [ \&_cmd_edit_section, $self ]
    );

    $row++;
    $self->_tk_section_status(
        $self->_tk_top_frame->Label( -text => "" )->grid(
            '-', $btn_remove_section, $btn_section_edit,
            -sticky => "nsew",
            -row    => $row
        )
    );

    # blank line
    $row++;
    $self->_tk_top_frame->Label( -text => "" )
      ->grid( -columnspan => $row, -sticky => "nsew" );

    #--------------------------------------------------------
    # Teacher Add/Remove
    #--------------------------------------------------------

    # browse entry for all teachers
    $self->_tk_teacher_dropdown(
        $self->_tk_top_frame->JBrowseEntry(
            -variable => \$Txt_teacher,
            -state    => 'readonly',
            -width    => 12
        )
    );

    my $entry_teach = $self->_tk_teacher_dropdown->Subwidget("entry");
    $entry_teach->configure( -disabledbackground => "white" );
    $entry_teach->configure( -disabledforeground => "black" );

    # button to add teacher
    my $btn_add_teacher_sections = $self->_tk_top_frame->Button(
        -text    => "Add To All Sections",
        -command => [ \&_cmd_add_teacher_to_all_sections, $self ],
    );

    # label
    $self->_tk_top_frame->Label( -text => "Add Teacher: ", -anchor => 'w' )
      ->grid( $self->_tk_teacher_dropdown,
        '-', $btn_add_teacher_sections, -sticky => "nsew" );

    # browse entry for teachers currently assigned to course
    $self->_tk_teacher_assigned_dropdown(
        $self->_tk_top_frame->JBrowseEntry(
            -variable => \$Txt_teacher_assigned,
            -state    => 'readonly',
            -width    => 12
        )
    );

    my $entry_teach_assigned =
      $self->_tk_teacher_assigned_dropdown->Subwidget("entry");
    $entry_teach_assigned->configure( -disabledbackground => "white" );
    $entry_teach_assigned->configure( -disabledforeground => "black" );

    # button to remove teacher from sections
    my $btn_remove_teacher_all_sections = $self->_tk_top_frame->Button(
        -text    => "Remove From All Sections",
        -command => [ \&_cmd_remove_teacher_all_sections, $self ],
    );

    $self->_tk_top_frame->Label( -text => "Remove Teacher: ", -anchor => 'w' )
      ->grid(
        $self->_tk_teacher_assigned_dropdown, '-',
        $btn_remove_teacher_all_sections, -sticky => "nsew"
      );

    $self->_tk_teacher_status(
        $self->_tk_top_frame->Label( -text => "" )->grid( -columnspan => 4 ) );

    #--------------------------------------------------------
    # Stream Add/Remove
    #--------------------------------------------------------

    # browse entry all streams
    $self->_tk_stream_dropdown(
        $self->_tk_top_frame->JBrowseEntry(
            -variable => \$Txt_stream,
            -state    => 'readonly',
            -width    => 12
        )
    );

    my $entry_stream = $self->_tk_stream_dropdown->Subwidget("entry");
    $entry_stream->configure( -disabledbackground => "white" );
    $entry_stream->configure( -disabledforeground => "black" );

    # button to add stream to sections
    my $btn_add_stream_all_sections = $self->_tk_top_frame->Button(
        -text    => "Set To All Sections",
        -command => [ \&_cmd_add_stream_all_sections, $self ],
    );

    $self->_tk_top_frame->Label( -text => "Add Stream: ", -anchor => 'w' )
      ->grid( $self->_tk_stream_dropdown,
        '-', $btn_add_stream_all_sections, -sticky => 'nsew' );

    # browse entry curretnly assigned streams
    $self->_tk_stream_assigned_dropdown(
        $self->_tk_top_frame->JBrowseEntry(
            -variable => \$Txt_stream_assigned,
            -state    => 'readonly',
            -width    => 12
        )
    );

    my $entry_stream_assigned =
      $self->_tk_stream_assigned_dropdown->Subwidget("entry");
    $entry_stream_assigned->configure( -disabledbackground => "white" );
    $entry_stream_assigned->configure( -disabledforeground => "black" );

    # button to remove all streams from sections
    my $btn_stream_remove_all_sections = $self->_tk_top_frame->Button(
        -text    => "Remove From All Sections",
        -command => [ \&_cmd_remove_stream_all_sections, $self ],
    );

    $self->_tk_top_frame->Label( -text => "Remove Stream: ", -anchor => 'w' )
      ->grid(
        $self->_tk_stream_assigned_dropdown,
        '-',
        $btn_stream_remove_all_sections,
        -sticky => 'nsew'
      );

    $self->_tk_stream_status( $self->_tk_top_frame->Label( -text => "", )
          ->grid( -columnspan => 4, -sticky => 'n' ) );

    #--------------------------------------------------------
    # gui layout commands
    #--------------------------------------------------------

    my ( $columns, $rows ) = $self->_tk_top_frame->gridSize();
    for ( my $i = 1 ; $i < $columns ; $i++ ) {
        $self->_tk_top_frame->gridColumnconfigure( $i, -weight => 1 );
    }
    $self->_tk_top_frame->gridRowconfigure( $rows - 1, -weight => 1 );

    $Edit_dialog->configure( -focus => $self->_tk_section_dropdown );
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
    my $answer = "";
    while ( $answer ne "Close" ) {
        $answer = $Edit_dialog->Show();
        $answer = "Close" unless $answer;
        $answer = "Delete" unless $Txt_course_number;
        $answer = $self->_respond_to_dialog_closing($answer);
    }
}

# ============================================================================
# update section choices
# ============================================================================
sub update_section_choices {
    my $self            = shift;
    my $choices_section = shift;

    $self->_choices_section($choices_section);
    $self->_tk_section_dropdown->configure( -choices => $choices_section );
    $self->_tk_section_dropdown->update;
    $Txt_section = "";
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

# ----------------------------------------------------------------------------
# add sections (simple)
# ----------------------------------------------------------------------------
sub _cmd_add_section {
    my $self = shift;

    my ( $section_names, $block_hours ) =
      AddSectionDialogTk->new( $self->_tk_top_frame );

    if ( $section_names && $block_hours ) {
        $self->cb_add_sections_with_blocks->(
            $self->course_id, $section_names, $block_hours
        );
        $self->_tk_section_status->configure( -text => "Section(s) Added" );
        $self->_tk_top_frame->bell;
    }
    else {
        $self->_tk_section_status->configure( -text => "" );
    }
    $self->_tk_section_status->update;
}

# ----------------------------------------------------------------------------
# add section (advanced)
# ----------------------------------------------------------------------------
sub _cmd_add_section_advanced {
    my $self = shift;

    my $answer = $self->cb_edit_section->( $self->course_id );

    $self->_tk_section_status->configure( -text => $answer );
    $self->_tk_top_frame->bell if $answer;
    $self->_tk_section_status->update;
}

# ----------------------------------------------------------------------------
# add streams all sections
# ----------------------------------------------------------------------------
sub _cmd_add_stream_all_sections {
    my $self = shift;
    return unless $Txt_stream;
    my $id = __get_id( $self->_choices_stream, $Txt_stream );
    $self->cb_add_stream_to_course->( $self->course_id, $id );

    $Txt_stream = "";
    $self->_tk_stream_status->configure( -text => "Stream Added" );
    $self->_tk_stream_status->update;
    $self->_tk_stream_status->bell;
}

# ----------------------------------------------------------------------------
# add teacher all sections
# ----------------------------------------------------------------------------
sub _cmd_add_teacher_to_all_sections {
    my $self = shift;
    return unless $Txt_teacher;
    my $id = __get_id( $self->_choices_teacher, $Txt_teacher );
    $self->cb_add_teacher_to_course->( $self->course_id, $id );

    $Txt_teacher = "";
    $self->_tk_teacher_status->configure( -text => "Teacher Added" );
    $self->_tk_teacher_status->bell;
    $self->_tk_teacher_status->update;
}

# ----------------------------------------------------------------------------
# edit section
# ----------------------------------------------------------------------------
sub _cmd_edit_section {
    my $self = shift;
    return unless $Txt_section;

    my $sec_id = __get_id( $self->_choices_section, $Txt_section );

    my $answer = $self->cb_edit_section->( $self->course_id, $sec_id );

    $self->_tk_section_status->configure( -text => $answer );
    $self->_tk_top_frame->bell if $answer;
    $self->_tk_section_status->update;

}

# ----------------------------------------------------------------------------
# remove section
# ----------------------------------------------------------------------------
sub _cmd_remove_section {
    my $self = shift;
    return unless $Txt_section;
    my $id = __get_id( $self->_choices_section, $Txt_section );
    $self->cb_remove_section_from_course->( $self->course_id, $id );

    $self->_tk_section_status->configure( -text => "Section Removed" );
    $self->_tk_section_status->bell;
    $self->_tk_section_status->update;
}

# ----------------------------------------------------------------------------
# remove teacher all sections
# ----------------------------------------------------------------------------
sub _cmd_remove_teacher_all_sections {
    my $self = shift;
    return unless $Txt_teacher_assigned;
    my $id =
      __get_id( $self->_choices_teacher_assigned, $Txt_teacher_assigned );
    $self->cb_remove_teacher_from_course->( $self->course_id, $id );

    $Txt_teacher_assigned = "";
    $self->_tk_teacher_status->configure( -text => "Teacher Removed" );
    $self->_tk_teacher_status->bell;
    $self->_tk_teacher_status->update;
}

# ----------------------------------------------------------------------------
# remove streams from all sections
# ----------------------------------------------------------------------------
sub _cmd_remove_stream_all_sections {
    my $self = shift;
    return unless $Txt_stream_assigned;
    my $id = __get_id( $self->_choices_stream_assigned, $Txt_stream_assigned );
    $self->cb_remove_stream_from_course->( $self->course_id, $id );

    $Txt_stream_assigned = "";
    $self->_tk_stream_status->configure( -text => "Stream Removed" );
    $self->_tk_stream_status->update;
    $self->_tk_stream_status->bell;
}

# ================================================================
# Validate that the course number is new/unique
# (alway return true, just change input to red and disable close button)
# ================================================================
sub _cmd_validate_course_number {
    my $self          = shift;
    my $proposed_text = shift;

    # blank is always invalid
    if ( $proposed_text =~ /^\s*$/ ) {
        $self->_tk_close_btn->configure( -state => 'disabled' );
        $self->_tk_entry_course_number->configure( -bg => 'red' );
        $self->_tk_entry_course_number->bell;
        return 1;
    }

    # returned to the original setting
    return 1 if $self->course_number eq $proposed_text;

    # new course number
    if ( $self->cb_is_course_num_unique->($proposed_text) ) {
        $self->_tk_close_btn->configure( -state => 'normal' );
        $self->_tk_entry_course_number->configure( -bg => 'white' );
    }
    else {
        $self->_tk_close_btn->configure( -state => 'disabled' );
        $self->_tk_entry_course_number->configure( -bg => 'red' );
        $self->_tk_entry_course_number->bell;
    }

    return 1;
}

# --------------------------------------------------------
# respond to user closing box
# --------------------------------------------------------
sub _respond_to_dialog_closing {
    my $self   = shift;
    my $answer = shift;

    # if delete, make sure that user is ok with this
    if ( $answer eq 'Delete' ) {

        my $sure = $self->_tk_top_frame->DialogBox(
            -title   => "Delete?",
            -buttons => [ 'Yes', 'NO' ]
        );

        if ($Txt_course_number) {
            $sure->Label( -text => "Are you Sure You\nWant To Delete?" )->pack;

            my $answer2 = $sure->Show();
            $answer2 = 'NO' unless $answer2;
            return 'NO' if $answer2 eq 'NO';
        }
        $self->cb_remove_course_by_id->( $self->course_id );
        return 'Close';

    }

    # change course name or number if necessary
    if ( $self->course_name ne $Txt_course_name ) {
        $self->cb_change_course_name_by_id->(
            $self->course_id, $Txt_course_name
        );
    }
    if ( $self->course_number ne $Txt_course_number ) {
        $self->cb_change_course_number_by_id->(
            $self->course_id, $Txt_course_number
        );
    }

    # return
    return 'Close';
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
        -category   => "course",
        -properties => [qw(id name number)],
        -default    => ""
    );

    __create_setters_and_getters(
        -category   => "_choices",
        -properties => [
            qw(stream_assigned stream teacher_assigned teacher
              section)
        ],
        -default => ""
    );

    # ------------------------------------------------------------------------
    # getters and setters for callback routines
    # ------------------------------------------------------------------------
    my @callbacks = (
        qw(remove_course_by_id change_course_name_by_id change_course_number_by_id
          add_stream_to_course remove_stream_from_course remove_teacher_from_course
          add_teacher_to_course add_sections_with_blocks edit_section
          is_course_num_unique set_allocation remove_section_from_course)
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
        qw(top_frame stream_assigned_dropdown stream_dropdown section_dropdown
          stream_status teacher_assigned_dropdown teacher_dropdown teacher_status
          section_status entry_course_number close_btn )
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

