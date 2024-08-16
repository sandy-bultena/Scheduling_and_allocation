#!/usr/bin/perl
use strict;
use warnings;
# ============================================================================
# Create and manage the EditCourseDialog
#
# - provides callback methods for EditCourseDialogTk
#
# INPUTS:
#   frame       - a gui object that can be used as a container
#   schedule    - the schedule object
#   course      - the course that is to be edited
#
# METHODS:
#   - none -
#
# ============================================================================
# NOTE: this module is dependent on functions in EditCourses
# ============================================================================


package EditCourseDialog;
use FindBin;
use Carp;
use lib "$FindBin::Bin/..";

use GUI::EditCourseDialogTk;
use Presentation::EditSectionDialog;

my $Schedule;
my $Gui;
my $Course;
my $Frame;

# ============================================================================
# constructor
# ============================================================================
sub new {
    my $class = shift;
    $Frame = shift;
    $Schedule = shift;
    $Course   = shift;
    my $self = bless { -course => $Course };

   # ------------------------------------------------------------------------
    # make dialog box
    # ------------------------------------------------------------------------
    $Gui = EditCourseDialogTk->new( $Frame, $Course->id, $Course->number,
        $Course->name, $Course->needs_allocation, );

    _update_stream_choices();
    _update_teacher_choices();
    _update_section_choices();

    # set the callback functions (event handlers)

    $Gui->cb_remove_course_by_id( \&_cb_remove_course_by_id );
    $Gui->cb_change_course_name_by_id( \&_cb_change_course_name_by_id );
    $Gui->cb_change_course_number_by_id( \&_cb_change_course_number_by_id );
    $Gui->cb_add_stream_to_course( \&_cb_add_stream_to_course );
    $Gui->cb_remove_stream_from_course( \&_cb_remove_stream_from_course );
    $Gui->cb_remove_teacher_from_course( \&_cb_remove_teacher_from_course );
    $Gui->cb_add_teacher_to_course( \&_cb_add_teacher_to_course );
    $Gui->cb_add_sections_with_blocks( \&_cb_add_sections_with_blocks );
    $Gui->cb_edit_section( \&_cb_edit_section );
    $Gui->cb_is_course_num_unique( \&_cb_is_course_num_unique );
    $Gui->cb_set_allocation( \&_cb_set_allocation );
    $Gui->cb_remove_section_from_course( \&_cb_remove_section_from_course );

    $Gui->Show();
}

# ============================================================================
# add sections with blocks to course
# ============================================================================
sub _cb_add_sections_with_blocks {
        my $course_id     = shift;
    my $section_names = shift || [];
    my $block_hours   = shift || [];
    my $course        = $Schedule->courses->get($course_id);
    return unless $course;

    EditCourses::add_sections_with_blocks($course,$section_names,$block_hours);
    _update_section_choices();

}

# ============================================================================
# add stream to course
# ============================================================================
sub _cb_add_stream_to_course {
    my $course_id = shift;
    my $stream_id = shift;
    my $course    = $Schedule->courses->get($course_id);
    return unless $course;
    my $stream = $Schedule->streams->get_by_id($stream_id);
    $course->assign_stream($stream);
    EditCourses::_refresh_course_gui( $course, "Schedule/Course" . $course_id );
    EditCourses::set_dirty();
    _update_stream_choices();
}

# ============================================================================
# add teacher to course
# ============================================================================
sub _cb_add_teacher_to_course {
    my $course_id  = shift;
    my $teacher_id = shift;
    my $course     = $Schedule->courses->get($course_id);
    return unless $course;
    my $teacher = $Schedule->teachers->get($teacher_id);
    $course->assign_teacher($teacher);
    EditCourses::_refresh_course_gui( $course, "Schedule/Course" . $course_id );
    EditCourses::set_dirty();
    _update_teacher_choices();
}

# ============================================================================
# change course name
# ============================================================================
sub _cb_change_course_name_by_id {
    my $course_id  = shift;
    my $name = shift;
    my $course     = $Schedule->courses->get($course_id);
    return unless $course;
    $course->name($name);
    EditCourses::_refresh_schedule_gui();
    EditCourses::set_dirty();
}

