# What We Need To Do Now

**Date**: 2026-03-16
**Status**: MVP Phase — foundations built, core product loop not yet functional

---

## Current State Summary

| Layer | Status |
|-------|--------|
| Architecture docs | Done (system, AI, prompts, ADRs, PRD, safety) |
| Data models | Done (User, Content, Chapter in SQLModel) |
| Backend API | Partial — read endpoints only (health, age-verify, content CRUD) |
| AI Generation | Steps 1-7 done (service, API, SSE). Step 8 tests pending. |
| Safety filtering | Not started |
| Frontend | Not started |
| Tests | Not started |
| Database | SQLite (fine for MVP) |

**The core product loop (user opens app -> browses content -> reads a story -> generates new content) is not yet functional.** That's what we need to build.

---

## Recommended Build Order

### Phase 1: Complete the Backend Core (Backend-first, testable without UI)

#### Step 1.1 — OpenAI Generation Service
**Executor**: engineer
**Priority**: P0
**Files to create/modify**:
- `backend/services/generation.py` — OpenAI client wrapper, prompt assembly, chapter generation logic
- `backend/core/config.py` — Add `OPENAI_API_KEY`, generation model settings
- `backend/models/content.py` — Ensure `GenerationJob` model exists per Data_Model.md schema
- `requirements.txt` — Add `openai` package

**Context**: See `docs/architecture/AI_Generation_Design.md` for prompt templates, model selection, and the 3-phase LLM strategy. MVP uses GPT-4o mini. Prompts must be model-agnostic per ADR-0003.

**What it does**:
1. Accept generation parameters (genre, tags, tone, length, language)
2. Assemble prompt from template + parameters
3. Call OpenAI API (streaming)
4. Return generated text chunk-by-chunk
5. Track job status (pending → generating → completed/failed)

---

#### Step 1.2 — Generation API Endpoints + SSE Streaming
**Executor**: engineer
**Priority**: P0
**Files to create/modify**:
- `backend/api/generate.py` — New router with endpoints:
  - `POST /api/v1/generate/story` — Create new story + first chapter
  - `POST /api/v1/generate/chapter` — Generate next chapter for existing story
  - `GET /api/v1/generate/status/{job_id}` — Poll job status
  - `GET /api/v1/generate/stream/{job_id}` — SSE streaming endpoint
- `backend/main.py` — Register the new router

**Context**: See `docs/architecture/System_Architecture.md` section on SSE streaming. FastAPI's `StreamingResponse` with `text/event-stream` content type. Follow existing patterns in `backend/api/content.py`.

---

#### Step 1.3 — Safety Filtering Service
**Executor**: engineer
**Priority**: P0
**Files to create/modify**:
- `backend/services/safety.py` — Pre-generation input validation + post-generation output filtering
- `backend/services/safety_wordlists.py` — Keyword blocklists (or load from config)

**Context**: See `docs/safety/Trust_and_Safety.md` for the full policy. MVP needs:
1. **Pre-generation**: Block prompts requesting minors, non-consensual scenarios, real people, extreme violence
2. **Post-generation**: Keyword scan on output, flag/reject if blocklist terms detected
3. Log all flagged content with metadata for audit trail

Wire this into the generation service from Step 1.1 (call safety check before and after LLM call).

---

#### Step 1.4 — Reading Progress & Library Endpoints
**Executor**: engineer
**Priority**: P1
**Files to create/modify**:
- `backend/api/library.py` — New router:
  - `POST /api/v1/library/bookmark` — Add content to library
  - `DELETE /api/v1/library/bookmark/{content_id}` — Remove bookmark
  - `GET /api/v1/library` — List user's library
- `backend/api/progress.py` — New router:
  - `POST /api/v1/chapters/{chapter_id}/progress` — Save reading position
  - `GET /api/v1/me/progress` — Get all reading progress
- `backend/models/content.py` — Add `ReadingProgress` and `LibraryItem` models if not present
- `backend/main.py` — Register new routers

**Context**: Follow existing Content model patterns. Device-based user auth (device_id in header).

---

### Phase 2: Frontend MVP (Reading Experience)

#### Step 2.1 — App Shell & Navigation
**Executor**: ui_designer
**Priority**: P0
**Files to create**:
- `frontend/index.html` — App shell with age gate
- `frontend/css/styles.css` — Base styles, mobile-first responsive layout
- `frontend/js/app.js` — SPA router (hash-based), API client, state management
- `frontend/js/api.js` — Fetch wrapper for backend API calls
- `frontend/manifest.json` — PWA manifest
- `frontend/sw.js` — Service worker (basic caching)

