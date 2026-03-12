"""
Shared state schema for the dev team LangGraph workflow.
All agents read from and write to this state object.
"""
from typing import TypedDict, Literal, Optional


class DevTeamState(TypedDict):
    # The original task from the user
    task: str

    # Planner output: list of steps, each assigned to an executor role
    plan: list[dict]  # [{"step": "...", "executor": "engineer", "context": "..."}]

    # Current step index being executed
    current_step_index: int

    # Latest output from the executor (Claude Code CLI stdout)
    executor_output: str

    # Mentor coaching notes for the current step (shown to user)
    mentor_notes: str

    # Presenter's summary of completed work
    presentation: str

    # Control flow: "continue" | "done" | "error"
    status: Literal["continue", "done", "error"]

    # Full message log for tracing
    messages: list[dict]

    # Error message if something went wrong
    error: Optional[str]
