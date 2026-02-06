# ADR-0001: Initial System Architecture

## Status
Accepted

## Date
[[2026-02-05]]

## Context
The project is at an early MVP stage with the following constraints:

- Team size: solo founder / single engineer
- Goal: validate user demand for an AI-native adult content platform
- Time constraint: <= 2 weeks
- Cost constraint: less than $100 per month
- Legal and compliance considerations require clear system boundaries and auditability

At this stage, the system is expected to support:
- Content reading
- On-demand AI content generation
- Basic trust and safety enforcement

---

## Decision
We will implement a **modular monolithic architecture** with a **hybrid API layer** (REST + real-time streaming) organized around **domain-driven design (DDD)** boundaries.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                   │
│                  - Static + SSR + CSR                    │
└─────────────────────────────────────────────────────────┘
                            │
                    ┌───────┴───────┐
                    ▼               ▼
            ┌──────────────┐  ┌─────────────────┐
            │   REST API   │  │     SSE (Stream) │
            │   (Express)  │  │  (Real-time)     │
            └──────┬───────┘  └────────┬────────┘
                   │                   │
                   └────────┬──────────┘
                            ▼
              ┌─────────────────────────────┐
              │     Service Layer (DDD)     │
              ├─────────────┬───────────────┤
              │             │               │
        ┌─────▼─────┐ ┌────▼────┐  ┌──────▼──────┐
        │   Content │ │  AI/Gen │  │    User     │
        │  Service  │ │ Service │  │  Service    │
        └───────────┘ └─────────┘  └─────────────┘
              │             │               │
              └────────┬────┴───────────────┘
                       ▼
         ┌─────────────────────────────┐
         │   Infrastructure Layer      │
         ├───────────┬─────────────────┤
         │           │                 │
    ┌────▼────┐ ┌───▼────┐  ┌─────────▼───┐
    │  SQL DB │ │ Vector │  │ Object Store│
    │(User/   │ │  DB    │  │ (Media/CDN) │
    │ Content)│ │(Memory)│  │             │
    └─────────┘ └────────┘  └─────────────┘
