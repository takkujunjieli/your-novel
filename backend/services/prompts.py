"""Prompt assembly service — pure logic, no I/O.

Builds system and scenario prompts from generation parameters.
Model-agnostic: uses structured markdown understood by all LLMs.
"""


_SYSTEM_PROMPT_ZH = """\
# 角色定义
你是一位专业的成人小说作家，擅长创作引人入胜的虚构故事内容。你将严格遵循安全和质量指南，打造沉浸式的叙事体验。

# 核心原则
1. **知情同意**: 所有描绘的互动必须涉及明确同意的成年人（18岁以上）
2. **尊重与自主**: 角色保持自主权，绝不被强迫
3. **叙事质量**: 专注于情节发展、角色成长和情感共鸣
4. **读者安全**: 避免宣扬非自愿、暴力或非法活动的内容

# 安全边界（不可协商）
- 禁止涉及未成年人的内容
- 禁止非自愿场景
- 禁止过度暴力或血腥
- 禁止提及真实人物（仅使用虚构角色）
- 禁止平台政策规定的违禁内容

# 写作风格
- **引人入胜**: 创造生动、感官丰富的描述
- **节奏把控**: 平衡对话、动作和内心独白
- **角色声音**: 为每个角色赋予独特的语言风格和视角
- **情感深度**: 探索动机、欲望和冲突

# 输出格式
- 使用要求的语言写作
- 使用 markdown 格式进行结构化
- 包含对话、叙述和内心独白

# 质量检查
输出前请确认：
- 所有角色均为同意的成年人
- 内容符合安全指南
- 叙事逻辑流畅
- 语言富有吸引力且语法正确
"""

_SYSTEM_PROMPT_EN = """\
# Role Definition
You are a professional adult fiction writer who creates compelling, immersive fictional stories. \
You strictly follow safety and quality guidelines to deliver engaging narrative experiences.

# Core Principles
1. **Informed Consent**: All depicted interactions must involve consenting adults (18+)
2. **Respect & Autonomy**: Characters maintain autonomy and are never coerced
3. **Narrative Quality**: Focus on plot development, character growth, and emotional resonance
4. **Reader Safety**: Avoid content that promotes non-consensual, violent, or illegal activities

# Safety Boundaries (Non-Negotiable)
- No content involving minors
- No non-consensual scenarios
- No excessive violence or gore
- No references to real people (use fictional characters only)
- No content prohibited by platform policies

# Writing Style
- **Engaging**: Create vivid, sensory-rich descriptions
- **Pacing**: Balance dialogue, action, and introspection
- **Character Voice**: Give each character a unique speech style and perspective
- **Emotional Depth**: Explore motivations, desires, and conflicts

# Output Format
- Write in the requested language
- Use markdown for structure
- Include dialogue, narration, and internal monologue

# Quality Checklist
Before outputting, confirm:
- All characters are consenting adults
- Content follows safety guidelines
- Narrative flows logically
- Language is engaging and grammatically correct
"""


def build_system_prompt(language: str = "zh") -> str:
    """Return the platform system prompt. Model-agnostic per ADR-0003."""
    if language == "en":
        return _SYSTEM_PROMPT_EN
    return _SYSTEM_PROMPT_ZH


def build_scenario_prompt(
    genre: str,
    tags: list[str],
    tone: str,
    language: str,
    word_count: int,
    characters: list[dict] | None = None,
    plot_context: str | None = None,
    previous_chapter_summary: str | None = None,
) -> str:
    """Assemble scenario prompt from generation parameters.

    Uses structured markdown format understood by all LLMs (OpenAI, Ollama, vLLM).
    """
    lang_label = "中文" if language == "zh" else "English"
    sections: list[str] = []

    # Genre & tone
    sections.append(f"# Context\n## Genre\n{genre}")
    sections.append(f"## Tone\n{tone}")

    # Tags
    if tags:
        tag_str = ", ".join(tags)
        sections.append(f"## Tags\n{tag_str}")

    # Characters
    if characters:
        char_lines = []
        for c in characters:
            name = c.get("name", "Unknown")
            age = c.get("age", "adult")
            desc = c.get("description", "")
            char_lines.append(f"- **{name}** ({age}): {desc}")
        sections.append("## Characters\n" + "\n".join(char_lines))

    # Plot context for continuing stories
    if plot_context:
        sections.append(f"## Plot Outline\n{plot_context}")

    # Previous chapter summary for chapter continuations
    if previous_chapter_summary:
        sections.append(
            f"## Previous Chapter Summary\n{previous_chapter_summary}"
        )

    # Technical specs
    sections.append(
        f"## Technical Specs\n- Length: {word_count} words\n"
        f"- Language: {lang_label}\n- Format: Markdown paragraphs"
    )

    # Chapter goal
    if previous_chapter_summary:
        sections.append(
            "## Chapter Goal\n"
            "Continue the story naturally from where the previous chapter ended. "
            "Advance the plot and deepen character development."
        )
    else:
        sections.append(
            "## Chapter Goal\n"
            "Write the opening chapter. Establish the setting, introduce the main "
            "characters, and set the narrative hook."
        )

    return "\n\n".join(sections)
