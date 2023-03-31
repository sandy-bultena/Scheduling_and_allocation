import pytest
import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__)))

from ..Course import Course
from ..Section import Section
from ..Teacher import Teacher
from ..Block import Block
from ..Lab import Lab
from ..Stream import Stream

from ..database.PonyDatabaseConnection import define_database, Course as dbCourse, \
    Section as dbSection, Schedule as dbSchedule, Scenario as dbScenario
from pony.orm import *
from .db_constants import *
from ..ScheduleEnums import SemesterType

db: Database


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    global db
    db = define_database(host=HOST, passwd=PASSWD, db=DB_NAME, provider=PROVIDER, user=USERNAME)
    yield
    db.drop_all_tables(with_all_data=True)
    db.disconnect()
    db.provider = db.schema = None


@pytest.fixture(autouse=True)
def before_and_after():
    db.create_tables()
    Course.reset()
    yield
    db.drop_all_tables(with_all_data=True)


def test_id():
    """Verifies that Course's ID property increments automatically."""
    courses = []
    for i in range(5):
        courses.append(Course(i))
    assert courses[-1].id == len(courses)


def test_full_constructor():
    """Verifies that constructor parameters are applied correctly"""
    num = "102-NYA-043"
    name = "My Course"
    sem = SemesterType.summer
    allo = False
    c = Course(num, name, sem, allo)
    assert c.name == name
    assert c.number == num
    assert c.semester == SemesterType.validate(sem)
    assert c.needs_allocation == allo


def test_name_getter():
    """Verifies that name getter works as intended."""
    course = Course(1, "Intro to Programming")
    assert course.name == "Intro to Programming"


def test_name_setter():
    """Verifies that name setter works as intended."""
    course = Course(1)
    name = "Intro to Programming"
    course.name = name
    assert name == course.name


def test_number_getter():
    """Verifies that the number getter works as intended."""
    course = Course(1)
    assert course.number == '1'


def test_number_setter():
    """Verifies that the number setter works as intended."""
    course = Course(1)
    course.number = 2
    assert course.number == 2


def test_add_section_good():
    """Verifies that add_section can add a valid Section to this Course, and that the Course is
    added to the Section itself. """
    course_1 = Course(1)
    course_2 = Course(2)
    section = Section(id=1, course=course_1)
    course_2.add_section(section)
    commit()
    sections = list(getattr(course_2, '_sections').values())
    assert len(sections) == 1 and section in sections and section.course == course_2


def test_add_section_invalid_input():
    """Verifies that add_section raises a TypeError if the user tries to add something that
    isn't a Section (or in this case, an object). """
    # NOTE: This test cannot possibly succeed because of the changes I made to the
    # validation, since everything is an object in Python, even the primitives.
    course = Course(1)
    bad_sect = None
    with pytest.raises(TypeError) as e:
        course.add_section(bad_sect)
    assert "invalid section" in str(e.value)


def test_add_section_duplicate():
    """Verifies that add_section() raises an Exception when trying to add a duplicate of an
    existing Section to the Course. """
    course_1 = Course(1)
    section_1 = Section(id=1, course=course_1)
    course_2 = Course(2)
    section_2 = Section(id=2, course=course_2)
    with pytest.raises(Exception) as e:
        course_2.add_section(section_1)
    assert "section number is not unique" in str(e.value).lower()


@db_session
def test_add_section_updates_database():
    """Verifies that add_section() links this Course's database record to that of the passed
    Section. """
    course = Course(1)
    d_scenario = dbScenario(name="Test")
    flush()
    d_schedule = dbSchedule(official=False, scenario_id=d_scenario.id)
    flush()
    sect = Section(course=course, schedule_id=d_schedule.id)
    commit()
    course.add_section(sect)
    commit()
    d_course = dbCourse[course.id]
    d_sect = dbSection[sect.id]
    assert d_sect in d_course.sections and d_sect.course_id == d_course


def test_get_section_good():
    """Verifies that get_section() returns an existing section from this Course."""
    course = Course(1)
    num = "420.AO"
    sect = Section(num, id=1, course=course)
    course.add_section(sect)
    assert course.get_section(num) == sect


def test_get_section_bad():
    """Verifies that get_section() doesn't crash the program when trying to get a Section
    that doesn't exist. """
    course = Course(1)
    bad_num = "420"
    assert course.get_section(bad_num) is None


def test_get_section_by_id_good():
    """Verifies that get_section_by_id() works when receiving a valid Section ID as input."""
    course = Course(1)
    section = Section(id=1, course=course)
    sect_id = 1
    course.add_section(section)
    assert course.get_section_by_id(sect_id) == section


