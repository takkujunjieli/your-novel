# System Architecture Design

## 1. High-level Overview

TODO: 用一句话描述系统形态  
Example:
> A web-based AI content platform with a monolithic backend and modular services.

---

## 2. Core Components

### 2.1 Frontend
TODO

Example:
- React / Next.js
- Handles user input, content display

### 2.2 Backend API
TODO

Example:
- REST API
- Auth, content retrieval, generation requests

### 2.3 AI Generation Service
TODO

Example:
- Prompt assembly
- Model invocation
- Safety filtering

### 2.4 Data Storage
TODO

Example:
- PostgreSQL for metadata
- Object storage for content

---

## 3. Request Flow

TODO: 描述一次生成请求的完整链路

Example:
User → Frontend → Backend API → AI Service → Safety Check → Storage → Response

---

## 4. Scalability & Evolution

TODO: 哪些模块未来可能拆分

Example:
- AI service separated for cost control
- Moderation pipeline async
