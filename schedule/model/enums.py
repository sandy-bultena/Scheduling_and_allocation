"""Enums for global use"""
from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING

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
        # want to allow user to enter a value,  but also want to
        # allow it to be an enum, for interface reasons (forces the user to pass
        # the correct resource_type)
        if isinstance(user_input, cls):
            return user_input
        elif user_input in cls.names():
            return cls[user_input]
        elif user_input not in cls.values():
            raise ValueError(f"Error: input <{user_input}> is invalid")
        return user_input


class WeekDay(Enum):
    Sunday = 0
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6

    def __lt__(self, other):
        return self.value < other.value

    @staticmethod
    def get_from_string(value) -> WeekDay:
        value = value[0:3].lower()
        return {"mon": WeekDay.Monday,
                "tue": WeekDay.Tuesday,
                "wed": WeekDay.Wednesday,
                "thu": WeekDay.Thursday,
                "fri": WeekDay.Friday,
                "sat": WeekDay.Saturday,
                "sun": WeekDay.Sunday}.get(value, None)


class SemesterType(ExtendedEnum):
    fall = 1
    winter = 2
    summer = 3
    any = 4


# NOTE: if adding new conflict types, then make sure that the value refers to a single bit!


class ResourceType(ExtendedEnum):
    lab = "Lab"
    teacher = "Teacher"
    stream = "Stream"
    none = "None"