**Context**: See PRD for the 4 user personas. Mobile-first design. Dark theme (reading comfort). No frameworks — vanilla JS only. Age verification gate must appear before any content.

---

#### Step 2.2 — Content Browse & Discovery Page
**Executor**: ui_designer
**Priority**: P0
**Files to create/modify**:
- `frontend/js/pages/browse.js` — Trending content grid, tag filters, search
- `frontend/css/components/card.css` — Content card component styles

**What it shows**: Cover image, title, tags, chapter count, word count. Tap to open reader.

---

#### Step 2.3 — Reader Page (Core UX)
**Executor**: ui_designer
**Priority**: P0
**Files to create/modify**:
- `frontend/js/pages/reader.js` — Chapter reader with:
  - Paginated or scroll reading mode
  - Font size / theme controls
  - Progress tracking (auto-save position)
  - "Generate next chapter" button (calls generation API)
  - SSE streaming display (text appears word-by-word)
- `frontend/css/components/reader.css` — Reading typography, comfortable line spacing

**Context**: This is the **core product experience**. Reading comfort is paramount. See PRD "Reader Screen" specifications.

---

#### Step 2.4 — Generation UI
**Executor**: ui_designer
**Priority**: P0
**Files to create/modify**:
- `frontend/js/pages/generate.js` — Generation form:
  - Genre selector, tag picker, tone slider, length preference
  - "Generate" button → shows streaming text output
  - Error handling for safety rejections
- `frontend/css/components/generate.css` — Form styling

---

#### Step 2.5 — Library Page
**Executor**: ui_designer
**Priority**: P1
**Files to create/modify**:
- `frontend/js/pages/library.js` — User's bookmarked content, reading history, progress indicators

---

### Phase 3: Testing & Hardening

#### Step 3.1 — Backend Unit Tests
**Executor**: tester
**Priority**: P1
**Files to create**:
- `backend/tests/conftest.py` — Test fixtures (test DB, test client)
- `backend/tests/test_auth.py` — Age verification tests
- `backend/tests/test_content.py` — Content CRUD tests
- `backend/tests/test_generation.py` — Generation service tests (mock OpenAI)
- `backend/tests/test_safety.py` — Safety filter tests (ensure blocklist works)

**Context**: Use `pytest` + `httpx` for async FastAPI testing. Mock OpenAI calls — don't hit real API in tests.

---

#### Step 3.2 — Integration Tests
**Executor**: tester
**Priority**: P1
**Files to create**:
- `backend/tests/test_integration.py` — End-to-end flows:
  1. Age verify → browse → read chapter
  2. Age verify → generate story → stream result → read
  3. Safety filter blocks bad input
  4. Bookmark → view library

---

#### Step 3.3 — Frontend Smoke Tests
**Executor**: tester
**Priority**: P2
- Manual test checklist or lightweight Playwright tests
- Age gate works, navigation works, reader renders, generation streams

---

## What to Build First (Immediate Next Task)

**Start with Step 1.1 + Step 1.2 together** — the generation service and its API endpoints. This is the product's core differentiator and the hardest technical piece. Everything else builds on top of it.

Suggested single task for the engineer:

> "Implement the AI generation service (`backend/services/generation.py`) and generation API endpoints (`backend/api/generate.py`) with SSE streaming. Use OpenAI GPT-4o mini. Follow prompt templates from `docs/architecture/AI_Generation_Design.md`. Include job tracking with the GenerationJob model. Wire into `main.py`."

After that works end-to-end via curl/Swagger, move to safety filtering (Step 1.3), then the frontend (Phase 2).

---

## Dependency Graph

```
Step 1.1 (Generation Service)
  └── Step 1.2 (Generation API + SSE)
        └── Step 1.3 (Safety Filtering) ← wires into generation
              └── Step 2.4 (Generation UI) ← needs backend ready

Step 2.1 (App Shell) ← can start in parallel with backend work
  ├── Step 2.2 (Browse Page)
  ├── Step 2.3 (Reader Page)
  └── Step 2.5 (Library Page)

Step 1.4 (Library/Progress API) ← can start in parallel
  └── Step 2.5 (Library Page)

All backend steps ← Step 3.1 (Unit Tests)
All steps ← Step 3.2 (Integration Tests)
```

**Parallelizable**: Steps 2.1 (frontend shell) and 1.1-1.3 (backend generation) can run simultaneously if two agents are available.
