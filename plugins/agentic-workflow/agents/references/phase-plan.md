# Phase: PLAN

## Purpose
Create actionable plan and get human approval before any implementation.

## Activities

### 1. Create plan.md
Write to `.claude/plan.md` with structure:

```markdown
# Implementation Plan: [Feature]

## Objective
[One sentence describing the goal]

## Approach
[Technical strategy in 2-3 sentences]

## Task Decomposition

### Wave 1 (Parallel)
- Task A: [description]
  - Branch: task-a-[name]
  - Files: [list]
  - Success: [criteria]

- Task B: [description]
  - Branch: task-b-[name]
  - Files: [list]
  - Success: [criteria]

### Wave 2 (Depends on Wave 1)
- Task C: [description]
  - Branch: task-c-[name]
  - Depends: A, B
  - Success: [criteria]

## Success Criteria
- [ ] All tasks completed
- [ ] Tests pass
- [ ] Type check clean
- [ ] Code review approved
```

### 2. Validate Plan
Check for issues:
- All mentioned files exist or will be created?
- Dependencies form valid DAG (no cycles)?
- Success criteria are measurable?
- Task scope is clear and bounded?

### 3. Set Phase to PLAN_WAITING
```bash
echo "PLAN_WAITING" > "${STATE_DIR}/workflow-phase"
```

### 4. Request Approval
Use AskUserQuestion tool:

```
AskUserQuestion({
  questions: [{
    question: "I've created the implementation plan. Should I proceed?",
    header: "Plan",
    multiSelect: false,
    options: [
      { label: "Approve and proceed (Recommended)", description: "Plan looks good, start delegating" },
      { label: "Modify plan", description: "Adjust the approach before proceeding" },
      { label: "Reject and start over", description: "Return to exploration" }
    ]
  }]
})
```

### 5. Handle Response
- **Approve**: Hook will set `.claude/plan-approved`, transition to DELEGATE
- **Modify**: Ask what to change, update plan, ask again
- **Reject**: Return to EXPLORE phase

## Constraints
- No code modifications
- No spawning subagents until approved
- Plan must be written to file (not just displayed)

## Duration
Target: Plan approval before context reaches 40% usage.

## Transition
After approval, proceed to DELEGATE phase:
```bash
Read("${CLAUDE_PLUGIN_ROOT}/agents/references/phase-delegate.md")
```
