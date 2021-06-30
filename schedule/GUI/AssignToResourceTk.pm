#!/usr/bin/perl
use strict;
use warnings;

=head1 NAME

AssignToResourceTk  

=head1 VERSION

Version 6.00

=head1 DESCRIPTION

Gui companion to AssignToResource object

=head1 REQUIRED EVENT HANDLERS

=over

=item * cb_course_selected (course id)

=item * cb_section_selected (section id)

=item * cb_block_selected (block id)

=item * cb_teacher_selected (teacher id)

=item * cb_lab_selected (lab id)
    
=item * cb_add_new_section (section name)

=item * cb_add_new_block (block description)

=item * cb_add_new_teacher (firstname, lastname)

=item * cb_add_new_lab (lab_name, lab_number)

=back

=head1 METHODS

=cut

package AssignToResourceTk;

use FindBin;
use lib "$FindBin::Bin/..";

use Tk;
use Tk::Dialog;
use Tk::JBrowseEntry;
use PerlLib::Colours;
use GUI::FontsAndColoursTk;

# ============================================================================
# globals
# ============================================================================
my $fonts;
my $bigFont;
my $boldFont;

my $OKAY;

my $Type;

__setup();

# ============================================================================
# constructor
# ============================================================================

=head2 new

Create an instance of AssignToResourceTk object, but does NOT draw the
dialog box at this point. This allows the calling function to set up the
callback routines first, as well as the lists for courses, etc.

B<Parameters>

- Type => type of scheduable object (Teacher/Lab/Stream)

I<Should not use Stream, this gui is not setup for that>

=cut

sub new {

    my $class = shift;
    $Type = shift;
    my $self = bless {}, $class;

    # set fonts
    $fonts    = FontsAndColoursTk->Fonts;
    $bigFont  = $fonts->{bigbold};
    $boldFont = $fonts->{bold};

    # create all the getters and setter properties
    return $self;

}

# ============================================================================
# draw
# ============================================================================

=head2 draw

Create and display the dialog box

B<Parameters>

- frame => a gui object that can support calls to create dialog boxes

- title => title of the dialog box

- block_text => description of the block that is the default block to assign

=cut

sub draw {
    my $self       = shift;
    my $frame      = shift;
    my $title      = shift;
    my $block_text = shift;

    # -----------------------------------------------
    # create dialog box
    # -----------------------------------------------
    my $db = $frame->DialogBox( -title   => "Assign Block",
                                -buttons => [ "Ok", "Cancel" ] );
    $self->{-frame} = $db;

    $OKAY = $db->Subwidget("B_Ok");
    $OKAY->configure( -state => 'disabled' );
    $OKAY->configure(-width=>10);
    my $cancel = $db->Subwidget("B_Cancel");
    $cancel->configure(-width=>10);

    # -----------------------------------------------
    # description of selected block
    # -----------------------------------------------
    $self->_new_block($block_text);

    # -----------------------------------------------
    # create labels
    # -----------------------------------------------
    $self->_create_main_labels($title);

    # -----------------------------------------------
    # course / section / block widgets
    # -----------------------------------------------
    $self->_setup_course_widgets();
    $self->_setup_section_widgets();
    $self->_setup_block_widgets();
    $self->_setup_teacher_widgets();
    $self->_setup_lab_widgets();

    # -----------------------------------------------
    # layout
    # -----------------------------------------------
    $self->_layout();
}

=head2 clear_sections_and_blocks 

reset the choices for sections and blocks to empty lists, etc

=cut

sub clear_sections_and_blocks {
    my $self = shift;

    $self->_tb_section("");
    my %sections;
    $self->list_sections( \%sections );
    $self->set_section_choices();
    $self->_tk_section_new_btn->configure( -state => 'disabled' );

    $self->clear_blocks();
    $OKAY->configure( -state => 'disabled' );

    # Updating the Drop down with the new options
    $self->_tk_section_jbe->configure( -choices => $self->list_sections );
    $self->_tk_block_jbe->configure( -choices => $self->list_blocks );
}

=head2 clear_blocks 

reset the choices for blocks to empty lists, etc

=cut

