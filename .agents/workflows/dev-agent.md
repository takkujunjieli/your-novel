---
description: Run a single dev team agent on a quick task (skips the full workflow)
---

# /dev-agent Workflow

Triggered when user types `/dev-agent [role] [folder] "task description"` in the chat.
Valid roles: `planner`, `presenter`, `mentor`, `engineer`, `ui_designer`, `tester`.
Optional folder: `context` or `memory`. If provided, the agent will be instructed to save its output directly to this folder.

## Steps

1. Extract the role, the optional folder, and the task from the user's message.

2. Confirm the task back to the user:
   > 🤖 **`[role]` starting isolated task:** `<task>`
   > *(If folder specified)*: **Saving output to:** `/[folder]`

3. Run the single agent:
```bash
if [ -z "$folder" ]; then
    cd /Users/takku/Documents/ML-EKS-copy/dev-team-agents && source venv/bin/activate && python run_agent.py "<role>" "<task>"
else
    cd /Users/takku/Documents/ML-EKS-copy/dev-team-agents && source venv/bin/activate && python run_agent.py "<role>" "<folder>" "<task>"
fi
```

4. Display the output directly to the user in the chat, nicely formatted.
