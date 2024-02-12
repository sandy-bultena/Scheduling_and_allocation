from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class Semester(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    semester_year: int
    semester_season: str
