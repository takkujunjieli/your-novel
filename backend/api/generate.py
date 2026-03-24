"""Generation API endpoints — story creation, chapter generation, job status, SSE streaming."""

import json
import logging
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Field, SQLModel

from core.db import SessionDep
from models.content import Content, GenerationJob, GenerationJobPublic
from services.generation import (
    create_next_chapter,
    create_story,
    generate_chapter_stream,
)
from services.prompts import build_scenario_prompt, build_system_prompt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["generation"])


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class StoryGenerateRequest(SQLModel):
    """Request body for creating a new story."""
    genre: str
    tags: list[str] = []
    tone: str = "romantic"
    language: str = "zh"
    word_count: int = Field(default=1500, ge=500, le=3000)


class ChapterGenerateRequest(SQLModel):
    """Request body for generating the next chapter."""
    word_count: int = Field(default=1500, ge=500, le=3000)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

# TODO: Replace hardcoded user_id with real auth dependency when auth is wired up
_PLACEHOLDER_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@router.post("/generate/story", response_model=GenerationJobPublic)
async def generate_story(request: StoryGenerateRequest, session: SessionDep):
    """Create a new story with its first chapter via LLM generation."""
    job = await create_story(
        session=session,
        user_id=_PLACEHOLDER_USER_ID,
        genre=request.genre,
        tags=request.tags,
        tone=request.tone,
        language=request.language,
        word_count=request.word_count,
    )
    return job


@router.post("/generate/chapter/{content_id}", response_model=GenerationJobPublic)
async def generate_chapter(content_id: uuid.UUID, request: ChapterGenerateRequest, session: SessionDep):
    """Generate the next chapter for an existing story."""
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    job = await create_next_chapter(
        session=session,
        user_id=_PLACEHOLDER_USER_ID,
        content_id=content_id,
        word_count=request.word_count,
    )
    return job


@router.get("/generate/status/{job_id}", response_model=GenerationJobPublic)
def get_job_status(job_id: uuid.UUID, session: SessionDep):
    """Poll generation job status."""
    job = session.get(GenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/generate/stream/{job_id}")
async def stream_generation(job_id: uuid.UUID, session: SessionDep):
    """SSE streaming endpoint — streams generated text chunk-by-chunk.

    Returns text/event-stream with JSON payloads:
    - Progress chunks: {"text": "..."}
    - Completion:      {"done": true, "word_count": 1234}
    - Error:           {"error": "..."}
    """
    job = session.get(GenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not job.content_id:
        raise HTTPException(status_code=400, detail="Job has no associated content")

    content = session.get(Content, job.content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Build prompts from content metadata
    genre = content.tags[0] if content.tags else "fiction"
    language = "zh"
    system_prompt = build_system_prompt(language)
    scenario_prompt = build_scenario_prompt(
        genre=genre,
        tags=content.tags or [],
        tone="romantic",
        language=language,
        word_count=1500,
    )

    async def event_stream():
        """Yield SSE events as the LLM generates text."""
        full_text = ""
        try:
            async for chunk in generate_chapter_stream(system_prompt, scenario_prompt):
                full_text += chunk
                yield f"data: {json.dumps({'text': chunk})}\n\n"

            yield f"data: {json.dumps({'done': True, 'word_count': len(full_text)})}\n\n"
        except Exception as exc:
            logger.error("SSE stream error for job %s: %s", job_id, exc)
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
