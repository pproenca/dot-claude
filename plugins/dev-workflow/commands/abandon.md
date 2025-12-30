---
description: Abandon active workflow and clear TodoWrite
allowed-tools: Bash, TodoWrite, AskUserQuestion, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*
---

# Abandon Workflow

Discard the active workflow state. Use this when you want to start fresh or the previous plan is no longer relevant.

## Step 1: Show Current State

Check TodoWrite for current progress and show summary.

```bash
# Check git for recent work
git log --oneline --since="1 day ago" | head -10
```

## Step 2: Confirm

Use AskUserQuestion:

```claude
AskUserQuestion:
  header: "Confirm"
  question: "Clear TodoWrite and abandon workflow? Completed commits will remain, but tracking will be lost."
  multiSelect: false
  options:
    - label: "Yes, abandon"
      description: "Clear TodoWrite and start fresh"
    - label: "Cancel"
      description: "Keep workflow for later resume"
```

## Step 3: Clear State

**If Yes, abandon:**

Clear TodoWrite by setting an empty list:

```claude
TodoWrite:
  todos: []
```

Report: "Workflow abandoned. You can start a new workflow with /dev-workflow:brainstorm or EnterPlanMode."

**If Cancel:**

Report: "Workflow preserved. Use /dev-workflow:resume to continue."
