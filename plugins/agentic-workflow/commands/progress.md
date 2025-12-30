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

1. **Read todo.md** if exists:
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

1. **Ask what to update**:
   - Mark task(s) complete
   - Add new task(s)
   - Update progress notes
   - Record decision

2. **Make changes**:
   - Edit todo.md as needed
   - Update progress.txt with new state

3. **Confirm**:
   - Show updated state
   - Verify changes are correct

### reset

Clear state for fresh start:

1. **Confirm reset** (use AskUserQuestion):
   - "This will delete todo.md and progress.txt. Are you sure?"

2. **If confirmed**:
   - Delete todo.md
   - Delete progress.txt
   - Optionally clear .claude/artifacts/

3. **Report**:
   - "State cleared. Ready for new orchestration."

## Example: show

```
/progress

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

What would you like to update?
1. Mark task complete
2. Add new task
3. Update progress notes
4. Record a decision

> 1

Which task to mark complete?
- [ ] Session service
- [ ] API endpoints
- [ ] Integration tests
- [ ] Documentation

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

⚠️ This will delete:
- todo.md
- progress.txt
- Optionally: .claude/artifacts/

Are you sure?
- Yes, reset everything
- Yes, keep artifacts
- Cancel

> Yes, reset everything

State cleared.
- Deleted todo.md
- Deleted progress.txt
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
