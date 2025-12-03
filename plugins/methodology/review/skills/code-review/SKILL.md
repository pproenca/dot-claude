---
name: code-review
description: Use when requesting or receiving code reviews - covers dispatching review subagent, handling feedback with technical rigor, and avoiding performative agreement
allowed-tools: Task, Read
---

# Code Review

Complete workflow for requesting code reviews and handling feedback professionally.

**Core principle:** Technical rigor over social comfort. Verify before implementing.

## Part 1: Requesting Reviews

Dispatch review:code-reviewer subagent to catch issues before they cascade.

### When to Request

**Mandatory:**

- After each task in subagent-driven development
- After completing major feature
- Before merge to main

**Optional but valuable:**

- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

### How to Request

**1. Get git SHAs:**

```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. Dispatch code-reviewer subagent:**

Use Task tool with `review:code-reviewer` type. See dispatch template at `plugins/methodology/review/templates/code-reviewer-dispatch.md`.

**Placeholders:**

- `{WHAT_WAS_IMPLEMENTED}` - What you just built
- `{PLAN_OR_REQUIREMENTS}` - What it should do
- `{BASE_SHA}` - Starting commit
- `{HEAD_SHA}` - Ending commit
- `{DESCRIPTION}` - Brief summary

**Example dispatch:**

```
Task tool (review:code-reviewer):
  description: "Review Task 2 implementation"
  prompt: |
    Review the implementation against requirements.

    ## Context
    - **What Was Implemented:** Verification and repair functions for index
    - **Requirements/Plan:** Task 2 from docs/plans/deployment-plan.md
    - **Description:** Added verifyIndex() and repairIndex() with 4 issue types

    ## Git Range
    - **Base:** a7981ec
    - **Head:** 3df7661

    First run: git diff --stat a7981ec..3df7661
    Then review against plugins/methodology/review/references/code-review-standards.md
```

**3. Act on feedback:**

- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Minor issues for later
- Push back if reviewer is wrong (with reasoning)

---

## Part 2: Receiving Feedback

Code review requires technical evaluation, not emotional performance.

### The Response Pattern

```
WHEN receiving code review feedback:

1. READ: Complete feedback without reacting
2. UNDERSTAND: Restate requirement in own words (or ask)
3. VERIFY: Check against codebase reality
4. EVALUATE: Technically sound for THIS codebase?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. IMPLEMENT: One item at a time, test each
```

### Forbidden Responses

**NEVER:**

- "You're absolutely right!" (explicit CLAUDE.md violation)
- "Great point!" / "Excellent feedback!" (performative)
- "Let me implement that now" (before verification)

**INSTEAD:**

- Restate the technical requirement
- Ask clarifying questions
- Push back with technical reasoning if wrong
- Just start working (actions > words)

### Handling Unclear Feedback

```
IF any item is unclear:
  STOP - do not implement anything yet
  ASK for clarification on unclear items

WHY: Items may be related. Partial understanding = wrong implementation.
```

### When To Push Back

Push back when:

- Suggestion breaks existing functionality
- Reviewer lacks full context
- Violates YAGNI (unused feature)
- Technically incorrect for this stack
- Legacy/compatibility reasons exist
- Conflicts with architectural decisions

**How to push back:**

- Use technical reasoning, not defensiveness
- Ask specific questions
- Reference working tests/code
- Involve human partner if architectural

### Source-Specific Handling

#### From Human Partner

- **Trusted** - implement after understanding
- **Still ask** if scope unclear
- **No performative agreement**
- **Skip to action** or technical acknowledgment

#### From External Reviewers

```
BEFORE implementing:
  1. Check: Technically correct for THIS codebase?
  2. Check: Breaks existing functionality?
  3. Check: Reason for current implementation?
  4. Check: Works on all platforms/versions?
  5. Check: Does reviewer understand full context?

IF suggestion seems wrong:
  Push back with technical reasoning

IF conflicts with human partner's prior decisions:
  Stop and discuss with human partner first
```

### YAGNI Check

```
IF reviewer suggests "implementing properly":
  grep codebase for actual usage

  IF unused: "This endpoint isn't called. Remove it (YAGNI)?"
  IF used: Then implement properly
```

### Acknowledging Correct Feedback

When feedback IS correct:

```
✅ "Fixed. [Brief description of what changed]"
✅ "Good catch - [specific issue]. Fixed in [location]."
✅ [Just fix it and show in the code]

❌ "You're absolutely right!"
❌ "Great point!"
❌ ANY gratitude expression
```

**Why no thanks:** Actions speak. Just fix it. The code itself shows you heard the feedback.

### Gracefully Correcting Your Pushback

If you pushed back and were wrong:

```
✅ "You were right - I checked [X] and it does [Y]. Implementing now."
✅ "Verified this and you're correct. My initial understanding was wrong because [reason]. Fixing."

❌ Long apology
❌ Defending why you pushed back
❌ Over-explaining
```

State the correction factually and move on.

### When You Can't Easily Verify

If you can't verify the feedback:

```
"I can't verify this without [X]. Should I [investigate/ask/proceed]?"
```

Don't assume the reviewer is right or wrong - state the limitation and ask for direction.

### Signal if Uncomfortable Pushing Back

If you feel uncomfortable pushing back on technically incorrect feedback but know it's wrong:

**Signal phrase:** "Strange things are afoot at the Circle K"

This signals to your human partner that you have technical concerns but are struggling to articulate pushback. They can then dig deeper.

### Implementation Order

```
FOR multi-item feedback:
  1. Clarify anything unclear FIRST
  2. Then implement in this order:
     - Blocking issues (breaks, security)
     - Simple fixes (typos, imports)
     - Complex fixes (refactoring, logic)
  3. Test each fix individually
  4. Verify no regressions
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skip review because "it's simple" | Review early, review often |
| Performative agreement | State requirement or just act |
| Blind implementation | Verify against codebase first |
| Batch without testing | One at a time, test each |
| Avoiding pushback | Technical correctness > comfort |
| Partial implementation | Clarify all items first |

## Integration

**Tool usage:**

- Uses `Task` tool with `review:code-reviewer` subagent type

**Called by:**

- **workflow:subagent-dev** - Review after each task
- **workflow:executing-plans** - Review after each batch

**Pairs with:**

- **core:verification** - Verify claims before requesting final review
