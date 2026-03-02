# System Architecture Design

## 1. System Overview

**Your Novel** is a web-first AI-native content platform focused on immersive reading experiences with seamless AI content generation capabilities.

### 1.1 Core Product Philosophy

- **Reading-Centric**: Primary value proposition is content discovery and consumption
- **AI as Infrastructure**: Content generation operates seamlessly in the background
- **Web-First Experience**: Optimized for web usage patterns and mouse interactions
- **Accessibility First**: Frictionless onboarding with age-gated content discovery

### 1.2 Platform Scope

- **Web Application** (Primary): Progressive Web App (PWA) with installable capabilities
- **Android Application** (Secondary): Native Android app for enhanced experience
- **Backend Services**: Monolithic API with modular domain services
- **AI Infrastructure**: OpenAI API (Phase 1) → Self-hosted LLM (Phase 2) -> Fine-tuned LLM (Phase 3)

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                            │
├─────────────────────────┬───────────────────────────────────┤
│                         │                                   │
│  Web App + PWA           │  Android Native (Future)         │
│  (HTML/CSS/JavaScript)   │  (Kotlin + Jetpack Compose)      │
│                         │                                   │
└───────────┬─────────────┴───────────────┬───────────────────┘
            │                             │
            └────────────┬────────────────┘
                         │
                    ┌────▼────┐
                    │   CDN   │
                    └────┬────┘
                         │
        ┌────────────────┴────────────────┐
        │                                  │
┌───────▼────────┐              ┌─────────▼─────────┐
│  REST API      │              │  SSE Stream       │
│  (FastAPI)     │              │  (AI Generation)  │
└───────┬────────┘              └─────────┬─────────┘
        │                                  │
        └────────────┬─────────────────────┘
                     │
        ┌────────────▼─────────────────────┐
        │      Service Layer (DDD)         │
        ├──────────────────────────────────┤
        │                                  │
    ┌───▼────┐  ┌─────────┐  ┌──────────▼──┐
    │Content │  │  AI/Gen │  │    User     │
    │Service │  │ Service │  │  Service    │
    └───┬────┘  └────┬────┘  └──────────┬──┘
        │            │                │
        └────────────┼────────────────┘
                     │
    ┌────────────────▼────────────────────┐
    │      Infrastructure Layer           │
    ├──────────────┬──────────────────────┤
    │              │                      │
┌───▼────────┐ ┌──▼─────┐  ┌───────────▼──┐
│ PostgreSQL │ │ Redis  │  │ Object Store │
│ (Primary)  │ │ (Cache)│  │  (R2 + CDN)  │
└────────────┘ └────────┘  └──────────────┘
```

---

## 3. Client Architecture

### 3.1 Web Application (Primary)

#### Technology Stack

**Web + PWA**:
- **Core**: HTML5, CSS3, Vanilla JavaScript (no frameworks for MVP)
- **Progressive Enhancement**: Service workers for offline support
- **Installation**: PWA manifest for "Add to Home Screen" capability
- **iOS Support**: Safari PWA (no App Store needed)
- **Android Support**: Chrome PWA (installable as native-like app)
- **Storage**: IndexedDB for offline reading cache
- **Networking**: Fetch API + SSE (Server-Sent Events) for streaming
- **Image Loading**: Lazy loading + Intersection Observer API

#### Why Web + PWA First?

1. **Avoids iOS App Store**: No $99/year fee, no review delays, no adult content policy risks
2. **Faster Development**: Single codebase for all platforms
3. **Instant Updates**: No app store approval needed
4. **SEO Benefits**: Discoverable through web search
5. **Low Barrier**: Users can access immediately without downloading from app store

#### Core Web Features

**1. Content Reading Interface**

```
Reading Screen Components:
├── Header (minimal)
│   ├── Back button
│   ├── Chapter title
│   └── Settings (font size, theme)
│
├── Content View (scrollable)
│   ├── Text content (markdown-rendered)
│   ├── Illustrations (inline images)
│   └── Audio player (TTS controls)
│
├── Navigation Bar (bottom)
│   ├── Previous chapter
│   ├── Progress indicator
│   └── Next chapter
│
└── Hidden Features (swipe gestures)
    ├── Swipe right: Previous chapter
    ├── Swipe left: Next chapter
    └── Long press: Chapter menu (bookmark, share, adjust)
