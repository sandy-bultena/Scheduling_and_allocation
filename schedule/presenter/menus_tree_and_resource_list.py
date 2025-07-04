"""
# ============================================================================
# Create dynamic menus (dependent on the state of the Schedule object)
#
# METHODS:
#   create_tree_menus       # right-click popup menus for tree items
#   show_scheduable_menu    # right-click popup menu for teacher/stream/labs lists
#
# NOTE: this module is dependent on functions in EditCourses
# ============================================================================
"""
from typing import Any, TYPE_CHECKING

from schedule.Tk import MenuItem, MenuType
from schedule.gui_pages import EditCoursesTk
from schedule.model import Course, Teacher, Stream, ResourceType

if TYPE_CHECKING:
    from schedule.presenter.edit_courses import EditCourses


#def _edit_course(presenter: EditCourses, menu_list, sel_obj, tree_path):
def _edit_course(presenter, menu_list, sel_obj, tree_path):
    """prepare the menu item to edit a course via a gui dialog

    :param presenter: the instance of the class that actually does the work
    :param menu_list: a list of current menu items
    :param sel_obj:  the object to be deleted
    :param tree_path:
    :return:
    """
    menu_list.append(
        MenuItem(menu_type=MenuType.Command, label="Edit Course",
                 command=lambda *_: presenter.edit_course_dialog( sel_obj)
                 )
    )

def _remove_item(presenter, menu_list, sel_obj, parent_obj, parent_tree_path, text:str):
    """Create a menu item for removing one object from another

    :param presenter: the instance of the class that actually does the work
    :param menu_list: a list of current menu items
    :param sel_obj:  the object to be deleted
    :param parent_obj: the parent of the selected object
    :param parent_tree_path: the path/id of the parent of the selected element in the tree
    :param text: the text used to display on the pop-up menu
    """
    menu_list.append(
        MenuItem(menu_type=MenuType.Command, label=text,
                 command=lambda *_: presenter.remove_obj2_from_obj1( parent_obj, sel_obj, parent_tree_path) )
    )

def _needs_allocation(presenter, menu_list, course: Course, tree_path):
    """create a menu item that will toggle the current allocation flag for a specific course

    :param presenter: the instance of the class that actually does the work
    :param menu_list: a list of current menu items
    :param course:  the selected course
    :param tree_path: the path/id of the selected course
    """
    if course.needs_allocation:
        menu_list.append(
            MenuItem(menu_type=MenuType.Command, label="Unset 'needs allocation'",
                     command=lambda *_: presenter.modify_course_needs_allocation(course, False, tree_path))
        )
    else:
        menu_list.append(
            MenuItem(menu_type=MenuType.Command, label="Set 'needs allocation'",
                     command=lambda *_: presenter.modify_course_needs_allocation(course, True, tree_path))
        )

def _add_resource_items(presenter, menu_list, selected_obj, parent_obj, parent_tree_path, view: ResourceType):
    """make a sub menu with a list of items as menu choices

    :param presenter: the instance of the class that actually does the work
    :param menu_list: a list of current menu items
    :param selected_obj:  the object to be deleted
    :param parent_obj: the parent of the selected object
    :param parent_tree_path: the path/id of the parent of the selected element in the tree
    :param view: Resource type of object to add
    """

    match view:
        case ResourceType.lab:
            items = [o for o in presenter.schedule.labs() if not selected_obj.has_lab(o)]
            text = "Add Lab"
        case ResourceType.teacher:
            items = [ o for o in presenter.schedule.teachers() if not selected_obj.has_teacher(o)]
            text = "Add Teacher"
        case ResourceType.stream:
            items = [o for o in presenter.schedule.streams() if not selected_obj.has_stream(o)]
            text = "Add Stream"
        case _:
            items = []
            text = "Add generic item"

    sub_menu = MenuItem(menu_type=MenuType.Cascade, tear_off=False, label=text)
    for item in items:
        sub_menu.add_child( MenuItem(menu_type=MenuType.Command, label=str(item),
                                   command=lambda *_: presenter.assign_selected_to_parent(selected_obj, item, parent_tree_path)
                                   ))
    menu_list.append(sub_menu)


def _add_section(presenter, menu_list, selected_obj, parent_obj, tree_path):
    """

    :param presenter: the instance of the class that actually does the work
    :param menu_list: a list of current menu items
    :param selected_obj:  the object to be deleted
    :param parent_obj: the parent of the selected object
    :param tree_path:
    :return:

        push @$menu,
      [
        'command',
        "Add Sections(s)",
        -command => [ \&EditCourses::add_section_dialog, $sel_obj, $tree_path ]
      ];

    """


