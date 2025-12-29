---
description: Abandon active workflow and delete state
allowed-tools: Bash, AskUserQuestion, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*
---

# Abandon Workflow

Discard the active workflow state. Use this when you want to start fresh or the previous plan is no longer relevant.

## Step 1: Show Current State

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"

# Check hyh for active workflow
PROGRESS=$(harness_get_progress 2>/dev/null) || {
  echo "No active workflow found."
  exit 0
}

TOTAL=$(echo "$PROGRESS" | jq -r '.total // 0')
if [[ "$TOTAL" -eq 0 ]]; then
  echo "No active workflow found."
  exit 0
fi

COMPLETED=$(echo "$PROGRESS" | jq -r '.completed // 0')
PENDING=$(echo "$PROGRESS" | jq -r '.pending // 0')
RUNNING=$(echo "$PROGRESS" | jq -r '.running // 0')

echo "Active workflow:"
echo "  Progress: $COMPLETED/$TOTAL tasks completed"
echo "  - Pending: $PENDING"
echo "  - Running: $RUNNING"
```

## Step 2: Confirm

Use AskUserQuestion:

```claude
AskUserQuestion:
  header: "Confirm"
  question: "Discard workflow state? Completed commits will remain, but tracking will be lost."
  multiSelect: false
  options:
    - label: "Yes, discard"
      description: "Clear hyh state and start fresh"
    - label: "Cancel"
      description: "Keep workflow state for later resume"
```

## Step 3: Delete State

**If Yes, discard:**

```bash
# Clear hyh state
uvx hyh plan reset

# Clean up legacy state file if present
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
LEGACY_STATE="${REPO_ROOT}/.claude/dev-workflow-state.local.md"
[[ -f "$LEGACY_STATE" ]] && rm -f "$LEGACY_STATE"

echo "Workflow state cleared. You can start a new workflow with /dev-workflow:brainstorm or EnterPlanMode."
```

**If Cancel:**

Report: "Workflow state preserved. Use /dev-workflow:resume to continue."