```

**2. Content Discovery**

```
Discovery Flow:
├── Home Screen
│   ├── "Continue Reading" (last accessed content)
│   ├── "Trending Now" (popular content)
│   ├── "Recommended for You" (tag-based)
│   └── Genre categories (tap to explore)
│
├── Content Detail Screen
│   ├── Cover art
│   ├── Title & author
│   ├── Synopsis
│   ├── Tags/genres
│   ├── Chapter list
│   └── "Start Reading" / "Continue" CTA
│
└── Library Screen (user's saved content)
    ├── Currently Reading
    ├── Bookmarks
    └── History
```

**3. Age Verification Flow**

```
Age Gate (First Launch Only):
├── Full-screen modal
├── Date of birth picker (must be 18+)
├── Terms of service checkbox
└── "Enter" button (disabled until valid DOB + checkbox)

Design Principles:
- Non-intrusive (shown once)
- Clear legal language
- No data collection beyond DOB verification
- Persistent (stored in Keychain/EncryptedSharedPrefs)
```

**4. AI Generation Interface (Subtle)**

```
Generation Access Points (Intentionally Unobtrusive):

Option A: End-of-Chapter Prompt
└── After finishing last chapter
    └── "Continue to next chapter?" button
        └── If no next chapter exists
            └── "Generate Chapter N" (subtle button)

Option B: Library Screen
└── "My Stories" tab
    └── Tap into a story
        └── Chapter list with "+" button at bottom
            └── "Generate Next Chapter"

Generation Process (Background):
1. User taps "Generate"
2. Loading indicator appears (subtle spinner)
3. User can navigate away (background task)
4. Notification when ready: "Chapter N is ready to read"
5. User returns to see new chapter with "NEW" badge

No Progress Screens:
- Avoid "Generating... 23%" style indicators
- Frame as "Creating your story..."
- If generation takes > 30s, show: "This may take a few minutes"
```
---

## 4. Backend Architecture

### 4.1 API Layer

**Base Technology**: Python 3.11+ + FastAPI 0.104+

#### REST Endpoints

```python
# Content Discovery
GET    /api/v1/content/trending          # Trending content
GET    /api/v1/content/recommended       # Personalized recommendations
GET    /api/v1/content/{id}              # Content details
GET    /api/v1/content/{id}/chapters     # Chapter list

# Reading
GET    /api/v1/chapters/{id}             # Chapter content
POST   /api/v1/chapters/{id}/progress    # Save reading progress

# Generation (Authenticated)
POST   /api/v1/generate/chapter          # Request chapter generation
GET    /api/v1/generate/status/{id}      # Check generation status

# User Management
POST   /api/v1/auth/age-verify           # Age verification
POST   /api/v1/auth/register             # Device-based registration
GET    /api/v1/me/profile                # User profile

# Library
POST   /api/v1/library/bookmark          # Add to library
DELETE /api/v1/library/bookmark/{id}     # Remove from library
GET    /api/v1/library                   # User's library
```

#### SSE Streaming Endpoint

```python
GET /api/v1/generate/stream/{generation_id}

# Response format (Server-Sent Events)
data: {"type": "token", "content": "这是一段文字"}
data: {"type": "token", "content": "正在生成..."}
data: {"type": "done", "chapterId": "uuid-123"}
data: {"type": "error", "message": "..."}
```

### 4.2 Service Layer (Domain-Driven Design)

#### Content Service

**Responsibilities**: Content metadata, chapter management, reading progress

```python
class ContentService:
    async def get_trending(self, limit: int) -> List[ContentSummary]:
        ...

    async def get_recommended(self, user_id: str) -> List[ContentSummary]:
        ...

    async def get_content_details(self, content_id: str) -> Content:
        ...

    async def get_chapter_list(self, content_id: str) -> List[Chapter]:
        ...

    async def save_reading_progress(
        self, user_id: str, chapter_id: str, position: int
    ) -> None:
        ...

    async def get_reading_progress(self, user_id: str) -> ReadingProgress:
        ...
```

#### AI Generation Service

**Responsibilities**: Prompt assembly, LLM orchestration, safety filtering, output storage

```python
class AIGenerationService:
    async def generate_chapter(
        self, request: GenerationRequest
    ) -> GenerationJob:
        ...

    async def get_generation_status(self, job_id: str) -> GenerationStatus:
        ...

    async def stream_generation(self, job_id: str) -> AsyncGenerator[str, None]:
        ...

    # Internal methods
    async def _assemble_prompt(
        self, request: GenerationRequest
    ) -> SystemAndScenarioPrompt:
        ...

    async def _invoke_llm(
        self, prompt: str
    ) -> AsyncGenerator[str, None]:
        ...

    async def _validate_safety(self, content: str) -> SafetyResult:
        ...

    async def _save_chapter(
        self, content: str, metadata: ChapterMetadata
    ) -> Chapter:
        ...
```

#### User Service

**Responsibilities**: Authentication, profile management, preferences, library

```python
class UserService:
    async def verify_age(
        self, dob: date, device_id: str
    ) -> AgeVerificationResult:
        ...

    async def register_device(self, device_id: str) -> UserSession:
        ...

    async def get_profile(self, user_id: str) -> UserProfile:
        ...

    async def update_preferences(
        self, user_id: str, prefs: UserPreferences
    ) -> None:
        ...

    async def get_library(self, user_id: str) -> List[LibraryItem]:
        ...

    async def add_bookmark(self, user_id: str, content_id: str) -> None:
        ...
```

### 4.3 Infrastructure Layer

**Refer to [Data Model & Schema Design](../data/Data_Model.md)** for detailed database schemas (PostgreSQL), Redis caching structures, and Object Storage (R2) directory layouts.

- **PostgreSQL**: Primary transactional database for users, content metadata, reading progress, and vector search (pgvector).
- **Redis**: Caching, session management, and rate limiting.
- **Object Storage (R2 + CDN)**: Media files (images, audio) with edge caching.

---

## 5. Request Flows

### 5.1 Content Reading Flow

```
User                          Web App                       API                  Database
│                              │                              │                     │
│  Tap "Continue Reading"      │                              │                     │
├─────────────────────────────>│                              │                     │
│                              │  GET /api/v1/me/progress     │                     │
│                              ├─────────────────────────────>│                     │
│                              │                              │  Query progress      │
│                              │                              ├────────────────────>│
│                              │                              │  Return chapterId   │
│                              │                              │<────────────────────┤
│                              │  {chapterId, position}      │                     │
│                              │<─────────────────────────────┤                     │
│                              │                              │                     │
│                              │  GET /api/v1/chapters/:id    │                     │
│                              ├─────────────────────────────>│                     │
│                              │                              │  Query chapter      │
│                              │                              ├────────────────────>│
│                              │                              │  Return content     │
│                              │                              │<────────────────────┤
│                              │  {title, content, images}   │                     │
│                              │<─────────────────────────────┤                     │
│                              │                              │                     │
│  Display reading screen     │                              │                     │
│<─────────────────────────────┤                              │                     │
│                              │                              │                     │
│  Scroll, read...            │                              │                     │
│  (App handles offline)      │                              │                     │
│                              │                              │                     │
│  Close screen (autosave)     │                              │                     │
├─────────────────────────────>│                              │                     │
│                              │  POST /api/v1/chapters/:id/progress             │
│                              ├─────────────────────────────>│                     │
│                              │                              │  Save progress      │
│                              │                              ├────────────────────>│
│                              │  200 OK                      │                     │
│                              │<─────────────────────────────┤                     │
```

### 5.2 AI Generation Flow

```
User                      Web App                  API                     LLM
│                            │                        │                        │
│  Tap "Generate Chapter"   │                        │                        │
├───────────────────────────>│                        │                        │
│                            │  POST /api/v1/generate  │                        │
│                            ├───────────────────────>│                        │
│                            │                        │  Create job (pending)  │
│                            │                        │  Return {jobId}        │
│                            │  {jobId: "uuid-123"}   │                        │
│                            │<───────────────────────┤                        │
│                            │                        │                        │
│  Show "Creating..."       │                        │                        │
│<───────────────────────────┤                        │                        │
│                            │                        │                        │
│  (User navigates away)     │                        │                        │
│                            │                        │                        │
│                            │                        │  Background job:       │
│                            │                        │  1. Assemble prompt    │
│                            │                        │  2. Call LLM (stream)  │
│                            │                        ├───────────────────────>│
│                            │                        │  Stream tokens...      │
│                            │                        │< ~~~~~~~~~~~~~~~~~~~~~ │
│                            │                        │  3. Validate safety    │
│                            │                        │  4. Save to DB         │
│                            │                        │  5. Update job: done   │
│                            │                        │                        │
│  (Push notification)       │                        │                        │
│  "Chapter N is ready"      │                        │                        │
│<────────────────────────────┤                        │                        │
│                            │                        │                        │
│  Tap notification          │                        │                        │
├───────────────────────────>│                        │                        │
│                            │  GET /api/v1/generate/status/:jobId              │
│                            ├───────────────────────>│                        │
│                            │                        │  Return {status: done} │
│                            │<───────────────────────┤                        │
│                            │                        │                        │
│  Show "NEW" badge          │                        │                        │
│<───────────────────────────┤                        │                        │
```

### 5.3 Content Discovery Flow

```
User                      Web App                  API                    Database
│                            │                        │                       │
│  Launch app                │                        │                       │
├───────────────────────────>│                        │                       │
│                            │  Check local cache      │                       │
│                            │  (IndexedDB/PWA)        │                       │
│                            │                        │                       │
│  Display home screen       │                        │                       │
│  (cached + placeholder)    │                        │                       │
│<───────────────────────────┤                        │                       │
│                            │                        │                       │
│  Background refresh        │                        │                       │
│                            │  GET /api/v1/content/trending               │
│                            ├───────────────────────>│                       │
│                            │                        │  Check Redis cache    │
│                            │                        ├──────────────>│
│                            │                        │  Cache miss           │
│                            │                        │<──────────────┤
│                            │                        │                       │
│                            │                        │  Query PostgreSQL     │
│                            │                        ├─────────────────────>│
│                            │                        │  Return trending      │
│                            │                        │<─────────────────────┤
│                            │                        │  Store in Redis       │
│                            │  {content: [...]}      │                       │
│                            │<───────────────────────┤                       │
│                            │  Update local cache    │                       │
│                            │                        │                       │
│  Update UI (refresh)       │                        │                       │
│<───────────────────────────┤                        │                       │
```

---

## 6. AI Generation System

### 6.1 Model Strategy

**Phase 1** (Launch - Month 2): OpenAI GPT-4o mini
- Fastest time-to-market
- High quality baseline
- Cost: ~$50/month for 500 users

**Phase 2** (Month 3-4): Self-hosted Qwen2.5 14B
- Cost optimization
- Data privacy
- 10x cost reduction

**Phase 3** (Month 6+): Fine-tuned models
- Collect 10,000+ user-rated examples
- Train specialized models for genres
- Platform-specific style consistency

### 6.2 Prompt Architecture

**Refer to [AI Generation Design](./AI_Generation_Design.md) and [Prompt Quick Reference](./Prompt_Quick_Reference.md)** for detailed prompt architectures, templates, and LLM-specific routing logic.

### 6.3 Safety & Quality Assurance

**Refer to [Trust & Safety Design](../safety/Trust_and_Safety.md)** for detailed pre-generation gates, post-generation LLM safety filtering, fallback behavior, and compliance logging.

---

## 7. Offline & Sync Strategy

### 7.1 PWA Offline Support

**What Works Offline**:
- Read previously downloaded chapters
- Browse library
- Adjust reading settings (font size, theme)
- View reading progress

**What Requires Online**:
- Content generation
- Downloading new content
- Syncing progress across devices

**Sync Strategy**:
```javascript
// PWA (IndexedDB + Service Worker)
class SyncManager {
  async syncReadingProgress() {
    const localProgress = await this.getLocalProgress()
    const remoteProgress = await fetch('/api/v1/me/progress').then(r => r.json())

    const merged = this.mergeProgress(localProgress, remoteProgress)
    await fetch('/api/v1/me/progress', {
      method: 'POST',
      body: JSON.stringify(merged)
    })
    await this.saveLocal(merged)
  }

  async getLocalProgress() {
    // IndexedDB access
    const db = await this.openDB()
    return db.getAll('progress')
  }

  async saveLocal(progress) {
    const db = await this.openDB()
    await db.put('progress', progress)
  }

  openDB() {
    return indexedDB.open('YourNovelDB', 1)
  }
}

// Service worker for offline caching
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request)
    })
  )
})
```

**Sync Triggers**:
- App foreground (every 5 minutes)
- After reading session ends
- Before downloading new content
- Manual "Refresh" gesture

---

## 8. Performance & Scalability

### 8.1 Target Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| App launch time | < 2s | Cold start to home screen |
| Content load | < 1s | Chapter fetch to display |
| Generation time | < 30s | Request to "ready" notification |
| API response (p95) | < 200ms | Non-streaming endpoints |
| Concurrent readers | 10,000 | Simultaneous active users |
| Daily generations | 5,000 | AI generation requests/day |

### 8.2 Caching Strategy

**Multi-Layer Caching**:

```
┌─────────────────────────────────────┐
│  Client-Side (IndexedDB/PWA)        │
│  - Downloaded chapters              │
│  - User library                     │
│  - Reading progress                 │
│  TTL: 7 days                        │
└──────────────┬──────────────────────┘
               │ Miss
               ▼
