---
description: Create detailed implementation plan saved to docs/plans/
argument-hint: [feature] or [@design-doc.md]
allowed-tools: Read, Write, Grep, Glob, Bash, TodoWrite, AskUserQuestion, Task, mcp__plugin_serena_serena, mcp__plugin_serena_serena_*
---

# Write Implementation Plan

Create TDD implementation plan by exploring codebase, resolving ambiguities, and producing executable task list.

## Input

$ARGUMENTS

**If empty:** Use AskUserQuestion to ask what feature to plan.

**If @file referenced:** Read it, use as context.

## Step 1: Explore Codebase

Dispatch code-explorer to survey the codebase:

```claude
Task:
  subagent_type: dev-workflow:code-explorer
  description: "Explore codebase"
  prompt: |
    Survey codebase for [feature]:
    1. Similar features - existing implementations to reference
    2. Integration points - boundaries and dependencies
    3. Testing patterns - conventions and test file locations

    Report 10-15 essential files. Limit to 10 tool calls.
```

After return: Note patterns for Step 3.

## Step 2: Clarify Ambiguities

**Skip if:** Design doc from `/dev-workflow:brainstorm` exists AND is comprehensive.

Identify underspecified aspects:

- Edge cases and error handling
- Integration points
- Scope boundaries

Present using AskUserQuestion (one question at a time, 2-4 options each).

**Wait for answers before Step 3.**

## Step 3: Design Architecture

For complex features (5+ files), dispatch code-architect:

```claude
Task:
  subagent_type: dev-workflow:code-architect
  description: "Design architecture"
  prompt: |
    Design architecture for [feature] using exploration context.

    Present 2 approaches:
    1. Minimal changes - smallest diff, maximum reuse
    2. Clean architecture - best maintainability

    For each: key files, components, trade-offs.
    Recommend one.
```

Use AskUserQuestion to confirm approach.

## Step 4: Write Plan

**CRITICAL:** Save to `docs/plans/YYYY-MM-DD-<feature-name>.md`, NOT to `.claude/plans/`.

### Header

```markdown
# [Feature Name] Implementation Plan

> **Execution:** Use `/dev-workflow:execute-plan docs/plans/[this-file].md` to implement task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences from Step 3]

**Tech Stack:** [Key technologies, libraries, frameworks]

---
```

### Task Structure

Each task MUST be self-contained with bite-sized steps.

**The Golden Rule:**

> **Write plans assuming the executor has zero context and questionable taste.**

They are skilled developers who know almost nothing about:
- This codebase's conventions
- The problem domain
- Good test design
- When to abstract vs duplicate

They will take shortcuts if the plan allows it.

**Step Granularity: 2-5 minutes each**

Each "Step N:" is ONE action:
- "Write the failing test" - one step (2-5 min)
- "Run it to verify failure" - one step (30 sec)
- "Implement minimal code" - one step (2-5 min)
- "Run to verify pass" - one step (30 sec)
- "Commit" - one step (30 sec)

**Why 2-5 minutes matters:**
- Steps that take longer need to be broken down
- Enables accurate progress tracking
- Prevents scope creep within steps
- Makes resume/interrupt easier

````markdown
### Task N: [Component Name]

**Effort:** simple (3-10 tool calls) | standard (10-15) | complex (15-25)

**Files:**
- Create: `exact/path/to/new.py`
- Modify: `exact/path/to/existing.py:50-75`
- Test: `tests/exact/path/test_file.py`

**Step 1: Write the failing test** (2-5 min)

```python
def test_specific_behavior():
    # Arrange
    input_data = {"key": "value"}
    # Act
    result = function_name(input_data)
    # Assert
    assert result == expected_output
```

**Step 2: Run test to verify it fails** (30 sec)

```bash
pytest tests/exact/path/test_file.py::test_specific_behavior -v
```

Expected: FAIL with `[specific error, e.g., "NameError: name 'function_name' is not defined"]`

**Step 3: Write minimal implementation** (2-5 min)

```python
def function_name(input_data):
    # Minimal code to make test pass
    return expected_output
```

**Step 4: Run test to verify it passes** (30 sec)

```bash
pytest tests/exact/path/test_file.py::test_specific_behavior -v
```

Expected: PASS (1 passed)

**Step 5: Commit** (30 sec)

```bash
git add tests/exact/path/test_file.py src/exact/path/module.py
git commit -m "feat(scope): add specific_behavior"
```
````

**What to Document (zero context assumption):**

| Item | Reason |
|------|--------|
| Exact file paths | Not "the auth file" |
| Complete code snippets | Not "add validation" |
| Specific test targets | `::test_name` prevents wrong tests |
| Expected output | Proves test tests the right thing |
| Commit message | Prevents "update" commits |

### Parallel Groups

Tasks with NO file overlap execute in parallel (3-5 per group):

| Task Group | Tasks | Rationale |
|------------|-------|-----------|
| Group 1 | 1, 2, 3 | Independent modules, no file overlap |
| Group 2 | 4, 5 | Both touch shared types, must be serial |
| Group 3 | 6, 7, 8 | Independent tests, no file overlap |

### Final Task

Always include "Code Review" as the final task.

### Save and Commit

```bash
mkdir -p docs/plans
# Write plan content to docs/plans/YYYY-MM-DD-<feature>.md
git add docs/plans/
git commit -m "docs: implementation plan for <feature>"
```

## Step 5: Execution Handoff

Use AskUserQuestion:

```claude
AskUserQuestion:
  header: "Execute"
  question: "Plan saved. How to proceed?"
  multiSelect: false
  options:
    - label: "Execute now"
      description: "Run /dev-workflow:execute-plan immediately"
    - label: "Later"
      description: "Execute manually when ready"
    - label: "Revise plan"
      description: "Adjust the plan first"
```

**If "Execute now":**

```text
/dev-workflow:execute-plan docs/plans/[filename].md
```

**If "Later":**

Report the plan file path for manual execution.

**If "Revise plan":**

Wait for feedback, update plan, return to Step 5.

## Remember

Before finalizing any plan, verify:

- [ ] Exact file paths (not "the auth file")
- [ ] Complete code snippets (not "add validation")
- [ ] Specific test commands with `::test_name` targets
- [ ] Expected output for each verification step
- [ ] "Step N:" labels for each action
- [ ] DRY, YAGNI, TDD, frequent commits
- [ ] ≤3 new files per feature (colocation)
- [ ] No "for future use" abstractions
