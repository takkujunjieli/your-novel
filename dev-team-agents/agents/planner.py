"""
Planner Agent — Gemini Flash
Reads the task and codebase, produces an ordered execution plan.
"""
import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from skills.registry import registry
from state import DevTeamState


def planner_node(state: DevTeamState) -> DevTeamState:
    """LangGraph node: decompose task into steps and assign executor roles."""

    system_prompt = registry.load_system_prompt("planner")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
    )

    user_msg = f"""
Task: {state["task"]}

Project root: {os.getenv("PROJECT_ROOT", "/Users/takku/Documents/your-novel")}

Produce a JSON plan as a list of steps. Each step must have:
- "step": a clear description of what to do
- "executor": one of "engineer", "ui_designer", or "tester"
- "context": any specific files, patterns, or constraints to keep in mind

Respond with ONLY valid JSON. Example:
[
  {{"step": "Add /ping endpoint to main.py", "executor": "engineer", "context": "Follow existing route patterns in backend/api/"}},
  {{"step": "Write test for /ping endpoint", "executor": "tester", "context": "Use pytest, see backend/tests/ for patterns"}}
]
"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg),
    ])

    raw = response.content.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        plan = json.loads(raw)
    except json.JSONDecodeError:
        plan = [{"step": state["task"], "executor": "engineer", "context": ""}]

    return {
        **state,
        "plan": plan,
        "current_step_index": 0,
        "status": "continue",
        "messages": state.get("messages", []) + [
            {"role": "planner", "content": f"Plan created: {len(plan)} steps"}
        ],
    }
