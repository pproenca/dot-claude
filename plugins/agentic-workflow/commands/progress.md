---
description: Manage external state files - show, update, or reset todo.md and progress.txt
argument-hint: [show|update|reset]
allowed-tools: Read, Write, Bash, Edit, AskUserQuestion
---

# /progress - External State Management

Manage the external state files that track task progress across context boundaries.

## Input

Action: $ARGUMENTS
- `show` (default): Display current todo.md and progress.txt
- `update`: Interactive update of state files
- `reset`: Clear state files for fresh start

## Validation

1. **Parse action** from arguments (case-insensitive):
   ```
   action = lowercase(first_word($ARGUMENTS)) or "show"
   ```

2. **Validate action**:
   - If action not in [show, update, reset]:
     ```
     Error: Invalid action '${action}'

     Valid options:
     - show (default): Display current state
     - update: Interactive update
     - reset: Clear state files

     Usage: /progress [show|update|reset]
     ```
     Stop execution.

## Worktree Awareness

This command is worktree-aware. Source utilities first:
```bash
source "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/worktree-utils.sh"
STATE_DIR=$(worktree_state_dir)
```

State files are scoped to the current context (main repo or worktree).

## Actions

### show (default)

Display current state:

1. **Show worktree context** (if in worktree):
   ```bash
   source "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/worktree-utils.sh"
   if worktree_is_worktree; then
       echo "## Worktree Context"
       echo "Name: $(worktree_current)"
       echo "Branch: $(worktree_current_branch)"
       echo "Main repo: $(worktree_main_repo)"
   fi
   ```

2. **Read workflow phase** (.claude/workflow-phase):
   ```bash
   STATE_DIR=$(worktree_state_dir)
   cat "${STATE_DIR}/workflow-phase" 2>/dev/null || echo "No workflow active"
   cat "${STATE_DIR}/plan-approved" 2>/dev/null || echo "Not approved"
   ```

   Display:
   ```
   ## Workflow Phase
   Current: [IDLE|EXPLORE|PLAN_WAITING|DELEGATE|VERIFY|COMPLETE]
   Plan approved: [yes/no]
   ```

2. **Read todo.md** if exists:
   ```
   ## todo.md
   [contents]

   Progress: X/Y items complete (Z%)
   Next incomplete: [first [ ] item]
   ```

2. **Read progress.txt** if exists:
   ```
   ## progress.txt
   [contents]
   ```

3. **Check artifacts**:
   ```bash
   STATE_DIR=$(worktree_state_dir)
   ls "${STATE_DIR}/artifacts/" 2>/dev/null
   ```
   ```
   ## Artifacts
   Found X artifacts in .claude/artifacts/
   - [list filenames]
   ```

4. **List active worktrees** (from main repo only):
   ```bash
   source "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/worktree-utils.sh"
   worktree_list
   ```
   ```
   ## Active Worktrees
   - myapp--task-a [in progress]
   - myapp--task-b [in progress]
   ```

5. **Summary**:
   ```
   ## Status Summary
   - Context: [main repo | worktree name]
   - Phase: [current phase]
   - Progress: [X/Y complete]
   - Next action: [recommendation]
   ```

### update

Interactive state update:

1. **Ask what to update** using AskUserQuestion tool:

```
AskUserQuestion({
  questions: [{
    question: "What would you like to update in the workflow state?",
    header: "Update type",
    multiSelect: false,
    options: [
      {
        label: "Mark task complete (Recommended)",
        description: "Check off a completed task in todo.md"
      },
      {
        label: "Add new task",
        description: "Add a new task to todo.md"
      },
      {
        label: "Update progress notes",
        description: "Update the session state in progress.txt"
      },
      {
        label: "Record decision",
        description: "Document an important decision made"
      }
    ]
  }]
})
```

Handle responses:
- "Mark task complete" → Show pending tasks with multiSelect (see below)
- "Add new task" → Ask for task description
- "Update progress notes" → Ask what to record
- "Record decision" → Ask for decision details
- "Other" (custom input) → Process user's specific request

**Error Handling**: If AskUserQuestion fails or returns empty/invalid response:
- Report: "Unable to process response. Let me try a different approach."
- Fallback: Proceed with "Mark task complete" as default, or ask user to type preference directly

2. **If "Mark task complete"**, use multiSelect for batch completion:

Read pending tasks from todo.md, then ask:

```
AskUserQuestion({
  questions: [{
    question: "Which tasks have been completed?",
    header: "Completed",
    multiSelect: true,
    options: [
      // Dynamically populated from pending tasks in todo.md
      // Example:
      { label: "Token service", description: "Implement JWT token generation" },
      { label: "Session service", description: "Session management implementation" },
      { label: "API endpoints", description: "REST API for auth flow" }
    ]
  }]
})
```

