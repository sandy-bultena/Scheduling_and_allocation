from typing import Optional, Callable, Any, TYPE_CHECKING

from schedule.Tk.menu_and_toolbars import MenuItem, MenuType
from schedule.model import Schedule, ResourceType, Section, Block, Teacher, Lab, Stream, Course
from schedule.gui_pages import EditCoursesTk
import schedule.presenter.menus_tree_and_resource_list as menu
from schedule.presenter.menus_tree_and_resource_list import EditCoursePopupMenuActions

if TYPE_CHECKING:
    pass
#    from schedule.model import Teacher, Lab, Stream

RESOURCE_OBJECT = Teacher | Lab | Stream
TREE_OBJECT = Any

# =================================================================
# model subroutine lookups
# =================================================================
REMOVE_SUBS = {
    "teacher": lambda parent, teacher: parent.remove_teacher(teacher),
    "lab": lambda parent, lab: parent.remove_lab(lab),
    "stream": lambda parent, stream: parent.remove_stream(stream),
    "course": lambda parent, course: parent.remove_course(course),
    "block": lambda parent, block: parent.remove_block(block),
    "section": lambda parent, section: parent.remove_section(section),
}
REMOVE_ALL_SUBS = {
    "teacher": lambda parent: parent.remove_all_teachers(),
    "lab": lambda parent: parent.remove_all_labs(),
    "stream": lambda parent: parent.remove_all_streams(),
    "block": lambda parent: parent.remove_all_blocks(),
    "section": lambda parent: parent.remove_all_sections(),
}
REFRESH_SUBS = {
    "schedule": lambda presenter: presenter.refresh(),
    "course": lambda presenter, parent_id, obj1:  presenter.refresh_course_gui(parent_id, obj1, True),
    "block": lambda presenter, parent_id, obj1: presenter.refresh_block(parent_id, obj1, True),
    "section": lambda presenter, parent_id, obj1: presenter.refresh_section(parent_id, obj1, True),
}
ASSIGN_SUBS = {
    "teacher": lambda parent, teacher: parent.add_teacher(teacher),
    "lab": lambda parent, lab: parent.add_lab(lab),
    "stream": lambda parent, stream: parent.add_stream(stream),
}


