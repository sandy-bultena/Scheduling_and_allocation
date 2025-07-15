from typing import Optional, Callable, Any, TYPE_CHECKING, Literal

from schedule.Tk.menu_and_toolbars import MenuItem, MenuType
from schedule.gui_dialogs.add_edit_block_dialog_tk import AddEditBlockDialogTk
from schedule.gui_dialogs.add_section_dialog_tk import AddSectionDialogTk
from schedule.gui_dialogs.edit_course_dialog_tk import EditCourseDialogTk
from schedule.gui_dialogs.edit_section_dialog_tk import EditSectionDialogTk
from schedule.model import Schedule, ResourceType, Section, Block, Teacher, Lab, Stream, Course, TimeSlot, ScheduleTime, \
    WeekDay, ClockTime
from schedule.gui_pages import EditCoursesTk
import schedule.presenter.edit_courses_tree_and_resources as menu
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
                    blocks: list[tuple[str, str, float]]):
    section.descr = descr
    section.remove_all_teachers()
    section.remove_all_labs()
    section.remove_all_blocks()
    section.remove_all_streams()
    for b in blocks:
        day = WeekDay[b[0]]
        start = ClockTime(b[1])
        hrs = b[2]
        section.add_block(TimeSlot(day, start, hrs))
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
                          labs:list[Lab],  blocks:list[tuple[str,str,float]]):
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
                    day = WeekDay[b[0]]
                    start = ClockTime(b[1])
                    hrs = b[2]
                    section.add_block(TimeSlot(day, start, hrs))
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
                    block_data.append((b.time_slot.day.name, str(b.time_slot.time_start), str(b.time_slot.duration)))

            non_assigned_teachers, assigned_teachers = list_minus_list(self.schedule.teachers(), course.teachers())
            non_assigned_labs, assigned_labs = list_minus_list(self.schedule.labs(), course.labs())


        db = EditCourseDialogTk(self.frame,
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

        db = AddSectionDialogTk(self.frame,
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
            block_data.append((b.time_slot.day.name, str(b.time_slot.time_start), str(b.time_slot.duration)))
        non_assigned_teachers, assigned_teachers = list_minus_list(self.schedule.teachers(),section.teachers())
        non_assigned_labs, assigned_labs = list_minus_list(self.schedule.labs(),section.labs())
        non_assigned_streams, assigned_streams = list_minus_list(self.schedule.streams(), section.streams())

        db = EditSectionDialogTk(self.frame,
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
                block = section.add_block(TimeSlot(start=ScheduleTime(8),duration=hours))
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
            block.time_slot.duration = hours
            for t in teachers:
                block.add_teacher(t)
            for l in labs:
                block.add_lab(l)
            REFRESH_SUBS["section"](self,parent_id, section)
            self.set_dirty_flag(True)

        non_assigned_teachers, assigned_teachers = list_minus_list(self.schedule.teachers(), section.teachers())
        non_assigned_labs, assigned_labs = list_minus_list(self.schedule.labs(), section.labs())

        AddEditBlockDialogTk(self.frame, "edit", block.time_slot.duration, list(block.teachers()),
                             non_assigned_teachers, list(block.labs()), non_assigned_labs, _apply_changes)



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
