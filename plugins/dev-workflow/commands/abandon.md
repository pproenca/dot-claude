---
description: Abandon active workflow and delete state
allowed-tools: Bash, AskUserQuestion, mcp__plugin_serena_serena__activate_project, mcp__plugin_serena_serena__find_symbol, mcp__plugin_serena_serena__find_referencing_symbols, mcp__plugin_serena_serena__get_symbols_overview, mcp__plugin_serena_serena__search_for_pattern, mcp__plugin_serena_serena__read_file, mcp__plugin_serena_serena__list_dir
---

# Abandon Workflow

Discard the active workflow state. Use this when you want to start fresh or the previous plan is no longer relevant.

## Step 1: Show Current State

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
STATE_FILE="$(get_state_file)"
if [[ -f "$STATE_FILE" ]]; then
  PLAN=$(frontmatter_get "$STATE_FILE" "plan" "")
  CURRENT=$(frontmatter_get "$STATE_FILE" "current_task" "0")
  TOTAL=$(frontmatter_get "$STATE_FILE" "total_tasks" "0")
  echo "Active workflow:"
  echo "  Plan: $PLAN"
  echo "  Progress: $CURRENT/$TOTAL tasks"
else
  echo "No active workflow found."
fi
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
      description: "Delete state file and start fresh"
    - label: "Cancel"
      description: "Keep workflow state for later resume"
```

## Step 3: Delete State

**If Yes, discard:**

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/hook-helpers.sh"
delete_state_file
echo "Workflow state deleted. You can start a new workflow with /dev-workflow:brainstorm or EnterPlanMode."
```

**If Cancel:**

Report: "Workflow state preserved. Use /dev-workflow:resume to continue."