def test_get_section_by_id_bad():
    """Verifies that get_section_by_id() won't crash the program when given a bad ID as input,
    returning None instead. """
    course = Course(1)
    section = Section(id=1, course=course)
    bad_id = 999
    course.add_section(section)
    assert course.get_section_by_id(bad_id) is None


def test_get_section_by_name_good():
    """Verifies that get_section_by_name() returns a list with the correct section when given
    a valid name as input. """
    course = Course(1)
    name = "test"
    section = Section("", 1.5, name, id=1, course=course)
    course.add_section(section)
    sections = course.get_section_by_name(name)
    assert len(sections) == 1 and sections[0] == section


def test_get_section_by_name_bad():
    """Verifies that get_section_by_name() returns an empty list when given an invalid
    section name. """
    course = Course(1)
    section = Section("", 1.5, "test", id=1, course=course)
    bad_name = "foo"
    course.add_section(section)
    sections = course.get_section_by_name(bad_name)
    assert len(sections) == 0


def test_remove_section_good():
    """Verifies that remove_section() works as intended when asked to remove a legitimate
    Section. """
    course = Course(1)
    section = Section(id=1, course=course)
    course.add_section(section)
    course.remove_section(section)
    assert len(course.sections()) == 0


def test_remove_section_bad():
    """Verifies that remove_section() raises an Exception when asked to remove a non-Section
    object. """
    course = Course(1)
    section = Section(id=1, course=course)
    course.add_section(section)
    bad_section = "foo"
    with pytest.raises(TypeError) as e:
        course.remove_section(bad_section)
    assert "invalid section" in str(e.value).lower()


def test_remove_section_no_crash():
    """Verifies that remove_section() will not crash the program if asked to remove a Section
    that doesn't exist. """
    course = Course(1)
    section_1 = Section("420", id=1, course=course)
    course.add_section(section_1)
    bad_section = Section("421", id=666, course=course)
    course.remove_section(bad_section)
    assert len(course.sections()) == 1 and section_1 in course.sections()


@db_session
def test_remove_section_updates_database():
    """Verifies that remove_section breaks the connection and deletes the passed Section."""
    course = Course(1)
    d_scenario = dbScenario(name="Test")
    flush()
    d_schedule = dbSchedule(official=False, scenario_id=d_scenario.id)
    flush()
    sect = Section(course=course, schedule_id=d_schedule.id)
    commit()
    course.add_section(sect)
    commit()
    course.remove_section(sect)
    commit()
    d_sects = select(s for s in dbSection)
    d_course = dbCourse[course.id]
    assert len(d_sects) == 0 and len(d_course.sections) == 0


def test_delete():
    """Verifies that delete() will remove all Sections from the Course, and remove the Course
    from the backend list of Courses. """
    course = Course(1)
    section_1 = Section("420", id=1, course=course)
    section_2 = Section("555", id=2, course=course)
    course.add_section(section_1)
    course.add_section(section_2)
    course.delete()
    assert len(course.sections()) == 0 and course not in Course.list()


@db_session
def test_delete_updates_database():
    """Verifies that delete() removes the Course record from the database."""
    course = Course(1)
    course.delete()
    commit()
    d_courses = select(c for c in dbCourse)
    assert len(d_courses) == 0


@db_session
def test_remove_ignores_database():
    """Verifies that remove() doesn't affect the Course's corresponding database record."""
    course = Course(1)
    course.remove()
    d_courses = select(c for c in dbCourse)
    courses = list(d_courses)
    a_courses = Course.list()
    assert len(a_courses) == 0
    assert len(courses) == 1
    assert courses[0].name == course.name


def test_sections():
    """Verifies that sections() returns a list of all the Sections assigned to this Course."""
    course = Course(1)
    section_1 = Section("420", id=1, course=course)
    section_2 = Section("555", id=2, course=course)
    course.add_section(section_1)
    course.add_section(section_2)
    sections = course.sections()
    assert len(sections) == 2 and section_1 in sections and section_2 in sections


def test_number_of_sections():
    """Verifies that number_of_sections() correctly returns the number of Sections assigned
    to this Course. """
    course = Course(1)
    section_1 = Section("420", id=1, course=course)
    section_2 = Section("555", id=2, course=course)
    course.add_section(section_1)
    course.add_section(section_2)
    assert course.number_of_sections() == len(course.sections())