def _remove_all_items(presenter, menu_list, selected_obj, tree_path):
    """

    :param presenter: the instance of the class that actually does the work
    :param menu_list: a list of current menu items
    :param selected_obj:  the object to be deleted
    :param tree_path: the path/id of the selected course
    """

    #     def remove_all_types_from_selected_object(self, obj_type, selected_object, selected_id):
    sub_menu = MenuItem(menu_type=MenuType.Cascade, tear_off=False, label="Remove All")
    sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label="sections",
                                command=lambda *_: presenter.remove_all_types_from_selected_object("section",
                                                                                                   selected_obj,
                                                                                                   tree_path)
                                )
                       )
    sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label="streams",
                                command=lambda *_: presenter.remove_all_types_from_selected_object("stream",
                                                                                                   selected_obj,
                                                                                                   tree_path)
                                )
                       )
    sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label="labs",
                                command=lambda *_: presenter.remove_all_types_from_selected_object("lab",
                                                                                                   selected_obj,
                                                                                                   tree_path)
                                )
                       )
    sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label="teachers",
                                command=lambda *_: presenter.remove_all_types_from_selected_object("teacher",
                                                                                                   selected_obj,
                                                                                                   tree_path)
                                )
                       )
    menu_list.append(sub_menu)


def _remove_teachers(presenter, menu, sel_obj, parent_obj, tree_path):...
def _remove_all(presenter, menu, sel_obj, parent_obj, tree_path):...

def create_tree_menus(presenter, selected_obj: Any, parent_obj: Any, tree_path:str, parent_tree_path:str)->list[MenuItem]:
    """create popup menus for trees

    menus are dynamic, depending on the current schedule, and what tree item was selected
    :param presenter: The presenter that is handling all the logic
    :param selected_obj: The object that is the target of this menu
    :param parent_obj: The parent of the object (ex. which block this teacher is attached to)
    :param tree_path: the id of the selected tree object
    :param parent_tree_path:
    :return: None
    """

    menu_list: list[MenuItem] = []

    # ------------------------------------------------------------------------
    # course
    # ------------------------------------------------------------------------
    if isinstance(selected_obj, Course):
        _edit_course( presenter, menu_list, selected_obj, tree_path )
        _remove_item( presenter, menu_list, selected_obj, presenter.schedule, parent_tree_path, "Remove Course" )

        menu_list.append(MenuItem(menu_type=MenuType.Separator))

        _needs_allocation(presenter, menu_list, selected_obj, tree_path )
        _add_section( presenter, menu_list, selected_obj, parent_obj,  parent_tree_path )
        _add_resource_items(presenter, menu_list, selected_obj, parent_obj, parent_tree_path, ResourceType.teacher)
        _add_resource_items(presenter, menu_list, selected_obj, parent_obj, parent_tree_path, ResourceType.lab)
        _add_resource_items(presenter, menu_list, selected_obj, parent_obj, parent_tree_path, ResourceType.stream)

        menu_list.append(MenuItem(menu_type=MenuType.Separator))

        _remove_teachers( presenter, menu_list, selected_obj, parent_obj, tree_path )
        _remove_all_items( presenter, menu_list, selected_obj, tree_path )

    return menu_list
