# AI Generation System Design

## 1. Prompt Architecture

### 1.1 System Prompt
TODO: 平台不可变规则

# 角色定义
你是一位专业的成人小说作家，擅长创作引人入胜的虚构故事内容。你将严格遵循安全和质量指南，打造沉浸式的叙事体验。

# 核心原则
1. **知情同意**: 所有描绘的互动必须涉及明确同意的成年人（18岁以上）
2. **尊重与自主**: 角色保持自主权，绝不被强迫
3. **叙事质量**: 专注于情节发展、角色成长和情感共鸣
4. **读者安全**: 避免宣扬非自愿、暴力或非法活动的内容

# 安全边界（不可协商）
- ❌ 禁止涉及未成年人的内容
- ❌ 禁止非自愿场景
- ❌ 禁止过度暴力或血腥
- ❌ 禁止提及真实人物（仅使用虚构角色）
- ❌ 禁止平台政策规定的违禁内容

# 写作风格
- **引人入胜**: 创造生动、感官丰富的描述
- **节奏把控**: 平衡对话、动作和内心独白
- **角色声音**: 为每个角色赋予独特的语言风格和视角
- **情感深度**: 探索动机、欲望和冲突

# 输出格式
- 使用要求的语言（中文/英文）写作
- 章节长度：1000-2000字
- 使用 markdown 格式进行结构化
- 包含对话、叙述和内心独白

# 质量检查
输出前请确认：
- [ ] 所有角色均为同意的成年人
- [ ] 内容符合安全指南
- [ ] 叙事逻辑流畅
- [ ] 语言富有吸引力且语法正确


### 1.2 Scenario Prompt

# 故事背景

## 类型
现代都市情感 / 成人浪漫

## 场景设定
上海，高端商务区，雨夜，私人画廊

## 主要人物
- **林雨萱（28岁）**: 独立策展人，外表优雅但内心渴望冒险
- **陈默（32岁）**: 神秘收藏家，深藏不露，充满魅力

## 情节大纲
雨萱正在为画展做最后准备，陈默在闭馆后突然造访。两人在艺术品的陪伴下展开对话。 tensions在讨论画作时悄然升温。本章聚焦于他们共同欣赏一幅名为《雨夜》的油画时，艺术与欲望交织的时刻。

## 基调
- 优雅而性感
- 暧昧的张力
- 成人之间的博弈
- 情欲与艺术的共鸣

## 风格偏好
- 注重感官描写（雨声、香水味、体温）
- 心理描写展现内心渴望
- 对话含蓄但充满暗示
- 男女势均力敌的互动模式

## 章节目标
撰写两人首次亲密接触的场景。通过欣赏艺术品的讨论，逐渐升温氛围。以一场意外但自愿的吻结束，留下悬念。

## 篇幅：1500字
## 语言：中文

# 故事背景

## 类型
古代宫廷 / 权谋情色

## 场景设定
架空王朝，皇宫，深夜，御书房

## 主要人物
- **苏清婉（20岁）**: 新入宫的女官，聪明谨慎，却难逃宿命
- **萧景宸（27岁）**: 年轻帝王，外表冷酷但内心渴望理解

## 情节大纲
清婉被召至御书房整理奏折。景宸已连续三日未眠，疲惫中卸下帝王面具。两人在处理政务时产生超越君臣的默契。本章聚焦于深夜独处时，权力与欲望交织的危险吸引力。

## 基调
- 压抑而炽热
- 权力的不对等 vs 情感的平等
- 宫廷禁忌
- 孤独者的相互慰藉

## 风格偏好
- 古风语言但不晦涩
- 描写宫廷的奢华与冰冷
- 心理描写展现身份的矛盾
- 尊重历史背景下的女性意识

## 章节目标
撰写两人在深夜独处时情感爆发的场景。通过奏折内容的讨论，逐渐揭示彼此的真实想法。以一个打破君臣界限的拥抱结束，暗示未来的危险关系。

## 篇幅：1800字
## 语言：中文


### 1.3 User Input

No user input required. AI generates content based on tag selection and prompt.

---

## 2. Multimodal Generation Strategy

### 2.1 Text Generation (Primary)

**Method**: Streaming via Server-Sent Events (SSE)

**Flow**:
1. User requests chapter generation
2. Backend sends prompt to LLM with `stream: true`
3. Backend forwards chunks to frontend via SSE
4. Frontend displays "typewriter" effect in real-time
5. Complete text saved to database

**Benefits**:
- Immediate user feedback (reduces perceived latency)
- Can interrupt generation mid-stream
- Better UX than waiting 30-60 seconds

