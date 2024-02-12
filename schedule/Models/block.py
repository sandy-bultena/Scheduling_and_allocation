from typing import TYPE_CHECKING, Optional, List
from sqlmodel import Field, SQLModel, Relationship
from .timeslot import Timeslot

if TYPE_CHECKING:
    from .section import Section
    from .lab import Lab


class BlockLabLink(SQLModel, table=True):
    block_id: Optional[int] = Field(
        default=None, foreign_key="block.id", primary_key=True
    )
    lab_id: Optional[int] = Field(
        default=None, foreign_key="lab.id", primary_key=True
    )


class Block(SQLModel, Timeslot, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    section_id: Optional[int] = Field(foreign_key="section.id")

    section: Optional['Section'] = Relationship(back_populates="blocks")
    labs: List['Lab'] = Relationship(back_populates="blocks", link_model=BlockLabLink)
