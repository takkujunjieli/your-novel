# AI Generation Service — Engineering Plan (Local-LLM-Ready)

**Date**: 2026-03-17
**Scope**: Steps 1.1 + 1.2 from `next_steps_plan.md` — Generation Service + API Endpoints
**Key Constraint**: Architecture must allow switching from OpenAI to local LLM (Ollama/vLLM) by changing config only — no code changes.

---

## Critical Design Decision: OpenAI SDK as Universal Client

**Insight**: Ollama, vLLM, llama.cpp, LM Studio, and text-generation-webui all expose **OpenAI-compatible** `/v1/chat/completions` endpoints. The `openai` Python package works with ALL of them by changing `base_url`.

```python
# OpenAI cloud
client = AsyncOpenAI(api_key="sk-...", base_url="https://api.openai.com/v1")

# Ollama local
client = AsyncOpenAI(api_key="ollama", base_url="http://localhost:11434/v1")

# vLLM local
client = AsyncOpenAI(api_key="not-needed", base_url="http://localhost:8000/v1")
```

**This means**: No `LLMProvider` interface, no adapter pattern, no factory. Just config. The OpenAI SDK IS the abstraction layer. This is simpler, less code, and already battle-tested.

**What changes when switching to local LLM**: Only 3 env vars:
- `LLM_BASE_URL` → from `https://api.openai.com/v1` to `http://localhost:11434/v1`
- `LLM_API_KEY` → from real key to `"ollama"` or `"not-needed"`
- `LLM_MODEL` → from `gpt-4o-mini` to `qwen2.5:14b` or `llama3.1:8b`

---

## Build Steps (Ordered)

### Step 1: Config & Dependencies
**Executor**: engineer
**Priority**: P0
**Files**: `backend/core/config.py`, `backend/requirements.txt`

**What to do**:

1. Add to `Settings` in `backend/core/config.py`:
```python
# LLM Configuration — change these 3 values to switch providers
LLM_BASE_URL: str = "https://api.openai.com/v1"
LLM_API_KEY: str = ""              # from .env
LLM_MODEL: str = "gpt-4o-mini"    # or "qwen2.5:14b" for Ollama
LLM_MAX_TOKENS: int = 2000
LLM_TEMPERATURE: float = 0.8
LLM_TIMEOUT: int = 120            # seconds — local LLMs may be slower
```

2. Add `openai` to `backend/requirements.txt`

**Why this matters for local LLM**: The config is provider-agnostic. When you deploy Ollama with Qwen2.5, you set `LLM_BASE_URL=http://localhost:11434/v1`, `LLM_API_KEY=ollama`, `LLM_MODEL=qwen2.5:14b` in `.env` and everything works. No code touch.

**Do NOT**:
- Add provider-specific config like `OPENAI_API_KEY` — use generic `LLM_API_KEY`
- Add separate config blocks for different providers
- Build any kind of provider registry or factory pattern

---

### Step 2: GenerationJob Model
**Executor**: engineer
**Priority**: P0
**Files**: `backend/models/content.py`

**What to do**:

Add `GenerationJob` SQLModel to `backend/models/content.py` (same file as Content/Chapter — keeps models together):

```python
class GenerationJobBase(SQLModel):
    status: str = Field(default="pending")  # pending, generating, completed, failed
    model_name: Optional[str] = None        # "gpt-4o-mini", "qwen2.5:14b", etc.
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
```

**Why `model_name` tracking matters for local LLM**: When you A/B test OpenAI vs Qwen locally, every generated chapter records which model produced it. This lets you compare quality, measure fallback rates, and decide when to fully cut over.

**Schema per `Data_Model.md`**: Matches the `generation_jobs` table spec exactly.

---

### Step 3: Prompt Assembly Service
**Executor**: engineer
**Priority**: P0
**Files**: `backend/services/prompts.py` (new)

**What to do**:

Create `backend/services/prompts.py` — responsible ONLY for assembling prompts from parameters. No LLM calls here.