┌─────────────────────────────────────┐
│  CDN Edge (Cloudflare)              │
│  - Cover images                     │
│  - Illustrations                    │
│  - Audio files                      │
│  TTL: 1 hour                        │
└──────────────┬──────────────────────┘
               │ Miss
               ▼
┌─────────────────────────────────────┐
│  Redis Cache                        │
│  - Trending content                 │
│  - User recommendations              │
│  - Session tokens                   │
│  TTL: 5-30 minutes                  │
└──────────────┬──────────────────────┘
               │ Miss
               ▼
┌─────────────────────────────────────┐
│  PostgreSQL (Primary DB)            │
│  - Content metadata                 │
│  - User accounts                    │
│  - Generation jobs                  │
└─────────────────────────────────────┘
```

### 8.3 Scalability Roadmap

**Current Capacity** (Single VPS):
- 10,000 daily active users
- 5,000 generations/day
- 100 GB database
- 500 GB object storage

**Scale Triggers** (When to upgrade):
- Database CPU > 70% for 1 hour
- API response time p95 > 500ms
- Generation queue depth > 100

**Scale Up Actions**:
1. **Database**: Add read replica for content queries
2. **Redis**: Upgrade to Redis Cluster
3. **API**: Horizontal scaling (load balancer + 2 instances)
4. **AI Service**: Extract to separate service (job queue + workers)

---

## 9. Security & Compliance

### 9.1 Age Verification

**Implementation**:
```javascript
// Client-side (JavaScript)
async function verifyAge(dob) {
  const age = calculateAge(dob)
  if (age < 18) {
    showBlockScreen("You must be 18+ to use this app")
    return false
  }

  // Send to server
  const result = await fetch('/api/v1/auth/age-verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dob })
  }).then(r => r.json())

  if (result.success) {
    localStorage.setItem('verification_token', result.token)
    enableAppAccess()
  }

  return result.success
}
```

```python
# Server-side (Python/FastAPI)
from datetime import date

