import uuid
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, JSON

class ContentBase(SQLModel):
    title: str = Field(index=True)
    description: Optional[str] = None
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    cover_image_url: Optional[str] = None

class Content(ContentBase, table=True):
    __tablename__ = "contents"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to Chapters
    chapters: List["Chapter"] = Relationship(back_populates="novel")

class ChapterBase(SQLModel):
    chapter_number: int
    title: Optional[str] = None
    content: str
    audio_url: Optional[str] = None
    illustration_urls: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    word_count: Optional[int] = None

class Chapter(ChapterBase, table=True):
    __tablename__ = "chapters"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content_id: uuid.UUID = Field(foreign_key="contents.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship back to Content
    novel: Content = Relationship(back_populates="chapters")

# Public schemas for API responses
class ContentPublic(ContentBase):
    id: uuid.UUID
    created_at: datetime

class ChapterPublic(ChapterBase):
    id: uuid.UUID
    content_id: uuid.UUID
    created_at: datetime
