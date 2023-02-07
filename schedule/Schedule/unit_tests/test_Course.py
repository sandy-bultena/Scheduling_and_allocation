import pytest
from ..Course import Course
from ..Section import Section


def test_id():
    """Verifies that Course's ID property increments automatically."""
    Course._max_id = 0
    courses = []
    for i in range(5):
        courses.append(Course(i))
    assert courses[-1].id == courses[-1]._max_id


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


def test_needs_allocation_getter():
    """Verifies that needs_allocation getter works as intended, returning a default value of True."""
    course = Course(1)
    assert course.needs_allocation is True


def test_needs_allocation_setter():
    """Verifies that needs_allocation setter works as intended."""
    course = Course(1)
    course.needs_allocation = False
    assert course.needs_allocation is False


def test_semester_getter():
    """Verifies that the semester getter works as intended."""
    semester = "fall"
    course = Course(1, "Intro to Programming", semester)
    assert course.semester == semester


def test_semester_setter_good():
    """Verifies that the semester setter accepts an appropriate value, in lowercase."""
    course = Course(1)
    semester = "FaLl"
    course.semester = semester
    assert semester.lower() == course.semester


def test_semester_setter_bad():
    """Verifies that the semester setter raises a warning without crashing the program when it receives an invalid
    input, and sets the value of semester to an empty string. """
    course = Course(1)
    bad_semester = "foo"
    with pytest.warns(Warning) as w:
        course.semester = bad_semester
    assert "invalid semester for course" in str(w[0].message) and course.semester == ''


def test_number_getter():
    """Verifies that the number getter works as intended."""
    course = Course(1)
    assert course.number == 1


def test_number_setter():
    """Verifies that the number setter works as intended."""
    course = Course(1)
    course.number = 2
    assert course.number == 2


def test_add_section_good():
    """Verifies that add_section can add a valid Section to this Course, and that the Course is added to the Section
    itself. """
    course = Course(1)
    section = Section()
    course.add_section(section)
    sections = list(getattr(course, '_sections').values())
    assert len(sections) == 1 and section in sections and section.course == course


# def test_add_section_invalid_input():
#     """Verifies that add_section raises a TypeError if the user tries to add something that isn't a Section (or in
#     this case, an object). """
#     # NOTE: This test cannot possibly succeed because of the changes I made to the validation, since everything is an
#     # object in Python, even the primitives.
#     course = Course(1)
#     bad_sect = None
#     with pytest.raises(TypeError) as e:
#         course.add_section(bad_sect)
#     assert "invalid section" in str(e.value)

def test_add_section_duplicate():
    """Verifies that add_section() raises an Exception when trying to add a duplicate of an existing Section to the
    Course. """
    course = Course(1)
    section_1 = Section()
    section_2 = section_1
    course.add_section(section_1)
    with pytest.raises(Exception) as e:
        course.add_section(section_2)
    assert "section number is not unique" in str(e.value).lower()


def test_get_section_good():
    """Verifies that get_section() returns an existing section from this Course."""
    course = Course(1)
    num = "420.AO"
    sect = Section(num)
    course.add_section(sect)
    assert course.get_section(num) == sect


def test_get_section_bad():
    """Verifies that get_section() doesn't crash the program when trying to get a Section that doesn't exist."""
    course = Course(1)
    bad_num = "420"
    assert course.get_section(bad_num) is None


def test_get_section_by_id_good():
    """Verifies that get_section_by_id() works when receiving a valid Section ID as input."""
    course = Course(1)
    section = Section()
    sect_id = Section._max_id
    course.add_section(section)
    assert course.get_section_by_id(sect_id) == section


def test_get_section_by_id_bad():
    """Verifies that get_section_by_id() won't crash the program when given a bad ID as input, returning None
    instead. """
    course = Course(1)
    section = Section()
    bad_id = 999
    course.add_section(section)
    assert course.get_section_by_id(bad_id) is None


def test_get_section_by_name_good():
    """Verifies that get_section_by_name() returns a list with the correct section when given a valid name as input."""
    course = Course(1)
    name = "test"
    section = Section("", 1.5, name)
    course.add_section(section)
    sections = course.get_section_by_name(name)
    assert len(sections) == 1 and sections[0] == section


def test_get_section_by_name_bad():
    """Verifies that get_section_by_name() returns an empty list when given an invalid section name."""
    course = Course(1)
    section = Section("", 1.5, "test")
    bad_name = "foo"
    course.add_section(section)
    sections = course.get_section_by_name(bad_name)
    assert len(sections) == 0


def test_remove_section_good():
    """Verifies that remove_section() works as intended when asked to remove a legitimate Section."""
    course = Course(1)
    section = Section()
    course.add_section(section)
    course.remove_section(section)
    assert len(course.sections()) == 0


def test_remove_section_no_crash():
    """Verifies that remove_section() will not crash the program if asked to remove a Section that doesn't exist."""
    course = Course(1)
    section_1 = Section("420")
    course.add_section(section_1)
    bad_section = Section("421")
    course.remove_section(bad_section)
    assert len(course.sections()) == 1 and section_1 in course.sections()


def test_delete():
    """Verifies that delete() will remove all Sections from the Course."""
    course = Course(1)
    section_1 = Section("420")
    section_2 = Section("555")
    course.add_section(section_1)
    course.add_section(section_2)
    course.delete()
    assert len(course.sections()) == 0


def test_sections():
    """Verifies that sections() returns a list of all the Sections assigned to this Course."""
    course = Course(1)
    section_1 = Section("420")
    section_2 = Section("555")
    course.add_section(section_1)
    course.add_section(section_2)
    sections = course.sections()
    assert len(sections) == 2 and section_1 in sections and section_2 in sections


def test_number_of_sections():
    """Verifies that number_of_sections() correctly returns the number of Sections assigned to this Course."""
    course = Course(1)
    section_1 = Section("420")
    section_2 = Section("555")
    course.add_section(section_1)
    course.add_section(section_2)
    assert course.number_of_sections() == len(course.sections())


def test_sections_for_teacher():
    assert False


def test_max_section_number():
    assert False


def test_blocks():
    assert False


def test_section():
    assert False


def test_print_description():
    assert False


def test_print_description2():
    assert False


def test_teachers():
    assert False


def test_has_teacher():
    assert False


def test_streams():
    assert False


def test_has_stream():
    assert False


def test_assign_teacher():
    assert False


def test_assign_lab():
    assert False


def test_assign_stream():
    assert False


def test_remove_teacher():
    assert False


def test_remove_all_teachers():
    assert False


def test_remove_stream():
    assert False


def test_remove_all_streams():
    assert False


def test_get_new_number():
    assert False
