class InvalidSectionNumberForCourseError(Exception):
    """Section Number already exists for specified course"""


class InvalidHoursForSectionError(Exception):
    """Section hours must be greater than zero"""


class InvalidTeacherNameError(Exception):
    """Teacher name cannot be just spaces or an empty string"""