### 2.2 Image Generation (Illustrations)

**Strategy**: On-demand generation during/after text creation

**Timing**:
- Option A: Generate after chapter completion (safer)
- Option B: Generate key scene images during text flow (more interactive)

**API**: OpenAI DALL-E 3 / Stability AI

**Storage**: R2 (Cloudflare) with CDN delivery

**Prompt Construction**:
```typescript
// Extract key scenes from generated text
const scenePrompt = `
  Based on this chapter excerpt:
  ${textExcerpt}

  Generate an illustration capturing the mood and key elements.
  Style: Anime/Manga/Realistic (user preference)
  Safety: Explicit content filtering applied
`
```

### 2.3 Voice Generation (Text-to-Speech) 🎯

**Critical Design Decision**: Voice is for **playback only**, not user input

**User Interaction Model**:
- User reads text chapter
- Clicks "🔊 Listen" button or individual paragraph/sentence
- Audio plays (browser-based or pre-generated)
- Third-person perspective only (no voice input from user)

#### Implementation Options

| Option | Description | Cost | Quality | Complexity | Recommendation |
|--------|-------------|------|---------|------------|----------------|
| **A. Browser TTS** | Web Speech API | FREE | ⭐⭐⭐ | Low | ✅ **MVP Choice** |
| **B. Pre-generated** | Generate MP3s upfront | $$ | ⭐⭐⭐⭐⭐ | Medium | Phase 2 |
| **C. On-demand** | Generate when clicked | $$$$ | ⭐⭐⭐⭐⭐ | High | Not recommended |

#### Option A: Browser Web Speech API (MVP)

```typescript
// Frontend - No backend needed
const synth = window.speechSynthesis

function playText(text: string, lang: string = 'zh-CN') {
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = lang
  utterance.rate = 1.0 // User adjustable (0.5x - 2x)
  utterance.pitch = 1.0
  synth.speak(utterance)
}

// UI: Click paragraph to play
<p onClick={() => playText(paragraphText)}>
  {paragraphText}
  <button>🔊</button>
</p>
```

**Pros**:
- Zero backend cost
- Instant playback
- No API latency
- User can adjust speed/pitch
- Works offline

**Cons**:
- Voice quality depends on browser/OS
- Limited voice options
- No custom voice training
- Inconsistent across devices

**Good for MVP** because:
- Validates demand for voice feature
- Zero infrastructure cost
- Immediate implementation

#### Option B: Pre-generated Audio Files (Phase 2)

```typescript
// Backend - Generate when chapter is created
async function generateAudio(chapterId: string, text: string) {
  const audio = await openai.audio.speech.create({
    model: 'tts-1',
    voice: 'alloy', // or 'nova', 'onyx', 'shimmer'
    input: text
  })

  const buffer = Buffer.from(await audio.arrayBuffer())
  const filename = `audio/${chapterId}.mp3`

  // Upload to R2
  await r2.put(filename, buffer)

  // Save URL to database
  return `${R2_PUBLIC_URL}/${filename}`
}

// Frontend - Play pre-generated audio
<audio controls src={chapter.audioUrl} />
```

**Pros**:
- High-quality AI voices
- Consistent experience across devices
- Can cache/CDN for fast playback
- Can use custom voice clones (future)

**Cons**:
- $15/1M characters (OpenAI TTS)
- Storage costs (R2: ~$0.015/GB)
- Generation latency (10-30s for long chapters)
- Need to regenerate if text is edited

**Cost Estimate** (10,000 word chapter ≈ 50,000 chars):
- 10 chapters = 500,000 chars = $7.50/month
- 100 chapters = 5,000,000 chars = $75/month

**Migration Path**:
1. Start with browser TTS (MVP)
2. Track which chapters are played most
3. Pre-generate audio for top 20% content
4. Offer premium users "high-quality voice" upgrade


---

## 3. Generation Order & Workflow

### 3.1 MVP Workflow (Browser TTS)

```
User Request "Generate Chapter 2"
    │
    ▼
┌─────────────────────┐
│  Text Generation    │ ← SSE Stream (real-time)
│  (GPT-4/Claude)     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Save to DB         │
│  (PostgreSQL)       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Key Scene Extract  │
│  (for illustrations)│
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Image Generation   │ ← Async (non-blocking)
│  (DALL-E 3)         │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Upload to R2 + CDN │
└─────────────────────┘
          │
          ▼
    User can:
    - Read text
    - Click 🔊 (browser TTS)
    - View illustrations
```

### 3.2 Phase 2 Workflow (Pre-generated Audio)

