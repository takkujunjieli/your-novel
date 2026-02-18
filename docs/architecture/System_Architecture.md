# System Architecture Design

## 1. System Overview

**Your Novel** is a mobile-first AI-native content platform focused on immersive reading experiences with seamless AI content generation capabilities.

### 1.1 Core Product Philosophy

- **Reading-Centric**: Primary value proposition is content discovery and consumption
- **AI as Infrastructure**: Content generation operates seamlessly in the background
- **Mobile-First Experience**: Optimized for mobile usage patterns and touch interactions
- **Accessibility First**: Frictionless onboarding with age-gated content discovery

### 1.2 Platform Scope

- **Mobile Applications** (Primary): iOS and Android native apps
- **Web Application** (Secondary): Responsive web for content discovery and account management
- **Backend Services**: Monolithic API with modular domain services
- **AI Infrastructure**: Self-hosted LLM with managed fallback

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                            │
├───────────────┬─────────────────┬───────────────────────────┤
│               │                 │                           │
│  iOS App      │  Android App    │   Web App (React)         │
│  (Swift/UI)   │  (Kotlin)       │   (Content Discovery)     │
│               │                 │                           │
└───────┬───────┴────────┬────────┴───────────┬───────────────┘
        │                │                    │
        └────────────────┼────────────────────┘
                         │
                    ┌────▼────┐
                    │   CDN   │
                    └────┬────┘
                         │
        ┌────────────────┴────────────────┐
        │                                  │
┌───────▼────────┐              ┌─────────▼─────────┐
│  REST API      │              │  SSE Stream       │
│  (Express)     │              │  (AI Generation)  │
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

### 3.1 Mobile Applications (Primary)

#### Technology Stack

**iOS**:
- **Language**: Swift 5.9+
- **UI Framework**: SwiftUI (iOS 15+)
- **Networking**: URLSession + async/await
- **Data Persistence**: Core Data + CloudKit sync
- **Image Loading**: Kingfisher (async image loading with caching)

**Android**:
- **Language**: Kotlin 1.9+
- **UI Framework**: Jetpack Compose (Android 7+)
- **Networking**: Retrofit + OkHttp
- **Data Persistence**: Room Database + WorkManager
- **Image Loading**: Coil (Compose Image Loading)

#### Core Mobile Features

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

**Base Technology**: Node.js 20 + Express 4.x + TypeScript 5.x

#### REST Endpoints

```typescript
// Content Discovery
GET    /api/v1/content/trending          // Trending content
GET    /api/v1/content/recommended       // Personalized recommendations
GET    /api/v1/content/:id               // Content details
GET    /api/v1/content/:id/chapters      // Chapter list

// Reading
GET    /api/v1/chapters/:id              // Chapter content
POST   /api/v1/chapters/:id/progress     // Save reading progress

// Generation (Authenticated)
POST   /api/v1/generate/chapter          // Request chapter generation
GET    /api/v1/generate/status/:id       // Check generation status

// User Management
POST   /api/v1/auth/age-verify           // Age verification
POST   /api/v1/auth/register             // Device-based registration
GET    /api/v1/me/profile                // User profile

// Library
POST   /api/v1/library/bookmark          // Add to library
DELETE /api/v1/library/bookmark/:id      // Remove from library
GET    /api/v1/library                   // User's library
```

#### SSE Streaming Endpoint

```typescript
GET /api/v1/generate/stream/:generationId

// Response format (Server-Sent Events)
data: {"type": "token", "content": "这是一段文字"}
data: {"type": "token", "content": "正在生成..."}
data: {"type": "done", "chapterId": "uuid-123"}
data: {"type": "error", "message": "..."}
```

### 4.2 Service Layer (Domain-Driven Design)

#### Content Service

**Responsibilities**: Content metadata, chapter management, reading progress

```typescript
class ContentService {
  async getTrending(limit: number): Promise<ContentSummary[]>
  async getRecommended(userId: string): Promise<ContentSummary[]>
  async getContentDetails(contentId: string): Promise<Content>
  async getChapterList(contentId: string): Promise<Chapter[]>
  async saveReadingProgress(userId: string, chapterId: string, position: number): Promise<void>
  async getReadingProgress(userId: string): Promise<ReadingProgress>
}
```

#### AI Generation Service

**Responsibilities**: Prompt assembly, LLM orchestration, safety filtering, output storage