sub clear_blocks {
    my $self = shift;

    $self->_tb_block("");
    my %blocks;
    $self->list_blocks( \%blocks );
    $self->set_block_choices();
    $self->_tk_block_new_btn->configure( -state => 'disabled' );

    $OKAY->configure( -state => 'disabled' );
}

=head2 enable_new_section_button 

=cut 

sub enable_new_section_button {
    my $self = shift;
    $self->_tk_section_new_btn->configure( -state => "normal" );
}

=head2 enable_new_block_button

=cut

sub enable_new_block_button {
    my $self = shift;
    $self->_tk_block_new_btn->configure( -state => "normal" );
}

=head2 set_teacher ( teacher_name )

=cut

sub set_teacher {
    my $self = shift;
    $self->_tb_teacher(shift);
    $self->_new_teacher_lname("");
    $self->_new_teacher_fname("");
}

=head2 set_section ( section_name )

=cut 

sub set_section {
    my $self = shift;
    $self->_tb_section(shift);
    $self->_new_section("");
}

=head2 set_block ( block_name )

=cut

sub set_block {
    my $self = shift;
    $self->_tb_block(shift);
    $self->_new_block("");
    $OKAY->configure(-state=>'normal');
}

=head2 set_lab ( lab_name )

=cut

sub set_lab {
    my $self = shift;
    $self->_tb_lab(shift);
    $self->_new_lab_name("");
    $self->_new_lab_number("");
}

=head2 set_lab_choices ( {id=>name} ) 

=cut 

sub set_lab_choices {
    my $self = shift;
    $self->list_labs(shift);
    $self->_tk_lab_jbe->configure( -choices => $self->list_labs );
}

=head2 set_teacher_choices ( {id=>name} ) 

=cut 

sub set_teacher_choices {
    my $self = shift;
    $self->list_teachers(shift);
    $self->_tk_teacher_jbe->configure( -choices => $self->list_teachers );
}

=head2 set_course_choices ( {id=>name} ) 

=cut 

sub set_course_choices {
    my $self = shift;
    $self->list_courses(shift);
    $self->_tk_course_jbe->configure( -choices => $self->list_courses );
    $OKAY->configure( -state => 'disabled' );
}

=head2 set_section_choices 

=cut

sub set_section_choices {
    my $self = shift;
    $self->list_sections(shift);
    $self->_tk_section_jbe->configure( -choices => $self->list_sections );
    $self->enable_new_section_button;
    $OKAY->configure( -state => 'disabled' );
}

=head2 set_block_choices

=cut

sub set_block_choices {
    my $self = shift;
    $self->list_blocks(shift);
    $self->_tk_block_jbe->configure( -choices => $self->list_blocks );
    $self->enable_new_block_button;
    $OKAY->configure( -state => 'disabled' );
}

=head2 Show

Displays the dialog box.

B<Returns>

"Ok" | "Cancel"

=cut

sub Show {
    my $self = shift;
    return $self->{-frame}->Show();
}

=head2 yes_no

Displays a yes/no dialog

B<Parameters>

- title

- question

B<Returns>

"Yes" | "No"

=cut

sub yes_no {
    my $self     = shift;
    my $title    = shift;
    my $question = shift;
    my $db =
      $self->{-frame}->DialogBox(
                                  -title   => $title,
                                  -buttons => [ "Yes", "No" ],
      );
      $db->Label(-text=>$question)->pack;
    return $db->Show() || "";
}

# ============================================================================
# course
# ============================================================================
sub _setup_course_widgets {
    my $self = shift;
    my $db   = $self->{-frame};

    $self->_tk_course_jbe(

        $db->JBrowseEntry(
            -variable  => $self->_tb_course_ptr,
            -state     => 'readonly',
            -width     => 20,
            -browsecmd => [
                sub {
                    my $self = shift;
                    my $id = _get_id( $self->list_courses, $self->_tb_course );
                    $self->cb_course_selected->($id);
                },
                $self
            ],
        )
    );

    my $courseDropEntry = $self->_tk_course_jbe->Subwidget("entry");
    $courseDropEntry->configure( -disabledbackground => "white" );
    $courseDropEntry->configure( -disabledforeground => "black" );

}

