"""
Entry point for the dev team agent system.
Called by the Antigravity /dev-team workflow.

Usage:
    python main.py "Add a /ping endpoint to the FastAPI backend"
"""
import sys
import json
import os
from dotenv import load_dotenv
from graph import graph

load_dotenv()


def run(task: str) -> dict:
    """Run the full dev team workflow for a given task."""
    initial_state = {
        "task": task,
        "plan": [],
        "current_step_index": 0,
        "executor_output": "",
        "mentor_notes": "",
        "presentation": "",
        "status": "continue",
        "messages": [],
        "error": None,
    }

    print(f"\n🚀 Dev Team starting task:\n   {task}\n")
    print("─" * 60)

    final_state = graph.invoke(initial_state)

    # ── Output ────────────────────────────────────────────────────
    plan = final_state.get("plan", [])
    print(f"\n📋 Plan ({len(plan)} steps):")
    for i, step in enumerate(plan, 1):
        print(f"   {i}. [{step['executor']}] {step['step']}")

    mentor_notes = final_state.get("mentor_notes", "")
    if mentor_notes:
        print(f"\n🎓 Mentor Notes:\n{mentor_notes}")

    print(f"\n✅ Presenter Summary:\n{final_state.get('presentation', '(no summary)')}")
    print("\n" + "─" * 60)

    return final_state


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py \"Your task description here\"")
        sys.exit(1)

    task = " ".join(sys.argv[1:])
    result = run(task)

    # Write result to a temp file so Antigravity can read it back
    output_path = "/tmp/dev_team_result.json"
    with open(output_path, "w") as f:
        # Serialize only the human-readable fields
        json.dump({
            "task": result["task"],
            "plan": result["plan"],
            "mentor_notes": result["mentor_notes"],
            "presentation": result["presentation"],
            "status": result["status"],
        }, f, indent=2)

    print(f"\n📄 Full result saved to: {output_path}")


if __name__ == "__main__":
    main()
