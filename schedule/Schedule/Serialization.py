from __future__ import annotations

from typing import Any, Protocol

from .Block import Block
from .Courses import Course
from .LabUnavailableTime import LabUnavailableTime
from .Labs import Lab
import csv

from .Sections import Section
from .Teachers import Teacher
from .TimeSlot import TimeSlot
from .Streams import Stream


class MainObject(Protocol):
    @property
    def labs(self): yield ...

    @property
    def streams(self): yield ...

    @property
    def courses(self): yield ...

    @property
    def teachers(self): yield ...

    def add_lab(self, number, description, lab_id) -> Lab: ...

    def add_stream(self, number, description, stream_id) -> Stream: ...

    def add_teacher(self, firstname, lastname, department, teacher_id) -> Teacher: ...

    def add_course(self, number, name, semester, needs_allocation) -> Course: ...

    def get_stream_by_id(self, stream_id: int) -> Stream | None: ...

    def get_lab_by_id(self, lab_id: int) -> Lab | None: ...

    def get_teacher_by_id(self, teacher_id: int) -> Teacher | None: ...

    def calculate_conflicts(self): ...


# TODO: give lab_unavailable_time and id
# TODO: not saving or reading synced blocks

# ============================================================================
# write csv file
# ============================================================================
def write(schedule: MainObject, file: str):
    """Write all the details of the schedule to a file, throws an exception if the file cannot be written to"""

    with open(file, 'w', newline='') as f:
        w = csv.writer(f, delimiter=',',
                       quotechar='|', quoting=csv.QUOTE_MINIMAL)

        # --------------------------------------------------------------------
        # write all the 'collectables' first
        # --------------------------------------------------------------------
        w.writerow([None, 'id', 'lab', 'number', 'description'])
        for lab in sorted(schedule.labs):
            w.writerow(["lab", lab.id, lab.number, lab.description])
            for unavail in lab.unavailable_slots:
                w.writerow(["unavailable", "", unavail.day, unavail.start, unavail.duration, int(unavail.movable)])
        w.writerow([])

        w.writerow([None, 'id', 'number', 'description'])
        for stream in sorted(schedule.streams):
            w.writerow(["stream", stream.id, stream.number, stream.description])
        w.writerow([])

        w.writerow([None, 'id', 'first name', 'last name', 'department', 'release'])
        for teacher in sorted(schedule.teachers):
            w.writerow(
                ["teacher", teacher.id, teacher.firstname, teacher.lastname, teacher.department, teacher.release])
        w.writerow([])

        # --------------------------------------------------------------------
        # courses/sections/blocks
        # --------------------------------------------------------------------
        w.writerow([])
        w.writerow([None, None, 'DESCRIPTION', 'OF', 'FIELDS'])
        w.writerow([None, 'id', 'number', 'name', 'semester', 'needs allocation', 'COURSE'])
        w.writerow([None, 'id', 'number', 'name', 'hours', 'students', 'SECTION'])
        w.writerow([None, 'id', 'day', 'start', 'duration', 'movable', 'BLOCK'])
        w.writerow([])
        for course in sorted(schedule.courses):
            w.writerow(["course", None, course.number, course.name, course.semester, int(course.needs_allocation)])

            for section in course.sections:
                w.writerow([])
                w.writerow(["section", None, section.number, section.name, section.hours, section.num_students])

                for s in section.streams:
                    w.writerow(["add_stream", s.id])

                for block in section.blocks:
                    w.writerow(["add_block", None, block.day, block.start, block.duration, int(block.movable)])
                    for teacher in sorted(block.teachers, key=lambda t: t.id):
                        w.writerow(["add_block_teacher", teacher.id])
                    for lab in sorted(block.labs, key=lambda l: l.id):
                        w.writerow(["add_lab", lab.id])

                if section.section_defined_teachers:
                    w.writerow([])
                    w.writerow([None, None, None, 'adds teacher to all defined blocks'])
                    w.writerow([None, 'id', 'allocation'])
                    for teacher in sorted(section.section_defined_teachers, key=lambda t: t.id):
                        w.writerow(["add_section_teacher", teacher.id, section.get_teacher_allocation(teacher)])

            w.writerow([])


# ============================================================================
# parse the csv file
# ============================================================================
def parse(schedule: MainObject, file: str):
    """Parse the details of a schedule from a file, throws an exception if the file cannot be read from"""

    with open(file, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        current_obj: Any = None
        section_obj: Section | None = None
        block_obj: Block | None = None

        for row in reader:

            # read all the 'collectables' first
            if not row or row[0] == "":
                continue

            if row[0] == "lab":
                (lab_id, num, descr) = row[1:4]
                current_obj = schedule.add_lab(number=num, description=descr, lab_id=int(lab_id))
            elif isinstance(current_obj, Lab) and row[0] == "unavailable":
                (day, start, duration, movable) = row[1:5]
                current_obj.add_unavailable_slot(LabUnavailableTime(
                    day=day, start=start, duration=float(duration), movable=bool(int(movable))))

            elif row[0] == 'stream':
                (stream_id, number, descr) = row[1:4]
                current_obj = schedule.add_stream(number=number, description=descr, stream_id=int(stream_id))

            elif row[0] == 'teacher':
                (teacher_id, fname, lname, dept, release) = row[1:6]
                current_obj: Teacher = schedule.add_teacher(firstname=fname, lastname=lname, department=dept,
                                                            teacher_id=int(teacher_id))
                current_obj.release = float(release)

            # courses/sections/blocks
            elif row[0] == 'course':
                (number, name, semester, allocation) = row[2:6]
                current_obj: Course = schedule.add_course(number=number, name=name, semester=int(semester),
                                                          needs_allocation=bool(int(allocation)))

            elif isinstance(current_obj, Course) and row[0] == 'section':
                (number, name, hours, students) = row[2:6]
                section_obj: Section = current_obj.add_section(number=number, name=name, hours=float(hours))
                section_obj.num_students = int(students)

            elif section_obj is not None and row[0] == "add_stream":
                section_obj.add_stream(schedule.get_stream_by_id(int(row[1])))

            elif section_obj is not None and row[0] == "add_section_teacher":
                section_obj.add_teacher(schedule.get_teacher_by_id(int(row[1])))
                if len(row) > 2 and row[2] != '':
                    section_obj.set_teacher_allocation(schedule.get_teacher_by_id(int(row[1])), float(row[2]))

            elif section_obj is not None and row[0] == "add_block":
                (day, start, duration, movable) = row[2:6]
                block_obj: Block = section_obj.add_block(
                    TimeSlot(day=day, start=start, duration=float(duration), movable=bool(int(movable))))

            elif block_obj is not None and row[0] == 'add_block_teacher':
                block_obj.add_teacher(schedule.get_teacher_by_id(int(row[1])))

            elif block_obj is not None and row[0] == 'add_lab':
                block_obj.add_lab(schedule.get_lab_by_id(int(row[1])))

    schedule.calculate_conflicts()
