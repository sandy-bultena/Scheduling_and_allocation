from typing import Any, Optional
import pprint

import pytest

from schedule.model import Schedule, SemesterType, TimeSlot, WeekDay, ScheduleTime
from schedule.gui_pages.edit_courses_tk import EditCoursesTk
from schedule.presenter.edit_courses import EditCourses


class EditCoursesTkTest(EditCoursesTk):
        # ========================================================================
        # constructor
        # ========================================================================
        def __init__(self, frame):
            self.structure = dict()
            self.called_clear_tree_text = False
            self.called_update_tree_text_arguments = []
            self.called_update_tree_text = False
            self.called_remove_tree_item_children = False
            self.called_remove_tree_item_children_arguments = []
            self.called_remove_tree_item = False
            self.called_remove_tree_item_arguments = []
            self.called_add_tree_item = False
            self.called_add_tree_item_arguments = []
            self.called_update_resource_type = False
            self.called_update_resource_type_arguments = []
            self.called_clear_tree = False
            self.frame = frame

        def get_new_id(self, parent_id):
            # find all current ids with this parent, and then add 1
            kid_ids = [iid for iid in self.structure.keys() if
                       iid.startswith(parent_id) and len(parent_id) < len(iid) < len(parent_id) + 5]
            id_numbers = [int(iid[-3:]) for iid in kid_ids]

            if len(id_numbers) == 0:
                id_numbers = [0]
            new_id_number = max(id_numbers) + 1

            return f"{parent_id}.{new_id_number:03d}"

        def update_resource_type_objects(self, resource_type, objs):
            self.called_update_resource_type = True
            self.called_update_resource_type_arguments.append ([resource_type])

        def add_tree_item(self, parent_id: str, name: str, child: Any, hide: bool = True):
            self.called_add_tree_item = True
            self.called_add_tree_item_arguments.append( [parent_id, name, child, hide])
            iid = self.get_new_id(parent_id)
            self.structure[iid] = name
            return iid

        def remove_tree_item(self, tree_iid: str):
            self.called_remove_tree_item = True
            self.called_remove_tree_item_arguments.append( [tree_iid])
            if tree_iid in self.structure.keys():
                self.structure.pop(tree_iid)

        def remove_tree_item_children(self, tree_iid: str):
            self.called_remove_tree_item_children = True
            self.called_remove_tree_item_children_arguments.append([tree_iid])

            ids = list(self.structure.keys())
            for this_iid in ids:
                if this_iid.startswith(tree_iid) and len(this_iid) > len(tree_iid):
                    self.structure.pop(this_iid)


        def update_tree_text(self, tree_iid: str, text: str):
            self.called_update_tree_text = True
            self.called_update_tree_text_arguments.append([tree_iid, text])
            if tree_iid in self.structure.keys():
                self.structure[tree_iid] = text

        def get_iid_from_name(self, name) -> str:
            for iid, s_name in self.structure.items():
                if name == s_name:
                    return iid
            return ""

        def clear_tree(self):
            self.called_clear_tree_text = True
            self.structure.clear()

        def get_parent(self, tree_id):
            return tree_id[0:-4]

        def get_iid_from_name_with_parent_id(self, name, parent_id) -> str:
            for iid, s_name in self.structure.items():
                if name == s_name and iid.startswith(parent_id):
                    return iid
            return ""



@pytest.fixture()
def valid_tree_structure():
    return {'.001': '001 BasketWeaving',
        '.001.001': 'Section 1  (1A)',
        '.001.001.001': 'Block: Monday: 8:00 to 9:30',
        '.001.001.001.001': 'P107: C-Lab',
        '.001.001.001.002': 'Jane Doe',
        '.001.001.002': 'Block: Monday: 10:00 to 11:30',
        '.001.001.002.001': 'P107: C-Lab',
        '.001.001.002.002': 'Jane Doe',
        '.001.002': 'Section 2  (1B)',
        '.001.002.001': 'Block: Tuesday: 8:00 to 9:30',
        '.001.002.001.001': 'P322: Mac Lab',
        '.001.002.001.002': 'John Doe',
        '.001.002.002': 'Block: Tuesday: 10:00 to 11:30',
        '.001.002.002.001': 'P325',
        '.001.002.002.002': 'Babe Ruth',
        '.002': '002 Thumb Twiddling',
        '.002.001': 'Section 1',
        '.002.001.001': 'Block: Monday: 8:00 to 9:30',
        '.002.001.002': 'Block: Monday: 10:00 to 11:30',
        '.002.002': 'Section 2',
        '.002.002.001': 'Block: Tuesday: 8:00 to 9:30',
        '.002.002.002': 'Block: Tuesday: 10:00 to 11:30'}


