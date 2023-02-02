import pytest
from ..Course import Course


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


def test_add_section():
    assert False


def test_get_section():
    assert False


def test_get_section_by_id():
    assert False


def test_get_section_by_name():
    assert False


def test_remove_section():
    assert False


def test_delete():
    assert False


def test_sections():
    assert False


def test_number_of_sections():
    assert False


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
