from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .section import Section


class Semester(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
    semester_year: int
    semester_season: str

    sections: List['Section'] = Relationship(back_populates='semester')
