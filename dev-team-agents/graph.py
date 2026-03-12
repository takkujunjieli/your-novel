"""
LangGraph workflow — wires all agents into a stateful directed graph.
Visualize with: langgraph dev (opens localhost:2024)
"""
import os
from langgraph.graph import StateGraph, END
from state import DevTeamState
from agents.planner import planner_node
from agents.executor import executor_node
from agents.presenter import presenter_node
from agents.mentor import mentor_node


def should_continue_executing(state: DevTeamState) -> str:
    """Route: keep executing steps or move to presenter when done."""
    if state["status"] == "done":
        return "present"
    if state["status"] == "error":
        return "present"  # Present errors too
    return "mentor" if os.getenv("ENABLE_MENTOR", "true").lower() == "true" else "execute"


def build_graph() -> StateGraph:
    graph = StateGraph(DevTeamState)

    # ── Add nodes ────────────────────────────────────────────────
    graph.add_node("plan",    planner_node)
    graph.add_node("mentor",  mentor_node)
    graph.add_node("execute", executor_node)
    graph.add_node("present", presenter_node)

    # ── Entry point ───────────────────────────────────────────────
    graph.set_entry_point("plan")

    # ── Edges ─────────────────────────────────────────────────────
    # After planning → mentor (if enabled) or directly execute
    graph.add_conditional_edges(
        "plan",
        lambda s: "mentor" if os.getenv("ENABLE_MENTOR", "true").lower() == "true" else "execute",
        {"mentor": "mentor", "execute": "execute"},
    )

    # After mentor → execute
    graph.add_edge("mentor", "execute")

    # After execute → loop back (more steps) or present (done)
    graph.add_conditional_edges(
        "execute",
        should_continue_executing,
        {"mentor": "mentor", "execute": "execute", "present": "present"},
    )

    # After presenting → end
    graph.add_edge("present", END)

    return graph


# Compiled graph — imported by langgraph.json for Studio visualization
graph = build_graph().compile()