def test_sections_for_teacher():
    """Verifies that sections_for_teacher() returns a list of all sections featuring this
    teacher in this course. """
    course = Course(1)
    section_1 = Section("420", id=1, course=course)
    teach = Teacher("John", "Smith")
    section_1.assign_teacher(teach)
    course.add_section(section_1)
    teach_sections = course.sections_for_teacher(teach)
    assert section_1 in teach_sections


def test_sections_for_teacher_empty():
    """Verifies that sections_for_teacher() returns an empty list if no Teacher has been
    assigned to the Course. """
    course = Course(1)
    section_1 = Section("420", id=1, course=course)
    teach = Teacher("John", "Smith")
    course.add_section(section_1)
    teach_sections = course.sections_for_teacher(teach)
    assert len(teach_sections) == 0


def test_max_section_number():
    """Verifies that max_section_number() returns the highest number of all the Sections
    assigned to this Course. """
    course = Course(1)
    section_1 = Section("420", id=1, course=course)
    section_2 = Section("500", id=2, course=course)
    section_3 = Section("120", id=3, course=course)
    course.add_section(section_1)
    course.add_section(section_2)
    course.add_section(section_3)
    max_num = course.max_section_number()
    assert max_num == section_2.number


def test_max_section_number_zero():
    """Verifies that max_section_number() returns zero if no Sections are assigned to this
    Course. """
    course = Course(1)
    assert course.max_section_number() == 0


def test_blocks_good():
    """Verifies that blocks() returns a list of all Blocks that have been assigned to this
    Course. """
    course = Course(1)
    section = Section("420", id=1, course=course)
    block_1 = Block("mon", "9:30", 1.5, 1)
    block_2 = Block("wed", "9:30", 1.5, 2)
    section.add_block(block_1, block_2)
    course.add_section(section)
    blocks = course.blocks()
    assert len(blocks[0]) == 2 and block_1 in blocks[0] and block_2 in blocks[0]


def test_blocks_bad():
    """Verifies that blocks() returns an empty list when the Sections of this Course contain
    no Blocks. """
    course = Course(1)
    section = Section("420", id=1, course=course)
    course.add_section(section)
    blocks = course.blocks()
    assert len(blocks[0]) == 0


def test_section():
    """Verifies that section() returns the correct Section when receiving a valid number."""
    course = Course(1)
    course_num = "420"
    section = Section(course_num, id=1, course=course)
    course.add_section(section)
    assert course.section(course_num) == section


def test_section_bad():
    """Verifies that section() returns nothing when receiving an invalid section number."""
    course = Course(1)
    section = Section("420", id=1, course=course)
    course.add_section(section)
    bad_num = "555"
    assert course.section(bad_num) is None


def test_str_representation_full():
    """Verifies that the string representation returns a detailed string containing information
    on the Course, its Sections, its Blocks, its Teachers, and its Labs. """
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    lab = Lab("R-101", "Worst place in the world")
    teacher = Teacher("John", "Smith")
    block.assign_lab(lab)
    block.assign_teacher(teacher)
    section.add_block(block)
    course.add_section(section)
    description = str(course)
    print(description)
    assert f"{course.number} {course.name}" in description \
           and f"Section {section.number}" in description \
           and f"{block.day} {block.start}, {block.duration} hours" in description \
           and f"labs: {lab.number}: {lab.descr}" in description \
           and f"teachers: {teacher.firstname} {teacher.lastname}" in description


def test_description():
    """Verifies that description prints a brief string containing the Course's
    number and name. """
    course = Course(1, "Course 1")
    description = course.description
    print(description)
    assert f"{course.number}: {course.name}" in description


def test_teachers_good():
    """Verifies that teachers() returns a list of the Teachers assigned to this course."""
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    lab = Lab("R-101", "Worst place in the world")
    teacher_1 = Teacher("John", "Smith")
    teacher_2 = Teacher("Jane", "Doe")
    block.assign_teacher(teacher_1)
    block.assign_teacher(teacher_2)
    block.assign_lab(lab)
    section.add_block(block)
    course.add_section(section)
    teachers = course.teachers()
    assert len(teachers) == 2 and teacher_1 in teachers and teacher_2 in teachers


def test_teachers_bad():
    """Verifies that teachers() returns an empty list if no teachers have been assigned."""
    course = Course(1)
    teachers = course.teachers()
    assert len(teachers) == 0


def test_has_teacher():
    """Verifies that has_teacher() returns True if the specified Teacher has been assigned to
    this course. """
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    lab = Lab("R-101", "Worst place in the world")
    teacher = Teacher("John", "Smith")
    block.assign_lab(lab)
    block.assign_teacher(teacher)
    section.add_block(block)
    course.add_section(section)
    assert course.has_teacher(teacher) is True


