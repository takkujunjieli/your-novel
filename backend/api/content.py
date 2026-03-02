from typing import List
from fastapi import APIRouter, HTTPException, Path
from sqlalchemy import select
from core.db import SessionDep
from models.content import Content, ContentPublic, Chapter, ChapterPublic

router = APIRouter(prefix="/api/v1", tags=["content"])

@router.get("/content/trending", response_model=List[ContentPublic])
def get_trending(session: SessionDep):
    # For MVP, we'll just return all content sorted by creation date
    statement = select(Content).order_by(Content.created_at.desc())
    results = session.exec(statement).all()
    return results

@router.get("/content/{content_id}", response_model=ContentPublic)
def get_content_details(content_id: str, session: SessionDep):
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.get("/chapters/{chapter_id}", response_model=ChapterPublic)
def get_chapter(chapter_id: str, session: SessionDep):
    chapter = session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter

@router.get("/content/{content_id}/chapters", response_model=List[ChapterPublic])
def get_content_chapters(content_id: str, session: SessionDep):
    # Fetch all chapters for a specific novel
    statement = select(Chapter).where(Chapter.content_id == content_id).order_by(Chapter.chapter_number)
    results = session.exec(statement).all()
    return results
