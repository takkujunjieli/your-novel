# ADR-XXXX: [[Decision Title]]

## Status
[[Proposed | Accepted | Superseded | Deprecated]]

## Date
YYYY-MM-DD

## Context
TODO: 描述当时的背景与约束条件  
- 团队规模  
- 产品阶段  
- 法律 / 合规 / 成本 / 时间限制  

Example:
At the MVP stage, the team consists of a single engineer aiming to validate product-market fit quickly while minimizing operational complexity.

---

## Decision
TODO: 用一句话明确「我们决定做什么」

Example:
We will use a monolithic backend architecture with modular internal components.

---

## Rationale
TODO: 为什么做这个选择（核心）

Example:
- Faster iteration speed
- Lower operational overhead
- Easier debugging for a solo developer

---

## Alternatives Considered
TODO: 列出 1–3 个备选方案及为什么没选

Example:
- Microservices: too complex for MVP
- Serverless-only: limited control over AI workflows

---

## Consequences
TODO: 这个决策带来的后果（好 & 坏）

Example:
Pros:
- Simpler deployment
- Easier onboarding

Cons:
- Requires refactoring when scaling
- Potential tight coupling

---

## Follow-ups
TODO: 未来可能需要 revisit 的点

Example:
- Re-evaluate architecture when daily active users exceed X