def test_has_teacher_bad_input():
    """Verifies that has_teacher() returns false when looking for something that isn't a
    Teacher. """
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    lab = Lab("R-101", "Worst place in the world")
    teacher = Teacher("John", "Smith")
    block.assign_lab(lab)
    block.assign_teacher(teacher)
    section.add_block(block)
    course.add_section(section)
    bad_teach = "foo"
    assert course.has_teacher(bad_teach) is False


def test_streams():
    """Verifies that streams() returns a list of all Streams belonging to the Sections of
    this Course. """
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    stream = Stream()
    section.add_block(block)
    section.assign_stream(stream)
    course.add_section(section)
    streams = course.streams()
    assert len(streams) == 1 and stream in streams


def test_streams_empty():
    """Verifies that streams() returns an empty list if no Streams are assigned to this
    Course. """
    course = Course(1)
    streams = course.streams()
    assert len(streams) == 0


def test_has_stream():
    """Verifies that has_stream() returns true if the passed Stream exists within the Course."""
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    stream = Stream()
    section.add_block(block)
    section.assign_stream(stream)
    course.add_section(section)
    assert course.has_stream(stream) is True


def test_has_stream_false():
    """Verifies that has_stream() returns false if the Course doesn't contain the passed
    Stream. """
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    stream = Stream()
    section.add_block(block)
    section.assign_stream(stream)
    course.add_section(section)

    bad_stream = Stream()
    assert course.has_stream(bad_stream) is False


def test_has_stream_bad_input():
    """Verifies that has_stream() returns false if no input is specified."""
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    stream = Stream()
    section.add_block(block)
    section.assign_stream(stream)
    course.add_section(section)
    assert course.has_stream(None) is False


def test_assign_teacher_good():
    """Verifies that assign_teacher() assigns the passed Teacher to all Sections of the
    Course. """
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    section.add_block(block)
    course.add_section(section)
    teacher = Teacher("John", "Smith")
    course.assign_teacher(teacher)
    teachers = course.teachers()
    assert len(teachers) == 1 and teacher in teachers


def test_assign_teacher_bad():
    """Verifies that assign_teacher throws a TypeError when trying to assign a non-Teacher
    object. """
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    section.add_block(block)
    course.add_section(section)
    bad_teach = "foo"
    with pytest.raises(TypeError) as e:
        course.assign_teacher(bad_teach)
    assert "invalid teacher" in str(e.value).lower()


def test_assign_lab_good():
    """Verifies that assign_lab() can assign a legitimate Lab to all Sections of the Course."""
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    section.add_block(block)
    course.add_section(section)
    lab = Lab()
    course.assign_lab(lab)
    assert block.has_lab(lab)


def test_assign_lab_bad():
    """Verifies that assign_lab throws an exception when it receives a non-Lab object."""
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    section.add_block(block)
    course.add_section(section)

    bad_lab = "foo"
    with pytest.raises(TypeError) as e:
        course.assign_lab(bad_lab)
    assert "invalid lab" in str(e.value).lower()


def test_assign_stream_good():
    """Verifies that assign_stream() can successfully assign a valid Stream to all Sections
    of the Course. """
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    section.add_block(block)
    course.add_section(section)

    stream = Stream()
    course.assign_stream(stream)
    assert len(section.streams) == 1 and stream in section.streams


def test_assign_stream_bad():
    """Verifies that assign_stream() will raise an exception if it receives a non-Stream
    object. """
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    section.add_block(block)
    course.add_section(section)

    bad_stream = "foo"
    with pytest.raises(TypeError) as e:
        course.assign_stream(bad_stream)
    assert "invalid stream" in str(e.value)


def test_remove_teacher_good():
    """Verifies that remove_teacher() can successfully remove the specified Teacher from the
    Course. """
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    section.add_block(block)
    course.add_section(section)
    teacher_1 = Teacher("John", "Smith")
    teacher_2 = Teacher("Jane", "Doe")
    course.assign_teacher(teacher_1)
    course.assign_teacher(teacher_2)
    course.remove_teacher(teacher_1)
    assert len(course.teachers()) == 1 and teacher_1 not in course.teachers()


def test_remove_teacher_bad():
    """Verifies that remove_teacher() raises an exception when trying to remove a non-Teacher
    object. """
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    section.add_block(block)
    course.add_section(section)
    teacher_1 = Teacher("John", "Smith")
    course.assign_teacher(teacher_1)
    bad_teacher = "foo"
    with pytest.raises(TypeError) as e:
        course.remove_teacher(bad_teacher)
    assert "invalid teacher" in str(e.value).lower()


