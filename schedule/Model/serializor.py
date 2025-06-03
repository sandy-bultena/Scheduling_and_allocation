from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

import csv

from .time_slot import TimeSlot
from .enums import ResourceType

# stuff that we need just for type checking, not for actual functionality
if TYPE_CHECKING:
    from .block import Block
    from .stream import Stream
    from .section import Section
    from .teacher import Teacher
    from .lab import Lab
    from .course import Course
    from .schedule import Schedule


#
# TODO: give lab_unavailable_time and id
# TODO: not saving or reading synced blocks

class CSVSerializor:

    # ============================================================================
    # write csv file
    # ============================================================================
    @staticmethod
    def write(schedule: Schedule, file: str):
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
            w.writerow([None, 'id', 'day', 'time_start', 'duration', 'movable', 'BLOCK'])
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
                        for teacher in sorted(block.get_teachers, key=lambda t: t.id):
                            w.writerow(["add_block_teacher", teacher.id])
                        for lab in sorted(block.labs, key=lambda ll: ll.id):
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
    @staticmethod
    def parse(schedule: Schedule, file: str):
        """Parse the details of a schedule from a file, throws an exception if the file cannot be read from"""

        with open(file, 'r', newline='') as f:
            reader = csv.reader(f, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            current_obj: Any = None
            course_obj: Optional[Course] = None
            section_obj: Optional[Section] = None
            block_obj: Optional[Block] = None

            for row in reader:
                print (f"{row}")

                # read all the 'collectables' first
                if not row or row[0] == "":
                    continue

                if row[0] == "lab":
                    (lab_id, num, descr) = row[1:4]
                    current_obj = schedule.add_lab(number=num, description=descr, lab_id=int(lab_id))
                elif current_obj.resource_type == ResourceType.lab and row[0] == "unavailable":
                    (day, start, duration, movable) = row[1:5]
                    current_obj.add_unavailable_slot(TimeSlot(
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
                    course_obj: Course = schedule.add_course(number=number, name=name, semester=int(semester),
                                                             needs_allocation=bool(int(allocation)))
                elif course_obj is not None and row[0] == 'section':
                    (number, name, hours, students) = row[2:6]
                    section_obj: Section = course_obj.add_section(number=number, name=name, hours=float(hours))
                    section_obj.num_students = int(students)

                elif section_obj is not None and row[0] == "add_stream":
                    s: Optional[Stream] = schedule.get_stream_by_id(int(row[1]))
                    if s is not None:
                        section_obj.add_stream(s)

                elif section_obj is not None and row[0] == "add_section_teacher":
                    t: Optional[Teacher] = schedule.get_teacher_by_id(int(row[1]))
                    if t is not None:
                        section_obj.add_teacher(t)
                        if len(row) > 2 and row[2] != '':
                            section_obj.set_teacher_allocation(t, float(row[2]))

                elif section_obj is not None and row[0] == "add_block":
                    (day, start, duration, movable) = row[2:6]
                    block_obj: Block = section_obj.add_block(
                        TimeSlot(day=day, start=start, duration=float(duration), movable=bool(int(movable))))

                elif block_obj is not None and row[0] == 'add_block_teacher':
                    t: Optional[Teacher] = schedule.get_teacher_by_id(int(row[1]))
                    if t is not None:
                        block_obj.add_teacher(t)

                elif block_obj is not None and row[0] == 'add_lab':
                    l: Lab = schedule.get_lab_by_id(int(row[1]))
                    if l is not None:
                        block_obj.add_lab(l)

        schedule.calculate_conflicts()