class EditCourses:
    """
    Creates the basic EditResources (a simple matrix)
    :param frame: gui container object
    :param schedule: The Schedule object
    """

    def __init__(self,
                 dirty_flag_method: Callable[[Optional[bool]], bool],
                 frame,
                 schedule: Optional[Schedule],
                 gui: EditCoursesTk=None):

        if not gui:
            self.gui = EditCoursesTk(frame)
        else:
            self.gui = gui

        self.set_dirty_flag = dirty_flag_method
        self.frame = frame
        self.schedule = schedule
        self.tree_ids: dict[str, str] = {}


        # ---------------------------------------------------------------------
        # set all the event required handlers
        # ---------------------------------------------------------------------
        self.gui.handler_tree_edit = self.edit_tree_obj
        self.gui.handler_new_course = self.create_new_course
        self.gui.handler_tree_create_popup = self.create_tree_popup
        self.gui.handler_resource_create_menu = self.create_resource_menu
        self.gui.handler_show_teacher_stat = self.show_teacher_stat
        self.gui.handler_drag_resource = self.is_valid_drop
        self.gui.handler_drop_resource = self.object_dropped


    def refresh(self):
        """ updates the gui will the data from schedule"""
        self.gui.clear_tree()
        self.tree_ids.clear()
        for course in self.schedule.courses():
            name = " ".join((course.number, course.name))
            obj_id = self.gui.add_tree_item("", name, course)
            self.refresh_course_gui(obj_id, course, True)
        self.gui.update_resource_type_objects(ResourceType.teacher, self.schedule.teachers())
        self.gui.update_resource_type_objects(ResourceType.lab, self.schedule.labs())
        self.gui.update_resource_type_objects(ResourceType.stream, self.schedule.streams())


    def refresh_course_gui(self, parent_id, course: Course, hide:bool = True):
        """
        refresh the contents of the course (sections) on the tree structure
        :param parent_id: the parent id of the Course tree item
        :param course:
        :param hide: leave the parent (and everything under it hidden?)
        :return:
        """
        self.gui.remove_tree_item_children(parent_id)
        for section in course.sections():
            name = str(section)
            obj_id = self.gui.add_tree_item(parent_id, name, section, hide)
            self.refresh_section_gui(obj_id, section, hide)

    def refresh_section_gui(self, parent_id, section: Section, hide: bool = True):
        """
        adds the contents of the section (blocks) on the tree structure
        :param parent_id: the parent id of the tree item
        :param section: course section
        :param hide: leave the parent (and everything under it hidden?)
        :return:
        """
        self.gui.remove_tree_item_children(parent_id)

        # change the name of the parent text if stream exists for this section
        name = str(section)
        if len(section.streams()):
            name += "  (" + ",".join([str(stream) for stream in section.streams()]) + ")"
            self.gui.update_tree_text(parent_id, name)

        for block in section.blocks():
            name = "Block: " + block.description()
            obj_id = self.gui.add_tree_item(parent_id, name, block, hide)
            self.refresh_block_gui(obj_id, block, hide= True)

    def refresh_block_gui(self, parent_id, block: Block, hide: bool=True):
        """
        adds the contents of the block (resources) onto the tree structure
        :param parent_id: the parent id of the tree item
        :param block: course section block
        :param hide: leave the parent (and everything under it hidden?)
        :return:
        """
        self.gui.remove_tree_item_children(parent_id)
        for lab in block.labs():
            self.gui.add_tree_item(parent_id, str(lab), lab, hide)
        for teacher in block.teachers():
            self.gui.add_tree_item(parent_id, str(teacher), teacher, hide)





    def edit_tree_obj(self, obj: Any): ...
    def create_new_course(self): ...

    def create_tree_popup(self, selected_obj: Any, parent_object, tree_path:str, tree_parent_path) -> list[MenuItem]:
        popup = EditCoursePopupMenuActions(self, selected_obj, parent_object, tree_path, tree_parent_path)
        return popup.create_tree_popup_menus()

    # =========================================================================
    # Actions
    # =========================================================================

    def edit_course_dialog(self, course):
        #EditCourseDialog->new( $frame, $Schedule, $course );
        pass

    def add_section_dialog(self, course):
        pass
    """
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
    
        EditCourses::dirty_flag_method();
    }

    """

    def remove_obj2_from_obj1(self, parent, selected, parent_id):
        obj_type = str(type(selected)).lower()
        key = obj_type.split(".")[-1][0:-2]
        REMOVE_SUBS[key](parent,selected)
        if isinstance(parent, Schedule):
            self.refresh()
        else:
            REFRESH_SUBS[key](self,parent_id, parent)
        self.set_dirty_flag(True)

    def modify_course_needs_allocation(self, course:Course, value: bool, tree_path):
        course.needs_allocation = value
        self.refresh_course_gui(tree_path, course)
        self.set_dirty_flag(True)

    def assign_selected_to_parent(self, parent, selected, parent_id):
        obj_type = str(type(selected)).lower()
        key = obj_type.split(".")[-1][0:-2]
        ASSIGN_SUBS[key](parent,selected)
        if isinstance(parent, Course):
            self.refresh()
        else:
            REFRESH_SUBS[obj_type](self,parent_id, parent)
        self.set_dirty_flag(True)


    def remove_all_types_from_selected_object(self, obj_type, selected, selected_id):
        REMOVE_ALL_SUBS[obj_type](selected)
        obj_type = str(type(selected)).lower()
        key = obj_type.split(".")[-1][0:-2]
        REFRESH_SUBS[key](self, selected_id, selected)
        self.set_dirty_flag(True)







    """
        sub create_tree_menus {

    # ------------------------------------------------------------------------
    # course
    # ------------------------------------------------------------------------
    if ( $type eq 'course' ) {
        _edit_course( $menu, $sel_obj, $tree_path );
        _remove_item( $menu, $sel_obj, $Schedule, $tree_path, "Remove Course" );
        push @$menu, "separator";
        _needs_allocation( $menu, $sel_obj, $tree_path );
        _add_teachers( $menu, $sel_obj, $tree_path );
        _add_section( $menu, $sel_obj, $tree_path );
        push @$menu, "separator";
        _remove_teachers( $menu, $sel_obj, $tree_path );
        _remove_all( $menu, $sel_obj, $tree_path );
    }

    # ------------------------------------------------------------------------
    # section
    # ------------------------------------------------------------------------
    elsif ( $type eq 'section' ) {
        _edit_section( $menu, $sel_obj, $tree_path );
        _remove_item( $menu, $sel_obj, $par_obj, $tree_path, "Remove Section" );
        push @$menu, "separator";
        _add_blocks( $menu, $sel_obj, $tree_path );
        _add_teachers( $menu, $sel_obj, $tree_path );
        _add_labs( $menu, $sel_obj, $tree_path );
        _add_streams( $menu, $sel_obj, $tree_path );
        push @$menu, "separator";
        _remove_blocks( $menu, $sel_obj, $tree_path );
        _remove_teachers( $menu, $sel_obj, $tree_path );
        _remove_labs( $menu, $sel_obj, $tree_path );
        _remove_streams( $menu, $sel_obj, $tree_path );
        _remove_all( $menu, $sel_obj, $tree_path );
    }

    # ------------------------------------------------------------------------
    # block
    # ------------------------------------------------------------------------
    elsif ( $type eq 'block' ) {
        _edit_block( $menu, $sel_obj, $par_obj, $tree_path );
        _remove_item( $menu, $sel_obj, $par_obj, $tree_path, "Remove Block" );
        _add_teachers( $menu, $sel_obj, $tree_path );
        _add_labs( $menu, $sel_obj, $tree_path );
        _remove_teachers( $menu, $sel_obj, $tree_path );
        _remove_labs( $menu, $sel_obj, $tree_path );
        _remove_all( $menu, $sel_obj, $tree_path );
    }

    # ------------------------------------------------------------------------
    # lab/teacher
    # ------------------------------------------------------------------------
    elsif ( $type eq 'teacher' ) {
        _remove_item( $menu, $sel_obj, $par_obj, $tree_path, "Remove Teacher" );
    }
    elsif ( $type eq 'lab' ) {
        _remove_item( $menu, $sel_obj, $par_obj, $tree_path, "Remove Lab" );
    }
    return $menu;

}
"""
    def create_resource_menu(self, view: ResourceType, obj: RESOURCE_OBJECT) -> list[MenuItem]: ...
    def show_teacher_stat(self, teacher: ResourceType ): ...
    def is_valid_drop(self, view: ResourceType, source: RESOURCE_OBJECT, destination: TREE_OBJECT) -> bool: ...
    def object_dropped(self, view: ResourceType, resource: RESOURCE_OBJECT, obj: TREE_OBJECT): ...

"""

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

    EditCourses::dirty_flag_method();
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
    EditCourses::dirty_flag_method();

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

    EditCourses::dirty_flag_method();
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
    EditCourses::dirty_flag_method();
}


# =================================================================
# clear all scheduables from object 1
# =================================================================
sub clear_all_from_obj1 {
    my $obj1      = shift;
    my $tree_path = shift;
    $Clear_all_subs{ $$s_ptr->get_object_type($obj1) }->($obj1);
    $Refresh_subs{ $$s_ptr->get_object_type($obj1) }->( $obj1, $tree_path );
    dirty_flag_method();
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

    dirty_flag_method();
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
# remove object2 from object 1
# =================================================================
sub remove_obj2_from_obj1 {
    my $obj1      = shift;
    my $obj2      = shift;
    my $tree_path = shift;
    $Remove_subs{ $$s_ptr->get_object_type($obj2) }->( $obj1, $obj2 );
    $Refresh_subs{ $$s_ptr->get_object_type($obj1) }->( $obj1, $tree_path );
    dirty_flag_method();
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
    dirty_flag_method();

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
