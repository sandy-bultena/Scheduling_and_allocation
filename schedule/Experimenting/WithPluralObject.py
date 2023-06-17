from typing import *
from __future__ import annotations


class Foos(list):

    @staticmethod
    def bar(x, y, z):
        pass
        # something special that works on __instances




class Foo:

    def __init__(self, id, a, b):
        self.id = id
        self.a = a
        self.b = b

    # A whole bunch of non-static functions
