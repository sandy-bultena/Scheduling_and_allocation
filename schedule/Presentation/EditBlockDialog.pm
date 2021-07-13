#!/usr/bin/perl
use strict;
use warnings;

package EditBlockDialog;
use FindBin;
use Carp;
use lib "$FindBin::Bin/..";

use GUI::EditBlockDialogTk;

my $Schedule;
my $Gui;
my $Section;
my $Block;
my $Course;
my $frame;

sub new {
    my $class = shift;
    $frame = shift;
    $Schedule = shift;
    $Course = shift;
    $Section  = shift;
    $Block = shift;

    # ------------------------------------------------------------------------
    # make dialog box
    # ------------------------------------------------------------------------
    my $title = $Course->number.":".$Section->name.
    ":".$Block->short_description;
    $Gui = EditBlockDialogTk->new( $frame, $title, $Block->id, 
     $Block->duration);

    _update_lab_choices();
    _update_teacher_choices();

    # set the callback functions (event handlers)

    $Gui->cb_add_lab_to_block( \&_cb_add_lab_to_block );
    $Gui->cb_remove_lab_from_block( \&_cb_remove_lab_from_block );
    $Gui->cb_remove_teacher_from_block( \&_cb_remove_teacher_from_block);
    $Gui->cb_add_teacher_to_block( \&_cb_add_teacher_to_block );
    $Gui->cb_remove_block_by_id(\&_cb_remove_block_by_id);
    $Gui->cb_change_block_duration(\&_cb_change_block_duration);

    $Gui->Show();
}

# ============================================================================
# update lab choices
# ============================================================================
sub _update_lab_choices {
    my @labsO = $Block->labs;
    my %labNameO;
    foreach my $i (@labsO) {
        $labNameO{ $i->id } = "$i";
    }
    my @labs = $Schedule->all_labs;
    my %labName;
    foreach my $i (@labs) {
        $labName{ $i->id } = "$i";
    }

    $Gui->update_lab_choices( \%labName, \%labNameO );
}

# ============================================================================
# update teacher choices
# ============================================================================
sub _update_teacher_choices {
    my @teachers = $Schedule->all_teachers;
    my %teacherName;
    foreach my $i (@teachers) {
        $teacherName{ $i->id } = "$i";
    }

    my @teachersO = $Block->teachers;
    my %teacherNameO;
    foreach my $i (@teachersO) {
        $teacherNameO{ $i->id } = "$i";
    }
    $Gui->update_teacher_choices( \%teacherName, \%teacherNameO );

}

# ============================================================================
# update block duration
# ============================================================================
sub _cb_change_block_duration{
    my $block_id  = shift;
    my $hours = shift;
    my $block = $Section->get_block_by_id($block_id);
    return unless $block;
    $block->duration($hours);
    EditCourses::_refresh_section_gui( $Section, "Schedule/Course" . $Course->id
    ."/Section".$Section->id );
    EditCourses::set_dirty();
}

# ============================================================================
# remove block
# ============================================================================
sub _cb_remove_block_by_id {
    my $block_id  = shift;
    my $block = $Section->get_block_by_id($block_id);
    return unless $block;
    $Section->remove_block($block);
    EditCourses::_refresh_section_gui( $Section, "Schedule/Course" . $Course->id
    ."/Section".$Section->id );
    EditCourses::set_dirty();
}

# ============================================================================
# remove teacher from block
# ============================================================================
sub _cb_remove_teacher_from_block{
    my $block_id  = shift;
    my $teacher_id = shift;
    my $block = $Section->get_block_by_id($block_id);
    return unless $block;
    my $teacher = $Schedule->teachers->get($teacher_id);
    $block->remove_teacher($teacher);
    EditCourses::_refresh_section_gui( $Section, "Schedule/Course" . $Course->id
    ."/Section".$Section->id );
    EditCourses::set_dirty();
    _update_teacher_choices();
}

# ============================================================================
# remove lab from section
# ============================================================================
sub _cb_remove_lab_from_block {
    my $block_id = shift;
    my $lab_id = shift;
    my $block = $Section->get_block_by_id($block_id);
    return unless $block;
    my $lab = $Schedule->labs->get($lab_id);
    $block->remove_lab($lab);
    EditCourses::_refresh_section_gui( $Section, "Schedule/Course" . $Course->id
    ."/Section".$Section->id );
    EditCourses::set_dirty();
    _update_lab_choices();
}

# ============================================================================
# add teacher to block
# ============================================================================
sub _cb_add_teacher_to_block {
    my $block_id  = shift;
    my $teacher_id = shift;
    my $block = $Section->get_block_by_id($block_id);
    return unless $block;
    my $teacher = $Schedule->teachers->get($teacher_id);
    $block->assign_teacher($teacher);
    EditCourses::_refresh_section_gui( $Section, "Schedule/Course" . $Course->id
    ."/Section".$Section->id );
    EditCourses::set_dirty();
    _update_teacher_choices();
}

# ============================================================================
# add lab to block
# ============================================================================
sub _cb_add_lab_to_block {
    my $block_id = shift;
    my $lab_id = shift;
    my $block = $Section->get_block_by_id($block_id);
    return unless $block;
    my $lab = $Schedule->labs->get($lab_id);
    $block->assign_lab($lab);
    EditCourses::_refresh_section_gui( $Section, "Schedule/Course" . $Course->id
    ."/Section".$Section->id );
    EditCourses::set_dirty();
    _update_lab_choices();
}
1;
