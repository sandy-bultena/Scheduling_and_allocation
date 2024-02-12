from typing import TYPE_CHECKING, Optional, List
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .section import Section


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: str
    name: str
    needs_alloc: bool = False

    sections: List['Section'] = Relationship(back_populates="course")
