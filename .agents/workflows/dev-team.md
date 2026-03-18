---
description: Run the dev team multi-agent workflow on a coding task
---

# /dev-team Workflow

Triggered when user types `/dev-team "task description"` in the chat.

## Steps

1. Extract the task from the user's message (everything after `/dev-team`).

2. Confirm the task back to the user in one line:
   > 🤖 **Dev Team starting:** `<task>`

3. Run the dev team workflow:
```
cd /Users/takku/Documents/ML-EKS-copy/dev-team-agents && source venv/bin/activate && python main.py "<task>"
```

4. Read the output file to get the structured result:
```
cat /tmp/dev_team_result.json
```

5. Present the results to the user in this format:

---
**📋 Plan**
List each step with its executor role in brackets: `[engineer]`, `[ui_designer]`, `[tester]`

**🎓 Mentor Notes** *(if ENABLE_MENTOR=true)*
Show the mentor coaching notes for the last executed step.

**✅ What Was Built**
Show the Presenter summary — what was built, why, and how to use it.

---

6. Ask the user: "Anything to adjust or should we move to the next task?"

## Notes
- The venv must be activated before running (step 3 handles this)
- If `python main.py` fails, check that GOOGLE_API_KEY is set in `.env`
- If Claude Code CLI fails, check that `/Users/takku/.local/bin/claude` is working
- To skip the Mentor, set `ENABLE_MENTOR=false` in `.env`
- To visualize the graph: run `langgraph dev` in `dev-team-agents/` → opens localhost:2024