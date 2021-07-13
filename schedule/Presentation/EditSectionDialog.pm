#!/usr/bin/perl
use strict;
use warnings;

package EditSectionDialog;
use FindBin;
use Carp;
use lib "$FindBin::Bin/..";

use GUI::EditSectionDialogTk;
use Presentation::EditBlockDialog;

my $Schedule;
my $Gui;
my $Course; 
my $Section;
my $frame;

sub new {
    my $class = shift;
    $frame = shift;
    $Schedule = shift;
    $Course   = shift;
    $Section  = shift;

    my $self = bless { -course => $Course, -section => $Section };

    # ------------------------------------------------------------------------
    # make dialog box
    # ------------------------------------------------------------------------
    $Gui = EditSectionDialogTk->new( $frame, $Course->name, $Section->id, 
     $Section->name);

    _update_stream_choices();
    _update_teacher_choices();
    _update_block_choices();

    # set the callback functions (event handlers)

    $Gui->cb_remove_section_by_id( \&_cb_remove_section_by_id );
    $Gui->cb_change_section_name_by_id( \&_cb_change_section_name_by_id );
    $Gui->cb_add_stream_to_section( \&_cb_add_stream_to_section );
    $Gui->cb_remove_stream_from_section( \&_cb_remove_stream_from_section );
    $Gui->cb_remove_teacher_from_section( \&_cb_remove_teacher_from_section );
    $Gui->cb_add_teacher_to_section( \&_cb_add_teacher_to_section );
    $Gui->cb_edit_block(\&_cb_edit_block);
    $Gui->cb_remove_block_from_section(\&_cb_remove_block_from_section);
    $Gui->cb_add_blocks_to_section(\&_cb_add_blocks_to_section);

    $Gui->Show();
}

# ============================================================================
# add blocks to section
# ============================================================================
sub _cb_add_blocks_to_section {
    my $section_id = shift;
    my $block_hours   = shift || [];
 
    my $section = $Course->get_section_by_id($section_id);
    return unless $section;
    
 
        # loop over blocks foreach section
        foreach my $hours (@$block_hours) {
            if ($hours) {
                my $block_num = $section->get_new_number;
                my $block = Block->new( -number => $block_num );
                $block->duration($hours);
                $section->add_block($block);
            }
    }

    # update the guis
    EditCourses::_refresh_section_gui( $section, "Schedule/Course" . $Course->id.
    "/Section".$section_id );
    EditCourses::set_dirty();
    _update_block_choices();

}


# ============================================================================
# remove section
# ============================================================================
sub _cb_remove_section_by_id {
    my $section_id = shift;
    my $section = $Course->get_section_by_id($section_id);
    return unless $section;
    $Course->remove_section($section);
    EditCourses::_refresh_course_gui( $Course,
        "Schedule/Course" . $Course->id );
    EditCourses::set_dirty();
}
# ============================================================================
# remove block from section
# ============================================================================
sub _cb_remove_block_from_section {
    my $section_id = shift;
    my $block_id = shift;
    my $section = $Course->get_section_by_id($section_id);
    return unless $section;
    my $block = $section->get_block_by_id($block_id);
    $section->remove_block($block);
    EditCourses::_refresh_section_gui( $section, "Schedule/Course" . $Course->id
    ."/Section".$section_id );
    EditCourses::set_dirty();
    _update_block_choices();
}

# ============================================================================
# change section name
# ============================================================================
sub _cb_change_section_name_by_id {
    my $section_id = shift;
    my $name = shift;
    my $section = $Course->get_section_by_id($section_id);
    return unless $section;
    $section->name($name);
    EditCourses::_refresh_course_gui( $Course,
        "Schedule/Course" . $Course->id );
    EditCourses::set_dirty();
}


# ============================================================================
# update stream choices
# ============================================================================
sub _update_stream_choices {
    my @streamsO = $Section->streams;
    my %streamNameO;
    foreach my $i (@streamsO) {
        $streamNameO{ $i->id } = $i->short_description;
    }
    my @streams = $Schedule->all_streams;
    my %streamName;
    foreach my $i (@streams) {
        $streamName{ $i->id } = $i->short_description;
    }

    $Gui->update_stream_choices( \%streamName, \%streamNameO );
}

# ============================================================================
# update block choices
# ============================================================================
sub _update_block_choices {
    my @blocksO = $Section->blocks;
    my %blockNameO;
    foreach my $i (@blocksO) {
        $blockNameO{ $i->id } = $i->short_description;
    }
    $Gui->update_block_choices( \%blockNameO );
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

    my @teachersO = $Section->teachers;
    my %teacherNameO;
    foreach my $i (@teachersO) {
        $teacherNameO{ $i->id } = "$i";
    }
    $Gui->update_teacher_choices( \%teacherName, \%teacherNameO );

}


# ============================================================================
# edit_block
# ============================================================================
sub _cb_edit_block {
    my $section_id  = shift;
    my $block_id = shift;
    my $section = $Course->get_section_by_id($section_id);
    return unless $section;
    my $block = $section->get_block_by_id($block_id);

    my $edit_block = EditBlockDialog->new($frame,$Schedule,$Course,$Section,$block);
    _update_block_choices();
}

# ============================================================================
# remove teacher from section
# ============================================================================
sub _cb_remove_teacher_from_section {
    my $section_id  = shift;
    my $teacher_id = shift;
    my $section = $Course->get_section_by_id($section_id);
    return unless $section;
    my $teacher = $Schedule->teachers->get($teacher_id);
    $section->remove_teacher($teacher);
    EditCourses::_refresh_section_gui( $section, "Schedule/Course" . $Course->id
    ."/Section".$section_id );
    EditCourses::set_dirty();
    _update_teacher_choices();
}

# ============================================================================
# remove stream from section
# ============================================================================
sub _cb_remove_stream_from_section {
    my $section_id = shift;
    my $stream_id = shift;
    my $section = $Course->get_section_by_id($section_id);
    return unless $section;
    my $stream = $Schedule->streams->get_by_id($stream_id);
    $section->remove_stream($stream);
    EditCourses::_refresh_section_gui( $section, "Schedule/Course" . $Course->id
    ."/Section".$section_id );
    EditCourses::set_dirty();
    _update_stream_choices();
}

# ============================================================================
# add teacher to section
# ============================================================================
sub _cb_add_teacher_to_section {
    my $section_id  = shift;
    my $teacher_id = shift;
    my $section = $Course->get_section_by_id($section_id);
    return unless $section;
    my $teacher = $Schedule->teachers->get($teacher_id);
    $section->assign_teacher($teacher);
    EditCourses::_refresh_section_gui( $section, "Schedule/Course" . $Course->id
    ."/Section".$section_id );
    EditCourses::set_dirty();
    _update_teacher_choices();
}

# ============================================================================
# add stream to section
# ============================================================================
sub _cb_add_stream_to_section {
    my $section_id = shift;
    my $stream_id = shift;
    my $section = $Course->get_section_by_id($section_id);
    return unless $section;
    my $stream = $Schedule->streams->get_by_id($stream_id);
    $section->assign_stream($stream);
    EditCourses::_refresh_section_gui( $section, "Schedule/Course" . $Course->id
    ."/Section".$section_id );
    EditCourses::set_dirty();
    _update_stream_choices();
}

1;

