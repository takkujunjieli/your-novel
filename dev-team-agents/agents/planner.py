"""
Planner Agent — Claude Code CLI
Reads the task and codebase, produces an ordered execution plan.
"""
import json
import os
import re
from skills.shell_tools import run_claude_code
from skills.registry import registry
from state import DevTeamState


def planner_node(state: DevTeamState) -> DevTeamState:
    """LangGraph node: decompose task into steps and assign executor roles."""

    system_prompt = registry.load_system_prompt("planner")
    
    user_msg = f"""
Task: {state["task"]}

Project root: {os.getenv("PROJECT_ROOT", "/Users/takku/Documents/your-novel")}

Produce a JSON plan as a list of steps. Each step must have:
- "step": a clear description of what to do
- "executor": one of "engineer", "ui_designer", or "tester"
- "context": any specific files, patterns, or constraints to keep in mind

Respond with ONLY valid JSON wrapped in ```json ... ``` blocks. Example:
```json
[
  {{"step": "Add /ping endpoint to main.py", "executor": "engineer", "context": "Follow existing route patterns in backend/api/"}},
  {{"step": "Write test for /ping endpoint", "executor": "tester", "context": "Use pytest, see backend/tests/ for patterns"}}
]
```
"""
    full_prompt = f"{system_prompt}\n\n## Input Task\n{user_msg}"
    
    raw = run_claude_code(full_prompt)
    
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```json\s*(.*?)\s*```', raw, re.DOTALL)
    if json_match:
        raw_json = json_match.group(1)
    else:
        # Fallback: try to find anything that looks like a JSON array
        array_match = re.search(r'\[\s*\{.*?\}\s*\]', raw, re.DOTALL)
        if array_match:
            raw_json = array_match.group(0)
        else:
            raw_json = raw.strip()

    try:
        plan = json.loads(raw_json)
    except json.JSONDecodeError as e:
        # If Claude fails to return valid JSON, create a single fallback step
        plan = [{"step": state["task"], "executor": "engineer", "context": f"Failed to parse plan JSON: {e}. Executing task directly."}]

    return {
        **state,
        "plan": plan,
        "current_step_index": 0,
        "status": "continue",
        "messages": state.get("messages", []) + [
            {"role": "planner", "content": f"Plan created: {len(plan)} steps"}
        ],
    }
