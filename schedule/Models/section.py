from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from .stream import StreamSectionLink

if TYPE_CHECKING:
    from .teacher import Teacher
    from .course import Course
    from .block import Block
    from .stream import Stream

class Section(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    number: int
    hours: float = Field(ge=0)
    number_of_students: int = Field(ge=0)
    course_id: Optional[int] = Field(default=None, foreign_key="course.id")
    teacher_id: Optional[int] = Field(default=None, foreign_key="teacher.id")

    course: Optional['Course'] = Relationship(back_populates="sections")
    teacher: Optional['Teacher'] = Relationship(back_populates="sections")
    streams: List['Stream'] = Relationship(back_populates="sections", link_model=StreamSectionLink)
    blocks: List['Block'] = Relationship(back_populates="section")
