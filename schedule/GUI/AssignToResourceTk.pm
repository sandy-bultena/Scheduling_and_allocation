#!/usr/bin/perl
use strict;
use warnings;

# ============================================================================
# id=>name hashes
# ============================================================================

package AssignToResourceTk;

use FindBin;
use lib "$FindBin::Bin/..";

use Tk;
use Tk::DragDrop;
use Tk::DropSite;
use Tk::ItemStyle;
use Tk::FindImages;
use Tk::FindImages;
use Tk::Dialog;
use Tk::Menu;
use Tk::LabEntry;
use Tk::Optionmenu;
use Tk::JBrowseEntry;
use PerlLib::Colours;
use GUI::FontsAndColoursTk;

my $image_dir = Tk::FindImages::get_image_dir();

my $Trash1_photo;
my $Trash2_photo;

my $fonts    ;
my $bigFont  ;
my $boldFont ;

sub _setup {
    my $self = shift;

  # ============================================================================
  # Entry or Text Box variable bindings
  # ============================================================================
    $self->_create_setters_and_getters(
        -category   => 'list',
        -properties => [
            qw(courses sections blocks
              teachers labs)
        ],
        -default => {}
    );

    $self->_create_setters_and_getters(
                         -category   => "tb",
                         -properties => [qw(course section block teacher lab )],
                         -default    => ""
    );

    $self->_create_setters_and_getters(
          -category => "new",
          -properties =>
            [qw(section teacher_fname teacher_lname lab_number lab_name block)],
          -default => ""
    );

  # ============================================================================
  # getters and setters for callback routines
  # ============================================================================
    my @callbacks = (
        qw(add_new_section section_selected course_selected
          block_selected teacher_selected lab_selected add_new_block
          add_new_teacher add_new_lab)
    );

    $self->_create_setters_and_getters(
                                        -category   => "cb",
                                        -properties => \@callbacks,
                                        -default    => sub { return }
    );

  # ============================================================================
  # Tk Labels
  # ============================================================================
    my @labels = (
        qw (
          title selected_block course_info teacher_info lab_info
          course teacher lab section block create_section
          create_teacher create_lab create_block
          )
    );
    $self->_create_setters_and_getters(
                                        -category   => "lbl",
                                        -properties => \@labels,
                                        -default    => undef
    );

  # ============================================================================
  # Defining widget getters and setters
  # ============================================================================
    my @widgets = (
        qw(
          CourseJBE SectionJBE TeacherJBE LabJBE BlockJBE
          SectionEntry TeacherFName TeacherLName BlockDescr LabDscr LabNumber
          SectionNewBtn TeacherNewBtn BlockNewBtn LabNewBtn
          )
    );
    $self->_create_setters_and_getters(
                                        -category   => "tk",
                                        -properties => \@widgets,
                                        -default    => undef
    );

}
my $selectedBlockText = "";
my $OKAY;

# ============================================================================
# getters and setters
# ============================================================================
sub _create_setters_and_getters {

    my $self    = shift;
    my %stuff   = @_;
    my $cat     = $stuff{-category};
    my $props   = $stuff{-properties};
    my $default = $stuff{-default};
    use Data::Dumper;
    print "Props are: ", Dumper $props;

    foreach my $prop (@$props) {
        no strict 'refs';
        *{ $cat . "_" . $prop } = sub {
            my $self = shift;
            $self->{ $cat . "_" . $prop } = shift if @_;
            return $self->{ $cat . "_" . $prop } || $default;
        };
        $self->{ $cat . "_" . $prop } = $default;

        *{ $cat . "_" . $prop . "_ptr" } = sub {
            my $self = shift;
            return \$self->{ $cat . "_" . $prop };
          }
    }
}
my $Type;

# ============================================================================
# constructor
# ============================================================================
sub new {
    $fonts    = FontsAndColoursTk->Fonts;
    $bigFont  = $fonts->{bigbold};
    $boldFont = $fonts->{bold};
    my $class = shift;
    $Type = shift;
    my $self = bless {}, $class;
    print "\n\n****** Calling setup ********\n";
    $self->_setup;
    return $self;

}

# ============================================================================
# draw
# ============================================================================
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

    # -----------------------------------------------
    # description of selected block
    # -----------------------------------------------
    $selectedBlockText = $block_text;

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