# ============================================================================
# section
# ============================================================================
sub _setup_section_widgets {
    my $self = shift;
    my $db   = $self->{-frame};

    $self->_tk_section_jbe(
        $db->JBrowseEntry(
            -variable  => $self->_tb_section_ptr,
            -state     => 'readonly',
            -width     => 20,
            -browsecmd => [
                sub {
                    my $self = shift;
                    my $id =
                      _get_id( $self->list_sections, $self->_tb_section );
                    $self->cb_section_selected->($id);
                },
                $self
            ],
        )
    );

    my $secDropEntry = $self->_tk_section_jbe->Subwidget("entry");
    $secDropEntry->configure( -disabledbackground => "white" );
    $secDropEntry->configure( -disabledforeground => "black" );

    $self->_tk_section_entry(
                       $db->Entry( -textvariable => $self->_new_section_ptr ) );

    $self->_tk_section_new_btn(
        $db->Button(
            -text    => "Create",
            -state   => 'disabled',
            -width   => 20,
            -command => [
                sub {
                    my $self = shift;
                    $self->cb_add_new_section->( $self->_new_section );
                },
                $self
            ]
        )
    );

}

# ============================================================================
# block
# ============================================================================
sub _setup_block_widgets {
    my $self = shift;
    my $db   = $self->{-frame};
    $self->_tk_block_jbe(
        $db->JBrowseEntry(
            -variable  => $self->_tb_block_ptr,
            -state     => 'readonly',
            -width     => 20,
            -browsecmd => [
                sub {
                    my $self = shift;
                    my $id = _get_id( $self->list_blocks, $self->_tb_block );
                    $self->cb_block_selected->($id);
                    $OKAY->configure( -state => 'normal' );
                },
                $self
            ],
        )
    );
    my $blockDropEntry = $self->_tk_block_jbe->Subwidget("entry");
    $blockDropEntry->configure( -disabledbackground => "white" );
    $blockDropEntry->configure( -disabledforeground => "black" );

    $self->_tk_block_entry(
                            $db->Entry(
                                        -textvariable => $self->_new_block_ptr,
                                        -state        => 'disabled',
                                        -disabledbackground => 'white'
                            )
    );

    $self->_tk_block_new_btn(
        $db->Button(
            -text    => "Create",
            -state   => 'disabled',
            -command => [
                sub {
                    my $self = shift;
                    $self->cb_add_new_block->( $self->_new_block );
                    $self->_tk_block_new_btn->configure(-state=>'disabled');
                    $self->_tk_block_entry->configure(-state=>'disabled');
                },
                $self
            ]
        )
    );
}

# ============================================================================
# teachers
# ============================================================================
sub _setup_teacher_widgets {
    my $self = shift;
    my $db   = $self->{-frame};

    $self->_tk_teacher_jbe(
        $db->JBrowseEntry(
            -variable  => $self->_tb_teacher_ptr,
            -state     => 'readonly',
            -width     => 20,
            -browsecmd => [
                sub {
                    my $self = shift;
                    my $id =
                      _get_id( $self->list_teachers, $self->_tb_teacher );
                    $self->cb_teacher_selected($id);
                },
                $self
            ],
        )
    );
    my $teacherDropEntry = $self->_tk_teacher_jbe->Subwidget("entry");
    $teacherDropEntry->configure( -disabledbackground => "white" );
    $teacherDropEntry->configure( -disabledforeground => "black" );

    $self->_tk_fname_entry(
                 $db->Entry( -textvariable => $self->_new_teacher_fname_ptr ) );
    $self->_tk_lname_entry(
                 $db->Entry( -textvariable => $self->_new_teacher_lname_ptr ) );

    $self->_tk_teacher_new_btn(
        $db->Button(
            -text    => "Create",
            -command => [
                sub {
                    my $self = shift;
                    $self->cb_add_new_teacher->( $self->_new_teacher_fname,
                                               $self->_new_teacher_lname );
                },
                $self
            ]
        )
    );

}