```python
def build_system_prompt(language: str = "zh") -> str:
    """Return the platform system prompt. Model-agnostic per ADR-0003."""
    ...

def build_scenario_prompt(
    genre: str,
    tags: list[str],
    tone: str,
    language: str,
    word_count: int,
    characters: list[dict] | None = None,
    plot_context: str | None = None,
    previous_chapter_summary: str | None = None,
) -> str:
    """Assemble scenario prompt from generation parameters."""
    ...
```

**Key rules** (from ADR-0003):
- Use structured markdown format (`#`, `##`, `-`) — all LLMs understand this
- Explicit instructions, not vague ("Write 1500 words" not "Write a chapter")
- Include safety rules in every prompt (different models have different training)
- No model-specific instructions (no "Think step-by-step", no "As ChatGPT...")
- Provide example passages for style (few-shot)

**Why separate from generation service**: Prompt assembly is pure logic with no I/O. Easy to unit test, easy to swap prompt templates per model if needed (e.g., slightly different framing for Qwen vs Llama). But start with ONE universal template.

**Context**: Copy the system prompt from `docs/architecture/AI_Generation_Design.md` Section 1.1 and the scenario template from ADR-0003's Scenario Prompt Template.

---

### Step 4: Generation Service (Core)
**Executor**: engineer
**Priority**: P0
**Files**: `backend/services/generation.py` (new)

**What to do**:

Create `backend/services/generation.py` — the core generation logic.

```python
from openai import AsyncOpenAI
from core.config import settings

# Single client instance — works for OpenAI, Ollama, vLLM, any OpenAI-compatible server
_client = AsyncOpenAI(
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
    timeout=settings.LLM_TIMEOUT,
)

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
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta

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
    return response.choices[0].message.content
```

**What NOT to build** (yet):
- ❌ Fallback chain (multiple models) — premature for MVP. Add when local LLM is deployed.
- ❌ Retry logic with different models — just retry same model.
- ❌ Quality scoring on output — that's Phase 2 evaluation framework.
- ❌ Provider abstraction class hierarchy — the OpenAI SDK already abstracts this.

**Error handling**: Catch `openai.APIError`, `openai.APITimeoutError`, `openai.APIConnectionError`. Log the error, update GenerationJob status to `"failed"` with error message.

**Why this is local-LLM-ready**: This code works TODAY with OpenAI. When you run `ollama serve` with Qwen2.5, change 3 env vars, and this exact code generates from local LLM. Tested pattern — Ollama's OpenAI compatibility is mature.

---

### Step 5: Generation Orchestrator
**Executor**: engineer
**Priority**: P0
**Files**: `backend/services/generation.py` (extend)

**What to do**:

Add orchestration logic that ties prompt assembly, generation, job tracking, and DB persistence together:

```python
async def create_story(
    session: Session,
    user_id: uuid.UUID,
    genre: str,
    tags: list[str],
    tone: str,
    language: str = "zh",
    word_count: int = 1500,
) -> GenerationJob:
    """Full workflow: create Content + GenerationJob, start generation."""
    # 1. Create Content record (empty, populated after generation)
    # 2. Create GenerationJob (status="pending")
    # 3. Build prompts via prompts.py
    # 4. Update job status to "generating"
    # 5. Call generate_chapter_full() or start streaming
    # 6. Create Chapter record with generated text
    # 7. Update job status to "completed", record model_name
    # 8. Return job
    ...

async def create_next_chapter(
    session: Session,
    user_id: uuid.UUID,
    content_id: uuid.UUID,
    word_count: int = 1500,
) -> GenerationJob:
    """Generate next chapter for existing story."""
    # 1. Load existing Content + Chapters
    # 2. Build scenario prompt with previous chapter context
    # 3. Same generation flow as above
    ...
```

**Important**: Store `settings.LLM_MODEL` in `GenerationJob.model_name` at generation time. This creates an audit trail of which model generated what — essential for comparing OpenAI vs local LLM quality later.

---

### Step 6: Generation API Endpoints
**Executor**: engineer
**Priority**: P0
**Files**: `backend/api/generate.py` (new), `backend/main.py` (register router)

**What to do**:

Create `backend/api/generate.py` with these endpoints:

