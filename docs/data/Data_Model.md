# Data Model & Schema Design

## 1. PostgreSQL Schema (Primary Database)

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

## 2. Redis Caching Structure

- **Session storage (30 days)**: `session:{device_id}` -> `session_token`
- **Rate limiting**: `rate:generate:{user_id}`
- **Content caching (5 minutes)**: `cache:trending` -> `json.dumps(content)`

## 3. Object Storage (R2 + CDN)

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
