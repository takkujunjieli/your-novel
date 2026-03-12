"""
Executor Router — dispatches each plan step to the right Claude Code executor.
Engineer / UI Designer / Tester all use Claude Code CLI under the hood.
"""
import os
from skills.shell_tools import run_claude_code
from skills.registry import registry
from state import DevTeamState


EXECUTOR_ROLE_MAP = {
    "engineer":    "engineer",
    "ui_designer": "ui_designer",
    "tester":      "tester",
}


def executor_node(state: DevTeamState) -> DevTeamState:
    """LangGraph node: run the current step using the appropriate Claude Code executor."""

    plan = state["plan"]
    idx = state["current_step_index"]

    if idx >= len(plan):
        return {**state, "status": "done"}

    current_step = plan[idx]
    role = current_step.get("executor", "engineer")
    step_desc = current_step.get("step", "")
    context = current_step.get("context", "")

    # Load the executor's role prompt for framing the Claude Code call
    role_name = EXECUTOR_ROLE_MAP.get(role, "engineer")
    role_prompt = registry.load_system_prompt(role_name)

    # Build the full prompt sent to Claude Code CLI
    full_prompt = f"""{role_prompt}

## Current Task
{step_desc}

## Context
{context}

## Project Root
{os.getenv("PROJECT_ROOT", "/Users/takku/Documents/your-novel")}

Please implement this step now. Be precise and follow existing patterns in the codebase.
"""

    output = run_claude_code(full_prompt)

    next_idx = idx + 1
    new_status = "continue" if next_idx < len(plan) else "done"

    return {
        **state,
        "executor_output": output,
        "current_step_index": next_idx,
        "status": new_status,
        "messages": state.get("messages", []) + [
            {"role": role_name, "content": f"Step {idx+1}: {step_desc[:80]}..."}
        ],
    }
