from typing import Optional
from schedule.Model import schedule
from schedule.GUI_Pages import EditCoursesTk

"""
#!/usr/bin/perl
use strict;
use warnings;

package EditCourses;
use FindBin;
use Carp;
use lib "$FindBin::Bin/..";

use GUI::EditCoursesTk;
use Presentation::DynamicMenus;
use Presentation::EditCourseDialog;

=head1 NAME

EditCourses - provides GUI interface to modify (add/delete) courses 

=head1 VERSION

Version 1.00

=head1 SYNOPSIS

    use Schedule::Schedule;
    use GuiSchedule::ViewsManager
    use Tk;
    use Tk::InitGui;
    
    my $Dirtyflag           = 0;
    my $mw                  = MainWindow->new();
    my ( $Colours, $Fonts ) = InitGui->set($mw);    
    my $Schedule = Schedule->read_YAML('myschedule_file.yaml');
    my $Views_manager         = ViewsManager->new( $mw, \$Dirtyflag, \$Schedule );
    
    # create gui for editing courses
    # NOTE: requires $Views_manager just so that it can update
    #       the views if data has changed (via the dirty flag)
    
    my $de = EditCourses->new( $mw, $Schedule, \$Dirtyflag, $Views_manager )

=head1 DESCRIPTION

Create / Delete courses, assign teachers, labs, etc.

=head1 TODO

Assigning a teacher to a section that has no blocks appears not to
work, because they are not shown in the course_ttkTreeView.  However, they are there.

=head1 METHODS

=cut

# =================================================================
# Class/Global Variables
# =================================================================
our $Schedule;
my $Views_manager;
my $Dirty_ptr;
my $Gui;
my $frame;

# =================================================================
# new_basic
# =================================================================

=head2 new_basic ()

creates the basic Data Entry (simple matrix)

B<Returns>

data entry object

=cut
"""
class EditCourses:

    def __init__(self, frame, schedule: Optional[Schedule], test_gui=None):
        """
        Creates the basic EditResources (a simple matrix)
        :param frame: gui container object
        :param schedule: The Schedule object
        """
        if not test_gui:
            self.gui = EditCoursesTk(frame)
        else:
            self.gui = test_gui


