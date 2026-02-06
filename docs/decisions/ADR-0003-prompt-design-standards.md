# ADR-0003: Model-Agnostic Prompt Design Standards

## Status
Accepted

## Date
2026-02-05

## Context
The platform plans to migrate from OpenAI API to self-hosted open-source LLMs (Qwen, Llama, Mistral, etc.).

**Challenge**: Different LLMs respond differently to the same prompt. What works for GPT-4 may fail for Llama 3.

**Solution**: Design prompts that work consistently across multiple LLM families.

---

## Core Principles

### 1. Explicit Over Implicit
❌ **Bad** (relies on model intuition):
```
Write something spicy
```

✅ **Good** (explicit instructions):
```
Write a romantic scene between two consenting adults.
Focus on emotional connection and sensory details.
Include dialogue, narration, and internal monologue.
Length: 1000-1500 words.
```

### 2. Structure Over Prose
❌ **Bad** (unstructured):
```
You're a great writer, make it engaging and interesting with good pacing and character development...
```

✅ **Good** (structured sections):
```
# Role
Creative fiction writer

# Requirements
- Length: 1000-1500 words
- Structure: Dialogue, narration, introspection
- Style: Vivid sensory descriptions
- Tone: Romantic and sensual
```

### 3. Examples Over Abstractions
❌ **Bad** (vague):
```
Write in an engaging style
```

✅ **Good** (with example):
```
# Writing Style
Use vivid, sensory-rich descriptions.

Example of desired style:
"The rain tapped against the windowpane, each droplet a tiny drum building toward the crescendo she knew was coming. She could feel his gaze before she saw it—a warmth spreading across her skin like honey in tea."
```

### 4. Universal Formatting
Use markdown and clear delimiters that all LLMs understand:

```markdown
# Section Header (use #)

## Subsection (use ##)

- Bullet points (use -)

1. Numbered lists (use 1.)

**Bold** for emphasis (use **)

`Code blocks` for examples (use `)

---

Horizontal rule (use ---)
```

---

## Prompt Template Structure

### System Prompt Template

```markdown
# Role
[Clear role definition]

# Core Principles
1. [Principle 1]
2. [Principle 2]
3. [Principle 3]

# Constraints
- [Constraint 1]
- [Constraint 2]

# Output Format
- Length: [specific word/token count]
- Structure: [dialogue, narration, etc.]
- Language: [English/Chinese]

# Safety Rules
❌ [What NOT to do]
✅ [What TO do]

# Quality Checklist
Before outputting, verify:
- [ ] [Check 1]
- [ ] [Check 2]
```

### Scenario Prompt Template

```markdown
# Context
## Genre
[Specific genre]

## Setting
[Time period, location, atmosphere]

## Characters
- **[Name]** ([Age]): [Role, personality, motivation]
- **[Name]** ([Age]): [Role, personality, motivation]

## Plot Outline
[Step-by-step summary of what should happen]

## Scene Focus
[Specific focus for this chapter/scene]

## Style Guidelines
- [Style preference 1]
- [Style preference 2]

## Example Passage
[Provide 1-2 paragraphs showing desired style]

## Chapter Goal
[Clear objective for this generation]

## Technical Specs
- Length: [word count]
- Language: [English/Chinese]
- Format: [Markdown, paragraphs, etc.]
```

---

## Language-Specific Guidelines

### For Chinese Generation (ChatGLM, Qwen)

**Key Considerations**:
- Chinese models benefit from explicit punctuation guidance
- Idioms and cultural references need context
- Formal vs. informal language should be specified

**Template**:
```markdown
# 语言风格
- 使用现代白话文（非文言文）
- 对话使用口语化表达
- 叙述使用文学性描述
- 避免过度使用网络用语

# 标点规范
- 对话使用引号："..."
- 叙述使用逗号、句号
- 内心独白使用括号：（...）

# 示例段落
林雨萱站在落地窗前，看着窗外的雨。雨水模糊了城市的天际线，就像她此刻混乱的心绪。

"在想什么？"身后传来熟悉的声音。

她转身，看到了陈默温柔的目光。那一刻，所有的犹豫都烟消云散了。
```

### For English Generation (Llama, Mistral)

**Key Considerations**:
- Specify dialect (US/UK) if important
- Formal vs. casual tone matters
- Cultural references should be explained

**Template**:
```markdown
# Language Style
- Modern American English
- Conversational dialogue
- Literary narration
- Avoid overly formal or archaic language

# Punctuation
- Dialogue: "..."
- Narration: Standard punctuation
- Internal thoughts: Italics or (parentheses)

# Example Paragraph
Emma stood by the floor-to-ceiling window, watching the rain blur the city skyline like her own tangled thoughts.

