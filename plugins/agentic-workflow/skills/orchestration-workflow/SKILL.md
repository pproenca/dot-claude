---
name: orchestration-workflow
description: This skill activates when handling complex multi-step tasks, coordinating multiple agents, planning large implementations, or when phrases like "orchestrate", "complex task", "multi-step", "coordinate work", or "plan and implement" are used. Provides the Explore-Plan-Delegate framework for IC7-level orchestration.
---

# Multi-Agent Orchestration Workflow

When handling complex tasks, follow the Explore → Plan → Delegate → Verify → Synthesize workflow. You are the Lead Agent (IC7 level) responsible for coordination, not direct implementation.

## CRITICAL: Phase Management

The workflow uses a phase file (`.claude/workflow-phase`) to prevent premature test execution. **You MUST update this file at each phase transition**:

```bash
# Set phase (must do at each transition)
mkdir -p .claude && echo "PHASE_NAME" > .claude/workflow-phase
```

**Phase flow**:
```
IDLE → EXPLORE → PLAN_WAITING → (user approval) → DELEGATE → VERIFY → COMPLETE
```

**Stop hooks only run tests during**: DELEGATE, VERIFY, COMPLETE phases.

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

**First action**: Set phase
```bash
mkdir -p .claude && echo "EXPLORE" > .claude/workflow-phase
```

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

5. **Set phase to PLAN_WAITING**:
```bash
echo "PLAN_WAITING" > .claude/workflow-phase
```

6. **CRITICAL: Get human approval via AskUserQuestion**

Use AskUserQuestion tool with proper structure:

```
AskUserQuestion({
  questions: [{
    question: "I've created the implementation plan above. Should I proceed with delegating tasks to subagents?",
    header: "Plan",
    multiSelect: false,
    options: [
      {
        label: "Approve and proceed (Recommended)",
        description: "Plan looks good, start delegating to task-executor subagents"
      },
      {
        label: "Modify plan",
        description: "I want to adjust the approach before you proceed"
      },
      {
        label: "Reject and start over",
        description: "This approach won't work, return to exploration"
      }
    ]
  }]
})
```

**DO NOT proceed until user explicitly approves.**

Handle responses:
- "Approve and proceed" → Continue to DELEGATE phase
- "Modify plan" → Ask follow-up question (see below), update plan, ask again
- "Reject and start over" → Return to EXPLORE phase
- "Other" (custom input) → Process user's specific feedback

**If user selects "Modify plan"**, ask follow-up question:

```
AskUserQuestion({
  questions: [{
    question: "What aspect of the plan would you like to modify?",
    header: "Modify",
    multiSelect: false,
    options: [
      {
        label: "Task breakdown (Recommended)",
        description: "Adjust how tasks are divided or their dependencies"
      },
      {
        label: "Technical approach",
        description: "Change the implementation strategy or architecture"
      },
      {
        label: "Scope",
        description: "Add, remove, or adjust what's included"
      },
      {
        label: "Success criteria",
        description: "Modify how we'll know tasks are complete"
      }
    ]
  }]
})
```

Then: Update plan based on feedback, present updated plan for approval again.

## Phase 3: DELEGATE

**First action after approval**: Set phase
```bash
echo "DELEGATE" > .claude/workflow-phase
```

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

**Set phase**:
```bash
echo "VERIFY" > .claude/workflow-phase
```

After subagents complete, spawn verification agents:

1. **code-reviewer** - Fresh context, security/performance/patterns
2. **anti-overfit-checker** - Detect hardcoded values, narrow solutions
3. **integration-tester** - Full test suite, typecheck, lint

Run these in parallel. Collect results.

### Parallel Invocation Pattern (CRITICAL)

To run agents in parallel, include MULTIPLE Task tool calls in a SINGLE assistant message:

**Example: Verification Phase**
```
In your response, invoke ALL THREE tools at once:

[Task tool call 1]
- description: "Security and patterns review"
- subagent_type: "code-reviewer"
- prompt: [task packet with implementation + tests]

[Task tool call 2]
- description: "Generalization check"
- subagent_type: "anti-overfit-checker"
- prompt: [task packet with implementation ONLY - no tests]

[Task tool call 3]
- description: "Full test suite"
- subagent_type: "integration-tester"
- prompt: [task packet with full project]
```

All three execute **simultaneously** because they're in the same message.

**Example: Wave 1 Delegation**
For independent tasks in Wave 1, spawn multiple task-executors in one message:
```
[Task tool call 1]
- subagent_type: "task-executor"
- prompt: [Task A packet - token service]

[Task tool call 2]
- subagent_type: "task-executor"
- prompt: [Task B packet - session service]
```

**WRONG (Sequential):**
```
Message 1: Task(task-executor, Task A)
[wait for result]
Message 2: Task(task-executor, Task B)
[wait for result]
```

**RIGHT (Parallel):**
```
Single Message: Task(task-executor, Task A) + Task(task-executor, Task B)
[both execute simultaneously]
```

## Phase 5: SYNTHESIZE

**Goal**: Collect artifacts, resolve issues, finalize implementation.

1. **Collect all artifacts** from .claude/artifacts/
2. **Review verification results** - Any issues found?
3. **If issues**: Create remediation task packets, return to Delegate
4. **If clean**: Synthesize final implementation
5. **Update external state** - todo.md marked complete, progress.txt updated

**Set phase to COMPLETE**:
```bash
echo "COMPLETE" > .claude/workflow-phase
```

## External State Management

Throughout orchestration, maintain:

- **.claude/workflow-phase** - Current phase (CRITICAL for hook behavior)
- **todo.md** - Track task progress (DONE/PENDING markers)
- **progress.txt** - Session state for cross-session continuity
- **.claude/artifacts/** - Subagent handoff summaries

See context-management skill for formats.

## Key Principles

1. **Explore before coding** - Understand what exists
2. **Plan with approval** - Never implement without human sign-off via AskUserQuestion (use proper question/header/options structure)
3. **Manage phases** - Update .claude/workflow-phase at each transition
4. **Minimal context per agent** - 15-20K tokens, not full codebase
5. **Verify independently** - Fresh context catches what you missed
6. **External state** - Don't trust internal memory across compaction
7. **Re-inject regularly** - Every 5-10 turns, re-read task checklist

---

For scaling examples by complexity level, see references/scaling-examples.md
