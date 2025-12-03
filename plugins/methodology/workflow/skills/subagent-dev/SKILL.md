---
name: subagent-dev
description: Use when executing implementation plans with independent tasks in the current session - dispatches fresh subagent for each task with code review between tasks, enabling fast iteration with quality gates
allowed-tools: Task, Read, Skill
---

# Subagent-Driven Development

Execute plan by dispatching fresh subagent per task, with code review after each.

**Core principle:** Fresh subagent per task + review between tasks = high quality, fast iteration

## Overview

**vs. Executing Plans (parallel session):**

- Same session (no context switch)
- Fresh subagent per task (no context pollution)
- Code review after each task (catch issues early)
- Faster iteration (no human-in-loop between tasks)

**When to use:**

- Staying in this session
- Tasks are mostly independent
- Want continuous progress with quality gates

**When NOT to use:**

- Need to review plan first (use executing-plans)
- Tasks are tightly coupled (manual execution better)
- Plan needs revision (brainstorm first)

## The Process

### 1. Load Plan

Read plan file, create TodoWrite with:
- All tasks from the plan
- **MANDATORY FINAL TODO:** "Complete development (finish-branch)" - this ensures finish-branch is invoked after all tasks complete

### 2. Execute Task with Subagent

For each task:

**Dispatch fresh subagent:**

```
Task tool (general-purpose):
  description: "Implement Task N: [task name]"
  prompt: |
    You are implementing Task N from [plan-file].

    Read that task carefully. Your job is to:
    1. Implement exactly what the task specifies
    2. Write tests (following TDD if task says to)
    3. Verify implementation works
    4. Commit your work
    5. Report back

    Work from: [directory]

    Report: What you implemented, what you tested, test results, files changed, any issues
```

**Subagent reports back** with summary of work.

**Note:** Subagents implement individual tasks only. The parent (you) handles finish-branch after ALL tasks complete - subagents don't need to know about it.

### 3. Review Subagent's Work

**Dispatch code-reviewer subagent:**

Use template at `plugins/methodology/review/templates/code-reviewer-dispatch.md`.

```
Task tool (review:code-reviewer):
  description: "Review Task N implementation"
  prompt: |
    Review the implementation against requirements.

    ## Context
    - **What Was Implemented:** [from subagent's report]
    - **Requirements/Plan:** Task N from [plan-file]
    - **Description:** [task summary]

    ## Git Range
    - **Base:** [commit before task]
    - **Head:** [current commit]

    First run: git diff --stat [BASE_SHA]..[HEAD_SHA]
    Then review against plugins/methodology/review/references/code-review-standards.md
```

**Code reviewer returns:** Strengths, Issues (Critical/Important/Minor), Assessment

### 4. Apply Review Feedback

**If issues found:**

- Fix Critical issues immediately
- Fix Important issues before next task
- Note Minor issues

**Dispatch follow-up subagent if needed:**

```
"Fix issues from code review: [list issues]"
```

### 5. Mark Complete, Next Task

- Mark task as completed in TodoWrite
- Move to next task
- Repeat steps 2-5

### 6. Final Review

After all tasks complete, dispatch final code-reviewer:

- Reviews entire implementation
- Checks all plan requirements met
- Validates overall architecture

### 7. Complete Development

After final review passes:

1. Mark the "Complete development (finish-branch)" todo as **in_progress**
2. Announce: "I'm using the finish-branch skill to complete this work."
3. **REQUIRED:** Use `Skill("workflow:finish-branch")`
4. Follow that skill to verify tests, present options, execute choice
5. Mark the "Complete development (finish-branch)" todo as **completed**

**This step is NOT optional.** The mandatory final todo ensures this step is visible throughout execution.

## Example Workflow

```
You: I'm using Subagent-Driven Development to execute this plan.

[Load plan, create TodoWrite with tasks + "Complete development (finish-branch)"]

Task 1: Hook installation script

[Dispatch implementation subagent]
Subagent: Implemented install-hook with tests, 5/5 passing

[Get git SHAs, dispatch code-reviewer]
Reviewer: Strengths: Good test coverage. Issues: None. Ready.

[Mark Task 1 complete]

Task 2: Recovery modes

[Dispatch implementation subagent]
Subagent: Added verify/repair, 8/8 tests passing

[Dispatch code-reviewer]
Reviewer: Strengths: Solid. Issues (Important): Missing progress reporting

[Dispatch fix subagent]
Fix subagent: Added progress every 100 conversations

[Verify fix, mark Task 2 complete]

...

[After all tasks]
[Dispatch final code-reviewer]
Final reviewer: All requirements met, ready to merge

[Mark "Complete development (finish-branch)" as in_progress]
You: I'm using the finish-branch skill to complete this work.
[Use Skill("workflow:finish-branch")]
[Present 4 options: merge, PR, keep, discard]
[User chooses option, execute it]
[Mark "Complete development (finish-branch)" as completed]

Done!
```

## Advantages

**vs. Manual execution:**

- Subagents follow TDD naturally
- Fresh context per task (no confusion)
- Parallel-safe (subagents don't interfere)

**vs. Executing Plans:**

- Same session (no handoff)
- Continuous progress (no waiting)
- Review checkpoints automatic

**Cost:**

- More subagent invocations
- But catches issues early (cheaper than debugging later)

## Red Flags

**Never:**

- Skip code review between tasks
- Proceed with unfixed Critical issues
- Dispatch multiple implementation subagents in parallel (conflicts)
- Implement without reading plan task

**If subagent fails task:**

- Dispatch fix subagent with specific instructions
- Don't try to fix manually (context pollution)

## Integration

**Required workflow skills:**

- **writing-plans** - **REQUIRED SUB-SKILL:** Use workflow:writing-plans to create the plan that this skill executes
- **code-review** - **REQUIRED SUB-SKILL:** Use review:code-review for review after each task (see Step 3)
- **finish-branch** - **REQUIRED SUB-SKILL:** Use workflow:finish-branch to complete development after all tasks (see Step 7)

**Subagents must use:**

- **tdd** - **REQUIRED SUB-SKILL:** Use core:tdd for TDD in each task

**Alternative workflow:**

- **executing-plans** - Use for parallel session instead of same-session execution

**Templates:**

- Code reviewer dispatch: `plugins/methodology/review/templates/code-reviewer-dispatch.md`
