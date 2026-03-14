"""
Mentor Agent — Claude Code CLI (optional)
Runs alongside each executor step to coach the user on design decisions.
Toggle with ENABLE_MENTOR=true in .env
"""
import os
from skills.shell_tools import run_claude_code
from skills.registry import registry
from state import DevTeamState


def mentor_node(state: DevTeamState) -> DevTeamState:
    """LangGraph node: provide coaching notes on the current step being executed."""

    if os.getenv("ENABLE_MENTOR", "true").lower() != "true":
        return {**state, "mentor_notes": ""}

    plan = state.get("plan", [])
    idx = state.get("current_step_index", 0)

    # Mentor runs before executor, so comment on the upcoming step
    upcoming_idx = idx  # executor hasn't incremented yet
    if upcoming_idx >= len(plan):
        return {**state, "mentor_notes": ""}

    current_step = plan[upcoming_idx]

    system_prompt = registry.load_system_prompt("mentor")
    
    user_msg = f"""
The team is about to execute this step:
Executor: {current_step.get("executor")}
Task: {current_step.get("step")}
Context: {current_step.get("context")}

Overall project task: {state["task"]}

Provide brief coaching notes (3-5 bullet points) covering:
- The design reasoning behind this approach
- A key concept the developer should understand
- One thing to watch out for
Keep it concise — this is a coaching note, not a lecture.
"""

    full_prompt = f"{system_prompt}\n\n## Input Information\n{user_msg}"
    
    output = run_claude_code(full_prompt)

    return {
        **state,
        "mentor_notes": output,
        "messages": state.get("messages", []) + [
            {"role": "mentor", "content": f"Coaching step {upcoming_idx+1}"}
        ],
    }