"""
sub create_tree_menus {
    $Schedule = shift;
    my $sel_obj   = shift;    # selected object
    my $par_obj   = shift;    # parent object
    my $tree_path = shift;    # tree path (i.e. parent.child)

    my $type = $Schedule->get_object_type($sel_obj);
    my $menu = [];

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

# ============================================================================
# create popup menus for streams/labs/teacher
# - menus are dynamic, depending on the current schedule, and what
#   type of object was selected
# ============================================================================
sub show_scheduable_menu {
    my $Schedule   = shift;
    my $sel_obj_id = shift;
    my $type       = shift;
    my $sel_obj    = $Schedule->get_object_by_id_and_type( $sel_obj_id, $type );

    my $menu    = [];
    my $courses = [];

    push @$menu,
      [
        "command", "Delete $type",
        -command => [ \&EditCourses::remove_scheduable, $type, $sel_obj ]
      ];

    push @$menu,
      [
        'cascade', "Add $type to Course",
        -tearoff   => 0,
        -menuitems => $courses
      ];

    # ------------------------------------------------------------------------
    # all courses
    # ------------------------------------------------------------------------
    foreach my $course ( sort { &_sort_by_alphabet } $Schedule->courses->list )
    {
        my $sections = [];
        push @$courses,
          [
            'cascade', $course->short_description,
            -tearoff   => 0,
            -menuitems => $sections
          ];
        if ( $type ne 'stream' ) {
            push @$sections,
              [
                'command',
                'All Sections',
                -command => [
                    \&EditCourses::assign_obj2_to_obj1,
                    $course,
                    $sel_obj,
                    "Schedule/Course" . $course->id,
                ]
              ];
        }

        # --------------------------------------------------------------------
        # all sections per course
        # --------------------------------------------------------------------
        foreach my $section ( sort { &_sort_by_number } $course->sections ) {
            my $blocks = [];
            push @$sections,
              [ "cascade", "$section", -tearoff => 0, -menuitems => $blocks ];
            push @$blocks,
              [
                'command',
                'All Blocks',
                -command => [
                    \&EditCourses::assign_obj2_to_obj1,
                    $section,
                    $sel_obj,
                    "Schedule/Course" . $course->id . "/Section" . $section->id
                ]
              ];

            # ----------------------------------------------------------------
            # all blocks per section
            # ---------------------------------------------------------------
            if ( $type ne 'stream' ) {
                foreach
                  my $block ( sort { &_sort_by_block_id } $section->blocks )
                {
                    push @$blocks,
                      [
                        'command',
                        "$block",
                        -command => [
                            \&EditCourses::assign_obj2_to_obj1,
                            $block,
                            $sel_obj,
                            "Schedule/Course"
                              . $course->id
                              . "/Section"
                              . $section->id
                              . "/Block"
                              . $block->id
                        ]
                      ];

                }
            }

        }

    }
    return $menu;
}

# --------------------------------------------------------------------
# add blocks,
# --------------------------------------------------------------------
sub _add_blocks {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;

    push @$menu,
      [
        'command',
        "Add Blocks",
        -command => [ \&EditCourses::add_blocks_dialog, $sel_obj, $tree_path ]
      ];
}



# --------------------------------------------------------------------
# edit block
# --------------------------------------------------------------------
sub _edit_block {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $par_obj   = shift;
    my $tree_path = shift;

    push @$menu,
      [
        'command',
        "Edit Block",
        -command =>
          [ \&EditCourses::edit_block_dialog, $sel_obj, $tree_path ]
      ];
}

# --------------------------------------------------------------------
# edit course
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# edit section
# --------------------------------------------------------------------
sub _edit_section {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;

    push @$menu,
      [
        'command',
        "Edit Section",
        -command => [ \&EditCourses::edit_section_dialog, $sel_obj, $tree_path ]
      ];
}

# --------------------------------------------------------------------
# needs allocation
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# remove all resources menu
# --------------------------------------------------------------------
sub _remove_all {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;
    push @$menu,
      [
        'command',
        "Clear All Teachers, Labs, and Streams",
        -command => [ \&EditCourses::clear_all_from_obj1, $sel_obj, $tree_path ]
      ];
}

# --------------------------------------------------------------------
# removing blocks
# --------------------------------------------------------------------
sub _remove_blocks {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;

    my $blocks = [];
    foreach my $block ( $sel_obj->blocks ) {
        push @$blocks, { name => $block->short_description, obj => $block };
    }
    _remove_items( $menu, $sel_obj, $tree_path, $blocks, "Blocks", "block" );

}

# --------------------------------------------------------------------
# Remove a single item
# --------------------------------------------------------------------
sub _remove_item {
    my ( $menu, $obj1, $obj2, $path, $title ) = @_;

    $path =~ s:^(.*)/.*$:$1:;
    push @$menu,
      [
        "command", $title,
        -command =>
          [ \&EditCourses::remove_obj2_from_obj1, $obj2, $obj1, $path ]
      ];
}

# --------------------------------------------------------------------
# removing items
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# removing labs
# --------------------------------------------------------------------
sub _remove_labs {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;

    my $labs = [];

    foreach my $lab ( $sel_obj->labs ) {
        push @$labs, { name => "$lab", obj => $labs };
    }
    _remove_items( $menu, $sel_obj, $tree_path, $labs, "Labs", "lab" );
}

# --------------------------------------------------------------------
# removing streams
# --------------------------------------------------------------------
sub _remove_streams {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;

    my $streams = [];

    foreach my $stream ( $sel_obj->streams ) {
        push @$streams, { name => "$stream", obj => $stream };
    }
    _remove_items( $menu, $sel_obj, $tree_path, $streams, "Streams", "stream" );
}

# --------------------------------------------------------------------
# removing teachers
# --------------------------------------------------------------------
sub _remove_teachers {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;

    my $teachers = [];
    foreach my $teacher ( $sel_obj->teachers ) {
        push @$teachers, { name => "$teacher", obj => $teacher };
    }
    _remove_items( $menu, $sel_obj, $tree_path, $teachers, "Teachers",
        "teacher" );
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
    $a->lastname cmp $b->lastname
      || $a->firstname cmp $b->firstname;
}

1;

"""