```
POST /api/v1/generate/story
  Body: { genre, tags[], tone, language, word_count }
  Returns: GenerationJobPublic (with job_id)

POST /api/v1/generate/chapter/{content_id}
  Body: { word_count }
  Returns: GenerationJobPublic

GET /api/v1/generate/status/{job_id}
  Returns: GenerationJobPublic (poll job status)

GET /api/v1/generate/stream/{job_id}
  Returns: SSE stream (text/event-stream)
```

**Request model**:
```python
class StoryGenerateRequest(SQLModel):
    genre: str
    tags: list[str] = []
    tone: str = "romantic"
    language: str = "zh"
    word_count: int = Field(default=1500, ge=500, le=3000)
```

**Follow existing patterns**: Use `SessionDep` for DB access (see `backend/api/content.py`). Use `APIRouter(prefix="/api/v1", tags=["generation"])`.

**Register in `main.py`**: Add `from api.generate import router as generate_router` and `app.include_router(generate_router)`.

---

### Step 7: SSE Streaming Endpoint
**Executor**: engineer
**Priority**: P0
**Files**: `backend/api/generate.py` (extend)

**What to do**:

Implement the SSE streaming endpoint using FastAPI's `StreamingResponse`:

```python
from fastapi.responses import StreamingResponse

@router.get("/generate/stream/{job_id}")
async def stream_generation(job_id: uuid.UUID, session: SessionDep):
    job = session.get(GenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    async def event_stream():
        system_prompt = build_system_prompt(...)
        scenario_prompt = build_scenario_prompt(...)

        full_text = ""
        async for chunk in generate_chapter_stream(system_prompt, scenario_prompt):
            full_text += chunk
            yield f"data: {json.dumps({'text': chunk})}\n\n"

        # Save completed text to DB
        yield f"data: {json.dumps({'done': True, 'word_count': len(full_text)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

**Why SSE works identically for local LLM**: The OpenAI SDK's `stream=True` returns the same async iterator format regardless of backend (OpenAI, Ollama, vLLM). The SSE endpoint doesn't know or care what's generating the text.

**`X-Accel-Buffering: no`**: Prevents nginx/reverse proxies from buffering the stream. Important for production.

---

### Step 8: Unit Tests for Generation Service
**Executor**: tester
**Priority**: P1
**Files**: `backend/tests/test_generation.py` (new), `backend/tests/test_prompts.py` (new)

**What to do**:

1. **`test_prompts.py`** — test prompt assembly (pure logic, no mocks needed):
   - System prompt contains safety rules
   - Scenario prompt includes all parameters
   - Different languages produce different prompts
   - Prompt output is valid markdown (model-agnostic)

2. **`test_generation.py`** — test generation service (mock the OpenAI client):
   - Mock `AsyncOpenAI.chat.completions.create` — return fake streaming chunks
   - Test `generate_chapter_stream` yields text chunks
   - Test `generate_chapter_full` returns complete text
   - Test error handling (API timeout, connection error)
   - Test `create_story` creates Content + Chapter + Job records
   - Test GenerationJob status transitions: pending → generating → completed/failed

3. **`test_generate_api.py`** — test API endpoints:
   - `POST /generate/story` returns job with status "pending"
   - `GET /generate/status/{job_id}` returns job status
   - `GET /generate/stream/{job_id}` returns SSE content-type
   - Invalid job_id returns 404

**Mock pattern**:
```python
from unittest.mock import AsyncMock, patch

@patch("services.generation._client")
async def test_generate_stream(mock_client):
    # Mock the streaming response
    mock_client.chat.completions.create = AsyncMock(return_value=fake_stream)
    ...
