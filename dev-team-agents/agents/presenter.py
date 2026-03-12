"""
Presenter Agent — Gemini Flash
Summarizes what was built in plain language for the user.
Runs after all executor steps are complete.
"""
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from skills.registry import registry
from state import DevTeamState


def presenter_node(state: DevTeamState) -> DevTeamState:
    """LangGraph node: produce a human-readable summary of what was done."""

    system_prompt = registry.load_system_prompt("presenter")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.5,
    )

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

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg),
    ])

    return {
        **state,
        "presentation": response.content,
        "status": "done",
        "messages": state.get("messages", []) + [
            {"role": "presenter", "content": "Summary ready"}
        ],
    }
