# todo.md Template

Copy and adapt this template for tracking task progress.

```markdown
# [Feature/Task Name]

## Overview
[One-line description of the overall goal]

## Phase 1: [Phase Name]
- [ ] Task description here
- [ ] Another task
- [x] Completed task (mark with x)

## Phase 2: [Phase Name]
- [ ] Task description
- [ ] Task with sub-items:
  - [ ] Sub-item 1
  - [ ] Sub-item 2

## Phase 3: [Phase Name]
- [ ] Final tasks
- [ ] Verification and cleanup

## Completion Criteria
- [ ] All tests pass
- [ ] Type check clean
- [ ] Lint clean
- [ ] Documentation updated
- [ ] PR created
```

## Alternative Format with DONE/PENDING

```markdown
# [Feature Name]

## Phase 1: Setup
DONE Read existing code
DONE Document architecture
DONE Create plan

## Phase 2: Implementation
DONE Write tests
PENDING Implement feature
PENDING Run integration tests

## Phase 3: Finalization
PENDING Update docs
PENDING Create PR
```

## Usage Rules

1. **Update immediately** - Mark tasks DONE as soon as completed
2. **Before stopping** - Always read todo.md, check for incomplete items
3. **After compaction** - First action should be reading todo.md
4. **Be specific** - "Implement token service" not "Do the thing"

## Checking Progress

```bash
# Count completed vs pending
grep -c "\[x\]" todo.md  # completed
grep -c "\[ \]" todo.md  # pending

# Or with DONE/PENDING format
grep -c "DONE" todo.md
grep -c "PENDING" todo.md
```
