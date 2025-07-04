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
from __future__ import annotations
from typing import Any, TYPE_CHECKING

from schedule.Tk import MenuItem, MenuType
from schedule.model import Course, Teacher, Stream, ResourceType

if TYPE_CHECKING:
    from schedule.presenter.edit_courses import EditCourses

class EditCoursePopupMenuActions:
    def __init__(self, presenter: EditCourses, selected_object: Any, parent_object: Any, tree_id, tree_parent_id):
        """
        :param presenter: The presenter that is handling all the logic
        :param selected_object: The object that is the target of this menu
        :param parent_object: The parent of the object (ex. which block this teacher is attached to)
        :param tree_id: the id of the selected tree object
        :param parent_tree_id:

        """
        self.presenter = presenter
        self.selected_object = selected_object
        self.parent_object = parent_object if parent_object is not None else presenter.schedule
        self.tree_id = tree_id
        self.tree_parent_id = tree_parent_id

    def create_tree_popup_menus(self):
        """create popup menus for trees

        menus are dynamic, depending on the current schedule, and what tree item was selected
        :return: None
        """

        menu_list: list[MenuItem] = []

        # ------------------------------------------------------------------------
        # course
        # ------------------------------------------------------------------------
        if isinstance(self.selected_object, Course):
            self._edit_course(menu_list)
            self._remove_item(menu_list, "Remove Course")

            menu_list.append(MenuItem(menu_type=MenuType.Separator))

            self._needs_allocation(menu_list)
            self._add_section( menu_list)
            self._add_resource_items(menu_list, ResourceType.teacher)
            self._add_resource_items(menu_list, ResourceType.lab)
            self._add_resource_items(menu_list, ResourceType.stream)

            menu_list.append(MenuItem(menu_type=MenuType.Separator))

            self._remove_all_items(menu_list)

        return menu_list

    def _edit_course(self, menu_list: list[MenuItem]):
        menu_list.append(
            MenuItem(menu_type=MenuType.Command, label="Edit Course",
                     command=lambda *_: self.presenter.edit_course_dialog(self.selected_object)
                     )
        )

    def _remove_item( self, menu_list: list[MenuItem], text):
        menu_list.append(
            MenuItem(menu_type=MenuType.Command, label=text,
                     command=lambda *_: self.presenter.remove_obj2_from_obj1(self.parent_object, self.selected_object, self.tree_parent_id))
        )

    def _needs_allocation(self, menu_list: list[MenuItem]):
        if self.selected_object.needs_allocation:
            menu_list.append(
                MenuItem(menu_type=MenuType.Command, label="Unset 'needs allocation'",
                         command=lambda *_: self.presenter.modify_course_needs_allocation(self.selected_object, False, self.tree_id))
            )
        else:
            menu_list.append(
                MenuItem(menu_type=MenuType.Command, label="Set 'needs allocation'",
                         command=lambda *_: self.presenter.modify_course_needs_allocation(self.selected_object, True, self.tree_id))
            )

    def _add_section(self, menu_list: list[MenuItem]):
        menu_list.append(
            MenuItem(menu_type=MenuType.Command, label="Add Sections",
                     command=lambda *_: self.presenter.add_section_dialog(self.selected_object))
        )

    def _add_resource_items(self, menu_list: list[MenuItem], view: ResourceType):
        match view:
            case ResourceType.lab:
                items = [o for o in self.presenter.schedule.labs() if not self.selected_object.has_lab(o)]
                text = "Add Lab"
            case ResourceType.teacher:
                items = [o for o in self.presenter.schedule.teachers() if not self.selected_object.has_teacher(o)]
                text = "Add Teacher"
            case ResourceType.stream:
                items = [o for o in self.presenter.schedule.streams() if not self.selected_object.has_stream(o)]
                text = "Add Stream"
            case _:
                items = []
                text = "Add generic item"

        sub_menu = MenuItem(menu_type=MenuType.Cascade, tear_off=False, label=text)
        for item in items:
            sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label=str(item),
                                        command=lambda *_: self.presenter.assign_selected_to_parent(self.selected_object, item,
                                                                                               self.tree_parent_id)
                                        ))
        menu_list.append(sub_menu)

    def _remove_all_items(self, menu_list: list[MenuItem]):
        sub_menu = MenuItem(menu_type=MenuType.Cascade, tear_off=False, label="Remove All")

        # ------------------------------------------------------------------------------------------------------------
        # NOTE: do not put the following in a loop, because the closures won't work properly if you do.
        #       If you don't know what a closure is... https://en.wikipedia.org/wiki/Closure_(computer_programming)
        # ------------------------------------------------------------------------------------------------------------
        sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label="sections",
                                    command=lambda *_: self.presenter.remove_all_types_from_selected_object("section",
                                                                                                       self.selected_object,
                                                                                                       self.tree_id)
                                    )
                           )
        sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label="streams",
                                    command=lambda *_: self.presenter.remove_all_types_from_selected_object("stream",
                                                                                                       self.selected_object,
                                                                                                       self.tree_id)
                                    )
                           )
        sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label="labs",
                                    command=lambda *_: self.presenter.remove_all_types_from_selected_object("lab",
                                                                                                       self.selected_object,
                                                                                                       self.tree_id)
                                    )
                           )
        sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label="teachers",
                                    command=lambda *_: self.presenter.remove_all_types_from_selected_object("teacher",
                                                                                                       self.selected_object,
                                                                                                       self.tree_id)
                                    )
                           )
        menu_list.append(sub_menu)


def _remove_teachers(presenter, menu, sel_obj, parent_obj, tree_path):...
def _remove_all(presenter, menu, sel_obj, parent_obj, tree_path):...

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