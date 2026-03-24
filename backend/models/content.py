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

# --- GenerationJob ---

class GenerationJobBase(SQLModel):
    status: str = Field(default="pending")  # pending, generating, completed, failed
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    error_message: Optional[str] = None

class GenerationJob(GenerationJobBase, table=True):
    __tablename__ = "generation_jobs"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    content_id: Optional[uuid.UUID] = Field(default=None, foreign_key="contents.id")
    chapter_id: Optional[uuid.UUID] = Field(default=None, foreign_key="chapters.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class GenerationJobPublic(GenerationJobBase):
    id: uuid.UUID
    content_id: Optional[uuid.UUID]
    chapter_id: Optional[uuid.UUID]
    created_at: datetime
    completed_at: Optional[datetime]

# --- Public schemas for API responses ---

class ContentPublic(ContentBase):
    id: uuid.UUID
    created_at: datetime

class ChapterPublic(ChapterBase):
    id: uuid.UUID
    content_id: uuid.UUID
    created_at: datetime