Mark all selected tasks as complete in todo.md.

3. **Based on response, gather details** (may require follow-up questions)

3. **Make changes**:
   - Edit todo.md as needed
   - Update progress.txt with new state

4. **Confirm**:
   - Show updated state
   - Verify changes are correct

### reset

Clear state for fresh start:

1. **Confirm reset** using AskUserQuestion tool:

```
AskUserQuestion({
  questions: [{
    question: "This will delete todo.md, progress.txt, and workflow state. What would you like to reset?",
    header: "Reset scope",
    multiSelect: false,
    options: [
      {
        label: "Keep artifacts (Recommended)",
        description: "Reset workflow but preserve .claude/artifacts/ for reference"
      },
      {
        label: "Reset everything",
        description: "Delete all state files including .claude/artifacts/"
      },
      {
        label: "Cancel",
        description: "Don't reset anything, keep current state"
      }
    ]
  }]
})
```

Handle responses:
- "Keep artifacts" → Delete todo.md, progress.txt, .claude/workflow-phase, .claude/plan-approved only (keep artifacts and worktrees)
- "Reset everything" → Delete todo.md, progress.txt, .claude/workflow-phase, .claude/plan-approved, .claude/artifacts/, and all worktrees
- "Cancel" → Exit without changes
- "Other" (custom input) → Process user's custom request

**Error Handling**: If AskUserQuestion fails or returns empty/invalid response:
- Report: "Unable to process response. Cancelling reset for safety."
- Fallback: Do not reset anything, ask user to confirm manually

3. **Clean up worktrees** (if resetting everything):
   ```bash
   source "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/worktree-utils.sh"
   worktree_cleanup
   ```

4. **Report**:
   - "State cleared. Ready for new orchestration."

## Example: show (from main repo)

```
/progress

## Worktrees for project: myapp

## Workflow Phase
Current: DELEGATE
Plan approved: yes

## todo.md
# User Authentication

## Phase 1: Setup
- [x] Read existing code
- [x] Create plan.md

## Phase 2: Implementation
- [x] Token service
- [ ] Session service
- [ ] API endpoints

## Phase 3: Integration
- [ ] Integration tests
- [ ] Documentation

Progress: 3/7 items complete (43%)
Next incomplete: Session service

## progress.txt
=== Session State ===
Last completed: Token service implementation
Next task: Session service
Blockers: None
Current phase: 2 of 3

## Artifacts
Found 1 artifact in .claude/artifacts/
- task-a-token-service.md

## Active Worktrees
~/.dot-claude-worktrees/myapp--token-service    [completed]
~/.dot-claude-worktrees/myapp--session-service  [in progress]

## Status Summary
- Context: main repo
- Phase: DELEGATE
- Progress: 43% complete
- Active worktrees: 2
- Next action: Continue with session service implementation
```

## Example: show (from worktree)

```
/progress

## Worktree Context
Name: myapp--session-service
Branch: session-service
Main repo: /Users/pedro/Projects/myapp

## Workflow Phase
Current: DELEGATE
Plan approved: yes

## todo.md
# Session Service Implementation
- [x] Create session model
- [ ] Implement session store
- [ ] Add session middleware

Progress: 1/3 items complete (33%)
Next incomplete: Implement session store

## Status Summary
- Context: worktree (myapp--session-service)
- Phase: DELEGATE
- Progress: 33% complete
- Next action: Implement session store
```

## Example: update

```
/progress update

[AskUserQuestion: What would you like to update in the workflow state?]
Options: Mark task complete | Add new task | Update progress notes | Record decision

User selects: "Mark task complete"

[Follow-up - shows pending tasks]
Pending tasks:
- [ ] Session service
- [ ] API endpoints
- [ ] Integration tests
- [ ] Documentation

Which task to mark complete?
> Session service

Updated todo.md:
- [x] Session service

Updated progress.txt:
- Last completed: Session service
- Next task: API endpoints

Progress now: 4/7 items complete (57%)
```

## Example: reset

```
/progress reset

[AskUserQuestion: This will delete todo.md, progress.txt, and workflow state. What would you like to reset?]
Options: Reset everything | Keep artifacts | Cancel

User selects: "Reset everything"

State cleared.
- Deleted todo.md
- Deleted progress.txt
- Deleted .claude/workflow-phase
- Deleted .claude/plan-approved
- Cleared .claude/artifacts/

Ready for new orchestration. Start with:
/orchestrate <your task>
```

## If No State Files Exist

```
/progress

No external state files found.

To start tracking progress:
1. Run /orchestrate <task> to begin orchestrated workflow
2. Or manually create todo.md with your task checklist

Example todo.md:
# My Task
- [ ] First step
- [ ] Second step
- [ ] Final step
```
