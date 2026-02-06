# ADR-0002: LLM Strategy - Open Source vs Closed Source

## Status
Proposed

## Date
2026-02-05

## Context
The platform requires AI content generation at scale. Key considerations:

- **Cost**: OpenAI API would cost $200-500/month for 1000 daily generations
- **Privacy**: Adult content + user data cannot be sent to third-party APIs (GDPR/compliance)
- **Customization**: Need fine-tuning for specific content styles and quality standards
- **Control**: Must ensure content safety and adhere to platform policies
- **Reliability**: Cannot depend on external service availability or policy changes

## Decision

### Phase 1: MVP (Weeks 1-2)
**Use OpenAI API for rapid validation**

- **Model**: GPT-4o mini ($0.15/1M input tokens)
- **Why**: Fastest way to validate product-market fit
- **Cost estimate**: ~$50/month for 500 users
- **Exit criterion**: 100 confirmed users or clear product-market fit signal

### Phase 2: Migration to Open Source (Month 2-3)
**Self-host open-source LLM with gradual rollout**

| Candidate Model | Parameters | Context | Strengths | Weaknesses |
|----------------|-----------|---------|-----------|------------|
| **Llama 3.1 8B** | 8B | 128K | Strong reasoning, good English | Weaker Chinese |
| **Qwen2.5 14B** | 14B | 32K | Excellent Chinese, fast | Higher VRAM need |
| **Mistral 7B** | 7B | 32K | Good balance, efficient | Less fine-tuning data |
| **ChatGLM4 9B** | 9B | 128K | Optimized for Chinese dialogue | Commercial license unclear |

**Recommended**: **Qwen2.5 14B** or **Llama 3.1 8B** (fine-tuned)

### Phase 3: Optimization (Month 4+)
**Fine-tune on user-approved content**

- Collect 10,000+ high-quality user-rated chapters
- Fine-tune base model for:
  - Platform-specific writing style
  - Safety guideline adherence
  - Chinese + English bilingual generation
  - Specific genre specialization (romance, fantasy, etc.)

## Rationale

### Cost Comparison

| Approach | Monthly Cost | 1000 Users | 10,000 Users |
|----------|-------------|------------|--------------|
| OpenAI API | $0.15/1M tokens | $200 | $2,000 |
| Self-hosted 14B | Fixed hardware | $50 | $100 |
| Fine-tuned 8B | Fixed + training | $30 | $60 |

**Hardware Requirements**:
- NVIDIA RTX 4090 (24GB VRAM) - $1,500 one-time
- OR Cloud GPU (RunPod/Vast.ai) - $0.50/hour = $360/month

### Privacy & Compliance

✅ **Self-hosted advantages**:
- No data leaves your infrastructure
- Full audit trail of all generations
- No API rate limits or surprise bans
- No content policy conflicts (OpenAI prohibits adult content)

❌ **OpenAI API risks**:
- Terms of service violation (adult content generation)
- Account suspension risk
- Data sent to OpenAI servers (US jurisdiction)
- No control over model updates

### Customization Benefits

**Fine-tuned model advantages**:
1. **Style consistency**: All content matches platform voice
2. **Safety built-in**: Model trained on platform-approved examples
3. **Cost efficiency**: Smaller fine-tuned model vs larger general model
4. **User preference**: Learn from user ratings and feedback

## Implementation Strategy

### Step 1: Model-Agnostic Prompt Design (Current Phase)

Design prompts that work across multiple LLMs:

```markdown
# Principles
- Use clear, structured formatting
- Avoid model-specific instructions
- Provide examples (few-shot learning)
- Use explicit role definition
- Include safety guidelines in every prompt
```

### Step 2: Evaluation Framework

Before migration, test candidate models:

```typescript
const evaluationCriteria = {
  coherence: 0.25,      // Logical story flow
  engagement: 0.25,     // User interest (measured by read-through)
  safety: 0.30,         // Adherence to guidelines
  style: 0.20          // Writing quality
}

// Test with 100 diverse prompts
// Compare to GPT-4 baseline
```

### Step 3: Gradual Rollout

```
Week 1-2:  OpenAI API (100% of traffic)
Week 3-4:  A/B testing (10% open source, 90% OpenAI)
Week 5-6:  Ramp up (50% open source, 50% OpenAI)
Week 7-8:  Full migration (95% open source, 5% OpenAI fallback)
Month 3+:  Fine-tuning data collection
Month 4:   Deploy fine-tuned model
```

### Step 4: Fine-tuning Pipeline

