from typing import Optional, Callable, Any, TYPE_CHECKING, Literal

from schedule.Tk.menu_and_toolbars import MenuItem
from schedule.gui_dialogs.add_edit_block_dialog_tk import AddEditBlockDialogTk
from schedule.gui_dialogs.add_section_dialog_tk import AddSectionDialogTk
from schedule.gui_dialogs.edit_course_dialog_tk import EditCourseDialogTk
from schedule.gui_dialogs.edit_section_dialog_tk import EditSectionDialogTk
from schedule.model import Schedule, ResourceType, Section, Block, Teacher, Lab, Stream, Course,\
    WeekDay
from schedule.gui_pages import EditCoursesTk
from schedule.presenter.edit_courses_tree_and_resources import EditCoursePopupMenuActions

if TYPE_CHECKING:
    pass
#    from schedule.model import Teacher, Lab, Stream

RESOURCE_OBJECT = Teacher | Lab | Stream
TREE_OBJECT = Any

# =====================================================================================================================
# model subroutine lookups
# =====================================================================================================================
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
    "schedule": lambda presenter, parent_id, obj1: presenter.refresh(),
    "course": lambda presenter, parent_id, obj1:  presenter.refresh_course_gui(parent_id, obj1, False),
    "block": lambda presenter, parent_id, obj1: presenter.refresh_block_gui(parent_id, obj1, False),
    "section": lambda presenter, parent_id, obj1: presenter.refresh_section_gui(parent_id, obj1, False),
}
ASSIGN_SUBS = {
    "teacher": lambda parent, teacher: parent.add_teacher(teacher),
    "lab": lambda parent, lab: parent.add_lab(lab),
    "stream": lambda parent, stream: parent.add_stream(stream),
}

# =====================================================================================================================
# update a section with teachers and blocks and labs and streams
# =====================================================================================================================
def _update_section(descr:str, section: Section, teachers: list[Teacher], labs: list[Lab], streams: list[Stream],
                    blocks: list[tuple[float, float, float]]):
    section.name = descr
    section.remove_all_teachers()
    section.remove_all_labs()
    section.remove_all_blocks()
    section.remove_all_streams()
    for b in blocks:
        day = WeekDay(round(b[0]))
        start = b[1]
        hrs = b[2]
        section.add_block(day, start, hrs)
    for t in teachers:
        section.add_teacher(t)
    for l in labs:
        section.add_lab(l)
    for s in streams:
        section.add_stream(s)

def list_minus_list(all_list, other_list):
    other_list = set(other_list)
    minus_list = list(set(all_list).difference(other_list))
    minus_list.sort()
    return  minus_list, list(other_list)


