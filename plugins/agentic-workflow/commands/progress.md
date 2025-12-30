---
description: Manage external state files - show, update, or reset todo.md and progress.txt
argument-hint: [show|update|reset]
allowed-tools: Read, Write, Bash, Edit
---

# /progress - External State Management

Manage the external state files that track task progress across context boundaries.

## Input

Action: $ARGUMENTS
- `show` (default): Display current todo.md and progress.txt
- `update`: Interactive update of state files
- `reset`: Clear state files for fresh start

## Actions

### show (default)

Display current state:

1. **Read workflow phase** (.claude/workflow-phase):
   ```bash
   cat .claude/workflow-phase 2>/dev/null || echo "No workflow active"
   cat .claude/plan-approved 2>/dev/null || echo "Not approved"
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
   ```
   ## Artifacts
   Found X artifacts in .claude/artifacts/
   - [list filenames]
   ```

4. **Summary**:
   ```
   ## Status Summary
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
        label: "Mark task complete",
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

2. **Based on response, gather details** (may require follow-up questions):
   - "Mark task complete" → Show pending tasks, ask which to mark done
   - "Add new task" → Ask for task description
   - "Update progress notes" → Ask what to record
   - "Record decision" → Ask for decision details

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
        label: "Reset everything",
        description: "Delete all state files including .claude/artifacts/"
      },
      {
        label: "Keep artifacts",
        description: "Reset workflow but preserve .claude/artifacts/ for reference"
      },
      {
        label: "Cancel",
        description: "Don't reset anything, keep current state"
      }
    ]
  }]
})
```

2. **Based on response**:
   - "Reset everything" → Delete todo.md, progress.txt, .claude/workflow-phase, .claude/plan-approved, .claude/artifacts/
   - "Keep artifacts" → Delete todo.md, progress.txt, .claude/workflow-phase, .claude/plan-approved only
   - "Cancel" → Exit without changes
   - "Other" → Process custom user request

3. **Report**:
   - "State cleared. Ready for new orchestration."

## Example: show

```
/progress

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

## Status Summary
- Phase: 2 (Implementation)
- Progress: 43% complete
- Next action: Continue with session service implementation
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