@pytest.fixture()
def schedule_obj():
    schedule = Schedule()

    # teachers
    t1 = schedule.add_update_teacher("Jane", "Doe", "0.25", teacher_id=1)
    t2 = schedule.add_update_teacher("John", "Doe", teacher_id=2)
    t3 = schedule.add_update_teacher("Babe", "Ruth", teacher_id=3)
    t4 = schedule.add_update_teacher("Bugs", "Bunny", teacher_id = 4)

    # labs
    l1 = schedule.add_update_lab("P107", "C-Lab")
    l2 = schedule.add_update_lab("P322", "Mac Lab")
    l3 = schedule.add_update_lab("P325")
    l4 = schedule.add_update_lab("BH311", "Britain Hall")

    # streams
    st1 = schedule.add_update_stream("1A", "calculus available")
    st2 = schedule.add_update_stream("1B", "no calculus")
    st3 = schedule.add_update_stream("2A")
    st4 = schedule.add_update_stream("2B")

    # courses
    c_001 = schedule.add_update_course("001","BasketWeaving", SemesterType.fall )
    s_001_1 = c_001.add_section("1",1.5, section_id=1)
    s_001_1.add_stream(st1)
    b_001_1_1 = s_001_1.add_block(TimeSlot(WeekDay.Monday, ScheduleTime( 8) ))
    b_001_1_2 = s_001_1.add_block(TimeSlot(WeekDay.Monday, ScheduleTime( 10) ))
    b_001_1_1.add_teacher(t1)
    b_001_1_2.add_teacher(t1)
    b_001_1_1.add_lab(l1)
    b_001_1_2.add_lab(l1)

    s_001_2 = c_001.add_section("2",1.5,section_id=2)
    s_001_2.add_stream(st2)
    b_001_2_1 = s_001_2.add_block(TimeSlot(WeekDay.Tuesday, ScheduleTime( 8) ))
    b_001_2_2 = s_001_2.add_block(TimeSlot(WeekDay.Tuesday, ScheduleTime( 10) ))
    b_001_2_1.add_teacher(t2)
    b_001_2_2.add_teacher(t3)
    b_001_2_1.add_lab(l2)
    b_001_2_2.add_lab(l3)


    c_002 = schedule.add_update_course("002","Thumb Twiddling", SemesterType.fall )
    s_002_1 = c_002.add_section("1",1.5)
    b_002_1_1 = s_002_1.add_block(TimeSlot(WeekDay.Monday, ScheduleTime( 8) ))
    b_002_1_2 = s_002_1.add_block(TimeSlot(WeekDay.Monday, ScheduleTime( 10) ))
    s_002_2 = c_002.add_section("2",1.5)
    b_002_2_1 = s_002_2.add_block(TimeSlot(WeekDay.Tuesday, ScheduleTime( 8) ))
    b_002_2_2 = s_002_2.add_block(TimeSlot(WeekDay.Tuesday, ScheduleTime( 10) ))



    return schedule

@pytest.fixture()
def gui():
    return EditCoursesTkTest(None)

dirty_flag = False


@pytest.fixture()
def dirty():
    global dirty_flag
    dirty_flag = False

    def set_dirty(value: Optional[bool] = None) -> bool:
        global dirty_flag
        if value is not None:
            dirty_flag = value
        return dirty_flag

    return set_dirty

# =============================================================================
# Tests
# =============================================================================
def test_init_edit_course(gui, dirty, schedule_obj):
    """can initialize an instance of EditCourses"""

    # execute
    ec = EditCourses(dirty, None, schedule_obj, gui)

    # verify
    assert ec is not None
    assert isinstance(ec, EditCourses)

def test_refresh_updates_tree(gui, dirty, schedule_obj, valid_tree_structure):
    """can create a pop-up menu for course and all required items are there"""

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)

    # execute
    ec.refresh()

    # verify
    for key in valid_tree_structure.keys():
        assert key in gui.structure
        assert gui.structure[key] == valid_tree_structure[key]

