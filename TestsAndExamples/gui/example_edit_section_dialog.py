from tkinter import *

from schedule.gui_dialogs.edit_section_dialog import AddEditSectionDialogTk
from schedule.model import SemesterType, TimeSlot, WeekDay, ScheduleTime
from schedule.model.schedule import Schedule
from schedule.gui_dialogs.add_edit_block_dialog_tk import AddEditBlockDialogTk

mw=Tk()
frame = Frame(mw)
frame.pack()
mw.geometry("400x400")

schedule = Schedule()

# teachers
t1 = schedule.add_update_teacher("Jane", "Doe", "0.25", teacher_id=1)
t2 = schedule.add_update_teacher("John", "Doe", teacher_id=2)
t3 = schedule.add_update_teacher("Babe", "Ruth", teacher_id=3)
t4 = schedule.add_update_teacher("Bugs", "Bunny", teacher_id=4)

# labs
l1 = schedule.add_update_lab("P107", "C-Lab")
l2 = schedule.add_update_lab("P322", "Mac Lab")
l3 = schedule.add_update_lab("P325")
l4 = schedule.add_update_lab("BH311", "Britain Hall")

# streams
st1 = schedule.add_update_stream("1A", "Math Stream")
st2 = schedule.add_update_stream("1B")

# courses
c_001 = schedule.add_update_course("001", "BasketWeaving", SemesterType.fall)
s_001_1 = c_001.add_section("1", 1.5, section_id=1)
s_001_1.add_stream(st1)
b_001_1_1 = s_001_1.add_block(TimeSlot(WeekDay.Monday, ScheduleTime(8)))
b_001_1_2 = s_001_1.add_block(TimeSlot(WeekDay.Monday, ScheduleTime(10)))
b_001_1_1.add_teacher(t1)
b_001_1_2.add_teacher(t1)
b_001_1_1.add_lab(l1)
b_001_1_2.add_lab(l1)

s_001_2 = c_001.add_section("2", 1.5, section_id=2)
s_001_2.add_stream(st2)
b_001_2_1 = s_001_2.add_block(TimeSlot(WeekDay.Tuesday, ScheduleTime(8)))
b_001_2_2 = s_001_2.add_block(TimeSlot(WeekDay.Tuesday, ScheduleTime(10)))
b_001_2_1.add_teacher(t2)
b_001_2_2.add_teacher(t3)
b_001_2_1.add_lab(l2)
b_001_2_2.add_lab(l3)


def apply_changes(teachers, labs, streams):
    print( teachers, labs, streams)

def go_edit():
    text = s_001_1.course.__repr__()+": "+str(s_001_1)
    db = AddEditSectionDialogTk(frame, "edit", text, [t1, t2, t3], [t4], [l2], [l1, l3, l4], [],[st1,st2], apply_changes)
def go_add():
    text = s_001_1.course.__repr__()+": "+str(s_001_1)
    db = AddEditSectionDialogTk(frame, "add", text, [t1, t2, t3], [t4], [l2], [l1, l3, l4], [], [st1, st2], apply_changes)

Button(frame, text="Edit Section", command=go_edit).pack()
#Button(frame, text="Add Blocks", command=go_add).pack()

mw.mainloop()