```

**Do NOT hit real LLM APIs in tests.** Mock at the `_client` level.

---

## File Summary

| File | Action | Step |
|------|--------|------|
| `backend/core/config.py` | Edit — add LLM settings | 1 |
| `backend/requirements.txt` | Edit — add `openai` | 1 |
| `backend/models/content.py` | Edit — add GenerationJob model | 2 |
| `backend/services/__init__.py` | Create (empty) | 3 |
| `backend/services/prompts.py` | Create — prompt assembly | 3 |
| `backend/services/generation.py` | Create — LLM client + orchestration | 4, 5 |
| `backend/api/generate.py` | Create — API endpoints + SSE | 6, 7 |
| `backend/main.py` | Edit — register generate router | 6 |
| `backend/tests/test_prompts.py` | Create — prompt tests | 8 |
| `backend/tests/test_generation.py` | Create — service tests | 8 |
| `backend/tests/test_generate_api.py` | Create — endpoint tests | 8 |

---

## Local LLM Migration Checklist (When the Time Comes)

When you're ready to switch to local LLM, here's what changes:

### Infrastructure (one-time setup)
- [ ] Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
- [ ] Pull model: `ollama pull qwen2.5:14b`
- [ ] OR deploy vLLM: `python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-14B-Instruct`

### Config changes (3 env vars in `.env`)
```bash
# Before (OpenAI)
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-xxx
LLM_MODEL=gpt-4o-mini

# After (Ollama + Qwen)
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=qwen2.5:14b

# After (vLLM + Qwen)
LLM_BASE_URL=http://localhost:8000/v1
LLM_API_KEY=not-needed
LLM_MODEL=Qwen/Qwen2.5-14B-Instruct
```

### Code changes needed: **ZERO**

### Optional enhancements (build only when needed)
- [ ] Fallback chain: try local → fallback to OpenAI (add `LLM_FALLBACK_BASE_URL` etc.)
- [ ] Model-specific prompt tweaks via `backend/services/prompts.py` (add Qwen-specific framing)
- [ ] A/B test routing: random % of traffic to different `base_url` endpoints
- [ ] Quality monitoring: compare `model_name` in GenerationJob against user ratings

---

## Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| Use `openai` SDK for everything | Ollama/vLLM/llama.cpp all support OpenAI-compatible API. One client, zero abstraction overhead. |
| Generic `LLM_*` config, not `OPENAI_*` | Makes config provider-agnostic. No mental model of "this is an OpenAI thing." |
| Store `model_name` on every GenerationJob | Essential for A/B comparison when testing local LLM quality vs OpenAI baseline. |
| Separate `prompts.py` from `generation.py` | Prompt assembly is pure logic (testable, no I/O). Keeps generation service thin. Allows model-specific prompt tweaks later without touching generation code. |
| No provider abstraction layer | YAGNI. The OpenAI SDK already abstracts providers. Building our own adds complexity with zero benefit. |
| No fallback chain in MVP | Premature optimization. Build it when local LLM is deployed and you need reliability. |
| `LLM_TIMEOUT=120` default | Local LLMs on consumer GPUs can be 3-5x slower than cloud API. 120s prevents premature timeout. |

---

## Dependency Graph

```
Step 1 (Config + Deps)
  └── Step 2 (GenerationJob Model)
        └── Step 3 (Prompt Assembly)
              └── Step 4 (Generation Service)
                    └── Step 5 (Orchestrator)
                          └── Step 6 (API Endpoints)
                                └── Step 7 (SSE Streaming)
                                      └── Step 8 (Tests)
```

Steps 1-2 are foundations. Steps 3-4 can be developed together. Steps 6-7 depend on 4-5. Tests (8) come last.

---

## Implementation Status

| Step | Description | Status | Date |
|------|-------------|--------|------|
| 1 | Config & Dependencies | Done | 2026-03-18 |
| 2 | GenerationJob Model | Done | 2026-03-18 |
| 3 | Prompt Assembly Service | Done | 2026-03-18 |
| 4 | Generation Service (Core) | Done | 2026-03-18 |
| 5 | Generation Orchestrator | Done | 2026-03-18 |
| 6 | Generation API Endpoints | Done | 2026-03-18 |
| 7 | SSE Streaming Endpoint | Done | 2026-03-18 |
| 8 | Unit Tests | Not started | — |

## Immediate Next Action

> **tester**: Implement Step 8 — unit tests for prompts, generation service, and API endpoints. See Step 8 section above for detailed test plan.