def test_create_tree_menu_for_course(gui, dirty, schedule_obj):
    """can create a pop-up menu for course and all required items are there"""

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)

    # execute
    menu = ec.create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)

    # verify
    assert len([mi for mi in menu if mi.label == 'Edit Course']) == 1
    assert len([mi for mi in menu if mi.label == 'Remove Course']) == 1
    assert len([mi for mi in menu if 'needs allocation' in mi.label]) == 1
    assert len([mi for mi in menu if mi.label == 'Add Teacher']) == 1
    assert len([mi for mi in menu if mi.label == 'Add Lab']) == 1
    assert len([mi for mi in menu if mi.label == 'Add Stream']) == 1
    assert len([mi for mi in menu if mi.label == 'Remove All']) == 1

def test_tree_menu_for_course_edit_course(gui, dirty, schedule_obj):
    """TODO: edit that this method is called, etc..."""

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    menu = ec.create_tree_popup(schedule_obj.get_course_by_number("001"), None, "001", "")

    # execute

    # verify
    assert True

def test_tree_menu_for_course_remove_course(gui, dirty, schedule_obj):
    """run menu command for course: remove_course
    - dirty flag is set
    - tree is cleared of course
    - schedule has been update
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)

    menu = ec.create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove Course'][0]

    # execute
    mi.command()

    # verify
    assert dirty_flag
    assert schedule_obj.get_course_by_number("001") is None
    assert schedule_obj.get_course_by_number("002") is not None
    assert gui.clear_tree
    assert not gui.get_iid_from_name("001 BasketWeaving")
    assert gui.get_iid_from_name("002 Thumb Twiddling")

def test_tree_menu_for_course_unset_needs_allocation(gui, dirty, schedule_obj):
    """run menu command for course: needs allocation
    - dirty flag is set
    - needs allocation is unset
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)

    menu = ec.create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if "allocation" in mi.label and 'Unset' in mi.label][0]

    # execute
    mi.command()

    # verify
    assert dirty_flag
    assert not schedule_obj.get_course_by_number("001").needs_allocation

def test_tree_menu_for_course_set_needs_allocation(gui, dirty, schedule_obj):
    """run menu command for course: needs allocation
    - dirty flag is set
    - needs allocation is unset
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    course = schedule_obj.get_course_by_number("001")
    course.needs_allocation = False
    assert not schedule_obj.get_course_by_number("001").needs_allocation

    menu = ec.create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if "allocation" in mi.label and 'Set' in mi.label][0]

    # execute
    mi.command()

    # verify
    assert dirty_flag
    assert schedule_obj.get_course_by_number("001").needs_allocation

def test_tree_menu_for_course_add_teacher_sub_menu(gui, dirty, schedule_obj):
    """run menu command for course: add teachers
    - sub menu only contains teachers not already assigned to course
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    schedule_obj.add_update_teacher("Mickey","Mouse")

    # execute
    menu = ec.create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)

    # verify
    mi = [mi for mi in menu if mi.label == "Add Teacher"]
    print()
    pprint.pp(mi)
    assert len(mi[0].children) == 2
    assert mi[0].children[0].label == "Bugs Bunny"
    assert mi[0].children[1].label == "Mickey Mouse"

def test_tree_menu_for_course_add_teacher(gui, dirty, schedule_obj):
    """run menu command for course: add teachers - select teacher
    - teacher added to course/schedule
    - teacher added to course/tree
    - dirty flag is set
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    schedule_obj.add_update_teacher("Mickey","Mouse")
    menu = ec.create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == "Add Teacher"]
    add_menu = mi[0].children[1]

    # execute
    add_menu.command()

    # verify
    assert dirty_flag
    assert schedule_obj.get_course_by_number("001").has_teacher(schedule_obj.get_teacher_by_name("Mickey", "Mouse"))
    assert gui.get_iid_from_name_with_parent_id("Mickey Mouse", parent_id)

def test_tree_menu_for_course_add_stream_sub_menu(gui, dirty, schedule_obj):
    """run menu command for course: add streams
    - sub menu only contains streams not already assigned to course
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)

    # execute
    menu = ec.create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)

    # verify
    mi = [mi for mi in menu if mi.label == "Add Stream"]
    assert len(mi[0].children) == 2
    assert mi[0].children[0].label == "2A"
    assert mi[0].children[1].label == "2B"

