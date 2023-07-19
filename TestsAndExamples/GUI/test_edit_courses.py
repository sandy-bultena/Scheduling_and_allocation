from tkinter import *
from os import path
import sys

sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))

from schedule.GUI_Pages.EditCoursesTk import EditCoursesTk
from schedule.GUI_Pages.EditCoursesTk import TreeViewObjectType
from schedule.Schedule.ScheduleEnums import ResourceType


class Nothing:
    def __init__(self, a):
        self.a = a

    def checking(self):
        print(f"object = {self.a=}")

    def __str__(self):
        return str(self.a)


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

test_page.update_view_type_objects(ResourceType.teacher, [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12])
test_page.update_view_type_objects(ResourceType.stream, [s1, s2, s3, s4, s5, s6])
test_page.update_view_type_objects(ResourceType.lab, [l1, l2, l3, l4])

c1 = Nothing("Operating Systems")
tt1 = TreeViewObjectType(obj=c1, children=[
    TreeViewObjectType(Nothing("Section 1"), children=[
        TreeViewObjectType(Nothing("Mon 8am-9am"), children=[
            TreeViewObjectType(l1), TreeViewObjectType(t2)
        ])
    ]),
    TreeViewObjectType(Nothing("Section 2"), children=[
        TreeViewObjectType(Nothing("Tue 8am-9am"), children=[
            TreeViewObjectType(l2), TreeViewObjectType(t3)
        ])
    ])
])


test_page.update_courses_tree([tt1, ])

mw.mainloop()
