from tkinter import *
from tkinter import messagebox
from os import path
import sys
from typing import Any


sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))
from schedule.UsefulClasses.MenuItem import MenuItem, MenuType

from schedule.GUI_Pages.EditCoursesTk import EditCoursesTk
from schedule.Model.ScheduleEnums import ResourceType


# ----------------------------------------------------------------------------
# generic objects for putting in listbox and trees
# ----------------------------------------------------------------------------
class Nothing:
    def __init__(self, a):
        self.a = a

    def checking(self):
        print(f"object: a = {self.a}")

    def __str__(self):
        return str(self.a)

    def __repr__(self):
        return str(self.a)

    def __lt__(self, other):
        return self.a < other.a


# ----------------------------------------------------------------------------
# methods for use in callback methods
# ----------------------------------------------------------------------------
def tree_menu(obj) -> list[MenuItem]:
    menu = MenuItem(name=str(obj),
                    label=f"Testing: {str(obj)}",
                    menu_type=MenuType.Command,
                    command=lambda: None)
    return [menu, ]


def resource_menu(resource_type: ResourceType, obj) -> list[MenuItem]:
    menu_title = MenuItem(name=str(resource_type),
                          label=f"Testing: {str(resource_type)}",
                          menu_type=MenuType.Command,
                          command=lambda: None)
    menu = MenuItem(name=str(obj),
                    label=f"Testing: {str(obj)}",
                    menu_type=MenuType.Command,
                    command=lambda: None)
    return [menu_title, menu]


def edit_dialog(obj: Any):
    messagebox.showinfo(title="Testing", message=f"Edit {str(obj)}")


def new_course_dialog():
    messagebox.showinfo(title="Testing", message="New Course dialog")


def teacher_stat_dialog(obj: Any):
    messagebox.showinfo(title="Testing", message=f"Teacher stat for {str(obj)}")


def valid_drop_site(resource_type: ResourceType, source: Any, target: Any) -> bool:
    if resource_type == ResourceType.teacher:
        if str(target).startswith("Section") or str(target).startswith("Block"):
            return True
    if str(target).startswith("Block"):
        return True
    return False


def item_dropped(resource_type: ResourceType, source: Any, target: Any):
    messagebox.showinfo(title="Testing",
                        message=f"{str(source)} [{str(resource_type)}] dropped on {str(target)}")


# ----------------------------------------------------------------------------
# setup for creating the EditCourseTk page
# ----------------------------------------------------------------------------
mw = Tk()
f = Frame(mw)
f.pack(expand=1, fill="both")

test_page = EditCoursesTk(f)
t1 = Nothing("Sandy")
t2 = Nothing("Bob")
t3 = Nothing("Sandy1")
t4 = Nothing("Bob1")
t5 = Nothing("Sandy2")
t6 = Nothing("Bob2")
t7 = Nothing("Sandy3")
t8 = Nothing("Bob3")
t9 = Nothing("Sandy4")
t10 = Nothing("Bob4")
t11 = Nothing("Sandy5")
t12 = Nothing("Bob5")
l1 = Nothing("P325")
l2 = Nothing("P322")
l3 = Nothing("P326")
l4 = Nothing("P323")
s1 = Nothing("1A")
s2 = Nothing("1B")
s3 = Nothing("2A")
s4 = Nothing("2B")
s5 = Nothing("3A")
s6 = Nothing("3B")

test_page.update_resource_type_objects(ResourceType.teacher, [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12])
test_page.update_resource_type_objects(ResourceType.stream, [s1, s2, s3, s4, s5, s6])
test_page.update_resource_type_objects(ResourceType.lab, [l1, l2, l3, l4])

c1 = Nothing("Operating Systems")
c1_id = test_page.add_tree_item("", str(c1), c1)
s1_id = test_page.add_tree_item(c1_id, f"Section 1 ({s1})", Nothing("Section 1"))
s2_id = test_page.add_tree_item(c1_id, f"Section 2 ({s2})", Nothing("Section 2"))
b1_id = test_page.add_tree_item(s1_id, "Block 1", Nothing("Block 1"))
b2_id = test_page.add_tree_item(s1_id, "Block 2", Nothing("Block 2"))
test_page.add_tree_item(b1_id, "Teacher: " + str(t1), t1)
test_page.add_tree_item(b1_id, "Lab: " + str(l1), l1)

# ----------------------------------------------------------------------------
# add all the callback routines
# ----------------------------------------------------------------------------
# call back routines
test_page.cb_edit_obj = edit_dialog
test_page.cb_new_course = new_course_dialog
test_page.cb_get_tree_menu = tree_menu
test_page.cb_get_resource_menu = resource_menu
test_page.cb_show_teacher_stat = teacher_stat_dialog
test_page.cb_target_is_valid_drop_site = valid_drop_site
test_page.cb_dropped_resource_onto_course_item = item_dropped

mw.mainloop()