# =====================================================================================================================
# EditCourse
# =====================================================================================================================
class EditCourses:
    """
    Creates the page for editing courses, with a tree view, lists of resources, drag'n'drop, etc.
    """

    def __init__(self,
                 dirty_flag_method: Callable[[Optional[bool]], bool],
                 frame,
                 schedule: Optional[Schedule],
                 gui: EditCoursesTk=None):
        """
        :param dirty_flag_method: a function that is used to set the flag if schedule has been changed
        :param frame: the frame to put all the gui stuff in
        :param schedule: the model
        :param gui: the gui page
        """

        if not gui:
            self.gui = EditCoursesTk(frame)
        else:
            self.gui = gui

        self.set_dirty_flag = dirty_flag_method
        self.frame = frame
        self.schedule = schedule
        self.tree_ids: dict[str, str] = {}


        # set all the event required handlers
        self.gui.handler_tree_edit = self.edit_tree_obj
        self.gui.handler_new_course = self.create_new_course
        self.gui.handler_tree_create_popup = self.create_tree_popup
        self.gui.handler_resource_create_menu = self.create_resource_menu
        self.gui.handler_show_teacher_stat = self.show_teacher_stat
        self.gui.handler_drag_resource = self.is_valid_drop
        self.gui.handler_drop_resource = self.object_dropped

    # -----------------------------------------------------------------------------------------------------------------
    # subs for refreshing the tree
    # -----------------------------------------------------------------------------------------------------------------
    def refresh(self):
        """ updates the gui with the data from schedule"""
        self.gui.clear_tree()
        self.tree_ids.clear()
        for course in self.schedule.courses():
            name = " ".join((course.number, course.name))
            course_id = self.gui.add_tree_item("", name, course)
            self.refresh_course_gui(course_id, course, True)
        self.gui.update_resource_type_objects(ResourceType.teacher, self.schedule.teachers())
        self.gui.update_resource_type_objects(ResourceType.lab, self.schedule.labs())
        self.gui.update_resource_type_objects(ResourceType.stream, self.schedule.streams())


    def refresh_course_gui(self, course_id, course: Course, hide:bool = True):
        """
        refresh the contents of the course (sections) on the tree structure
        :param course_id: the id of the Course tree item
        :param course:
        :param hide: leave the parent (and everything under it hidden?)
        :return:
        """
        self.gui.remove_tree_item_children(course_id)
        for section in course.sections():
            name = str(section)
            section_id = self.gui.add_tree_item(course_id, name, section, hide)
            self.refresh_section_gui(section_id, section, hide)

    def refresh_section_gui(self, section_id, section: Section, hide: bool = True):
        """
        adds the contents of the section (blocks) on the tree structure
        :param section_id: the id of the Section tree item
        :param section: course section
        :param hide: leave the parent (and everything under it hidden?)
        :return:
        """
        self.gui.remove_tree_item_children(section_id)

        # change the name of the parent text if stream exists for this section
        name = str(section)
        if len(section.streams()):
            name += "  (" + ",".join([str(stream) for stream in section.streams()]) + ")"
            self.gui.update_tree_text(section_id, name)

        for block in section.blocks():
            name = "Class Time: " + block.description()
            block_id = self.gui.add_tree_item(section_id, name, block, hide)
            self.refresh_block_gui(block_id, block, hide)


    def refresh_block_gui(self, block_id, block: Block, hide: bool=True):
        """
        adds the contents of the block (resources) onto the tree structure
        :param block_id: the id of the Block tree item
        :param block: course section block
        :param hide: leave the parent (and everything under it hidden?)
        :return:
        """
        self.gui.remove_tree_item_children(block_id)
        for lab in block.labs():
            self.gui.add_tree_item(block_id, str(lab), lab, hide)
        for teacher in block.teachers():
            self.gui.add_tree_item(block_id, str(teacher), teacher, hide)



    # -------------------------------------------------------------------------------------------------------------
    # Menus and Actions
    # -------------------------------------------------------------------------------------------------------------

    def edit_tree_obj(self, obj: Any,  parent_obj: Any, tree_id: str, parent_id: str):
        """
        Given a particular tree object, edit it (Blocks, Section, Course)
        :param obj: Any tree object, but will ignore it if it is not a Block, Section or Course
        :param parent_obj: Who is the parent of this object
        :param tree_id: What is the tree_id of this object
        :param parent_id: What is the tree_id of this object's parent object
        :return:
        """
        if isinstance(obj, Block):
            self.edit_block_dialog(obj,parent_obj, parent_id)
        if isinstance(obj, Section):
            self.edit_section_dialog(obj, tree_id)
        if isinstance(obj, Course):
            self.edit_course_dialog(obj, tree_id)

    def create_tree_popup(self, selected_obj: Any, parent_object, tree_path:str, tree_parent_path) -> list[MenuItem]:
        """
        Create a pop-up menu based on the selected object

        :param selected_obj: object that was selected on the tree
        :param parent_object: parent of selected object
        :param tree_path: the id of the tree item that was selected
        :param tree_parent_path: the id of the tree item that is the parent of the selected
        :return:
        """
        popup = EditCoursePopupMenuActions(self, selected_obj, parent_object, tree_path, tree_parent_path)
        return popup.create_tree_popup_menus()

    def create_new_course(self):
        """
        Create a new course
        """
        self._add_edit_course_dialog('add', None, None)

    def edit_course_dialog(self, course: Course, tree_id:str):
        """
        Create and use the edit course dialog to modify the selected course
        :param course:
        :param tree_id:
        """
        self._add_edit_course_dialog('edit',course,tree_id)

    def _add_edit_course_dialog(self, add_or_edit: Literal['add','edit'], course: Optional[Course], tree_id:Optional[str]):
        """
        Create and use the edit course dialog to modify the selected course
        :param course:
        :param tree_id:
        """

        def apply_changes(course_number: str, course_name:str, hours_per_week: float,
                          allocation: bool, num_sections:int, teachers:list[Teacher],
                          labs:list[Lab],  blocks:list[tuple[float,float,float]]):
            if course_number not in (c.number for c in self.schedule.courses()):
                this_course = self.schedule.add_update_course(number = course_number)
            else:
                this_course = self.schedule.get_course_by_number(course_number)

            this_course.name = course_name
            this_course.hours_per_week = hours_per_week
            this_course.needs_allocation = allocation
            this_course.remove_all_sections()
            for _ in range(num_sections):
                section = this_course.add_section()
                for b in blocks:
                    day = WeekDay(round(b[0]))
                    start = b[1]
                    hrs = b[2]
                    section.add_block(day, start, hrs)
                for t in teachers:
                    section.add_teacher(t)
                for l in labs:
                    section.add_lab(l)
            if add_or_edit == 'edit':
                REFRESH_SUBS['course'](self, tree_id, this_course)
            else:
                REFRESH_SUBS['schedule'](self,None, None)
            self.set_dirty_flag( True)

        block_data = []

        non_assigned_teachers, assigned_teachers = list_minus_list(self.schedule.teachers(), [])
        non_assigned_labs, assigned_labs = list_minus_list( self.schedule.labs(), [])

        course_number = ""
        number_sections = 1
        hours_per_week = 3
        course_name = ""
        course_allocation = True

        if course is not None:
            course_number = course.number
            number_sections = len(course.sections())
            hours_per_week = course.hours_per_week
            course_name = course.name
            course_allocation = course.needs_allocation
            if len(course.sections()) != 0:
                for b in course.sections()[0].blocks():
                    block_data.append((b.day.name, b.start, b.duration))

            non_assigned_teachers, assigned_teachers = list_minus_list(self.schedule.teachers(), course.teachers())
            non_assigned_labs, assigned_labs = list_minus_list(self.schedule.labs(), course.labs())


        EditCourseDialogTk(self.frame,
                                course_number=course_number,
                                edit_or_add=add_or_edit,
                                existing_course_numbers=[c.number for c in self.schedule.courses()],
                                course_name=course_name,
                                course_hours=hours_per_week,
                                course_allocation= course_allocation,
                                num_sections=number_sections,

                                assigned_teachers=assigned_teachers,
                                non_assigned_teachers=non_assigned_teachers,
                                assigned_labs=assigned_labs,
                                non_assigned_labs=non_assigned_labs,
                                current_blocks=block_data,
                                apply_changes=apply_changes,
                                )
        pass

    def add_section_dialog(self, course: Course, tree_id: str):
        """Add section to Course
        :param course:
        :param tree_id:
        """
        def apply_changes(number:int, blocks):
            for i in range(number):
                section = course.add_section()
                _update_section(section.name, section, [], [], [], blocks)
            self.set_dirty_flag(True)

        title = f"{course.name} ({course.hours_per_week} hrs)"

        AddSectionDialogTk(self.frame,
                                course_description=title,
                                apply_changes=apply_changes,
                                course_hours=course.hours_per_week),
        REFRESH_SUBS["course"](self, tree_id, course)


    def edit_section_dialog(self, section: Section, tree_id: str):
        """Modify an existing section
        :param section:
        :param tree_id:
        """
        def apply_changes(descr: str, teachers:list[Teacher], labs:list[Lab], streams:list[Stream], blocks:list[tuple[str,str,float]]):
            _update_section(descr, section, teachers, labs, streams, blocks)
            self.set_dirty_flag(True)


        title = f"{section.course.name} ({section.course.hours_per_week} hrs)"
        text = section.title
        block_data = []
        for b in section.blocks():
            block_data.append((b.day.name, b.start, b.duration))
        non_assigned_teachers, assigned_teachers = list_minus_list(self.schedule.teachers(),section.teachers())
        non_assigned_labs, assigned_labs = list_minus_list(self.schedule.labs(),section.labs())
        non_assigned_streams, assigned_streams = list_minus_list(self.schedule.streams(), section.streams())

        EditSectionDialogTk(self.frame,
                                 course_description=title,
                                 section_description=text,
                                 assigned_teachers=list(section.teachers()),
                                 non_assigned_teachers=non_assigned_teachers,
                                 assigned_labs=list(section.labs()),
                                 non_assigned_labs=non_assigned_labs,
                                 assigned_streams=list(section.streams()),
                                 non_assigned_streams=non_assigned_streams,
                                 current_blocks=block_data,
                                 apply_changes=apply_changes,
                                 course_hours=section.course.hours_per_week)
        REFRESH_SUBS["section"](self, tree_id, section)


    def add_blocks_dialog(self, section: Section, tree_id: str):
        """
        :param section: the section to add a block to
        :param tree_id: the id of the section
        """
        def _apply_changes(number: int, hours, teachers, labs):
            for i in range(number):
                block = section.add_block(start=8,duration=hours)
                for t in teachers:
                    block.add_teacher(t)
                for l in labs:
                    block.add_lab(l)
            REFRESH_SUBS["section"](self,tree_id, section)
            self.set_dirty_flag(True)
        AddEditBlockDialogTk(self.frame, "add", 1.5, [], list(self.schedule.teachers()),
                              [], list(self.schedule.labs()), _apply_changes)


    def edit_block_dialog(self, block, section: Any, parent_id: str):
        """
        Modify the block
        :param block:
        :param section:
        :param parent_id: the id of the section
        """
        def _apply_changes(_, hours, teachers, labs):
            block.remove_all_labs()
            block.remove_all_teachers()
            block.duration = hours
            for t in teachers:
                block.add_teacher(t)
            for l in labs:
                block.add_lab(l)
            REFRESH_SUBS["section"](self,parent_id, section)
            self.set_dirty_flag(True)

        non_assigned_teachers, assigned_teachers = list_minus_list(self.schedule.teachers(), section.teachers())
        non_assigned_labs, assigned_labs = list_minus_list(self.schedule.labs(), section.labs())

        AddEditBlockDialogTk(
            frame = self.frame,
            add_edit_type = "edit",
            duration = block.duration,
            assigned_teachers = list(block.teachers()),
            non_assigned_teachers= non_assigned_teachers,
            non_assigned_labs=non_assigned_labs,
            assigned_labs=assigned_labs,
            apply_changes= _apply_changes)



    def remove_selected_from_parent(self, parent, selected, parent_id):
        obj_type = str(type(selected)).lower()
        key = obj_type.split(".")[-1][0:-2]
        REMOVE_SUBS[key](parent,selected)

        obj_type = str(type(parent)).lower()
        key = obj_type.split(".")[-1][0:-2]
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

        obj_type = str(type(parent)).lower()
        key = obj_type.split(".")[-1][0:-2]
        REFRESH_SUBS[key](self,parent_id, parent)
        self.set_dirty_flag(True)


    def remove_all_types_from_selected_object(self, obj_type, selected, selected_id):
        REMOVE_ALL_SUBS[obj_type](selected)
        obj_type = str(type(selected)).lower()
        key = obj_type.split(".")[-1][0:-2]
        REFRESH_SUBS[key](self, selected_id, selected)
        self.set_dirty_flag(True)



    def create_resource_menu(self, view: ResourceType, obj: RESOURCE_OBJECT) -> list[MenuItem]: ...
    def show_teacher_stat(self, teacher: ResourceType ): ...
    def is_valid_drop(self, view: ResourceType, destination: TREE_OBJECT) -> bool:
        match view:
            case ResourceType.teacher:
                if isinstance(destination, Course) or isinstance(destination, Section) or isinstance(destination, Block):
                    return True
                else:
                    return False
            case ResourceType.stream:
                if isinstance(destination, Section):
                    return True
                else:
                    return False
            case ResourceType.lab:
                if isinstance(destination, Course) or isinstance(destination, Section) or isinstance(destination, Block):
                    return True
                else:
                    return False

        return False

    def object_dropped(self, resource: RESOURCE_OBJECT, destination: TREE_OBJECT, tree_id):
        self.assign_selected_to_parent(destination, resource,tree_id)

"""


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