"What are you thinking about?" A familiar voice came from behind.

She turned to see James's gentle gaze. In that moment, all her hesitation vanished.
```

---

## Few-Shot Prompting Pattern

All models benefit from examples. Provide 1-3 complete examples:

```markdown
# Example 1: Romantic Encounter

## Input
Genre: Modern Romance
Characters: Sarah (28, artist), Michael (31, architect)
Setting: Coffee shop, rainy afternoon
Focus: First meeting, subtle attraction

## Output (Model Generated)
[Full 1000-word example showing desired style]

---

# Example 2: Fantasy Romance

## Input
Genre: Fantasy Romance
Characters: Elara (elf, guardian), Kael (human, adventurer)
Setting: Ancient temple, moonlit night
Focus: Magical attraction, forbidden love

## Output (Model Generated)
[Full 1000-word example showing desired style]
```

**Pro tip**: Use real examples from your best user-generated content (after consent).

---

## Model-Specific Adjustments

Even with universal prompts, slight tweaks help:

### For Qwen2.5 (Chinese-optimized)
```markdown
# 针对 Qwen 模型的优化
- 使用清晰的中文指令
- 提供中文示例段落
- 明确指定输出格式（markdown）
```

### For Llama 3 (English-optimized)
```markdown
# For Llama 3 Optimization
- Use clear English instructions
- Provide examples in English
- Specify output structure explicitly
```

### For ChatGLM (Bilingual)
```markdown
# ChatGLM 优化建议
- 中英文双语提示更有效
- 使用对话式指令
- 强调"循序渐进"（step-by-step）
```

---

## Anti-Patterns to Avoid

### ❌ Don't: Model-Specific Instructions

```markdown
# WRONG
Act like ChatGPT and use the style you were trained on...
Think step-by-step using Chain of Thought...
```

**Why**: Not all models support CoT or have the same "style".

### ❌ Don't: Vague Safety Instructions

```markdown
# WRONG
Be appropriate and follow guidelines...
```

**Why**: Different models have different interpretations of "appropriate".

### ✅ Do: Explicit Safety Boundaries

```markdown
# CORRECT
# Safety Rules
❌ No content involving minors
❌ No non-consensual scenarios
❌ No real person references
✅ All characters must be consenting adults (18+)
✅ Focus on emotional connection and narrative quality
```

---

## Testing Framework

Before deploying prompts, test across models:

```typescript
interface PromptTest {
  prompt: string
  models: string[]
  evaluator: (output: string) => {
    coherence: number
    safety: boolean
    style: number
    length: number
  }
}

async function testPromptAcrossModels(test: PromptTest) {
  const results = []

  for (const model of test.models) {
    const output = await generate(model, test.prompt)
    const scores = test.evaluator(output)

    results.push({
      model,
      scores,
      passed: scores.safety && scores.coherence > 0.7
    })
  }

  return results
}

// Test prompt works on GPT-4, Qwen, Llama
const testResults = await testPromptAcrossModels({
  prompt: systemPrompt,
  models: ['gpt-4o-mini', 'qwen2.5-14b', 'llama3.1-8b'],
  evaluator: evaluateOutput
})
```

---

## Implementation Checklist

For every prompt you create:

- [ ] Uses markdown structure (#, ##, -)
- [ ] Has explicit role definition
- [ ] Includes concrete examples
- [ ] Specifies output format (length, structure)
- [ ] Contains explicit safety rules
- [ ] Tested on at least 2 different models
- [ ] No model-specific instructions
- [ ] Language-specific if needed (Chinese/English)
- [ ] Includes quality checklist

---

## Migration Path

### Phase 1: OpenAI-Only Prompts
- Design for GPT-4o mini
- Use structured format (future-proof)
- Test with 100 generations

### Phase 2: Model-Agnostic Refinement
- Add explicit examples
- Remove GPT-specific patterns
- Test with Qwen/Llama (10% sample)

### Phase 3: Universal Prompts
- Fine-tune based on test results
- Ensure 90%+ consistency across models
- Document model-specific tweaks

---

## References

1. **Prompt Engineering Guide**: https://platform.openai.com/docs/guides/prompt-engineering
2. **Llama 2 Prompt Guide**: https://llama.meta.com/docs/model-cards-and-prompt-formats/meta-llama-2
3. **Qwen Prompt Best Practices**: https://github.com/QwenLM/Qwen/blob/main/README.md
4. **"Prompt Programming for Large Language Models"** (Research paper)

---

## Next Steps

1. ✅ Create prompt templates based on this ADR
2. ✅ Build testing framework
3. ⏳ Implement in AI_Generation_Design.md
4. ⏳ Validate with candidate models (Month 2)