```typescript
class AIGenerationService {
  async generateChapter(request: GenerationRequest): Promise<GenerationJob>
  async getGenerationStatus(jobId: string): Promise<GenerationStatus>
  async streamGeneration(jobId: string): Promise<ReadableStream>

  // Internal methods
  private async assemblePrompt(request: GenerationRequest): Promise<SystemAndScenarioPrompt>
  private async invokeLLM(prompt: string): AsyncGenerator<string>
  private async validateSafety(content: string): Promise<SafetyResult>
  private async saveChapter(content: string, metadata: ChapterMetadata): Promise<Chapter>
}
```

#### User Service

**Responsibilities**: Authentication, profile management, preferences, library

```typescript
class UserService {
  async verifyAge(dob: Date, deviceId: string): Promise<AgeVerificationResult>
  async registerDevice(deviceId: string): Promise<UserSession>
  async getProfile(userId: string): Promise<UserProfile>
  async updatePreferences(userId: string, prefs: UserPreferences): Promise<void>
  async getLibrary(userId: string): Promise<LibraryItem[]>
  async addBookmark(userId: string, contentId: string): Promise<void>
}
```

### 4.3 Infrastructure Layer

#### PostgreSQL (Primary Database)

```sql
-- Content Metadata
CREATE TABLE contents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  tags TEXT[],
  cover_image_url VARCHAR(500),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Chapters
CREATE TABLE chapters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content_id UUID REFERENCES contents(id),
  chapter_number INTEGER NOT NULL,
  title VARCHAR(255),
  content TEXT NOT NULL,
  audio_url VARCHAR(500),
  illustration_urls TEXT[],
  word_count INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Reading Progress
CREATE TABLE reading_progress (
  user_id UUID REFERENCES users(id),
  chapter_id UUID REFERENCES chapters(id),
  position_percent INTEGER DEFAULT 0,
  last_read_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (user_id, chapter_id)
);

-- Generation Jobs
CREATE TABLE generation_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  content_id UUID REFERENCES contents(id),
  status VARCHAR(50) DEFAULT 'pending', -- pending, generating, completed, failed
  model_name VARCHAR(100),
  model_version VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

-- Users (Device-based auth)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  device_id VARCHAR(255) UNIQUE NOT NULL,
  date_of_birth DATE NOT NULL,
  age_verified_at TIMESTAMP DEFAULT NOW(),
  preferences JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Library (Bookmarks)
CREATE TABLE library_items (
  user_id UUID REFERENCES users(id),
  content_id UUID REFERENCES contents(id),
  added_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (user_id, content_id)
);

-- Vector Search (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- Content embeddings for recommendations
CREATE TABLE content_embeddings (
  content_id UUID REFERENCES contents(id) PRIMARY KEY,
  embedding vector(1536) -- OpenAI embedding dimension
);

-- User preference embeddings for personalization
CREATE TABLE user_preferences_embeddings (
  user_id UUID REFERENCES users(id) PRIMARY KEY,
  embedding vector(1536)
);
```

#### Redis (Caching & Sessions)

**Use Cases**:
- Session storage (device-based auth tokens)
- Rate limiting (generation requests per user)
- Caching trending content (5-minute TTL)
- Caching user library (30-minute TTL)

```typescript
// Redis usage patterns
await redis.set(`session:${deviceId}`, sessionToken, 'EX', 86400 * 30) // 30 days
await redis.incr(`rate:generate:${userId}`)
await redis.set(`cache:trending`, JSON.stringify(content), 'EX', 300)
```

#### Object Storage (R2 + CDN)

**Storage Structure**:
```
/
├── covers/
│   ├── {contentId}/cover.jpg
│   └── {contentId}/cover.webp
├── illustrations/
│   └── {chapterId}/
│       ├── illustration-1.jpg
│       └── illustration-2.jpg
└── audio/
    └── {chapterId}/
        └── speech.mp3
```

**CDN Configuration**:
- Global edge caching (1-hour TTL)
- Image optimization (WebP, AVIF formats)
- Adaptive bitrate for audio

---

## 5. Request Flows

### 5.1 Content Reading Flow

```
User                          Mobile App                    API                  Database
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
User                      Mobile App                API                     LLM
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
User                      Mobile App                API                    Database
│                            │                        │                       │
│  Launch app                │                        │                       │
├───────────────────────────>│                        │                       │
│                            │  Check local cache      │                       │
│                            │  (Core Data/Room)       │                       │
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

**System Prompt** (Persistent):
```markdown
# Role
Expert fiction writer specializing in immersive narratives

