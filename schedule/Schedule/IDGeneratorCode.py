from __future__ import annotations
from typing import *


def _id_generator():
    """Creates a new id, but can specify existing id's"""
    the_id = 0
    while True:
        new_id: int = yield the_id
        if new_id is not None and new_id > the_id:
            the_id = new_id
        elif new_id is None:
            the_id = the_id + 1


def get_id_generator() -> Generator[int, int | None, None]:
    """set up an id generator for your object"""
    x: Generator[int, int | None, None] = _id_generator()
    next(x)
    return x


def set_id(generator: Generator[int, int | None, None], obj_id: int | None):
    """sets the next id if not set, else return valid id"""
    if obj_id:
        generator.send(obj_id)
        return obj_id
    else:
        return next(generator)