# ============================================================================
# change course number
# ============================================================================
sub _cb_change_course_number_by_id {
    my $course_id  = shift;
    my $number = shift;
    my $course     = $Schedule->courses->get($course_id);
    return unless $course;
    $course->number($number);
    EditCourses::_refresh_schedule_gui();
    EditCourses::set_dirty();
}

# ============================================================================
# edit/add section from course
# ============================================================================
sub _cb_edit_section {
    my $course_id  = shift;
    my $section_id = shift;
    my $course     = $Schedule->courses->get($course_id);
    return unless $course;

    my $section;
    
    # if section exists, use it
    if ($section_id) {
        $section = $Course->get_section_by_id($section_id);
    }
    
    # else create a new section
    else {
        my $section_num = $Course->get_new_number;    # gets a new section id
        $section     = Section->new(
            -number => $section_num,
            -hours  => 0,
        );
        $course->add_section($section);
    EditCourses::_refresh_course_gui( $course, "Schedule/Course" . $course_id );
    EditCourses::set_dirty();
    }

    my $change_message = EditSectionDialog->new($Frame,$Schedule,$Course,$section);

    # because many things could have changed in the other dialog,
    # we need to update everything just in case
    _update_stream_choices();
    _update_teacher_choices();
    _update_section_choices();
    return $change_message;
}

# ============================================================================
# is course number unique
# ============================================================================
sub _cb_is_course_num_unique {
    my $number = shift;
    return !$Schedule->courses->get_by_number($number);
}

# ============================================================================
# remove course 
# ============================================================================
sub _cb_remove_course_by_id {
    my $course_id  = shift;
    my $course     = $Schedule->courses->get($course_id);
    return unless $course;
    $Schedule->remove_course($course);
    EditCourses::_refresh_schedule_gui();
    EditCourses::set_dirty();
}

# ============================================================================
# remove section from course
# ============================================================================
sub _cb_remove_section_from_course {
    my $course_id  = shift;
    my $section_id = shift;
    my $course     = $Schedule->courses->get($course_id);
    return unless $course;
    my $section = $course->get_section_by_id($section_id);
    $course->remove_section($section);
    EditCourses::_refresh_course_gui( $course, "Schedule/Course" . $course_id );
    EditCourses::set_dirty();
    _update_section_choices();
}

# ============================================================================
# remove stream from course
# ============================================================================
sub _cb_remove_stream_from_course {
    my $course_id = shift;
    my $stream_id = shift;
    my $course    = $Schedule->courses->get($course_id);
    return unless $course;
    my $stream = $Schedule->streams->get_by_id($stream_id);
    $course->remove_stream($stream);
    EditCourses::_refresh_course_gui( $course, "Schedule/Course" . $course_id );
    EditCourses::set_dirty();
    _update_stream_choices();
}

# ============================================================================
# remove teacher from course
# ============================================================================
sub _cb_remove_teacher_from_course {
    my $course_id  = shift;
    my $teacher_id = shift;
    my $course     = $Schedule->courses->get($course_id);
    return unless $course;
    my $teacher = $Schedule->teachers->get($teacher_id);
    $course->remove_teacher($teacher);
    EditCourses::_refresh_course_gui( $course, "Schedule/Course" . $course_id );
    EditCourses::set_dirty();
    _update_teacher_choices();
}

# ============================================================================
# set allocation
# ============================================================================
sub _cb_set_allocation {
    my $alloc_ptr = shift;
    $Course->needs_allocation($$alloc_ptr);
    EditCourses::set_dirty();
}

# ============================================================================
# update section choices
# ============================================================================
sub _update_section_choices {
    my @sections = $Course->sections;
    my %sectionName;
    foreach my $i (@sections) {
        $sectionName{ $i->id } = "$i";
    }
    $Gui->update_section_choices( \%sectionName );

}

# ============================================================================
# update stream choices
# ============================================================================
sub _update_stream_choices {
    my @streamsO = $Course->streams;
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
# update teacher choices
# ============================================================================
sub _update_teacher_choices {
    my @teachers = $Schedule->all_teachers;
    my %teacherName;
    foreach my $i (@teachers) {
        $teacherName{ $i->id } = "$i";
    }

    my @teachersO = $Course->teachers;
    my %teacherNameO;
    foreach my $i (@teachersO) {
        $teacherNameO{ $i->id } = "$i";
    }
    $Gui->update_teacher_choices( \%teacherName, \%teacherNameO );

}




1;

