from typing import TYPE_CHECKING, Optional, List
from sqlmodel import Field, SQLModel, Relationship
from .section import SectionTeacherLink

if TYPE_CHECKING:
    from .section import Section


class Teacher(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nickname: Optional[str] = None
    given_name: str = Field(alias='first_name')
    family_name: str = Field(alias='last_name')
    department: str
    release: float = Field(ge=0.0)

    sections: List['Section'] = Relationship(back_populates="teachers", link_model=SectionTeacherLink)