# Core Principles
1. Consent: All characters are consenting adults (18+)
2. Quality: Plot development, character growth, emotional resonance
3. Safety: Follow platform guidelines

# Output Format
- Length: 1000-2000 words
- Structure: Dialogue, narration, introspection
- Language: Chinese (default) or English
```

**Scenario Prompt** (Per-generation):
```markdown
# Context
Genre: [Romance | Fantasy | Historical]
Setting: [Time, location, mood]
Characters: [Name, age, role, traits]

# Plot
1. Opening scene
2. Rising action
3. Climax
4. Resolution

# Style
- Descriptive: Sensory-rich, metaphorical
- Dialogue: Natural, character-specific
- Tone: [Hopeful | Melancholic | Passionate]

# Chapter Goal
[Single-sentence objective]
```

### 6.3 Safety & Quality Assurance

**Pre-Generation Checks**:
- User age verified (18+)
- Account in good standing (not flagged)
- Rate limit not exceeded (3 generations/day for free users)

**Post-Generation Validation**:
```typescript
interface SafetyCheck {
  hasMinors: boolean           // Block if true
  nonConsensual: boolean       // Block if true
  excessiveViolence: boolean   // Block if true
  realPersonReferences: boolean // Block if true
  qualityScore: number         // Must be > 0.6
}

async function validateGeneratedContent(content: string): Promise<SafetyCheck> {
  // 1. Keyword-based filtering
  const keywordCheck = await checkBlockedKeywords(content)

  // 2. LLM-based safety classification
  const llmCheck = await classifySafety(content)

  // 3. Quality scoring (coherence, engagement)
  const qualityScore = await assessQuality(content)

  return {
    hasMinors: llmCheck.hasMinors,
    nonConsensual: llmCheck.nonConsensual,
    excessiveViolence: keywordCheck.violenceCount > 3,
    realPersonReferences: keywordCheck.hasRealNames,
    qualityScore: qualityScore.overall
  }
}
```

**Fallback Behavior**:
- If safety check fails: Silently retry with different prompt
- If 3 retries fail: Notify user "Unable to generate. Try again later."
- If quality score < 0.6: Offer user option to accept or regenerate

---

## 7. Offline & Sync Strategy

### 7.1 Mobile Offline Support

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
```swift
// iOS (Core Data + CloudKit)
class SyncManager {
  func syncReadingProgress() async {
    let localProgress = fetchLocalProgress()
    let remoteProgress = await API.getProgress()

    let merged = mergeProgress(local: localProgress, remote: remoteProgress)
    await API.uploadProgress(merged)
    saveLocal(merged)
  }
}
```

```kotlin
// Android (Room + WorkManager)
class SyncWorker(context: Context, workerParams: WorkerParameters) : CoroutineWorker(context, workerParams) {
  override suspend fun doWork(): Result {
    val localProgress = database.progressDao().getAll()
    val remoteProgress = api.getProgress()

    val merged = mergeProgress(localProgress, remoteProgress)
    api.uploadProgress(merged)
    database.progressDao().insertAll(merged)

    return Result.success()
  }
}
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
│  Client-Side (Core Data/Room)       │
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
```typescript
// Client-side
async function verifyAge(dob: Date): Promise<boolean> {
  const age = calculateAge(dob)
  if (age < 18) {
    showBlockScreen("You must be 18+ to use this app")
    return false
  }

  // Send to server
  const result = await API.post('/auth/age-verify', { dob })

  if (result.success) {
    storeVerificationToken(result.token)
    enableAppAccess()
  }

  return result.success
}

// Server-side
async function handleAgeVerification(dob: Date, deviceId: string) {
  const age = calculateAge(dob)
  if (age < 18) {
    throw new Error('Age verification failed')
  }

  // Create user account (device-based)
  const user = await createOrUpdateUser(deviceId, dob)

  // Generate session token
  const token = generateSessionToken(user.id)

  return { success: true, token }
}
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
| **iOS** | Swift + SwiftUI | Native performance, modern UI, Apple ecosystem integration |
| **Android** | Kotlin + Jetpack Compose | Native performance, modern UI, Material Design 3 |
| **Web** | Next.js 14 + shadcn/ui | Fast development, SEO-friendly, modern DX |
| **Backend** | Node.js + Express + TypeScript | Solo developer efficiency, rich ecosystem |
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
│  │  │ Node.js    │  │ Redis        │        │ │
│  │  │ API        │  │ (Cache)      │        │ │
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
