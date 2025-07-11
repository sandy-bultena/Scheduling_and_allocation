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

from typing import TYPE_CHECKING

from schedule.Tk import MenuItem, MenuType
from schedule.model import Course, Teacher, ResourceType, Section, Block, Lab

if TYPE_CHECKING:
    from schedule.presenter.edit_courses import EditCourses


# ====================================================================================================================
# Creates all the pop menu items, and their sub-menus if required
# ... each menu type will then call the appropriate 'presenter' code that will manage the modifications to the
#     tree/list menus in the EditCourse gui
# ====================================================================================================================
class EditCoursePopupMenuActions:
    """Creates all the pop menu items, dependent on the selected object, and their sub-menus if required

        Each menu type will then call the appropriate 'presenter' code that will manage the modifications to the
        tree/list menus in the EditCourse gui
    """
    def __init__(self, presenter: EditCourses, selected_object, parent_object, tree_id: str, tree_parent_id: str):
        """
        :param presenter: The presenter that is handling all the logic
        :param selected_object: The object that is the target of this menu
        :param parent_object: The parent of the object (ex. which block this teacher is attached to)
        :param tree_id: the id of the selected tree object
        :param tree_parent_id: the id of the selected tree object
        """
        self.presenter = presenter
        self.selected_object = selected_object
        self.parent_object = parent_object if parent_object is not None else presenter.schedule
        self.tree_id = tree_id
        self.tree_parent_id = tree_parent_id

    # ================================================================================================================
    # Create pop up menu based on the selected object
    # ================================================================================================================
    def create_tree_popup_menus(self):
        """create popup menus for trees

        menus are dynamic, depending on the current schedule, and what tree item was selected
        """

        menu_list: list[MenuItem] = []

        # ------------------------------------------------------------------------------------------------------------
        # course
        # ------------------------------------------------------------------------------------------------------------
        if isinstance(self.selected_object, Course):
            self._edit_course(menu_list)
            self._remove_item(menu_list, "Remove Course")

            menu_list.append(MenuItem(menu_type=MenuType.Separator))

            self._needs_allocation(menu_list)

            menu_list.append(MenuItem(menu_type=MenuType.Separator))

            self._add_section( menu_list)
            self.sub_menu_add_items(menu_list, ResourceType.teacher)
            self.sub_menu_add_items(menu_list, ResourceType.lab)
            self.sub_menu_add_items(menu_list, ResourceType.stream)

            menu_list.append(MenuItem(menu_type=MenuType.Separator))

            self._remove_all_items(menu_list, "course")

        # ------------------------------------------------------------------------------------------------------------
        # section
        # ------------------------------------------------------------------------------------------------------------
        if isinstance(self.selected_object, Section):
            self._edit_section(menu_list)
            self._remove_item(menu_list, "Remove Section")

            menu_list.append(MenuItem(menu_type=MenuType.Separator))

            self._add_blocks(menu_list)
            self.sub_menu_add_items(menu_list, ResourceType.teacher)
            self.sub_menu_add_items(menu_list, ResourceType.lab)
            self.sub_menu_add_items(menu_list, ResourceType.stream)

            menu_list.append(MenuItem(menu_type=MenuType.Separator))
            self.sub_menu_remove_items(menu_list, ResourceType.teacher)
            self.sub_menu_remove_items(menu_list, ResourceType.lab)
            self.sub_menu_remove_items(menu_list, ResourceType.stream)
            self._remove_all_items(menu_list, "section")

        # ------------------------------------------------------------------------------------------------------------
        # block
        # ------------------------------------------------------------------------------------------------------------
        if isinstance(self.selected_object, Block):
            self._edit_block(menu_list)
            self._remove_item(menu_list, "Remove Block")

            menu_list.append(MenuItem(menu_type=MenuType.Separator))

            self.sub_menu_add_items(menu_list, ResourceType.teacher)
            self.sub_menu_add_items(menu_list, ResourceType.lab)

            menu_list.append(MenuItem(menu_type=MenuType.Separator))
            self.sub_menu_remove_items(menu_list, ResourceType.teacher)
            self.sub_menu_remove_items(menu_list, ResourceType.lab)
            self._remove_all_items(menu_list, "block")

        # ------------------------------------------------------------------------------------------------------------
        # lab/teacher
        # ------------------------------------------------------------------------------------------------------------
        if isinstance(self.selected_object, Teacher):
            self._remove_item(menu_list, "Remove Teacher")
        if isinstance(self.selected_object, Lab):
            self._remove_item(menu_list, "Remove Lab")

        return menu_list

    # ================================================================================================================
    # Private methods that create the MenuList items
    # ================================================================================================================

    def _edit_block(self, menu_list: list[MenuItem]):
        menu_list.append(
            MenuItem(menu_type=MenuType.Command, label="Edit Block",
                     command=lambda *_: self.presenter.edit_block_dialog(self.selected_object, self.tree_id)
                     )
        )

    # ------------------------------------------------------------------------------------------------------------
    def _add_blocks(self, menu_list: list[MenuItem]):
        menu_list.append(
            MenuItem(menu_type=MenuType.Command, label="Add Blocks",
                     command=lambda *_: self.presenter.add_blocks_dialog(self.selected_object, self.tree_id)
                     )

        )

    # ------------------------------------------------------------------------------------------------------------
    def _edit_section(self, menu_list: list[MenuItem]):
        menu_list.append(
            MenuItem(menu_type=MenuType.Command, label="Edit Section",
                     command=lambda *_: self.presenter.edit_section_dialog(self.selected_object, self.tree_id)
                     )
        )

    # ------------------------------------------------------------------------------------------------------------
    def _edit_course(self, menu_list: list[MenuItem]):
        menu_list.append(
            MenuItem(menu_type=MenuType.Command, label="Edit Course",
                     command=lambda *_: self.presenter.edit_course_dialog(self.selected_object, self.tree_id)
                     )
        )

    # ------------------------------------------------------------------------------------------------------------
    def _remove_item( self, menu_list: list[MenuItem], text):
        menu_list.append(
            MenuItem(menu_type=MenuType.Command, label=text,
                     command=lambda *_: self.presenter.remove_selected_from_parent(self.parent_object, self.selected_object, self.tree_parent_id))
        )

    # ------------------------------------------------------------------------------------------------------------
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

    # ------------------------------------------------------------------------------------------------------------
    def _add_section(self, menu_list: list[MenuItem]):
        menu_list.append(MenuItem(menu_type=MenuType.Command, label="Add Sections",
                     command=lambda *_: self.presenter.add_section_dialog(self.selected_object, self.tree_id))
        )

    # ------------------------------------------------------------------------------------------------------------
    def sub_menu_add_items(self, menu_list: list[MenuItem], view: ResourceType):
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

        # need to define new sub in each iteration, because otherwise the closures will get messed up
        # ... do NOT use lambda's in a loop, we need to bind the individual 'item' in loop rather than its last value
        # ... https://stackoverflow.com/questions/54288926/python-loops-and-closures
        for item in items:
            def f(item_closure= item):
                return  self.presenter.assign_selected_to_parent(self.selected_object, item_closure,
                                                                                               self.tree_id)
            sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label=str(item), command=f))
        menu_list.append(sub_menu)

    # ------------------------------------------------------------------------------------------------------------
    def sub_menu_remove_items(self, menu_list: list[MenuItem], view: ResourceType):
        match view:
            case ResourceType.lab:
                items = [o for o in self.presenter.schedule.labs() if self.selected_object.has_lab(o)]
                text = "Remove Lab"
            case ResourceType.teacher:
                items = [o for o in self.presenter.schedule.teachers() if self.selected_object.has_teacher(o)]
                text = "Remove Teacher"
            case ResourceType.stream:
                items = [o for o in self.presenter.schedule.streams() if not self.selected_object.has_stream(o)]
                text = "Remove Stream"
            case _:
                items = []
                text = "Remove generic item"

        sub_menu = MenuItem(menu_type=MenuType.Cascade, tear_off=False, label=text)
        for item in items:
            sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label=str(item),
                                        command=lambda *_: self.presenter.remove_selected_from_parent(self.selected_object, item,
                                                                                               self.tree_parent_id)
                                        ))
        menu_list.append(sub_menu)

    # ------------------------------------------------------------------------------------------------------------
    def _remove_all_items(self, menu_list: list[MenuItem], parent_type):
        sub_menu = MenuItem(menu_type=MenuType.Cascade, tear_off=False, label="Remove All")

        # NOTE: do not put the following in a loop, because the closures won't work properly if you do.
        #       If you don't know what a closure is... https://en.wikipedia.org/wiki/Closure_(computer_programming)
        if parent_type == "course":
            sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label="sections",
                                        command=lambda *_: self.presenter.remove_all_types_from_selected_object("section",
                                                                                                           self.selected_object,
                                                                                                           self.tree_id)
                                        )
                           )

        if parent_type == "section":
            sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label="blocks",
                                        command=lambda *_: self.presenter.remove_all_types_from_selected_object("block",
                                                                                                           self.selected_object,
                                                                                                           self.tree_id)
                                        )
                           )

        if parent_type == "course" or parent_type == "section":
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



"""

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


"""