def test_tree_menu_for_course_add_stream(gui, dirty, schedule_obj):
    """run menu command for course: add stream - select stream
    - stream added to course/schedule
    - stream added to course/tree
    - dirty flag is set
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    menu = ec.create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == "Add Stream"]
    add_menu = mi[0].children[1]

    # execute
    add_menu.command()

    # verify
    assert dirty_flag
    assert schedule_obj.get_course_by_number("001").has_stream(schedule_obj.get_stream_by_number("2B"))

def test_tree_menu_for_course_add_lab_sub_menu(gui, dirty, schedule_obj):
    """run menu command for course: add labs
    - sub menu only contains labs not already assigned to course
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)

    # execute
    menu = ec.create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)

    # verify
    mi = [mi for mi in menu if mi.label == "Add Lab"]

    assert len(mi[0].children) == 1
    assert mi[0].children[0].label == "BH311: Britain Hall"

def test_tree_menu_for_course_add_lab(gui, dirty, schedule_obj):
    """run menu command for course: add lab - select lab
    - lab added to course/schedule
    - lab added to course/tree
    - dirty flag is set
    """

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    menu = ec.create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == "Add Lab"]
    add_menu = mi[0].children[0]

    # execute
    add_menu.command()

    # verify
    assert dirty_flag
    assert schedule_obj.get_course_by_number("001").has_lab(schedule_obj.get_lab_by_number("BH311"))
    assert gui.get_iid_from_name_with_parent_id("BH311: Britain Hall", parent_id)

def test_tree_menu_for_course_remove_all_sub_menu(gui, dirty, schedule_obj):
    """create remove_all sub menu
    - sub menu for sections, streams, labs, and teachers"""

    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)

    # execute
    menu = ec.create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)

    # verify
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children
    assert len(sub_menu) == 4
    assert sub_menu[0].label == "sections"
    assert sub_menu[1].label == "streams"
    assert sub_menu[2].label == "labs"
    assert sub_menu[3].label == "teachers"


def test_tree_menu_for_course_remove_all_sections(gui, dirty, schedule_obj):
    """run menu command for course: remove_all section
    - dirty flag is set
    - all sections, etc have been removed from course/tree
    - schedule has been updated
    """
    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    menu = ec.create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children

    # execute
    mi2 = [mi for mi in sub_menu if mi.label == 'sections'][0]
    mi2.command()

    assert dirty_flag
    course = schedule_obj.get_course_by_number("001")
    assert len(course.sections()) == 0
    assert ".001.001" not in gui.structure.keys()
    assert ".001.002" not in gui.structure.keys()

def test_tree_menu_for_course_remove_all_streams(gui, dirty, schedule_obj):
    """run menu command for course: remove_all streams
    - dirty flag is set
    - schedule has been updated
    """
    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    menu = ec.create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children

    # execute
    mi2 = [mi for mi in sub_menu if mi.label == 'streams'][0]
    mi2.command()

    assert dirty_flag
    course = schedule_obj.get_course_by_number("001")
    assert len(course.streams()) == 0

def test_tree_menu_for_course_remove_all_labs(gui, dirty, schedule_obj):
    """run menu command for course: remove_all section
    - dirty flag is set
    - all labs, etc have been removed from course/tree
    - schedule has been updated
    """
    # prepare
    ec = EditCourses(dirty, None, schedule_obj, gui)
    ec.refresh()
    tree_id = gui.get_iid_from_name("001 BasketWeaving")
    parent_id = gui.get_iid_from_name(tree_id)
    menu = ec.create_tree_popup(schedule_obj.get_course_by_number("001"), None, tree_id, parent_id)
    mi = [mi for mi in menu if mi.label == 'Remove All'][0]
    sub_menu = mi.children

    # execute
    mi2 = [mi for mi in sub_menu if mi.label == 'labs'][0]
    mi2.command()

    assert dirty_flag
    course = schedule_obj.get_course_by_number("001")
    assert len(course.sections()) == 2
    ids = [iid for iid in gui.structure.keys() if iid.startswith(parent_id)]
    for iid in ids:
        assert not gui.structure[iid].startswith("P107")
        assert not gui.structure[iid].startswith("P322")
        assert not gui.structure[iid].startswith("P325")