async def handle_age_verification(dob: date, device_id: str):
    age = calculate_age(dob)
    if age < 18:
        raise HTTPException(
            status_code=403,
            detail="Age verification failed"
        )

    # Create user account (device-based)
    user = await create_or_update_user(device_id, dob)

    # Generate session token
    token = generate_session_token(user.id)

    return {"success": True, "token": token}
```

### 9.2 Content Moderation

**Pre-Generation**:
- User account flags (banned users cannot generate)
- Rate limiting (prevent abuse)

**Post-Generation**:
- Automated safety checks (see 6.3)
- User reporting system
- Human review for flagged content (manual queue)

### 9.3 Data Privacy

**Data Collection** (Minimal):
- Device ID (for auth)
- Date of birth (age verification)
- Reading progress (sync)
- Generation history (quality improvement)

**Data Storage**:
- PostgreSQL (encrypted at rest)
- Redis (ephemeral, session data)
- R2 (encrypted object storage)

**Data Retention**:
- User data: Retained until account deletion
- Generation history: 90 days (for quality improvement)
- Reading progress: Retained indefinitely (user value)

**Compliance**:
- GDPR-compliant data export
- Account deletion with data wipe
- Clear privacy policy in app
- No third-party data sharing

---

## 10. Monitoring & Observability

### 10.1 Metrics to Track

**Application Metrics**:
- App launch time (p50, p95, p99)
- API error rate
- Generation success rate
- Chapter read-through rate
- User session duration

**Business Metrics**:
- Daily active users (DAU)
- Generations per user per day
- Content completion rate
- User retention (Day 1, 7, 30)
- Average reading time per session

**Infrastructure Metrics**:
- CPU, memory, disk usage
- Database query performance
- Redis hit rate
- CDN bandwidth usage

### 10.2 Alerting

**Critical Alerts** (Page on-call):
- API error rate > 5%
- Database down
- Generation failure rate > 10%
- Age verification system down

**Warning Alerts** (Email within 1 hour):
- API response time p95 > 500ms
- Database CPU > 70%
- Generation queue depth > 50
- Disk space < 20%

---

## 11. Technology Stack Summary

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Web/PWA** | HTML5 + CSS3 + Vanilla JavaScript | Single codebase, no App Store needed, works on iOS/Android |
| **Android (Future)** | Kotlin + Jetpack Compose | User's familiar language, native performance for Phase 2 |
| **Backend** | Python 3.11+ + FastAPI 0.104+ | User knows Python, async support, automatic API docs |
| **Database** | PostgreSQL 15 + pgvector | Reliable, vector search, ACID compliance |
| **Cache** | Redis 7 | Fast in-memory storage, rate limiting |
| **Storage** | Cloudflare R2 + CDN | Free egress, global distribution, cost-effective |
| **LLM (Phase 1)** | OpenAI GPT-4o mini | Fast time-to-market, high quality |
| **LLM (Phase 2)** | Qwen2.5 14B (self-hosted) | Cost optimization, data privacy |
| **Monitoring** | Sentry + Datadog | Error tracking, performance monitoring |
| **Analytics** | Mixpanel + PostHog | User behavior analytics, funnel analysis |
| **CI/CD** | GitHub Actions | Free for public repos, integrated with GitHub |
| **Hosting** | VPS (Hetzner/DigitalOcean) | Cost-effective, full control |

---

## 12. Deployment Architecture

### 12.1 Initial Deployment (Month 1)

```
┌─────────────────────────────────────────────────┐
│              Single VPS Architecture            │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │     Docker Compose (Single Server)        │ │
│  ├───────────────────────────────────────────┤ │
│  │                                           │ │
│  │  ┌────────────┐  ┌──────────────┐        │ │
│  │  │ Nginx      │  │ PostgreSQL   │        │ │
│  │  │ (Reverse   │  │ (Primary DB) │        │ │
│  │  │  Proxy)    │  │              │        │ │
│  │  └──────┬─────┘  └──────────────┘        │ │
│  │         │                                 │ │
│  │  ┌──────▼─────┐  ┌──────────────┐        │ │
│  │  │ FastAPI    │  │ Redis        │        │ │
│  │  │ (Python)   │  │ (Cache)      │        │ │
│  │  └────────────┘  └──────────────┘        │ │
│  │                                           │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  VPS Specs: 4 vCPU, 8GB RAM, 160GB SSD        │
│  Cost: ~$25-40/month                            │
└─────────────────────────────────────────────────┘
```

### 12.2 Scale-Up Deployment (Month 3+)

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Server Architecture                 │
│                                                              │
│  ���────────────┐                                             │
│  │ Load       │    ┌──────────────────────────────────────┐ │
│  │ Balancer   │───>│  Application Servers (Auto-scaling)  │ │
│  │ (Nginx)    │    │  - API Server 1                      │ │
│  └────────────┘    │  - API Server 2                      │ │
│                    │  - API Server N                      │ │
│                    └──────────────────────────────────────┘ │
│                              │                               │
│  ┌──────────────────────────┴───────────────────────────┐  │
│  │                                                         │  │
│  │  ┌────────────┐  ┌──────────┐  ┌──────────────────┐  │  │
│  │  │ PostgreSQL │  │ Redis    │  │ AI Generation    │  │  │
│  │  │ Primary    │  │ Cluster  │  │ Workers (queue)  │  │  │
│  │  └────────────┘  └──────────┘  └──────────────────┘  │  │
│  │                                                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                              │
│  Infrastructure: Hetnser/AWS (mix of cost-optimized)        │
│  Cost: ~$100-200/month (at 10k DAU)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Related Documents

- **Product Requirements**: [PRD](../product/Product_Requirment_Doc.md)
- **Initial Architecture Decision**: [ADR-0001](../decisions/ADR-0001-initial-architecture.md)
- **LLM Strategy**: [ADR-0002](../decisions/ADR-0002-llm-strategy.md)
- **Prompt Design**: [ADR-0003](../decisions/ADR-0003-prompt-design-standards.md)
- **AI Generation Design**: [AI_Generation_Design.md](./AI_Generation_Design.md)
- **Data Model**: [Data_Model.md](../data/Data_Model.md)
- **Trust & Safety**: [Trust_and_Safety.md](../safety/Trust_and_Safety.md)