def test_remove_all_teachers():
    """Verifies that remove_all_teachers() works as intended."""
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    section.add_block(block)
    course.add_section(section)
    teacher_1 = Teacher("John", "Smith")
    teacher_2 = Teacher("Jane", "Doe")
    teacher_3 = Teacher("John", "Barleycorn")
    course.assign_teacher(teacher_1)
    course.assign_teacher(teacher_2)
    course.assign_teacher(teacher_3)
    course.remove_all_teachers()
    assert len(course.teachers()) == 0


def test_remove_stream_good():
    """Verifies that remove_stream() works as intended."""
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    section.add_block(block)
    course.add_section(section)
    stream_1 = Stream()
    stream_2 = Stream()
    course.assign_stream(stream_1)
    course.assign_stream(stream_2)
    course.remove_stream(stream_1)
    assert len(course.streams()) == 1 and stream_1 not in course.streams()


def test_remove_stream_bad():
    """Verifies that remove_stream() raises an exception when receiving a non-Stream object."""
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    section.add_block(block)
    course.add_section(section)
    stream_1 = Stream()
    course.assign_stream(stream_1)
    bad_stream = "foo"
    with pytest.raises(TypeError) as e:
        course.remove_stream(bad_stream)
    assert "invalid stream" in str(e.value).lower()


def test_remove_all_streams():
    """Verifies that remove_all_streams() works as intended."""
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    section.add_block(block)
    course.add_section(section)
    stream_1 = Stream()
    stream_2 = Stream()
    course.assign_stream(stream_1)
    course.assign_stream(stream_2)
    course.remove_all_streams()
    assert len(course.streams()) == 0


def test_get_new_number_good():
    """Verifies that get_new_number() works as intended."""
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    section.add_block(block)
    course.add_section(section)
    num = 420
    expected_num = 421
    assert course.get_new_number(num) == expected_num


def test_new_number_unused_number():
    """Verifies that get_new_number will return the same number it was passed if that number
    isn't in use. """
    course = Course(1, "Course 1")
    block = Block("mon", "8:30", 1.5, 1)
    section = Section("420", 1.5, "Section 1", id=1, course=course)
    section.add_block(block)
    course.add_section(section)
    num = 421
    assert course.get_new_number(num) == num


def test_get_good():
    """Verifies that the static get() method works as intended."""
    course = Course(1, "Course 1")
    assert Course.get(1) == course


def test_get_bad_id():
    """Verifies that get() returns None if there's no Course with the passed ID"""
    course = Course(1, "Course 1")
    bad_num = 666
    assert Course.get(bad_num) is None


def test_get_by_number_good():
    """Verifies that get_by_number() returns the first Course matching the passed number."""
    num = "420-6P3-AB"
    course_1 = Course(num, "Course 1")
    course_2 = Course("11111", "Course 2")
    assert Course.get_by_number(num) == course_1


def test_get_by_number_bad():
    """Verifies that get_by_number() returns None if no matching Course is found."""
    num = "420-6P3-AB"
    course_1 = Course(num, "Course 1")
    course_2 = Course("11111", "Course 2")
    bad_num = "666"
    assert Course.get_by_number(bad_num) is None


def test_get_by_number_no_input():
    """Verifies that get_by_number() returns None when receiving None or an empty string."""
    num = "420-6P3-AB"
    course_1 = Course(num, "Course 1")
    course_2 = Course("11111", "Course 2")
    bad_num = ""
    assert Course.get_by_number(bad_num) is None


def test_allocation_list():
    """Verifies that allocation_list() returns a list of the courses in need of allocation."""
    course_1 = Course("24601", "Course 1")
    course_2 = Course("11111", "Course 2")
    course_2.needs_allocation = False
    courses = Course.allocation_list()
    assert len(courses) == 1 and course_1 in courses


def test_allocation_list_sorted():
    """Verifies that the list returned by allocation_list() is sorted by Course number."""
    course_1 = Course("24601", "Course 1")
    course_2 = Course("11111", "Course 2")
    courses = Course.allocation_list()
    assert len(courses) == 2 and courses[0] == course_2 and courses[1] == course_1


@db_session
def test_save():
    """Verifies that save() works as intended."""
    course = Course("24601", "Course 1")
    flush()
    course.needs_allocation = False
    course.number = "11111"
    d_course = course.save()
    assert d_course.allocation == course.needs_allocation \
           and d_course.number == course.number \
           and d_course.name == course.name
