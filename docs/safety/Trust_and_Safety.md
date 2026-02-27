# Trust & Safety / Compliance Design

## 1. Age & Region Control

- **Age confirmation gate**: Required full-screen modal during onboarding (DOB must be 18+). No data collection beyond DOB verification.
- **IP-based region flagging**: To restrict certain jurisdictions if required by legal constraints.

## 2. Content Restrictions

- **Blocked categories**: No non-consensual scenarios, no excessive violence.
- **Real person references**: Must use fictional characters only. Do not generate stories referencing real individuals.
- **Minors**: All characters must explicitly be consenting adults (18+). Ensure prompts explicitly forbid minor-related content generation.

## 3. Safety Filtering

**Pre-Generation Checks**:
- User age verified (18+)
- Account in good standing (not flagged by previous violations)
- Rate limit not exceeded (e.g., 3 generations/day for free users)

**Post-Generation Validation**:
```python
from pydantic import BaseModel
from typing import Optional

class SafetyCheck(BaseModel):
    has_minors: bool              # Block if True
    non_consensual: bool          # Block if True
    excessive_violence: bool      # Block if True
    real_person_references: bool  # Block if True
    quality_score: float          # Must be > 0.6

async def validate_generated_content(content: str) -> SafetyCheck:
    # 1. Keyword-based filtering
    keyword_check = await check_blocked_keywords(content)

    # 2. LLM-based safety classification
    llm_check = await classify_safety(content)

    # 3. Quality scoring (coherence, engagement)
    quality_score = await assess_quality(content)

    return SafetyCheck(
        has_minors=llm_check.has_minors,
        non_consensual=llm_check.non_consensual,
        excessive_violence=keyword_check.violence_count > 3,
        real_person_references=keyword_check.has_real_names,
        quality_score=quality_score.overall
    )
```

**Fallback Behavior**:
- If safety check fails: Silently retry with different prompt
- If 3 retries fail: Notify user "Unable to generate. Try again later."
- If quality score < 0.6: Offer user option to accept or regenerate

## 4. Logging & Audit

- **Audit Trails**: Store generation metadata (user ID, prompt structure, timestamps)
- **Privacy**: Hash prompts instead of raw text when possible to protect privacy
- **Compliance**: Log all age verification timestamps to maintain a compliant audit trail
