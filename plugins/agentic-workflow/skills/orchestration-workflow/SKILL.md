---
name: orchestration-workflow
description: This skill activates when handling complex multi-step tasks, coordinating multiple agents, planning large implementations, or when phrases like "orchestrate", "complex task", "multi-step", "coordinate work", or "plan and implement" are used. Provides the Explore-Plan-Delegate framework for IC7-level orchestration.
---

# Multi-Agent Orchestration Workflow

When handling complex tasks, follow the Explore → Plan → Delegate → Verify → Synthesize workflow. You are the Lead Agent (IC7 level) responsible for coordination, not direct implementation.

## Complexity Assessment

Before starting, assess task complexity to determine the right approach:

| Complexity | Indicators | Approach |
|------------|-----------|----------|
| **Trivial** | Single file, single function, < 30 min work | Direct guidance, no subagent |
| **Small** | 1-3 files, clear scope | 1 subagent + verification |
| **Medium** | 3-10 files, multiple modules | 2-3 subagents + integration review |
| **Large** | 10+ files, architectural changes | 5+ subagents + staged milestones |
| **Huge** | Cross-system, multi-week scope | 10+ subagents + phased delivery |

## Phase 1: EXPLORE (No Coding)

**Goal**: Understand before acting. Never propose changes to code you haven't read.

1. **Read relevant files** - Identify entry points and related modules
2. **Grep/Glob for patterns** - Find similar implementations, conventions
3. **Document current architecture** - Write brief notes on what exists
4. **Identify integration points** - Where will new code connect?

Output: Clear understanding of codebase state and integration strategy.

## Phase 2: PLAN

**Goal**: Create actionable plan with human approval before implementation.

1. **Create plan.md** - Document approach in project root or .claude/
2. **Define task decomposition** - Break into parallelizable units
3. **Map dependencies** - Which tasks must complete before others?
4. **Define success criteria** - How do we know each task is done?
5. **Get human approval** - Present plan, wait for confirmation

If rejected, return to Explore phase with new understanding.

### Plan Document Format

```markdown
# Implementation Plan: [Feature Name]

## Objective
[One sentence describing the goal]

## Approach
[Brief description of technical approach]

## Task Decomposition

### Wave 1 (Parallel)
- Task A: [description] → Files: [list] → Success: [criteria]
- Task B: [description] → Files: [list] → Success: [criteria]

### Wave 2 (Depends on Wave 1)
- Task C: [description] → Depends: A, B → Success: [criteria]

### Wave 3 (Integration)
- Task D: Integration tests → Success: All tests pass

## Risks
- [Risk 1]: [Mitigation]
```

## Phase 3: DELEGATE

**Goal**: Create task packets and spawn subagents with minimal context.

For each task:

1. **Create task packet** - See task-packet-structure skill for format
2. **Determine context** - Only what subagent needs (15-20K tokens max)
3. **Spawn via Task tool** - Use task-executor agent with packet

### Dependency-Aware Scheduling

- **Wave 1**: Spawn independent tasks in parallel
- **Wave 2+**: Wait for dependencies, spawn with artifact context
- **Integration**: After all implementation waves complete

## Phase 4: VERIFY

After subagents complete, spawn verification agents:

1. **code-reviewer** - Fresh context, security/performance/patterns
2. **anti-overfit-checker** - Detect hardcoded values, narrow solutions
3. **integration-tester** - Full test suite, typecheck, lint

Run these in parallel. Collect results.

## Phase 5: SYNTHESIZE

**Goal**: Collect artifacts, resolve issues, finalize implementation.

1. **Collect all artifacts** from .claude/artifacts/
2. **Review verification results** - Any issues found?
3. **If issues**: Create remediation task packets, return to Delegate
4. **If clean**: Synthesize final implementation
5. **Update external state** - todo.md marked complete, progress.txt updated

## External State Management

Throughout orchestration, maintain:

- **todo.md** - Track task progress (DONE/PENDING markers)
- **progress.txt** - Session state for cross-session continuity
- **.claude/artifacts/** - Subagent handoff summaries

See context-management skill for formats.

## Key Principles

1. **Explore before coding** - Understand what exists
2. **Plan with approval** - Never implement without human sign-off
3. **Minimal context per agent** - 15-20K tokens, not full codebase
4. **Verify independently** - Fresh context catches what you missed
5. **External state** - Don't trust internal memory across compaction
6. **Re-inject regularly** - Every 5-10 turns, re-read task checklist

---

For scaling examples by complexity level, see references/scaling-examples.md
