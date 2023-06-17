from typing import *
from __future__ import annotations


class Foo:
    __instances: Dict[object, int] = dict()

    def __init__(self, id, a, b):
        self.id = id
        self.a = a
        self.b = b
        Foo.__instances[self.id] = self

    @staticmethod
    def append(other: Foo):
        Foo.__instances[other.id] = other

    @staticmethod
    def get(id:int) -> Foo | None:
        if id in Foo.__instances:
            return Foo.__instances[id]
        else:
            return None

    @staticmethod
    def bar(x,y,z):
        pass
        # something special that works on __instances

    # A whole bunch of non-static functions


Foo(1, 2, 3)
this_foo = Foo.get(1)
