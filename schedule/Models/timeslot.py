from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship, Column, String

if TYPE_CHECKING:
    from .lab import Lab


class Timeslot:
    day: int
    start: int
    duration: int
    movable: bool


class UnavailableTime(SQLModel, Timeslot, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lab_id: Optional[int] = Field(foreign_key="lab.id")

    lab: Optional['Lab'] = Relationship(back_populates="unavailable_times")