```python
# Data collection
user_ratings → high_quality_examples (4.5+ stars)

# Fine-tuning
base_model (Qwen2.5 14B) + high_quality_examples → fine_tuned_model

# Evaluation
fine_tuned_model vs base_model → human_eval → deploy if +15% improvement
```

## Technical Architecture

```
┌─────────────────────────────────────────────────┐
│              Application Layer                  │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────┴──────────┐
        ▼                    ▼
┌──────────────┐      ┌─────────────┐
│ LLM Router   │      │  Monitor    │
│ (Load bal.)  │      │  Quality     │
└──────┬───────┘      └─────────────┘
       │
   ┌───┴────┬─────────┬────────────┐
   ▼        ▼         ▼            ▼
┌──────┐ ┌──────┐ ┌─────────┐ ┌─────────┐
│Local │ │Local │ │ OpenAI  │ │ Future │
│ Qwen │ │Llama │ │ Fallback│ │ Models  │
│ 14B  │ │ 8B   │ │ (5%)    │ │         │
└──────┘ └──────┘ └─────────┘ └─────────┘
```

### Key Components

1. **LLM Router**: Directs requests to appropriate model
   - Default: Local model
   - Fallback: OpenAI API (if local fails)
   - Smart routing: Complex prompts → OpenAI, simple → local

2. **Quality Monitor**: Tracks generation quality
   - User ratings
   - Read-through rates
   - Safety flag rate
   - Auto-switch to fallback if quality drops

3. **Model Abstraction Layer**: Unified API for different LLMs
   ```typescript
   interface LLMProvider {
     generate(prompt: string, options: GenerateOptions): AsyncGenerator<string>
     embed(text: string): Promise<number[]>
   }

   // Implementations:
   // - OpenAIProvider
   // - OllamaProvider (local)
   // - vLLMProvider (optimized local)
   ```

## Alternatives Considered

### 1. Pure OpenAI API
❌ **Rejected** due to:
- High recurring costs at scale
- ToS violation risk (adult content)
- No data privacy
- No customization control

### 2. Pure Local LLM from Day 1
❌ **Rejected** due to:
- Slower iteration during MVP validation
- Hardware setup time (1-2 weeks)
- Unclear which model performs best for this use case
- Distraction from product-market fit validation

### 3. Hybrid: Cloud-hosted Open Source (Replicate, Anyscale)
⚠️ **Partial option**:
- ✅ No ToS issues
- ❌ Still depends on external service
- ❌ Higher cost than self-hosting
- **Verdict**: Good intermediate step, but end goal is self-hosting

## Consequences

### Positive
- **Cost predictability**: Fixed hardware cost vs per-token billing
- **Data privacy**: Full control over user data and generated content
- **Customization**: Fine-tuning for specific needs
- **Reliability**: No external dependencies
- **Compliance**: Easier to meet regulatory requirements

### Negative
- **Operational overhead**: GPU maintenance, model updates, monitoring
- **Upfront cost**: $1,500+ for GPU hardware
- **Technical complexity**: Need ML expertise for fine-tuning
- **Performance**: May need multiple GPUs for high concurrency
- **Model quality**: Open-source models lag behind GPT-4

### Mitigation Strategies

| Risk | Mitigation |
|------|------------|
| Lower quality | A/B testing, keep OpenAI fallback |
| Hardware failure | Cloud backup, redundant instances |
| High concurrency | Use vLLM for 5-10x throughput |
| ML expertise | Partner with fine-tuning platforms (Predibase, Mosaic) |
| Model updates | Automate testing pipeline, gradual rollouts |

## Follow-up Actions

1. **Immediate** (Week 1-2):
   - ✅ Design model-agnostic prompts (see ADR-0003)
   - ✅ Implement LLM abstraction layer
   - ✅ Use OpenAI API for MVP validation

2. **Short-term** (Month 2):
   - Set up local GPU (rent or buy)
   - Test 2-3 candidate models
   - Implement A/B testing framework
   - Begin migration at 10% traffic

3. **Medium-term** (Month 3-4):
   - Collect user ratings and feedback
   - Fine-tune selected model
   - Complete migration (95% local, 5% fallback)

4. **Long-term** (Month 6+):
   - Optimize inference (quantization, vLLM)
   - Expand to multiple specialized models
   - Consider training custom model from scratch

## Decision Makers
- @alvin (Product/Engineering)
- Date: 2026-02-05

## Related Decisions
- ADR-0001: Initial System Architecture
- ADR-0003: Model-Agnostic Prompt Design Guide (TODO)
