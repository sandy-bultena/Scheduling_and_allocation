from tkinter import *

from schedule.gui_dialogs.edit_section_dialog_tk import EditSectionDialogTk
from schedule.gui_dialogs.add_section_dialog_tk import AddSectionDialogTk
from schedule.model import SemesterType, TimeSlot, WeekDay, ScheduleTime, ClockTime
from schedule.model.schedule import Schedule, Course, Section
from schedule.gui_dialogs.add_edit_block_dialog_tk import AddEditBlockDialogTk

mw=Tk()
frame = Frame(mw)
frame.pack()
mw.geometry("400x400")

schedule = Schedule()

# teachers
t1 = schedule.add_update_teacher("Jane", "Doe", "0.25", teacher_id="1")
t2 = schedule.add_update_teacher("John", "Doe", teacher_id="2")
t3 = schedule.add_update_teacher("Babe", "Ruth", teacher_id="3")
t4 = schedule.add_update_teacher("Bugs", "Bunny", teacher_id="4")

# labs
l1 = schedule.add_update_lab("P107", "C-Lab")
l2 = schedule.add_update_lab("P322", "Mac Lab")
l3 = schedule.add_update_lab("P325")
l4 = schedule.add_update_lab("BH311", "Britain Hall")

# streams
st1 = schedule.add_update_stream("1A", "Math Stream")
st2 = schedule.add_update_stream("1B")

# courses
c_001:Course = schedule.add_update_course("001", "Basket Weaving", SemesterType.fall)
s_001_1:Section = c_001.add_section("1", section_id=1)
s_001_1.add_stream(st1)
b_001_1_1 = s_001_1.add_block(TimeSlot(WeekDay.Monday, ScheduleTime(8)))
b_001_1_2 = s_001_1.add_block(TimeSlot(WeekDay.Monday, ScheduleTime(10)))
b_001_1_1.add_teacher(t1)
b_001_1_2.add_teacher(t1)
b_001_1_1.add_lab(l1)
b_001_1_2.add_lab(l1)

s_001_2 = c_001.add_section("2", section_id=2)
s_001_2.add_stream(st2)
b_001_2_1 = s_001_2.add_block(TimeSlot(WeekDay.Tuesday, ScheduleTime(8)))
b_001_2_2 = s_001_2.add_block(TimeSlot(WeekDay.Tuesday, ScheduleTime(10)))
b_001_2_1.add_teacher(t2)
b_001_2_2.add_teacher(t3)
b_001_2_1.add_lab(l2)
b_001_2_2.add_lab(l3)


def apply_changes(descr, teachers, labs, streams, blocks):
    print( descr, teachers, labs, streams, blocks)
    for b in blocks:
        day = WeekDay[b[0]]
        start = ClockTime(b[1])
        hrs = b[2]

        print(day, start, hrs)

def apply_changes2(number, blocks):
    print( number,  blocks)
    for b in blocks:
        day = WeekDay[b[0]]
        start = ClockTime(b[1])
        hrs = b[2]

        print(day, start, hrs)

def go_edit():
    title = f"{s_001_1.course.name} ({s_001_1.hours} hrs)"
    text = s_001_1.title
    block_data = []
    for b in s_001_1.blocks():
        block_data.append( (b.time_slot.day.name, str(b.time_slot.time_start), str(b.time_slot.duration)))
    db = EditSectionDialogTk(frame,
                             course_description = title,
                             section_description = text,
                             assigned_teachers =[t1, t2, t3],
                             non_assigned_teachers = [t4],
                             assigned_labs = [l2],
                             non_assigned_labs = [l1, l3, l4],
                             assigned_streams = [],
                             non_assigned_streams = [st1,st2],
                             current_blocks= block_data,
                             apply_changes=apply_changes,
                             course_hours = s_001_1.course.hours_per_week)

def go_add():
    pass
    title = f"{s_001_1.course.name} ({s_001_1.hours} hrs)"
    db = AddSectionDialogTk(frame,
                             course_description = title,
                             apply_changes=apply_changes2,
                             course_hours = s_001_1.course.hours_per_week),

Button(frame, text="Edit Section", command=go_edit).pack()
Button(frame, text="Add Section", command=go_add).pack()
mw.mainloop()