```

### Key Architectural Decisions

#### 1. Modular Monolith with Domain Boundaries
- **Why**: Solo developer needs operational simplicity, but future-proof for microservices extraction
- **Domains**: Content, AI Generation, User/Auth, Media, Memory
- **Each domain** has its own models, services, and repository interfaces

#### 2. Hybrid API Layer (REST + SSE Streaming)
- **REST**: CRUD operations (user management, content library, billing)
- **SSE (Server-Sent Events)**: AI text streaming for real-time user feedback
- **Voice Playback**: Browser-based Web Speech API (MVP) or pre-generated MP3s via CDN (Phase 2)
- **Why**: SSE is simpler than WebSocket for unidirectional streaming (server → client); sufficient for current requirements

#### 3. Multi-Model Data Strategy
- **PostgreSQL**: Transactional data (users, content metadata, billing)
- **Vector DB (pgvector)**: AI memory module, content recommendation, semantic search
- **Object Storage (S3/R2)**: Media files (images, audio) with CDN
- **Redis**: Session management, rate limiting, caching

#### 4. Frontend: Next.js with App Router
- **SSR**: SEO-friendly content discovery pages
- **CSR**: Interactive reading/generation interface
- **ISR**: Semi-static pages for popular content

---

## Rationale
This decision is driven by the PRD requirements and future scalability needs:

### 1. Modular Monolith for Solo Developer Efficiency
- **Operational Simplicity**: Single deployment, unified logging, easier debugging
- **Domain Boundaries**: DDD modules map directly to business domains (Content, AI, User)
- **Future Extraction**: Each domain can become a microservice when needed (e.g., when AI generation becomes bottleneck)

### 2. Hybrid API for AI-Native Experience
- **Streaming is Critical**: AI text generation requires real-time delivery
- **User Expectation**: Modern AI apps (ChatGPT, Claude) set streaming as standard
- **SSE (Server-Sent Events)**: Enables chapter-by-chapter text streaming (单向：服务器 → 客户端)
- **Voice Playback**: Browser-based TTS (MVP) or pre-generated audio files (Phase 2) - no WebSocket needed
- **Future WebSocket**: Only needed if we add real-time chat, collaboration, or voice input (user→server)

### 3. Multi-Model Data for Diverse Requirements
- **PostgreSQL**: Proven reliability for user data, transactions, billing
- **pgvector**: Native PostgreSQL extension for vector search (no separate vector DB needed for MVP)
- **Object Storage**: Cost-effective media storage with built-in CDN (R2 is free for egress)
- **Redis**: Essential for rate limiting (API cost control) and session caching

### 4. Next.js for Full-Stack Efficiency
- **Single Codebase**: Solo developer can handle both frontend and backend logic
- **Built-in Optimization**: Image optimization, font optimization, automatic code splitting
- **Flexible Rendering**: SSR for discovery (SEO), CSR for app-like experience, ISR for content pages

### 5. Cost Optimization (< $100/month target)
- **Modular Monolith**: Reduced infrastructure overhead vs microservices
- **R2 + CDN**: Free egress saves ~$90/month vs S3
- **pgvector**: No separate vector DB subscription ($150+/month savings)
- **Serverful Architecture**: Predictable costs vs serverless cold starts

---

## Alternatives Considered

### 1. Microservices Architecture (Kubernetes/Docker Compose)
**Rejected** because:
- Operational overhead for solo developer (multiple deployments, service mesh, inter-service debugging)
- Premature optimization: PRD states MVP validation phase, not proven scale
- Cost overhead: Multiple container instances exceed $100/month budget
- **However**: Domain boundaries are preserved to allow future extraction

### 2. Fully Serverless (Vercel/Netlify + Lambda Functions)
**Rejected** because:
- **Cold starts**: AI generation workflows (30-60s) would timeout or incur high costs
- **Streaming difficulty**: Serverless functions have timeout limits that make SSE streaming unreliable
- **Cost unpredictability**: AI API calls + serverless execution time = billing surprises
- **Debugging complexity**: Harder to trace AI generation failures across function boundaries

### 3. Frontend-only + Direct AI API Calls
**Rejected** because:
- **Security**: API keys exposed in frontend (major vulnerability)
- **No cost control**: Users could abuse AI APIs directly
- **No audit trail**: Can't track generation history for safety/compliance
- **Limited context**: Can't implement sophisticated prompt chaining or memory management

### 4. WebSocket instead of SSE
**Rejected for MVP** because:
- **Overkill**: Voice is playback-only (browser TTS or static MP3s), not bidirectional
- **Complexity**: WebSocket connection management, heartbeats, reconnection logic
- **SSE is Sufficient**: Unidirectional streaming (server → client) is all we need for text generation
- **Future Path**: Can upgrade to WebSocket if we add real-time chat, voice input (user → server), or collaborative features

### 5. Dedicated Vector Database (Pinecone, Weaviate)
**Rejected** because:
- **Cost**: $70+/month for basic tier (70% of entire budget)
- **Overkill for MVP**: pgvector handles millions of vectors efficiently
- **Added complexity**: Another service to manage and monitor
- **Future path**: Can migrate to dedicated vector DB when scale requires it

---

## Consequences

### Positive
- **Fast Iteration**: Single codebase enables rapid feature development (2-week MVP target achievable)
- **Cost Predictability**: Fixed infrastructure costs (VPS + R2 + DB) fit $100/month budget
- **Operational Simplicity**: One deployment, one monitoring setup, one log stream
- **Domain Flexibility**: DDD boundaries allow extracting AI service as bottleneck emerges
- **Modern UX**: SSE streaming provides ChatGPT-like text generation experience
- **Zero-Cost Voice**: Browser TTS enables voice playback without backend infrastructure (MVP)
- **Future-Proof**: Architecture supports planned features (social, recommendations, creator tools, high-quality TTS)
- **Simplified Compliance**: Centralized logging for age verification, content moderation, billing

### Negative
- **Vertical Scaling Limit**: Single server has CPU/memory limits for concurrent AI generation
- **Domain Coupling Risk**: Poor discipline could blur boundaries between services
- **Single Point of Failure**: Backend outage affects all functionality (mitigated by health checks)
- **Deployment Downtime**: Blue-green deployments needed for zero-downtime (adds complexity)
- **Database Contention**: Single PostgreSQL for transactions + vector queries (monitoring required)

### Technical Debt Risks
- AI generation latency could block web server (need job queue if >3s average)
- SSE connection management complexity increases with concurrent users
- Browser TTS voice quality varies across devices/browsers
- Vector search performance degrades without proper indexing strategy

---

## Follow-ups

This architecture should evolve when the following **thresholds** are reached:

### Phase 2: Scale Preparation (500-1000 DAU)

**Trigger**: Any ONE of:
- 500+ daily active users
- Average AI generation time > 5 seconds
- Database size > 10GB
- Monthly infrastructure cost > $150

**Actions**:
1. Extract AI generation to background job queue (BullMQ)
2. Add Redis caching layer for frequently accessed content
3. Implement database read replicas for content queries
4. Add CDN caching for static assets
5. Set up monitoring (Datadog/New Relic) for performance baselines

### Phase 3: Service Extraction (2000-5000 DAU)

**Trigger**: Any ONE of:
- 2000+ daily active users
- AI generation requests > 100/minute
- Database CPU consistently > 70%
- SSE connections > 500 concurrent

**Actions**:
1. **Extract AI Service**: Separate microservice for generation (independent scaling)
2. **Dedicated Vector DB**: Migrate to Pinecone/Qdrant for better performance
3. **Message Queue**: RabbitMQ/Redis PubSub for async processing
4. **API Gateway**: Kong/AWS API Gateway for rate limiting and routing
5. **Database Sharding**: Separate read/write DBs, partition by user_id

### Phase 4: Cloud Migration (10000+ DAU)

**Trigger**: Any ONE of:
- 10000+ daily active users
- Multi-region deployment requirement
- Compliance requirements (SOC2, HIPAA)
- $2000+ monthly infrastructure spend

**Actions**:
1. **Kubernetes**: Container orchestration for auto-scaling
2. **Microservices**: Full extraction (User, Content, AI, Media, Notification services)
3. **Event-Driven**: Kafka/RabbitMQ for service communication
4. **Multi-region**: CDN + regional database replicas
5. **Dedicated DevOps**: CI/CD pipeline, automated testing, staging environment

## Migration Path to Microservices

When service extraction is needed, follow this order:

1. **AI Generation Service** (First to extract)
   - Compute-intensive, independent scaling needs
   - Clear domain boundary (text/image/audio generation)

2. **Media Service** (Second)
   - High storage/CDN bandwidth
   - Simple CRUD operations

3. **Content Service** (Third)
   - High read volume, caching benefits
   - Business logic complexity

4. **User/Auth Service** (Last)
   - Critical path, extract when team has DevOps capacity

## Performance Metrics to Monitor

Track these metrics weekly to anticipate scaling needs:

| Metric | Target | Threshold |
|--------|--------|-----------|
| AI generation latency (p95) | < 3s | > 5s |
| API response time (p95) | < 200ms | > 500ms |
| Database query time (p95) | < 50ms | > 100ms |
| SSE concurrent connections | < 500 | > 1000 |
| Error rate | < 0.1% | > 1% |
| Infrastructure cost/month | < $100 | > $150 |
