import pytest
from ..Course import Course


def test_id():
    """Verifies that Course's ID property increments automatically."""
    Course._max_id = 0
    courses = []
    for i in range(5):
        courses.append(Course(i))
    assert courses[-1].id == courses[-1]._max_id


def test_name():
    assert False


def test_name():
    assert False


def test_needs_allocation():
    assert False


def test_needs_allocation():
    assert False


def test_semester():
    assert False


def test_semester():
    assert False


def test_number():
    assert False


def test_number():
    assert False


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