# ======================================================
# Lab
# ======================================================
sub _setup_lab_widgets {
    my $self = shift;
    my $db   = $self->{-frame};

    $self->_tk_lab_jbe(
        $db->JBrowseEntry(
            -variable  => $self->_tb_lab_ptr,
            -state     => 'readonly',
            -width     => 20,
            -browsecmd => sub {
                my $id = _get_id( $self->list_labs, $self->_tb_lab );
                $self->cb_lab_selected->($id);
            }
        )
    );

    my $labDropEntry = $self->_tk_lab_jbe->Subwidget("entry");
    $labDropEntry->configure( -disabledbackground => "white" );
    $labDropEntry->configure( -disabledforeground => "black" );

    $self->_tk_lab_num_entry(
                        $db->Entry( -textvariable => $self->_new_lab_number_ptr ) );
    $self->_tk_lab_descr_entry(
                          $db->Entry( -textvariable => $self->_new_lab_name_ptr ) );

    $self->_tk_lab_new_btn(
        $db->Button(
            -text    => "Create",
            -command => sub {
                $self->cb_add_new_lab->( $self->_new_lab_name,
                                       $self->_new_lab_number );
            }
        )
    );
}

# ----------------------------------------------------------------------------
# Create Main Labels
# ----------------------------------------------------------------------------
sub _label {
    my $db      = shift;
    my $text    = shift;
    my $options = shift;
    return $db->Label( -text => $text, %$options );
}

sub _create_main_labels {
    my $self       = shift;
    my $main_title = shift;
    my $opts;
    my $db = $self->{-frame};

    $self->_lbl_title( _label( $db, $main_title, { -font => $bigFont } ) );
    $opts = { -anchor => 'w' };
    $self->_lbl_course( _label( $db, "Choose Course", $opts ) );
    $self->_lbl_lab( _label( $db, "Choose Lab", $opts ) );
    $self->_lbl_teacher( _label( $db, "Choose Teacher", $opts ) );
    $self->_lbl_section( _label( $db, "Choose Section", $opts ) );
    $self->_lbl_block( _label( $db, "Choose Block To Modify", $opts ) );

    $self->_lbl_create_section(
                         _label( $db, "Create new from Section Name", $opts ) );
    $self->_lbl_create_teacher(
                 _label( $db, "Create new from Firstname / Lastname", $opts ) );
    $self->_lbl_create_lab(
                  _label( $db, "Create new from Lab number and name", $opts ) );
    $self->_lbl_create_block(
                 _label( $db, "Create block from selected date/time", $opts ) );

    $opts = { -font => $boldFont, -anchor => 'w' };
    $self->_lbl_course_info( _label( $db, "Course Info (required)", $opts ) );
    $self->_lbl_teacher_info( _label( $db, "Teacher (optional)", $opts ) );
    $self->_lbl_lab_info( _label( $db, "Lab (optional)", $opts ) );
}

