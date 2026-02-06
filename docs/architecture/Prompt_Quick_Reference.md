# 本地开源 LLM Prompt 设计快速参考

> 为计划迁移到本地开源 LLM 的开发者准备

## 📋 核心原则总结

### 1. 明确优于隐含
❌ 不要："写一段引人入胜的内容"
✅ 应该："写一段 1000-1500 字的现代都市浪漫场景，包含对话、叙述和内心独白"

### 2. 结构化优于自然语言
❌ 不要："你是一个很棒的作家..."
✅ 应该：
```markdown
# Role
Creative fiction writer specializing in romance

# Requirements
- Length: 1000-1500 words
- Structure: Dialogue, narration, introspection
```

### 3. 示例优于抽象
❌ 不要："用生动的语言"
✅ 应该：
```markdown
## Example Style
"The rain tapped against the windowpane, each droplet a tiny drum building toward the crescendo..."
```

---

## 🎯 通用 Prompt 模板

### 中文版本（适合 Qwen, ChatGLM）

```markdown
# 角色定义
你是一位专业的成人小说作家

# 核心原则
1. **知情同意**: 所有角色均为同意的成年人
2. **叙事质量**: 注重情节发展和情感共鸣
3. **安全性**: 遵守平台安全���南

# 写作风格
- 感官丰富的描述
- 平衡对话、动作和内心独白
- 为每个角色赋予独特的声音

# 输出格式
- 语言: 中文
- 篇幅: 1000-2000字
- 格式: Markdown
- 视角: 第三人称限制视角

# 质量检查
输出前确认:
- [ ] 所有角色均为同意的成年人
- [ ] 内容符合安全指南
- [ ] 叙事逻辑流畅

---

# 故事背景

## 类型
[现代都市 / 古代宫廷 / 奇幻冒险]

## 场景设定
- **时间**: [具体时间]
- **地点**: [具体地点]
- **氛围**: [紧张 / 浪漫 / 神秘]

## 主要人物
- **[姓名]**([年龄]): [角色] - [性格特点]
- **[姓名]**([年龄]): [角色] - [性格特点]

## 情节大纲
1. [开场发生了什么]
2. [中段，张力如何升级]
3. [高潮]
4. [结局或悬念]

## 风格指南
- **描写**: [感官细节/比喻/简洁]
- **对话**: [自然/诗意/含蓄]
- **情感基调**: [充满希望/忧郁/激情]

## 示例段落
[提供1-2段展示期望风格的例子]

---

## 技术要求
- 篇幅: 1500字
- 语言: 中文
- 格式: Markdown

## 章节目标
[一句话明确目标]

开始生成。
```

### 英文版本（适合 Llama, Mistral）

```markdown
# Role
Expert creative fiction writer

# Core Principles
1. **Consent**: All characters are consenting adults (18+)
2. **Quality**: Focus on plot development and emotional resonance
3. **Safety**: Follow platform safety guidelines

# Writing Style
- Vivid sensory descriptions
- Balance dialogue, action, and introspection
- Distinct voice for each character

# Output Format
- Language: English
- Length: 1000-2000 words
- Format: Markdown
- POV: Third-person limited

# Quality Checklist
Before output, verify:
- [ ] All characters are consenting adults
- [ ] Content follows safety guidelines
- [ ] Narrative flows logically

---

# Story Context

## Genre
[MODERN_ROMANCE | HISTORICAL | FANTASY | SCI_FI]

## Setting
- **Time**: [Specific time period]
- **Location**: [Specific place with atmosphere]
- **Mood**: [Tense / Romantic / Mysterious]

## Characters
- **[Name]** ([Age]): [Role] - [Key traits]
- **[Name]** ([Age]): [Role] - [Key traits]

## Plot Outline
1. [Opening scene]
2. [Middle - rising action]
3. [Climax]
4. [Ending or cliffhanger]

## Style Guidelines
- **Descriptive Style**: [Sensory / Metaphorical / Minimal]
- **Dialogue**: [Natural / Poetic / Terse]
- **Emotional Tone**: [Hopeful / Melancholic / Passionate]

## Example Passage
[Provide 1-2 paragraphs showing desired style]

---

## Technical Requirements
- Length: 1500 words
- Language: English
- Format: Markdown

## Chapter Goal
[Single-sentence objective]

Begin generation now.
```

---

## 🔑 关键差异：开源 vs GPT-4

| 方面 | GPT-4 | 开源模型（Qwen/Llama） | 应对策略 |
|------|-------|---------------------|----------|
| **指令遵循** | 优秀 | 良好 | 更明确的指令 |
| **示例需求** | 可选 | 必须 | 总是提供 1-3 个示例 |
| **格式化** | 自动理解 | 需要明确 | 明确指定 Markdown 格式 |
| **安全对齐** | 强 | 中等 | 明确列出禁止事项 |
| **中文能力** | 良好 | Qwen 优秀，Llama 较弱 | 针对性选择模型 |

---

## 🛠️ 实现示例

```typescript
// 模型无关的生成接口
interface LLMProvider {
  generate(
    systemPrompt: string,
    scenarioPrompt: string,
    options?: { stream?: boolean }
  ): Promise<string | AsyncIterable<string>>
}

// OpenAI 实现
class OpenAIProvider implements LLMProvider {
  async generate(system: string, scenario: string) {
    return await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: system },
        { role: 'user', content: scenario }
      ],
      stream: true
    })
  }
}

// 本地 Ollama 实现
class OllamaProvider implements LLMProvider {
  async generate(system: string, scenario: string) {
    return await ollama.generate({
      model: 'qwen2.5:14b',
      system,
      prompt: scenario,
      stream: true
    })
  }
}

// 使用示例
const llm: LLMProvider = process.env.USE_LOCAL
  ? new OllamaProvider()
  : new OpenAIProvider()

for await (const chunk of llm.generate(systemPrompt, scenarioPrompt)) {
  // 流式输出到前端
  sendToClient(chunk)
}
```

---

## 📊 测试检查清单

在迁移到开源模型前，确保：

- [ ] 在至少 2 个不同模型上测试过 Prompt（GPT-4 + Qwen/Llama）
- [ ] 提供了 1-3 个具体示例
- [ ] 明确指定了输出格式和长度
- [ ] 包含了明确的安全规则
- [ ] 使用了 Markdown 结构（# ## - 1.）
- [ ] 测试了至少 100 个不同场景
- [ ] 人工评估质量 ≥ 85% 的 GPT-4 基线
- [ ] A/B 测试用户反馈

---

## 🎓 推荐学习资源

1. **Qwen 文档**: https://github.com/QwenLM/Qwen
2. **Llama Prompt Guide**: https://llama.meta.com/docs/model-cards-and-prompt-formats/
3. **Ollama 库**: https://ollama.com/library
4. **vLLM 优化**: https://docs.vllm.ai/（生产环境推理加速）

---

## 📞 需要帮助？

- 📖 详细设计：[ADR-0003: Prompt Design Standards](../decisions/ADR-0003-prompt-design-standards.md)
- 🤖 LLM 策略：[ADR-0002: LLM Strategy](../decisions/ADR-0002-llm-strategy.md)
- 🏗️ 架构设计：[AI_Generation_Design.md](./AI_Generation_Design.md)

---

**下一步行动**：
1. ✅ 使用上面的模板创建你的第一个 Prompt
2. ✅ 在 GPT-4 上测试并建立质量基线
3. ✅ 准备本地环境（Ollama + Qwen/Llama）
4. ✅ 对比测试，调整 Prompt 直到质量匹配
5. ✅ 部署开源模型，开始节省成本！