sub clear_sections_and_blocks {
    my $self = shift;
    $self->tb_section    ("");
    $self->tb_block      ("");
    $self->list_sections( {});
    $self->list_blocks( {});
    $self->tk_BlockNewBtn->configure( -state => 'disabled' );
    $self->tk_SectionNewBtn->configure (-state=>'normal');

    # Updating the Drop down with the new options
    $self->tk_SectionJBE->configure( -choices => $self->list_sections );
    $self->tk_BlockJBE->configure( -choices => $self->list_blocks );
}

sub clear_blocks {
    my $self = shift;
    $self->tb_block("");
    $self->list_blocks ( {});

    # Updating the Drop down with the new options
    $self->tk_BlockJBE->configure( -choices => $self->list_blocks );
}

sub enable_new_section_button {
    my $self = shift;
    $self->tk_SectionNewBtn->configure( -state => "normal" );
}

sub enable_new_block_button {
    my $self = shift;
    $self->tk_BlockNewBtn->configure( -state => "normal" );
}

sub set_teacher {
    my $self = shift;
    $self->tb_teacher(shift);
    $self->new_teacher_lname("");
    $self->new_teacher_fname("");
}

sub set_section {
    my $self = shift;
    $self->tb_section(shift);
    $self->new_section("");
}

sub set_block {
    my $self = shift;
    $self->tb_block(shift);
    $self->new_block("");
}

sub set_lab {
    my $self = shift;
    $self->tb_lab(shift);
    $self->new_lab_name("");
    $self->new_lab_number("");
}

sub set_section_choices {
    my $self = shift;
    $self->tk_SectionJBE->configure( -choices => $self->list_sections );
}
    
sub set_block_choices {
    my $self = shift;
    $self->tk_BlockJBE->configure( -choices => $self->list_blocks );
}


# ============================================================================
# course
# ============================================================================
sub _setup_course_widgets {
    my $self = shift;
    my $db   = $self->{-frame};

    $self->tk_CourseJBE(

        $db->JBrowseEntry(
            -variable  => $self->tb_course_ptr,
            -state     => 'readonly',
            -choices   => $self->list_courses,
            -width     => 20,
            -browsecmd => [
                sub {
                    print "Calling cb_course_selected\n";
                    my $self = shift;
                    $self->cb_course_selected->( $self->tb_course );
                },
                $self
            ],
        )
    );

    my $courseDropEntry = $self->tk_CourseJBE->Subwidget("entry");
    $courseDropEntry->configure( -disabledbackground => "white" );
    $courseDropEntry->configure( -disabledforeground => "black" );

}

# ============================================================================
# section
# ============================================================================
sub _setup_section_widgets {
    my $self = shift;
    my $db   = $self->{-frame};

    $self->tk_SectionJBE(
        $db->JBrowseEntry(
            -variable  => $self->tb_section_ptr,
            -state     => 'readonly',
            -width     => 20,
            -browsecmd => [
                sub {
                    my $self = shift;
                    $self->cb_section_selected->( $self->tb_section );
                },
                $self
            ],
        )
    );

    my $secDropEntry = $self->tk_SectionJBE->Subwidget("entry");
    $secDropEntry->configure( -disabledbackground => "white" );
    $secDropEntry->configure( -disabledforeground => "black" );

    $self->tk_SectionEntry(
                        $db->Entry( -textvariable => $self->new_section_ptr ) );

    $self->tk_SectionNewBtn(
        $db->Button(
            -text    => "Create",
            -state   => 'disabled',
            -width   => 20,
            -command => sub {
                my $self = shift;
                $self->cb_add_new_section( $self->new_section );
            },
        )
    );

}


