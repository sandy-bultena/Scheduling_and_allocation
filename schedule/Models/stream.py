from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .section import Section


class StreamSectionLink(SQLModel, table=True):
    stream_id: Optional[int] = Field(
        default=None, foreign_key="stream.id", primary_key=True
    )
    section_id: Optional[int] = Field(
        default=None, foreign_key="section.id", primary_key=True
    )


class Stream(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: str
    description: str

    sections: List['Section'] = Relationship(back_populates="streams", link_model=StreamSectionLink)
