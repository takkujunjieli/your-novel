# Product Requirements Document (PRD)

## 1. Background & Problem Statement

### 1.1 Product Vision
AI原生的成人小说阅读和创作平台: 用户可以阅读和创作成人小说，平台使用AI生成内容，用户可以对内容进行傻瓜式个性化定制。
兼顾了: 1. 互动性阅读 2. 创作/盈利 3. 社交性

### 1.2 Target Users
3 类核心用户

- 纯阅读用户: read-only，只想快速获取成人内容小说
- 深度使用者: 有付费意愿去解锁定制化AI生成内容和互动内容, 对阅读体验有较高要求
- 盈利用户: 有创作需求，希望通过平台创作和盈利

### 1.3 User Pain Points

- Existing platforms require complex prompts
- Content moderation is inconsistent
- Hard to find content matching niche preferences
- 缺乏中文原生支持

---

## 2. Core User Journeys

### Journey 1: 纯阅读用户


1. 通过年龄验证, 选择profile标签或直接进入
2. 选择小说(两种推荐机制混合:最流行的, 匹配标签的)
3. 阅读小说

### Journey 2: 深度使用者


0. (默认已经完成: 年龄验证, profile标签和丰富的历史记录, 包括阅读记录, 和AI相关的记忆模块记录)
1. 进入AI记忆模块, 找到自己上一次阅读的进度
2. 生成下一章节
3. 阅读文字,插图,进行语音互动
4. 对不满意的内容微调
5. 循环3-4

### Journey 3: 盈利用户

TODO: 后续需要为其开发创作工具, User Journeys待补充

---

## 3. Feature Scope

### P0 (Must-have for MVP)

- 年龄验证
- 内容阅读
- AI生成(文字+插图+语音)

### P1 (Nice to have)

- 章节微调
- 用户内容库
- 记忆模块

### P2 (Explicitly out of scope)

- 社交功能
- 公开评论
- 推荐算法