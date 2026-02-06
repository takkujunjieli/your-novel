# Data Model & Schema Design

## 1. User

TODO: 用户模型字段

Example:
- user_id
- age_verified (bool)
- region_code
- preferences (json)

---

## 2. Content

TODO: 内容对象定义

Example:
- content_id
- content_type (generated / edited)
- tags
- visibility
- created_at

---

## 3. Generation Record

TODO: 每一次 AI 生成的记录

Example:
- generation_id
- content_id
- model_version
- prompt_hash
- safety_flags
- cost_estimate

---

## 4. Relationships

TODO: 表之间的关系说明

Example:
- User 1 → N Content
- Content 1 → 1 GenerationRecord
