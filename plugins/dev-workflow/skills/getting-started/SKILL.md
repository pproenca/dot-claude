---
name: getting-started
description: This skill is loaded automatically at session start via SessionStart hook. Establishes protocols for finding and using skills, checking skills before tasks, brainstorming before coding, and creating tasks for checklists.
allowed-tools: Read, Skill, TaskCreate, TaskUpdate, TaskList
---

# Getting Started with Skills

## Skill Discovery

Before starting any task, check if a skill exists for that task type:

| Task Type | Skill |
|-----------|-------|
| New feature, bug fix, behavior change | `test-driven-development` |
| Bug, test failure, unexpected behavior | `systematic-debugging` |
| Deep call stack errors | `root-cause-tracing` |
| Flaky tests, race conditions | `condition-based-waiting` |
| Claiming work is done | `verification-before-completion` |
| Code review feedback received | `receiving-code-review` |
| Bug fix validation layers | `defense-in-depth` |
| Architecture, file organization | `pragmatic-architecture` |
| Test quality review | `testing-anti-patterns` |
| Git worktree operations | `simple-git-worktrees` |
| Branch completion, merge/PR | `finishing-a-development-branch` |

If a skill matches: load it with the Skill tool, then follow it.

## Skill Priority

When multiple skills apply:

1. **Process skills first** — determine HOW to approach (debugging, brainstorming)
2. **Implementation skills second** — guide execution (TDD, architecture)
3. **Verification skills last** — confirm results (verification-before-completion)

Examples:
- "Build X" → brainstorming first, then TDD
- "Fix bug" → systematic-debugging first, then TDD for the fix
- "Add feature" → TDD (implementation is the process)

## Skill Types

**Rigid** (TDD, debugging, verification): Follow exactly. The structure IS the value.

**Flexible** (architecture, brainstorming): Adapt principles to context.

## Checklists

If a skill contains a checklist, create tasks using TaskCreate for each step. Mental tracking leads to skipped steps.

## Reference

See `references/skill-integration.md` for decision trees and skill chains.

---

## Planning Workflows

### Plugin Commands (Recommended)

```
/dev-workflow:brainstorm → /dev-workflow:write-plan → /dev-workflow:execute-plan
```

- Plans persist to `docs/plans/` (version controlled, reviewable)
- Parallel execution via `Task(run_in_background)` + `TaskOutput`
- Dependency tracking via `addBlockedBy`
- Post-completion: code review + finish branch enforced
- Resume: TaskList tracks progress

### How Parallel Execution Works

1. Create tasks with TaskCreate, express dependencies via addBlockedBy
2. For each round of unblocked tasks:
   - Launch with `Task(run_in_background: true)`
   - Collect with `TaskOutput(block: true)`
   - Mark completed with TaskUpdate
3. Proceed to post-completion actions

### When to Use EnterPlanMode Directly

Use `EnterPlanMode` without plugin commands for:
- Quick prototyping (plan doesn't need to persist)
- Simple 1-3 task features
- Interactive planning

For features needing plan persistence, code review, and resume capability, use the plugin commands flow.

### Executing Existing Plans

1. Read and validate the plan file
2. Choose sequential or parallel execution
3. After all tasks: code review → receiving-code-review → finishing-a-development-branch
