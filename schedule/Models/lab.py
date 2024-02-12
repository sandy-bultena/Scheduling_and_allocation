from typing import TYPE_CHECKING, Optional, List
from sqlmodel import Field, SQLModel, Relationship
from .block import BlockLabLink

if TYPE_CHECKING:
    from .timeslot import UnavailableTime
    from .block import Block


class Lab(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: str
    description: str
    unavailable_times: List['UnavailableTime'] = Relationship(back_populates="lab")
    blocks: List['Block'] = Relationship(back_populates="labs", link_model=BlockLabLink)
