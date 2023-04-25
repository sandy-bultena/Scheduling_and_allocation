"""Enums for global use"""
from __future__ import annotations
from enum import Enum
import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__)))
import PerlLib.Colour as Colour

''' Not all the classes are enums, but this file contains data that is needed throughout the
program'''


class ExtendedEnum(Enum):
    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def names(cls):
        return list(map(lambda c: c.name, cls))

    @classmethod
    def validate(cls, user_input):
        # want to allow user to enter a value, for database reasons, but also want to
        # allow it to be an enum, for interface reasons (forces the user to pass
        # the correct type)
        if isinstance(user_input, cls):
            return user_input.value
        elif user_input in cls.names():
            return cls[user_input]
        elif user_input not in cls.values():
            raise ValueError(f"Error: input <{user_input}> is invalid")
        return user_input


class WeekDay(ExtendedEnum):
    Monday = "mon"
    Tuesday = "tue"
    Wednesday = "wed"
    Thursday = "thu"
    Friday = "fri"


class WeekDayNumber(ExtendedEnum):
    mon = 1
    tue = 2
    wed = 3
    thu = 4
    fri = 5
    sat = 6
    sun = 7

    @classmethod
    def days_by_number(cls):
        return {
            1: "mon",
            2: "tue",
            3: "wed",
            4: "thu",
            5: "fri",
            6: "sat",
            7: "sun"
        }


class SemesterType(ExtendedEnum):
    fall = 1
    winter = 2
    summer = 3
    any = 4


# NOTE: if adding new conflict types, then make sure that the value refers to a single bit!
class ConflictType(ExtendedEnum):
    TIME = 1
    LUNCH = 2
    MINIMUM_DAYS = 4
    AVAILABILITY = 8
    TIME_TEACHER = 16
    TIME_LAB = 32
    TIME_STREAM = 64

    @classmethod
    def colours(cls):
        return {
            cls.TIME: Colour.lighten('red2', 30),
            cls.LUNCH: "tan4",
            cls.MINIMUM_DAYS: "lightgoldenrod1",
            cls.AVAILABILITY: "mediumvioletred",
            cls.TIME_TEACHER: "red2",
            cls.TIME_LAB: "red2",
            cls.TIME_STREAM: "red2",
        }

    @classmethod
    def descriptions(cls):
        return {
            cls.TIME: "indirect time overlap",
            cls.LUNCH: "no lunch time",
            cls.MINIMUM_DAYS: "too few days",
            cls.TIME_TEACHER: "time overlap",
            cls.TIME_LAB: "time overlap",
            cls.TIME_STREAM: "time overlap",
            cls.AVAILABILITY: "not available"
        }


class ViewType(ExtendedEnum):
    from . import Teacher
    from . import Lab
    from . import Stream
    lab = Lab
    teacher = Teacher
    stream = Stream
    none = None