```
...after text generation...
          │
          ▼
┌─────────────────────┐
│  Audio Generation   │ ← Background job
│  (OpenAI TTS)       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Upload MP3 to R2   │
│  + CDN delivery     │
└─────────────────────┘
```

---

## 4. Model Strategy

### 4.1 Migration Path: Open Source LLM

**Status**: Preparing for migration from OpenAI API to self-hosted models

**Timeline**:
- **Phase 1 (MVP)**: OpenAI GPT-4o mini for rapid validation
- **Phase 2 (Month 2)**: Deploy open-source models (Qwen2.5 14B, Llama 3.1 8B)
- **Phase 3 (Month 4+)**: Fine-tuned models on user-approved content

**See**: [ADR-0002: LLM Strategy](../decisions/ADR-0002-llm-strategy.md) for detailed decision

### 4.2 Model-Agnostic Prompt Design

**Key Principle**: Prompts must work across GPT-4, Qwen, Llama, Mistral

**Universal Requirements**:
1. ✅ **Structured markdown format** (all LLMs understand #, ##, -)
2. ✅ **Explicit examples** (few-shot learning improves all models)
3. ✅ **Clear role definition** (don't rely on model "intuition")
4. ✅ **Concrete output specs** (word count, format, language)
5. ✅ **Explicit safety rules** (different models have different training)

**See**: [ADR-0003: Prompt Design Standards](../decisions/ADR-0003-prompt-design-standards.md) for complete guide

### 4.3 Model-Specific Considerations

#### For OpenAI GPT-4o mini (Current)
- ✅ Highest quality (baseline for comparison)
- ✅ Best instruction-following
- ❌ Expensive at scale ($0.15/1M tokens)
- ❌ ToS violation risk (adult content)

#### For Qwen2.5 14B (Primary Target)
- ✅ Excellent Chinese generation
- ✅ Strong safety alignment
- ✅ 10x cheaper than OpenAI
- ⚠️ Slightly lower quality (acceptable for MVP)
- **Best for**: Chinese content, romance genres

#### For Llama 3.1 8B (Alternative)
- ✅ Good English generation
- ✅ Efficient inference (8B parameters)
- ✅ Large community support
- ⚠️ Weaker Chinese performance
- **Best for**: English content, experimental features

#### For ChatGLM4 9B (Bilingual)
- ✅ Optimized for dialogue
- ✅ Good Chinese-English mixing
- ⚠️ Commercial license unclear
- **Best for**: Interactive features, dialogue-heavy scenes

### 4.4 Evaluation Framework

Before deploying open-source models:

```typescript
interface ModelEvaluation {
  model: string
  testPrompts: number // Test with 100+ diverse prompts
  metrics: {
    coherence: number // Logical flow (0-1)
    safety: boolean // Passes safety guidelines
    engagement: number // User ratings
    styleMatch: number // Matches desired style (0-1)
  }
  baseline: string // Compare to GPT-4 output
  decision: 'deploy' | 'tune' | 'reject'
}

// Evaluation process
1. Generate 100 test chapters with each model
2. Human evaluation (blind test)
3. User rating comparison (A/B test)
4. Deploy if ≥ 85% of GPT-4 quality
```

### 4.5 Version Tracking

Every generated content tracks model version:

```sql
CREATE TABLE generated_content (
  id UUID PRIMARY KEY,
  model_name VARCHAR(50),      -- 'gpt-4o-mini', 'qwen2.5-14b', etc.
  model_version VARCHAR(20),   -- '2024-01-15', 'v1.0-finetuned'
  prompt_template_id UUID,     -- Which prompt template was used
  generated_at TIMESTAMP,
  content TEXT,
  -- ... other fields
);

-- Benefits:
-- 1. Compare model performance over time
-- 2. Re-generate old content with better models
-- 3. A/B test different models
-- 4. Debug quality issues
```

### 4.6 Fallback Strategy

**Reliability is critical**: Never serve generation errors to users

```typescript
async function generateWithFallback(prompt: string) {
  const models = [
    { name: 'qwen2.5-14b', priority: 1 },
    { name: 'llama3.1-8b', priority: 2 },
    { name: 'gpt-4o-mini', priority: 3 } // Emergency fallback
  ]

  for (const model of models) {
    try {
      const result = await generate(model.name, prompt)
      // Quality check
      if (isValidOutput(result)) {
        return { content: result, model: model.name }
      }
    } catch (error) {
      logger.warn(`Model ${model.name} failed:`, error)
      continue // Try next model
    }
  }

  throw new Error('All models failed')
}

// Monitoring
// - Track fallback rate per model
// - Alert if > 5% requests use fallback
// - Auto-disable unhealthy models
```

### 4.7 Cost Optimization

| Model | Hardware | Monthly Cost | Generations |
|-------|----------|--------------|-------------|
| GPT-4o mini | None | $200 | 1,000 |
| Qwen2.5 14B | RTX 4090 | $50 (amortized) | 10,000 |
| Fine-tuned 8B | RTX 4090 | $30 | 15,000 |

**Break-even**: ~500 generations/month with self-hosted model

**See ADR-0002** for detailed cost analysis

---

## 5. Prompt Testing & Iteration

### 5.1 Testing Framework

```typescript
interface PromptTest {
  template: string // Prompt template
  variations: string[] // Different prompt versions
  testCases: TestCase[]
  models: string[] // Test across multiple LLMs
}

async function testPrompt(test: PromptTest) {
  const results = []

  for (const model of test.models) {
    for (const variation of test.variations) {
      for (const testCase of test.testCases) {
        const output = await generate(model, variation + testCase.input)

        results.push({
          model,
          variation,
          testCase: testCase.name,
          output,
          scores: await evaluate(output, testCase.expected)
        })
      }
    }
  }

  return analyzeResults(results)
}

// Metrics
// - Coherence: Does story make sense?
// - Safety: Does it follow guidelines?
// - Style: Does it match desired tone?
// - Engagement: Would users want to read more?
```

### 5.2 Iteration Process

```
1. Design prompt template
   ↓
2. Test with GPT-4 (baseline quality)
   ↓
3. Test with target model (Qwen/Llama)
   ↓
4. Compare quality metrics
   ↓
5a. If < 85% baseline → Refine prompt → Go to step 2
   ↓
5b. If ≥ 85% baseline → Deploy at 10% traffic
   ↓
6. Monitor user feedback
   ↓
7. Gradually ramp to 100% traffic
```

### 5.3 A/B Testing

```typescript
// Deploy two prompt versions
const promptVariants = {
  A: 'current-template-v1',
  B: 'improved-template-v2'
}

// Route 10% to B, 90% to A
const variant = Math.random() < 0.1 ? 'B' : 'A'

const content = await generate(promptVariants[variant], userContext)

// Track metrics
track({
  variant,
  userId: user.id,
  readThroughRate: calculateReadThrough(),
  userRating: getUserRating(),
  safetyFlags: countSafetyViolations()
})

// After 1000 generations, compare:
// - Does B have higher user ratings?
// - Does B have fewer safety flags?
// - If yes → Promote B to 100%
```

---

## 6. Future Enhancements

### 6.1 Dynamic Prompt Optimization

```typescript
// Learn from user feedback
async function optimizePrompt(userFeedback: UserFeedback[]) {
  const successfulExamples = userFeedback
    .filter(f => f.rating >= 4.5)
    .map(f => f.generatedContent)

  const poorExamples = userFeedback
    .filter(f => f.rating < 3.0)
    .map(f => f.generatedContent)

  // Use LLM to analyze what works
  const analysis = await analyze('gpt-4o-mini', `
    Successful examples:
    ${successfulExamples.slice(0, 5).join('\n')}

    Poor examples:
    ${poorExamples.slice(0, 5).join('\n')}

    What patterns distinguish successful from poor examples?
    Suggest prompt improvements.
  `)

  return generateImprovedPrompt(analysis)
}
```

### 6.2 Fine-Tuning Data Collection

```sql
-- Track high-quality generations for fine-tuning
CREATE TABLE fine_tuning_data (
  id UUID PRIMARY KEY,
  content_id UUID REFERENCES generated_content(id),
  user_rating DECIMAL(2,1), -- 4.5+ stars
  read_through_rate DECIMAL(3,2), -- 80%+ completion
  safety_passed BOOLEAN,
  selected_for_fine_tuning BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP
);

-- Auto-select best content
UPDATE fine_tuning_data
SET selected_for_fine_tuning = TRUE
WHERE user_rating >= 4.5
  AND read_through_rate >= 0.80
  AND safety_passed = TRUE
  AND created_at > NOW() - INTERVAL '3 months'
LIMIT 10000;
```

**Target**: Collect 10,000 high-quality examples before fine-tuning

---

## Related Documents

- **ADR-0002**: [LLM Strategy](../decisions/ADR-0002-llm-strategy.md) - Open source vs closed source decision
- **ADR-0003**: [Prompt Design Standards](../decisions/ADR-0003-prompt-design-standards.md) - Model-agnostic prompt guidelines
- **Trust & Safety**: [Content Moderation](../safety/Trust_and_Safety.md) - Safety guidelines and enforcement
