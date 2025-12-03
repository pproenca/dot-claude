---
name: executing-plans
description: Use when partner provides a complete implementation plan to execute in controlled batches with review checkpoints - loads plan, reviews critically, executes tasks in batches, reports for review between batches
allowed-tools: Bash, Read, Write, Edit, AskUserQuestion, TodoWrite, Skill, Task
---

# Executing Plans

## Overview

Load plan, review critically, execute tasks in batches, report for review between batches.

**Core principle:** Batch execution with checkpoints for architect review.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

## The Process

### Step 0: Verify Isolation Context

Before loading plan:

1. Check current git context:

   ```bash
   git branch --show-current
   git worktree list
   ```

2. **If on main/master without worktree:**
   Use AskUserQuestion:

   ```
   Question: "You're on the main branch. Plans should execute in isolated worktrees to protect main."
   Header: "Isolation"
   Options:
   - "Set up worktree": Create isolated workspace first (recommended)
   - "Continue on main": I understand the risk, proceed anyway
   ```

3. **If "Set up worktree":** Use workflow:git-worktrees skill first
4. **If "Continue on main":** Proceed with warning logged
5. **If already in worktree or feature branch:** Proceed normally

### Step 1: Load and Review Plan

1. Read plan file
2. Review critically - identify any questions or concerns about the plan
3. If concerns: Raise them with your human partner before starting
4. If no concerns: Create TodoWrite and proceed

### Step 2: Execute Batch

**Default: First 3 tasks**

For each task:

1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed

### Step 3: Code Review After Batch

When batch execution complete:

**Dispatch code-reviewer subagent:**

Use template at `plugins/methodology/review/templates/code-reviewer-dispatch.md`.

```
Task tool (review:code-reviewer):
  description: "Review Batch [N] implementation"
  prompt: |
    Review the implementation against requirements.

    ## Context
    - **What Was Implemented:** [Summary of tasks completed in this batch]
    - **Requirements/Plan:** Tasks [N-M] from [plan-file]
    - **Description:** Batch [N] - [brief summary of work]

    ## Git Range
    - **Base:** [commit before batch started]
    - **Head:** [current commit after batch]

    First run: git diff --stat [BASE_SHA]..[HEAD_SHA]
    Then review against plugins/methodology/review/references/code-review-standards.md
```

**Code reviewer returns:** Strengths, Issues (Critical/Important/Minor), Assessment

**If Critical or Important issues found:**

1. Address issues before proceeding
2. Re-run verification after fixes
3. Do NOT proceed to user feedback until resolved

**If only Minor issues:**

- Note for later
- Proceed to Step 4

### Step 4: Report and Request Feedback

After code review passes:

- Show what was implemented
- Show verification output
- **Show code review summary** (issues found and resolved)
- **Use `AskUserQuestion` tool** to request feedback:

```
Question: "Batch [N] complete. How should I proceed?"
Header: "Next step"
Options:
  - "Continue" - Proceed to next batch
  - "Review changes" - Show diffs or re-explain what was done
  - "Make adjustments" - Apply corrections before continuing
```

Wait for user response before proceeding.

### Step 5: Continue

Based on feedback:

- Apply changes if needed
- Execute next batch
- Repeat until complete

### Step 6: Complete Development

After all tasks complete and verified:

- Announce: "I'm using the finish-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use workflow:finish-branch
- Follow that skill to verify tests, present options, execute choice

## When to Stop and Ask for Help

**STOP executing immediately when:**

- Hit a blocker mid-batch (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**

- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember

- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Between batches: use AskUserQuestion to get explicit feedback
- Stop when blocked, don't guess
