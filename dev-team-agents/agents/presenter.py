"""
Presenter Agent — Claude Code CLI
Summarizes what was built in plain language for the user.
Runs after all executor steps are complete.
"""
import os
from skills.shell_tools import run_claude_code
from skills.registry import registry
from state import DevTeamState


def presenter_node(state: DevTeamState) -> DevTeamState:
    """LangGraph node: produce a human-readable summary of what was done."""

    system_prompt = registry.load_system_prompt("presenter")
    
    plan_summary = "\n".join(
        f"- [{s['executor']}] {s['step']}"
        for s in state.get("plan", [])
    )

    user_msg = f"""
Original task: {state["task"]}

Steps that were executed:
{plan_summary}

Last executor output:
{state.get("executor_output", "(none)")}

Write a clear, concise summary for the user explaining:
1. What was built / changed
2. Why each decision was made
3. How to test or use what was just implemented
"""
    
    full_prompt = f"{system_prompt}\n\n## Input Information\n{user_msg}"
    
    output = run_claude_code(full_prompt)

    return {
        **state,
        "presentation": output,
        "status": "done",
        "messages": state.get("messages", []) + [
            {"role": "presenter", "content": "Summary ready"}
        ],
    }