# ============================================================================
# block
# ============================================================================
sub _setup_block_widgets {
    my $self = shift;
    my $db   = $self->{-frame};
    $self->tk_BlockJBE(
        $db->JBrowseEntry(
            -variable => $self->tb_block_ptr,
            -state    => 'readonly',
                       -choices   => $self->list_blocks,
            -width     => 20,
            -browsecmd => [
                sub {
                    my $self = shift;
                    print "calling block_selected\n";
                    $self->cb_block_selected->( $self->tb_block );
                },
                $self
            ],
        )
    );
    my $blockDropEntry = $self->tk_BlockJBE->Subwidget("entry");
    $blockDropEntry->configure( -disabledbackground => "white" );
    $blockDropEntry->configure( -disabledforeground => "black" );

    $self->tk_BlockDescr(
                          $db->Entry(
                                      -textvariable => $self->new_block_ptr,
                                      -state        => 'disabled',
                                      -disabledbackground => 'white'
                          )
    );

    $self->tk_BlockNewBtn(
        $db->Button(
            -text    => "Create",
            -state   => 'disabled',
            -command => [
                sub {
                    my $self = shift;
                    $self->cb_add_new_block( $self->new_block );
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

    $self->tk_TeacherJBE(
        $db->JBrowseEntry(
            -variable  => $self->tb_teacher_ptr,
            -state     => 'readonly',
            -choices   => $self->list_teachers,
            -width     => 20,
            -browsecmd => [
                sub {
                    my $self = shift;
                    $self->cb_teacher_selected( $self->tb_teacher );
                },
                $self
            ],
        )
    );
    my $teacherDropEntry = $self->tk_TeacherJBE->Subwidget("entry");
    $teacherDropEntry->configure( -disabledbackground => "white" );
    $teacherDropEntry->configure( -disabledforeground => "black" );

    $self->tk_TeacherFName(
                  $db->Entry( -textvariable => $self->new_teacher_fname_ptr ) );
    $self->tk_TeacherLName(
                  $db->Entry( -textvariable => $self->new_teacher_lname_ptr ) );

    $self->tk_TeacherNewBtn(
        $db->Button(
            -text    => "Create",
            -command => [
                sub {
                    my $self = shift;
                    $self->cb_add_new_teacher( $self->new_teacher_fname,
                                               $self->teacher_lname );
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

    $self->tk_LabJBE(
        $db->JBrowseEntry(
            -variable  => $self->tb_lab_ptr,
            -state     => 'readonly',
            -choices   => $self->list_labs,
            -width     => 20,
            -browsecmd => sub {
                $self->cb_lab_selected->( $self->tb_lab );
            }
        )
    );

    my $labDropEntry = $self->tk_LabJBE->Subwidget("entry");
    $labDropEntry->configure( -disabledbackground => "white" );
    $labDropEntry->configure( -disabledforeground => "black" );

    $self->tk_LabNumber( $db->Entry( -textvariable => $self->new_lab_number ) );
    $self->tk_LabDscr( $db->Entry( -textvariable => $self->new_lab_name ) );

    foreach my $k ( sort keys %$self ) {
        no warnings;
        print $k, " \t=> ", $self->{$k}, "\n";
    }
    $self->tk_LabNewBtn(
        $db->Button(
            -text    => "Create",
            -command => sub {
                $self->cb_add_new_lab( $self->new_lab_name,
                                       $self->new_lab_number );
            }
        )
    );
}

# ----------------------------------------------------------------------------
# Create Main Labels
# ----------------------------------------------------------------------------
sub _create_main_labels {
    my $self       = shift;
    my $main_title = shift;

    my $db = $self->{-frame};

    $self->lbl_title( $db->Label( -text => $main_title, -font => $bigFont ) );
    $self->lbl_course( $db->Label( -text => "Choose Course", -anchor => 'w' ) );
    $self->lbl_lab( $db->Label( -text => "Choose Resource", -anchor => 'w' ) );

    $self->lbl_teacher(
                      $db->Label( -text => "Choose Teacher", -anchor => 'w' ) );
    $self->lbl_section(
                      $db->Label( -text => "Choose Section", -anchor => 'w' ) );
    $self->lbl_block(
              $db->Label( -text => "Choose Block To Modify", -anchor => 'w' ) );
    $self->lbl_create_section(
                               $db->Label(
                                        -text => "Create new from Section Name",
                                        -anchor => 'w'
                               )
    );

    $self->lbl_course_info(
                            $db->Label(
                                        -text   => "Course Info (required)",
                                        -font   => $boldFont,
                                        -anchor => 'w'
                            )
    );
    $self->lbl_teacher_info(
                             $db->Label(
                                         -text   => "Teacher (optional)",
                                         -font   => $boldFont,
                                         -anchor => 'w'
                             )
    );
    $self->lbl_lab_info(
                         $db->Label(
                                     -text   => "Resource (optional)",
                                     -font   => $boldFont,
                                     -anchor => 'w'
                         )
    );
    $self->lbl_create_teacher(
                            $db->Label(
                                -text => "Create new from Firstname / Lastname",
                                -anchor => 'w'
                            )
    );
    $self->lbl_create_lab(
                        $db->Label(
                            -text => "Create new from Resource number and name",
                            -anchor => 'w'
                        )
    );
    $self->lbl_create_block(
                            $db->Label(
                                -text => "Create block from selected date/time",
                                -anchor => 'w'
                            )
    );
}

sub _layout {
    my $self = shift;
    my $db   = $self->{-frame};

    # -------------------------------------------------------
    # title
    # -------------------------------------------------------
    $self->lbl_title->grid( "-", "-", "-", -padx => 2, -sticky => 'nsew' );

    # -------------------------------------------------------
    # course
    # -------------------------------------------------------
    $db->Label( -text => '' )->grid( "-", "-", "-", -sticky => 'nsew' );
    $self->lbl_course_info->grid(
                                  "-", "-", "-",
                                  -padx   => 2,
                                  -sticky => 'nsew'
    );
    $self->lbl_course->grid( "-", "-", "-", -padx => 2, -sticky => 'nsew' );
    $self->tk_CourseJBE->grid( "-", "-", "-", -padx => 2, -sticky => 'nsew' );

    # -------------------------------------------------------
    # section
    # -------------------------------------------------------
    $self->lbl_section->grid(
                              $self->lbl_create_section,
                              "-", "-",
                              -padx   => 2,
                              -sticky => 'nsew'
    );
    $self->tk_SectionJBE->grid(
                           $self->tk_SectionEntry, "-", $self->tk_SectionNewBtn,
                           -padx   => 2,
                           -sticky => 'nsew'
    );

    # -------------------------------------------------------
    # block
    # -------------------------------------------------------
    $self->lbl_block->grid(
                            $self->lbl_create_block,
                            "-", "-",
                            -padx   => 2,
                            -sticky => 'nsew'
    );
    $self->tk_BlockJBE->grid(
                              $self->tk_BlockDescr, "-", $self->tk_BlockNewBtn,
                              -padx   => 2,
                              -sticky => 'nsew'
    );

    # -------------------------------------------------------
    # teacher
    # -------------------------------------------------------
    unless ( $Type eq 'teacher' ) {
        $db->Label( -text => '' )
          ->grid( "-", "-", "-", -padx => 2, -sticky => 'nsew' );
        $self->lbl_teacher_info->grid(
                                       "-", "-", "-",
                                       -padx   => 2,
                                       -sticky => 'nsew'
        );
        $self->lbl_teacher->grid(
                                  $self->lbl_create_teacher,
                                  "-", "-",
                                  -padx   => 2,
                                  -sticky => 'nsew'
        );
        $self->tk_TeacherJBE->grid(
                                 $self->tk_TeacherFName, $self->tk_TeacherLName,
                                 $self->tk_TeacherNewBtn,
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
        $self->lbl_lab_info->grid(
                                   "-", "-", "-",
                                   -padx   => 2,
                                   -sticky => 'nsew'
        );
        $self->lbl_lab->grid(
                              $self->lbl_create_lab,
                              "-", "-",
                              -padx   => 2,
                              -sticky => 'nsew'
        );
        $self->tk_LabJBE->grid(
                                $self->tk_LabNumber, $self->tk_LabDscr,
                                $self->tk_LabNewBtn,
                                -sticky => 'nsew',
                                -padx   => 2
        );
        $db->Label( -text => '' )
          ->grid( "-", "-", "-", -padx => 2, -sticky => 'nsew' );
    }

}

sub Show {
    my $self = shift;
    return $self->{-frame}->Show();
}

# ============================================================================
# yes_no dialog
# ============================================================================
sub yes_no {
    my $self     = shift;
    my $title    = shift;
    my $question = shift;
    my $db =
      $self->{-frame}->DialogBox(
                                  -title   => $title,
                                  -buttons => [ "Yes", "No" ],
                                  -text    => $question
      );
    return $db->Show() || "";
}

1;
