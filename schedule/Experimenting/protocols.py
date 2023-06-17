from __future__ import annotations
from typing import *


class ParentContainer(Protocol):
    id: int

    @property
    def title(self) -> str: ...


class Block:
    def __init__(self, section: ParentContainer, day: str) -> None:
        self.section = section
        self.day = day

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: Section
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Section:

    # ========================================================
    # CONSTRUCTOR
    # ========================================================
    def __init__(self):
        self.id=3
        pass
    # --------------------------------------------------------
    # title
    # --------------------------------------------------------
    @property
    def title(self) -> str:
        """ Gets name if defined, otherwise 'Section num' """
        return "wtf"

    # --------------------------------------------------------
    # add_block
    # --------------------------------------------------------
    def add_block(self, day:  str) -> Section:
        block = Block(self, day)
        return self