"""
# ===================================================================
# new
# ===================================================================
sub new {
    my $class = shift;
    $frame         = shift;
    $Schedule      = shift;
    $Dirty_ptr     = shift;
    $Views_manager = shift;

    $Gui = EditCoursesTk->new($frame);

    # ---------------------------------------------------------------
    # add "Schedule" to course_ttkTreeView
    # ---------------------------------------------------------------
    my $path = '';
    $Gui->add(
        "Schedule",
        -text => 'Schedule',
        -data => { -obj => $Schedule },
    );
    _refresh_schedule_gui();

    # ---------------------------------------------------------------
    # populate teacher and lab and stream list
    # ---------------------------------------------------------------
    _refresh_scheduable_lists();

    # ---------------------------------------------------------------
    # define event handlers for EditCoursesTk
    # ---------------------------------------------------------------
    $Gui->cb_object_dropped_on_tree( \&_cb_object_dropped_on_tree );
    $Gui->cb_edit_obj( \&_cb_edit_obj );
    $Gui->cb_new_course( \&_cb_new_course );
    $Gui->cb_show_teacher_stat( \&_cb_show_teacher_stat );
    $Gui->cb_get_tree_menu( \&_cb_get_tree_menu );
    $Gui->cb_get_scheduable_menu_info( \&_cb_get_scheduable_menu );
}

# ===================================================================
# method look up tables
# ===================================================================

my $s_ptr        = \$Schedule;
my %Refresh_subs = (
    course   => \&_refresh_course_gui,
    section  => \&_refresh_section_gui,
    block    => \&_refresh_block_gui,
    schedule => \&_refresh_schedule_gui,
);

my %Assign_subs = (
    teacher => sub { my $obj = shift; $obj->assign_teacher(shift); },
    lab     => sub { my $obj = shift; $obj->assign_lab(shift); },
    stream  => sub { my $obj = shift; $obj->assign_stream(shift); },
);

my %Remove_subs = (
    teacher => sub { my $obj = shift; $obj->remove_teacher(shift); },
    lab     => sub { my $obj = shift; $obj->remove_lab(shift); },
    stream  => sub { my $obj = shift; $obj->remove_stream(shift); },
    course  => sub { my $obj = shift; $obj->courses->remove(shift); },
    block   => sub { my $obj = shift; $obj->remove_block(shift); },
    section => sub { my $obj = shift; $obj->remove_section(shift); },
);

my %Remove_all_subs = (
    teacher => sub { my $obj = shift; $obj->remove_all_teachers(); },
    lab     => sub { my $obj = shift; $obj->remove_all_labs(); },
    stream  => sub { my $obj = shift; $obj->remove_all_streams(); },
    section => sub { my $obj = shift; $obj->remove_all_sections(); },
    block   => sub { my $obj = shift; $obj->remove_all_blocks(); },
);
my %Clear_all_subs = (
    course  => sub { $$s_ptr->clear_all_from_course(shift); },
    section => sub { $$s_ptr->clear_all_from_section(shift); },
    block   => sub { $$s_ptr->clear_all_from_block(shift); },
);

# =================================================================
# add blocks to dialog
# =================================================================
sub add_blocks_dialog {
    my $section = shift;
    my $path    = shift;
    my $course;
    if ( $path =~ m:Schedule/Course(\d+)/: ) {
        $course = $Schedule->courses->get($1);
    }

    my $block_hours = AddBlocksDialogTk->new($frame);
    add_blocks_to_section( $course, $section, $block_hours );

    EditCourses::_refresh_course_gui( $course,
        "Schedule/Course" . $course->id );

    EditCourses::set_dirty();
}

# =================================================================
# add blocks to section
# =================================================================
sub add_blocks_to_section {
    my $course      = shift;
    my $section     = shift;
    my $block_hours = shift;

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
    EditCourses::_refresh_section_gui( $section,
        "Schedule/Course" . $course->id . "/Section" . $section->id );
    EditCourses::set_dirty();

}

# =================================================================
# add section dialog
# =================================================================
sub add_section_dialog {
    my $course      = shift;
    my $section_num = $course->get_new_number;    # gets a new section id
    my $section     = Section->new(
        -number => $section_num,
        -hours  => 0,
    );
    $course->add_section($section);
    EditCourses::_refresh_course_gui( $course,
        "Schedule/Course" . $course->id );

    my ( $section_names, $block_hours ) = AddSectionDialogTk->new($frame);
    add_sections_with_blocks( $course->id, $section_names, $block_hours );

    EditCourses::_refresh_course_gui( $course,
        "Schedule/Course" . $course->id );

    EditCourses::set_dirty();
}

# =================================================================
# add section with blocks
# =================================================================
sub add_sections_with_blocks {
    my $course        = shift;
    my $section_names = shift;
    my $block_hours   = shift || [];

    return unless $section_names;

    # loop over sections
    foreach my $sec_name (@$section_names) {
        my $section_num = $course->get_new_number;    # gets a new section id
        my $section     = Section->new(
            -number => $section_num,
            -hours  => 0,
            -name   => $sec_name,
        );
        $course->add_section($section);

        # loop over blocks foreach section
        foreach my $hours (@$block_hours) {
            if ($hours) {
                my $block_num = $section->get_new_number;
                my $block = Block->new( -number => $block_num );
                $block->duration($hours);
                $section->add_block($block);
            }
        }
    }

    # update the guis
    EditCourses::_refresh_course_gui( $course,
        "Schedule/Course" . $course->id );
    EditCourses::set_dirty();
}

# =================================================================
# assign object 2 to to object 1
# =================================================================
sub assign_obj2_to_obj1 {
    my $obj1      = shift;
    my $obj2      = shift;
    my $tree_path = shift;
    $Assign_subs{ $$s_ptr->get_object_type($obj2) }->( $obj1, $obj2 );
    $Refresh_subs{ $$s_ptr->get_object_type($obj1) }->( $obj1, $tree_path );
    set_dirty();
}

# =================================================================
# clear all scheduables from object 1
# =================================================================
sub clear_all_from_obj1 {
    my $obj1      = shift;
    my $tree_path = shift;
    $Clear_all_subs{ $$s_ptr->get_object_type($obj1) }->($obj1);
    $Refresh_subs{ $$s_ptr->get_object_type($obj1) }->( $obj1, $tree_path );
    set_dirty();
}

# =================================================================
# edit block dialog
# =================================================================
sub edit_block_dialog {
    my $block = shift;
    my $path  = shift;
    my $course;
    my $section;

    if ( $path =~ m:Schedule/Course(\d+)/Section(\d+): ) {
        $course  = $Schedule->courses->get($1);
        $section = $course->get_section_by_id($2);
    }
    return unless $course && $section;

    EditBlockDialog->new( $frame, $Schedule, $course, $section, $block );

    _refresh_course_gui( $course, "Schedule/Course" . $course->id );

    set_dirty();
}

# =================================================================
# edit course dialog
# =================================================================
sub edit_course_dialog {

    my $course = shift;
    EditCourseDialog->new( $frame, $Schedule, $course );
}

# =================================================================
# edit section dialog
# =================================================================
sub edit_section_dialog {
    my $section = shift;
    my $path    = shift;
    my $course;
    if ( $path =~ m:Schedule/Course(\d+)/: ) {

        $course = $Schedule->courses->get($1);
    }

    EditSectionDialog->new( $frame, $Schedule, $course, $section );
}

# =================================================================
# remove all specified scheduable types from object 1
# =================================================================
sub remove_all_type_from_obj1 {
    my $obj1      = shift;
    my $resource_type      = shift;
    my $tree_path = shift;
    $Remove_all_subs{$resource_type}->($obj1);
    $Refresh_subs{ $$s_ptr->get_object_type($obj1) }->( $obj1, $tree_path );
    set_dirty();
}

# =================================================================
# remove object2 from object 1
# =================================================================
sub remove_obj2_from_obj1 {
    my $obj1      = shift;
    my $obj2      = shift;
    my $tree_path = shift;
    $Remove_subs{ $$s_ptr->get_object_type($obj2) }->( $obj1, $obj2 );
    $Refresh_subs{ $$s_ptr->get_object_type($obj1) }->( $obj1, $tree_path );
    set_dirty();
}

# =================================================================
# remove scheduable (teacher/lab/stream)
# =================================================================
sub remove_scheduable {
    my $resource_type = shift;
    my $obj  = shift;
    $Schedule->remove_teacher($obj) if ( $resource_type eq 'teacher' );
    $Schedule->remove_lab($obj)     if ( $resource_type eq 'lab' );
    $Schedule->remove_stream($obj)  if ( $resource_type eq 'stream' );
    _refresh_schedule_gui();
}

# =================================================================
# set dirty flag
# =================================================================
sub set_dirty {
    $$Dirty_ptr = 1;
    $Views_manager->redraw_all_views if $Views_manager;
}

# ===================================================================
# add lab to course_ttkTreeView
# ===================================================================
sub _add_lab_to_gui {
    my $l        = shift;
    my $path     = shift;
    my $not_hide = shift;

    my $l_id = $l . $l->id;

    #no warnings;
    $Gui->add(
        "$path/$l_id",
        -text => "Lab: " . $l->number . " " . $l->descr,
        -data => { -obj => $l }
    );

}

# ===================================================================
# add teacher to the course_ttkTreeView
# ===================================================================
sub _add_teacher_to_gui {
    my $t        = shift;
    my $path     = shift;
    my $not_hide = shift || 0;

    my $t_id = "Teacher" . $t->id;
    $Gui->add(
        "$path/$t_id",
        -text => "Teacher: $t",
        -data => { -obj => $t }
    );
}

# =================================================================
# edit/modify a schedule object
# =================================================================
sub _cb_edit_obj {
    my $obj  = shift;
    my $path = shift;

    my $obj_type = $Schedule->get_object_type($obj);

    if ( $obj_type eq 'course' ) {
        edit_course_dialog( $obj, $path );
    }
    elsif ( $obj_type eq 'section' ) {
        edit_section_dialog( $obj, $path );
    }
    elsif ( $obj_type eq 'block' ) {
        edit_block_dialog( $obj, $path );
    }
    elsif ( $obj_type eq 'teacher' ) {
        _cb_show_teacher_stat( $obj->id );
    }
    else {
        $Gui->alert;
    }
}

# =================================================================
# get course_ttkTreeView menu
# =================================================================
sub _cb_get_tree_menu {
    return DynamicMenus::create_tree_menus( $Schedule, @_ );
}

# =================================================================
# get scheduable menu
# =================================================================
sub _cb_get_scheduable_menu {
    return DynamicMenus::show_scheduable_menu( $Schedule, @_ );
}

# ============================================================================================
# Create a new course
# ============================================================================================
sub _cb_new_course {
    my $course = Course->new( -number => "", -name => "" );
    $Schedule->courses->add($course);
    EditCourseDialog->new( $frame, $Schedule, $course );
}

# =================================================================
# object dropped on course_ttkTreeView
# =================================================================
sub _cb_object_dropped_on_tree {
    my $dragged_object_type = shift;
    my $id_of_obj_dropped   = shift;
    my $path                = shift;
    my $dropped_onto_obj    = shift;

    my $dropped_on_type = $Schedule->get_object_type($dropped_onto_obj);
    return unless $dropped_on_type;

    # -------------------------------------------------------------
    # assign dropped object to appropriate schedule object
    # -------------------------------------------------------------
    if ( $dragged_object_type eq 'teacher' ) {
        my $add_obj = $Schedule->teachers->get($id_of_obj_dropped);
        $dropped_onto_obj->assign_teacher($add_obj);
    }

    if ( $dragged_object_type eq 'lab' ) {
        if ( $dropped_on_type ne 'course' ) {
            my $add_obj = $Schedule->labs->get($id_of_obj_dropped);
            $dropped_onto_obj->assign_lab($add_obj);
        }
        else {
            $Gui->alert;
            return;
        }
    }

    if ( $dragged_object_type eq 'stream' ) {
        my $add_obj = $Schedule->streams->get($id_of_obj_dropped);
        if ( $dropped_on_type eq 'block' ) {
            $dropped_onto_obj = $dropped_onto_obj->section;
        }
        $dropped_onto_obj->assign_stream($add_obj);
    }

    # -------------------------------------------------------------
    # update the gui
    # -------------------------------------------------------------
    if ( $dragged_object_type eq 'stream' ) {
        _refresh_schedule_gui();
    }
    elsif ( $dropped_on_type eq 'block' ) {
        _refresh_block_gui( $dropped_onto_obj, $path, 1 );
    }
    elsif ( $dropped_on_type eq 'section' ) {
        _refresh_section_gui( $dropped_onto_obj, $path, 1 );
    }
    elsif ( $dropped_on_type eq 'course' ) {
        _refresh_course_gui( $dropped_onto_obj, $path, 1 );
    }
    set_dirty();

}

#===============================================================
# Show Teacher Stats
#===============================================================

sub _cb_show_teacher_stat {
    my $id      = shift;
    my $teacher = $Schedule->teachers->get($id);
    $Gui->show_message( "$teacher", $Schedule->teacher_stat($teacher) );
}

# ===================================================================
# labs/teachers/streams list
# ===================================================================
sub _refresh_scheduable_lists {

    my @teacher;
    foreach
      my $teacher ( sort { &_sort_by_teacher_name } $Schedule->teachers->list )
    {
        push @teacher, { -id => $teacher->id, -name => "$teacher" };
    }
    $Gui->set_teachers( \@teacher );

    my @labs;
    foreach my $lab ( sort { &_sort_by_alphabet } $Schedule->labs->list ) {
        push @labs, { -id => $lab->id, -name => "$lab" };
    }
    $Gui->set_labs( \@labs );

    my @streams;
    foreach my $stream ( sort { &_sort_by_alphabet } $Schedule->streams->list )
    {
        push @streams, { -id => $stream->id, -name => "$stream" };
    }
    $Gui->set_streams( \@streams );
}

# ===================================================================
# refresh Schedule
# ===================================================================
sub _refresh_schedule_gui {
    my $path = "Schedule";
    $Gui->delete( 'offsprings', $path );

    # refresh course_ttkTreeView
    foreach my $course ( sort { &_sort_by_alphabet } $Schedule->courses->list )
    {
        my $c_id    = "Course" . $course->id;
        my $newpath = "Schedule/$c_id";
        $Gui->add(
            $newpath,
            -text     => $course->number . "\t" . $course->name,
            -data     => { -obj => $course },
            -style    => $Gui->course_style,
            -itemtype => 'text',
        );
        _refresh_course_gui( $course, $newpath );
    }

    # refresh lists
    _refresh_scheduable_lists();

}

# ===================================================================
# refresh course branch
# ===================================================================
sub _refresh_course_gui {
    my $course   = shift;
    my $path     = shift;
    my $not_hide = shift;
    $Gui->delete( 'offsprings', $path );

    # add all the sections for each course
    foreach my $s ( sort { &_sort_by_number } $course->sections ) {
        my $s_id     = "Section" . $s->id;
        my $new_path = "$path/$s_id";
        my $text     = "$s";
        $Gui->add(
            $new_path,
            -text => $text,
            -data => { -obj => $s }
        );
        _refresh_section_gui( $s, $new_path, $not_hide );
    }

}

# ===================================================================
# refresh section branch
# ===================================================================
sub _refresh_section_gui {
    my $section  = shift;
    my $path     = shift;
    my $not_hide = shift;
    $Gui->delete( 'offsprings', $path );

    my $text = "$section";
    if ( @{ $section->streams } ) {
        $text = $text . " (" . join( ",", $section->streams ) . ")";
    }
    $Gui->update_tree_text( $path, $text );

    # add all the blocks for this section
    foreach my $bl ( sort { &_sort_by_block_id } $section->blocks ) {
        my $b_id     = "Block" . $bl->id;
        my $new_path = "$path/$b_id";

        $Gui->add(
            $new_path,
            -text => $bl->short_description,
            -data => { -obj => $bl }
        );

        _refresh_block_gui( $bl, $new_path, $not_hide );
    }

}

# ===================================================================
# refresh block branch
# ===================================================================
sub _refresh_block_gui {
    my $bl       = shift;
    my $path     = shift;
    my $not_hide = shift;
    $Gui->delete( 'offsprings', $path );

    # add all the teachers for this block
    foreach my $t ( sort { &_sort_by_teacher_name } $bl->teachers ) {
        _add_teacher_to_gui( $t, $path, $not_hide );
    }

    # add all the labs for this block
    foreach my $l ( sort { &_sort_by_alphabet } $bl->labs ) {
        _add_lab_to_gui( $l, $path, $not_hide );
    }

    #$course_ttkTreeView->hide( 'entry', $path ) unless $not_hide;
    #$course_ttkTreeView->autosetmode();
}

###################################################################
# sorting subs
###################################################################
sub _sort_by_number { $a->number <=> $b->number }

sub _sort_by_alphabet { $a->number cmp $b->number }

sub _sort_by_block_time {
    $a->day_number <=> $b->day_number
      || $a->start_number <=> $b->start_number;
}

sub _sort_by_block_id {
    $a->number <=> $b->number;
}

sub _sort_by_teacher_name {
    $a->firstname cmp $b->firstname
      || $a->lastname cmp $b->lastname;
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
"""