sub _layout {
    my $self = shift;
    my $db   = $self->{-frame};

    # -------------------------------------------------------
    # title
    # -------------------------------------------------------
    $self->_lbl_title->grid( "-", "-", "-", -padx => 2, -sticky => 'nsew' );

    # -------------------------------------------------------
    # course
    # -------------------------------------------------------
    $db->Label( -text => '' )->grid( "-", "-", "-", -sticky => 'nsew' );
    $self->_lbl_course_info->grid(
                                   "-", "-", "-",
                                   -padx   => 2,
                                   -sticky => 'nsew'
    );
    $self->_lbl_course->grid( "-", "-", "-", -padx => 2, -sticky => 'nsew' );
    $self->_tk_course_jbe->grid( "-", "-", "-", -padx => 2, -sticky => 'nsew' );

    # -------------------------------------------------------
    # section
    # -------------------------------------------------------
    $self->_lbl_section->grid(
                               $self->_lbl_create_section,
                               "-", "-",
                               -padx   => 2,
                               -sticky => 'nsew'
    );
    $self->_tk_section_jbe->grid(
                      $self->_tk_section_entry, "-", $self->_tk_section_new_btn,
                      -padx   => 2,
                      -sticky => 'nsew'
    );

    # -------------------------------------------------------
    # block
    # -------------------------------------------------------
    $self->_lbl_block->grid(
                             $self->_lbl_create_block,
                             "-", "-",
                             -padx   => 2,
                             -sticky => 'nsew'
    );
    $self->_tk_block_jbe->grid(
                          $self->_tk_block_entry, "-", $self->_tk_block_new_btn,
                          -padx   => 2,
                          -sticky => 'nsew'
    );

    # -------------------------------------------------------
    # teacher
    # -------------------------------------------------------
    unless ( $Type eq 'teacher' ) {
        $db->Label( -text => '' )
          ->grid( "-", "-", "-", -padx => 2, -sticky => 'nsew' );
        $self->_lbl_teacher_info->grid(
                                        "-", "-", "-",
                                        -padx   => 2,
                                        -sticky => 'nsew'
        );
        $self->_lbl_teacher->grid(
                                   $self->_lbl_create_teacher,
                                   "-", "-",
                                   -padx   => 2,
                                   -sticky => 'nsew'
        );
        $self->_tk_teacher_jbe->grid(
                                 $self->_tk_fname_entry, $self->_tk_lname_entry,
                                 $self->_tk_teacher_new_btn,
                                 -sticky => 'nsew',
                                 -padx   => 2
        );
        $db->Label( -text => '' )
          ->grid( "-", "-", "-", -padx => 2, -sticky => 'nsew' );
    }

    # -------------------------------------------------------
    # lab
    # -------------------------------------------------------
    unless ( $Type eq 'lab' ) {
        $db->Label( -text => '' )
          ->grid( "-", "-", "-", -padx => 2, -sticky => 'nsew' );
        $self->_lbl_lab_info->grid(
                                    "-", "-", "-",
                                    -padx   => 2,
                                    -sticky => 'nsew'
        );
        $self->_lbl_lab->grid(
                               $self->_lbl_create_lab,
                               "-", "-",
                               -padx   => 2,
                               -sticky => 'nsew'
        );
        $self->_tk_lab_jbe->grid(
                           $self->_tk_lab_num_entry, $self->_tk_lab_descr_entry,
                           $self->_tk_lab_new_btn,
                           -sticky => 'nsew',
                           -padx   => 2
        );
        $db->Label( -text => '' )
          ->grid( "-", "-", "-", -padx => 2, -sticky => 'nsew' );
    }

}

# ============================================================================
# setup getters and setters
# ============================================================================
sub __setup {

    # ------------------------------------------------------------------------
    # Entry or Text Box variable bindings
    # ------------------------------------------------------------------------
    _create_setters_and_getters(
                     -category   => 'list',
                     -properties => [qw(courses sections blocks teachers labs)],
                     -default    => {}
    );

    _create_setters_and_getters(
                         -category   => "_tb",
                         -properties => [qw(course section block teacher lab )],
                         -default    => ""
    );

    _create_setters_and_getters(
          -category => "_new",
          -properties =>
            [qw(section teacher_fname teacher_lname lab_number lab_name block)],
          -default => ""
    );

    # ------------------------------------------------------------------------
    # getters and setters for callback routines
    # ------------------------------------------------------------------------
    my @callbacks = (
        qw(add_new_section section_selected course_selected
          block_selected teacher_selected lab_selected add_new_block
          add_new_teacher add_new_lab)
    );
    _create_setters_and_getters(
                                        -category   => "cb",
                                        -properties => \@callbacks,
                                        -default    => sub { return }
    );

    # ------------------------------------------------------------------------
    # Tk Labels
    # ------------------------------------------------------------------------
    my @labels = (
        qw (
          title selected_block course_info teacher_info lab_info
          course teacher lab section block create_section
          create_teacher create_lab create_block
          )
    );
    _create_setters_and_getters(
                                        -category   => "_lbl",
                                        -properties => \@labels,
                                        -default    => undef
    );

    # ------------------------------------------------------------------------
    # Defining widget getters and setters
    # ------------------------------------------------------------------------
    my @widgets = (
        qw(
          course_jbe section_jbe teacher_jbe lab_jbe block_jbe
          section_entry fname_entry lname_entry block_entry lab_descr_entry lab_num_entry
          section_new_btn teacher_new_btn block_new_btn lab_new_btn
          )
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


        # set getter to property pointer
        *{ $cat . "_" . $prop . "_ptr" } = sub {
            my $self = shift;
            return \$self->{ $cat . "_" . $prop };
          }
    }
}

sub _get_id {
    my $hash_ptr = shift;
    my $name     = shift;
    my %ref      = reverse %{$hash_ptr};
    return $ref{$name};
}

1;
