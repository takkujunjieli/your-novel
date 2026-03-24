"""Generation service — LLM client, streaming, and orchestration.

Uses the OpenAI SDK as a universal client for OpenAI, Ollama, vLLM,
and any OpenAI-compatible server. Provider is selected via config only.
"""

import logging
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Optional

from openai import AsyncOpenAI, APIConnectionError, APIError, APITimeoutError
from sqlmodel import Session, select

from core.config import settings
from models.content import (
    Chapter,
    Content,
    GenerationJob,
)
from services.prompts import build_scenario_prompt, build_system_prompt

logger = logging.getLogger(__name__)

# Single client instance — works for OpenAI, Ollama, vLLM, any compatible server
_client = AsyncOpenAI(
    api_key=settings.LLM_API_KEY or "not-set",
    base_url=settings.LLM_BASE_URL,
    timeout=float(settings.LLM_TIMEOUT),
)


# ---------------------------------------------------------------------------
# Core generation functions
# ---------------------------------------------------------------------------

async def generate_chapter_stream(
    system_prompt: str,
    scenario_prompt: str,
) -> AsyncGenerator[str, None]:
    """Stream chapter text chunk-by-chunk. Works with any OpenAI-compatible API."""
    response = await _client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": scenario_prompt},
        ],
        max_tokens=settings.LLM_MAX_TOKENS,
        temperature=settings.LLM_TEMPERATURE,
        stream=True,
    )
    async for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def generate_chapter_full(
    system_prompt: str,
    scenario_prompt: str,
) -> str:
    """Non-streaming generation. Returns complete text."""
    response = await _client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": scenario_prompt},
        ],
        max_tokens=settings.LLM_MAX_TOKENS,
        temperature=settings.LLM_TEMPERATURE,
        stream=False,
    )
    return response.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# Orchestration — ties prompts, generation, job tracking, and DB together
# ---------------------------------------------------------------------------

async def create_story(
    session: Session,
    user_id: uuid.UUID,
    genre: str,
    tags: list[str],
    tone: str,
    language: str = "zh",
    word_count: int = 1500,
) -> GenerationJob:
    """Full workflow: create Content + GenerationJob, generate first chapter."""
    # 1. Create Content record (title populated after generation)
    content = Content(title=f"New {genre} Story", tags=tags)
    session.add(content)
    session.flush()

    # 2. Create GenerationJob
    job = GenerationJob(
        user_id=user_id,
        content_id=content.id,
        status="pending",
    )
    session.add(job)
    session.commit()
    session.refresh(job)

    # 3. Build prompts
    system_prompt = build_system_prompt(language)
    scenario_prompt = build_scenario_prompt(
        genre=genre,
        tags=tags,
        tone=tone,
        language=language,
        word_count=word_count,
    )

    # 4. Generate
    job.status = "generating"
    session.add(job)
    session.commit()

    try:
        text = await generate_chapter_full(system_prompt, scenario_prompt)

        # 5. Create Chapter
        chapter = Chapter(
            content_id=content.id,
            chapter_number=1,
            title="Chapter 1",
            content=text,
            word_count=len(text),
        )
        session.add(chapter)

        # 6. Mark job completed
        job.status = "completed"
        job.chapter_id = chapter.id
        job.model_name = settings.LLM_MODEL
        job.completed_at = datetime.utcnow()
        session.add(job)
        session.commit()
        session.refresh(job)

    except (APIError, APITimeoutError, APIConnectionError) as exc:
        logger.error("LLM generation failed: %s", exc)
        job.status = "failed"
        job.error_message = str(exc)
        session.add(job)
        session.commit()
        session.refresh(job)

    return job


async def create_next_chapter(
    session: Session,
    user_id: uuid.UUID,
    content_id: uuid.UUID,
    word_count: int = 1500,
) -> GenerationJob:
    """Generate next chapter for an existing story."""
    # 1. Load Content + existing chapters
    content = session.get(Content, content_id)
    if not content:
        raise ValueError(f"Content {content_id} not found")

    chapters = session.exec(
        select(Chapter)
        .where(Chapter.content_id == content_id)
        .order_by(Chapter.chapter_number)
    ).all()

    next_number = len(chapters) + 1

    # 2. Build previous chapter summary
    previous_summary: Optional[str] = None
    if chapters:
        last = chapters[-1]
        # Use last ~500 chars as context summary
        previous_summary = last.content[-500:] if len(last.content) > 500 else last.content

    # 3. Create GenerationJob
    job = GenerationJob(
        user_id=user_id,
        content_id=content_id,
        status="pending",
    )
    session.add(job)
    session.commit()
    session.refresh(job)

    # 4. Build prompts
    genre = (content.tags[0] if content.tags else "fiction")
    system_prompt = build_system_prompt("zh")
    scenario_prompt = build_scenario_prompt(
        genre=genre,
        tags=content.tags or [],
        tone="romantic",
        language="zh",
        word_count=word_count,
        previous_chapter_summary=previous_summary,
    )

    # 5. Generate
    job.status = "generating"
    session.add(job)
    session.commit()

    try:
        text = await generate_chapter_full(system_prompt, scenario_prompt)

        chapter = Chapter(
            content_id=content_id,
            chapter_number=next_number,
            title=f"Chapter {next_number}",
            content=text,
            word_count=len(text),
        )
        session.add(chapter)

        job.status = "completed"
        job.chapter_id = chapter.id
        job.model_name = settings.LLM_MODEL
        job.completed_at = datetime.utcnow()
        session.add(job)
        session.commit()
        session.refresh(job)

    except (APIError, APITimeoutError, APIConnectionError) as exc:
        logger.error("LLM generation failed for content %s: %s", content_id, exc)
        job.status = "failed"
        job.error_message = str(exc)
        session.add(job)
        session.commit()
        session.refresh(job)

    return job
