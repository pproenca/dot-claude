# Skill Overhaul Implementation Plan

> **Execution:** Use `/dev-workflow:execute-plan docs/plans/2026-02-22-skill-overhaul.md` to implement task-by-task.

**Goal:** Rewrite all dev-workflow skills to be concise, remove persuasion psychology, add few-shot examples, collapse agent review, and replace persuasion reference with prompt engineering guide.

**Architecture:** Direct file rewrites. No structural changes to plugin layout — same files, same frontmatter, dramatically shorter content. Three reference files deleted, one replaced. Execute-plan command restructured to remove two-stage review.

**Tech Stack:** Markdown, YAML frontmatter, shell scripts (bats tests)

---

### Task 1: Rewrite getting-started skill

**Files:**
- Modify: `plugins/dev-workflow/skills/getting-started/SKILL.md`

**Step 1: Rewrite the skill**

Replace the entire content of `plugins/dev-workflow/skills/getting-started/SKILL.md` with the following. Keep the frontmatter identical, rewrite the body to ~100 lines:

```markdown
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
```

**Step 2: Verify frontmatter is valid**

```bash
cd plugins/dev-workflow && head -5 skills/getting-started/SKILL.md
```

Expected: YAML frontmatter with `name: getting-started`

**Step 3: Run validation**

```bash
make validate
```

Expected: PASS

**Step 4: Commit**

```bash
git add plugins/dev-workflow/skills/getting-started/SKILL.md
git commit -m "refactor(getting-started): cut from 402 to ~100 lines

Remove duplicate tables, announcement requirement, move detailed
planning methodology to write-plan. Keep skill discovery mapping,
priority order, and condensed planning overview."
```

---

### Task 2: Rewrite test-driven-development skill and delete rationales.md

**Files:**
- Modify: `plugins/dev-workflow/skills/test-driven-development/SKILL.md`
- Delete: `plugins/dev-workflow/skills/test-driven-development/references/rationales.md`

**Step 1: Rewrite the skill**

Replace the entire content of `plugins/dev-workflow/skills/test-driven-development/SKILL.md` with the following (~170 lines):

```markdown
---
name: test-driven-development
description: Use this skill when implementing any feature, bug fix, or plan task. Triggers on "write tests", "add a test", "do TDD", "test-driven", "implement with tests", "implement task", or when dispatched as a subagent for plan execution. Write test first, watch it fail, write minimal code to pass.
allowed-tools: Read, Edit, Bash
---

# Test-Driven Development (TDD)

Write the test first. Watch it fail. Write minimal code to pass.

## The Cycle: Red → Green → Refactor

### RED — Write Failing Test

Write one minimal test showing what should happen.

**Good:**

```typescript
test("retries failed operations 3 times", async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error("fail");
    return "success";
  };

  const result = await retryOperation(operation);

  expect(result).toBe("success");
  expect(attempts).toBe(3);
});
```

Clear name, tests real behavior, one thing.

**Bad:**

```typescript
test("retry works", async () => {
  const mock = jest
    .fn()
    .mockRejectedValueOnce(new Error())
    .mockRejectedValueOnce(new Error())
    .mockResolvedValueOnce("success");
  await retryOperation(mock);
  expect(mock).toHaveBeenCalledTimes(3);
});
```

Vague name, tests mock not code.

Requirements:
- One behavior per test
- Clear name describing behavior
- Real code (mocks only if unavoidable)

### Verify RED — Run and Confirm Failure

```bash
npm test path/to/test.test.ts
```

Confirm:
- Test fails (not errors from typos)
- Failure is because the feature is missing
- If test passes immediately: you're testing existing behavior — fix the test

### GREEN — Minimal Code

Write the simplest code to pass the test. Nothing more.

**Good:**

```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === 2) throw e;
    }
  }
  throw new Error("unreachable");
}
```

**Bad:**

```typescript
async function retryOperation<T>(
  fn: () => Promise<T>,
  options?: {
    maxRetries?: number;
    backoff?: "linear" | "exponential";
    onRetry?: (attempt: number) => void;
  }
): Promise<T> { /* YAGNI */ }
```

Don't add features, refactor other code, or "improve" beyond the test.

### Verify GREEN — Run and Confirm Pass

```bash
npm test path/to/test.test.ts
```

Confirm: test passes, other tests still pass, output clean.

If test fails: fix code, not test. If other tests fail: fix now.

### REFACTOR — Clean Up (Green Only)

Remove duplication, improve names, extract helpers. Keep tests green.

### Repeat

Next failing test for next behavior.

## Why Test-First Matters

Tests written after code pass immediately — proving nothing. You never see them catch the bug they're supposed to catch. Test-first forces you to see the failure, proving the test actually validates behavior.

Tests-after are biased by your implementation: you test what you built, not what's required. Tests-first force edge case discovery before implementing.

If the test is hard to write, the design is telling you something — the interface is too complex.

## Good Tests

| Quality | Good | Bad |
|---------|------|-----|
| Minimal | One thing per test | `test('validates email and domain and whitespace')` |
| Clear | Name describes behavior | `test('test1')` |
| Shows intent | Demonstrates desired API | Obscures what code should do |
| Real code | Tests actual behavior | Tests mock behavior |

## When Stuck

| Problem | Solution |
|---------|----------|
| Don't know how to test | Write wished-for API. Write assertion first. |
| Test too complicated | Design too complicated. Simplify interface. |
| Must mock everything | Code too coupled. Use dependency injection. |
| Test setup huge | Extract helpers. Still complex? Simplify design. |

## Bug Fix Example

**Bug:** Empty email accepted

**RED:**
```typescript
test("rejects empty email", async () => {
  const result = await submitForm({ email: "" });
  expect(result.error).toBe("Email required");
});
```

**Verify RED:** `FAIL: expected 'Email required', got undefined`

**GREEN:**
```typescript
function submitForm(data: FormData) {
  if (!data.email?.trim()) {
    return { error: "Email required" };
  }
  // ...
}
```

**Verify GREEN:** `PASS`

**REFACTOR:** Extract validation for multiple fields if needed.

## Verification Checklist

Before marking work complete:

- [ ] Every new function has a test
- [ ] Watched each test fail before implementing
- [ ] Each test failed for expected reason (feature missing, not typo)
- [ ] Wrote minimal code to pass each test
- [ ] All tests pass, output clean
- [ ] Tests use real code (mocks only if unavoidable)
- [ ] Edge cases and errors covered

## Integration

- **testing-anti-patterns** — reviewing existing test quality
- **systematic-debugging** — write failing test reproducing bug
- **verification-before-completion** — verify tests pass before claiming done
```

**Step 2: Delete the redundant rationales reference**

```bash
rm plugins/dev-workflow/skills/test-driven-development/references/rationales.md
```

If the `references/` directory is now empty:

```bash
rmdir plugins/dev-workflow/skills/test-driven-development/references/ 2>/dev/null || true
```

**Step 3: Run validation**

```bash
make validate
```

Expected: PASS

**Step 4: Commit**

```bash
git add plugins/dev-workflow/skills/test-driven-development/
git commit -m "refactor(tdd): cut from 436 to ~170 lines, delete rationales.md

Remove rationalization tables, fabricated statistics, Iron Law framing,
announcement requirement, dot graph. Keep few-shot examples, condensed
'why test-first' rationale, bug fix walkthrough, verification checklist."
```

---

### Task 3: Rewrite systematic-debugging skill and delete reference files

**Files:**
- Modify: `plugins/dev-workflow/skills/systematic-debugging/SKILL.md`
- Delete: `plugins/dev-workflow/skills/systematic-debugging/references/rationalizations.md`
- Delete: `plugins/dev-workflow/skills/systematic-debugging/references/phase-details.md`

**Step 1: Rewrite the skill**

Replace the entire content of `plugins/dev-workflow/skills/systematic-debugging/SKILL.md` with the following (~100 lines):

```markdown
---
name: systematic-debugging
description: This skill should be used when the user reports a "bug", "not working", "fix this", "debug", "test failing", or when investigating unexpected behavior. Four-phase framework ensuring root cause understanding before attempting solutions.
allowed-tools: Read, Bash, Grep, Skill
---

# Systematic Debugging

Find root cause before attempting fixes. Symptom fixes mask underlying issues.

## The Four Phases

### Phase 1: Root Cause Investigation

Before attempting any fix:

1. **Read error messages carefully** — they often contain the solution. Read stack traces completely; note line numbers, file paths, error codes.
2. **Reproduce consistently** — exact steps, every time. If not reproducible, gather more data.
3. **Check recent changes** — git diff, new dependencies, config changes, environmental differences.
4. **Trace data flow** — where does the bad value originate? For deep call stack errors, use the **root-cause-tracing** skill.

For multi-component systems, add diagnostic logging at each component boundary before proposing fixes. Log what enters and exits each component.

### Phase 2: Pattern Analysis

1. **Find working examples** — similar working code in the same codebase.
2. **Compare against references** — read reference implementations completely, not skimmed.
3. **Identify differences** — list every difference, however small.
4. **Understand dependencies** — settings, config, environment assumptions.

### Phase 3: Hypothesis and Testing

1. **Form single hypothesis** — "I think X is the root cause because Y."
2. **Test minimally** — smallest possible change, one variable at a time.
3. **Verify** — didn't work? Form new hypothesis. Don't stack fixes.

### Phase 4: Implementation

1. **Create failing test** — simplest reproduction. Use the **test-driven-development** skill.
2. **Implement single fix** — address the root cause. One change at a time. No "while I'm here" improvements.
3. **Verify fix** — test passes, no other tests broken, issue resolved.
4. **If fix doesn't work** — return to Phase 1 with new information. If 3+ fixes have failed, see below.

## When 3+ Fixes Fail: Question Architecture

If each fix reveals a new problem in a different place, this is not a failed hypothesis — it's a wrong architecture.

Stop and question fundamentals:
- Is this pattern fundamentally sound?
- Are we sticking with it through inertia?
- Should we refactor architecture vs. continue fixing symptoms?

Discuss with the user before attempting more fixes. Present findings: "3 fix attempts, each revealed new problem."

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|-----------------|
| 1. Root Cause | Read errors, reproduce, trace | Understand WHAT and WHY |
| 2. Pattern | Find working examples, compare | Identify differences |
| 3. Hypothesis | Form theory, test minimally | Confirmed or new hypothesis |
| 4. Implementation | Create test, fix, verify | Bug resolved, tests pass |

## Red Flags — Stop and Return to Phase 1

- Proposing fixes before tracing data flow
- "Quick fix for now, investigate later"
- "I don't fully understand but this might work"
- Each fix reveals a new problem in a different place
- 3+ failed fix attempts without questioning architecture

## Integration

- **root-cause-tracing** — for deep call stack errors (Phase 1)
- **test-driven-development** — for failing test case (Phase 4)
- **defense-in-depth** — add validation layers after fix
- **verification-before-completion** — verify fix before claiming success
```

**Step 2: Delete redundant reference files**

```bash
rm plugins/dev-workflow/skills/systematic-debugging/references/rationalizations.md
rm plugins/dev-workflow/skills/systematic-debugging/references/phase-details.md
rmdir plugins/dev-workflow/skills/systematic-debugging/references/ 2>/dev/null || true
```

**Step 3: Run validation**

```bash
make validate
```

Expected: PASS

**Step 4: Commit**

```bash
git add plugins/dev-workflow/skills/systematic-debugging/
git commit -m "refactor(debugging): cut from 185 to ~100 lines, delete reference files

Remove rationalization table, fabricated statistics, Iron Law framing,
announcement. Fold essential phase-details content into main skill.
Delete rationalizations.md and phase-details.md."
```

---

### Task 4: Rewrite verification-before-completion skill

**Files:**
- Modify: `plugins/dev-workflow/skills/verification-before-completion/SKILL.md`

**Step 1: Rewrite the skill**

Replace the entire content with the following (~70 lines):

```markdown
---
name: verification-before-completion
description: This skill should be used when claiming a task is "done", "complete", "finished", "fixed", "passing", or before committing. Requires running verification commands before making success claims.
allowed-tools: Bash
---

# Verification Before Completion

Run the verification command. Read the output. Then claim the result.

## The Gate

Before claiming any status (done, fixed, passing, ready, complete):

1. **Identify** — what command proves this claim?
2. **Run** — execute the full command (fresh, not cached)
3. **Read** — full output, check exit code, count failures
4. **Verify** — does output confirm the claim?
   - If NO: state actual status with evidence
   - If YES: state claim with evidence
5. **Only then** — make the claim

## When to Apply

Before any completion claim, commit, PR creation, task completion, or moving to next task.

This applies to exact phrases ("tests pass", "done") and implications ("moving on to...", "looks good").

## Agent Report Verification

Do not trust agent success reports. Agents may report partial completion as full, claim tests pass without running them, or be optimistic about their work.

After an agent reports success:
1. Check VCS diff: `git diff HEAD~1`
2. Verify changes exist and match expectations
3. Run verification commands yourself
4. Then report actual state

## Verification Patterns

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags — Stop

- Using "should", "probably", "seems to" before running verification
- Expressing satisfaction before verification ("Done!")
- About to commit without running tests
- Trusting agent success reports without checking diff
- Relying on partial verification

## Integration

- **TDD** — verify RED, verify GREEN
- **finishing-a-development-branch** — verify tests before merge
- **execute-plan** — each task verified before marking complete
```

**Step 2: Run validation**

```bash
make validate
```

Expected: PASS

**Step 3: Commit**

```bash
git add plugins/dev-workflow/skills/verification-before-completion/SKILL.md
git commit -m "refactor(verification): cut from 170 to ~70 lines

Remove rationalization table, fabricated statistics, moral framing,
announcement. Keep gate function, verification patterns, agent
verification, red flags."
```

---

### Task 5: Replace persuasion-principles.md with prompt-engineering.md

**Files:**
- Delete: `plugins/dev-workflow/references/persuasion-principles.md`
- Create: `plugins/dev-workflow/references/prompt-engineering.md`

**Step 1: Delete old file and create new**

Delete `plugins/dev-workflow/references/persuasion-principles.md`.

Create `plugins/dev-workflow/references/prompt-engineering.md` with:

```markdown
# Effective Prompt Engineering for Skills

Techniques that improve model compliance, based on how language models actually process instructions.

## Techniques That Work

### 1. Few-Shot Examples

Show the exact pattern you want, 2-3 times. More effective than paragraphs of explanation.

```markdown
**Good:**
\```typescript
test("rejects empty email", async () => {
  const result = await submitForm({ email: "" });
  expect(result.error).toBe("Email required");
});
\```
Clear name, tests real behavior, one assertion.

**Bad:**
\```typescript
test("test1", async () => {
  const mock = jest.fn();
  await submitForm(mock);
  expect(mock).toHaveBeenCalled();
});
\```
Vague name, tests mock.
```

### 2. Trigger-Action Pairs

"When X happens, do Y" is more effective than general guidelines.

```markdown
✅ "Before claiming tests pass, run the test command and check exit code."
❌ "You should generally verify test results when possible."
```

### 3. Concise Instructions

50 clear lines outperform 400 verbose ones. Every token spent on meta-instruction is a token not available for task context. The model has a finite context window — treat it as a scarce resource.

### 4. Positive Instructions Over Prohibitions

Tell the model what to do, not what to avoid.

```markdown
✅ "Write test first, then implement."
❌ "Never write code before tests."
```

### 5. Tables for Quick Reference

Tables compress information efficiently and are easy for the model to scan.

```markdown
| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test output: 0 failures | "Should pass" |
```

## Anti-Patterns

### Rationalization Tables

Listing excuses and rebuttals teaches the model excuses it might not have considered. Instead: state the rule clearly once.

### Fabricated Statistics

Numbers without citations ("95% fix rate", "60% rework rate") undermine credibility. If a future model detects they're unsourced, the skill loses authority. Instead: state the principle without fake data.

### "YOU MUST" / "No Exceptions" / "Iron Law"

These have no special weight in the model's processing. A clear imperative instruction has the same effect with fewer tokens.

```markdown
✅ "Run tests before claiming they pass."
❌ "YOU MUST run tests. No exceptions. This is the Iron Law."
```

### Announcement Requirements

"Announce: I'm using the TDD skill" wastes generation tokens. The user sees which skill was loaded from tool calls.

### Duplicate Content

The same content in a skill AND a reference file costs double the tokens with consistency risk. Single source of truth.

## Principles Summary

| Principle | Application |
|-----------|-------------|
| Show, don't tell | Few-shot examples over prose |
| Be concise | Cut everything that doesn't change behavior |
| Be specific | Trigger-action pairs over general advice |
| Be positive | What to do, not what to avoid |
| Single source | One place per concept |
```

**Step 2: Run validation**

```bash
make validate
```

Expected: PASS

**Step 3: Commit**

```bash
git add plugins/dev-workflow/references/
git commit -m "refactor(references): replace persuasion-principles with prompt-engineering

Remove Cialdini/Meincke psychology framework. Replace with practical
prompt engineering: few-shot examples, trigger-action pairs, concise
instructions, anti-patterns to avoid."
```

---

### Task 6: Restructure execute-plan command (collapse two-stage review)

**Files:**
- Modify: `plugins/dev-workflow/commands/execute-plan.md`

**Step 1: Rewrite execute-plan.md**

Replace the entire content of `plugins/dev-workflow/commands/execute-plan.md` with the following (~250 lines). Key changes: remove two-stage review, add self-review to task agent template, remove "WRONG Pattern" example, tighten prose:

```markdown
---
description: Execute implementation plan with progress tracking
argument-hint: [plan-file]
allowed-tools: Read, Write, Bash, TaskCreate, TaskUpdate, TaskList, TaskGet, Task, Skill, AskUserQuestion
---

# Execute Plan

Execute implementation plan with TaskCreate/TaskUpdate tracking and mandatory post-completion actions.

## Input

$ARGUMENTS

If empty or file not found: stop with error "Plan file not found or not specified."

## Step 1: Worktree Decision

Check if working in main repo or already in a worktree:

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/worktree-manager.sh"

if is_main_repo; then
  echo "IN_MAIN_REPO=true"
else
  echo "IN_MAIN_REPO=false"
  echo "Already in worktree: $(basename "$(pwd)")"
fi
```

**If already in worktree:** skip creation, proceed to Step 2.

**If in main repo:**

```claude
AskUserQuestion:
  header: "Worktree"
  question: "Create isolated worktree for this work?"
  multiSelect: false
  options:
    - label: "Yes (Recommended)"
      description: "Creates ../repo--branch, switches current session to it"
    - label: "No"
      description: "Work directly in main repo"
```

If yes, create worktree:

```bash
source "${CLAUDE_PLUGIN_ROOT}/scripts/worktree-manager.sh"
PLAN_FILE="$ARGUMENTS"
PLAN_BASENAME="${PLAN_FILE##*/}"
PLAN_BASENAME="${PLAN_BASENAME%.md}"
BRANCH_NAME="$(echo "$PLAN_BASENAME" | sed 's/^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}-//')"
WORKTREE_PATH="$(create_worktree "$BRANCH_NAME")"
cd "$WORKTREE_PATH" && pwd
```

## Step 2: Read Plan and Create Tasks

```bash
PLAN_FILE="$ARGUMENTS"
if [[ ! -f "$PLAN_FILE" ]]; then
  echo "ERROR: Plan file not found: $PLAN_FILE"
  exit 1
fi
grep -E "^### Task [0-9]+(\.[0-9]+)?:" "$PLAN_FILE" | sed 's/^### Task \([0-9.]*\): \(.*\)/Task \1: \2/'
```

Create a task for each plan task using TaskCreate, plus "Code Review" and "Finish Branch" at the end.

Set dependencies with TaskUpdate `addBlockedBy`: tasks touching the same files must have the later blocked by the earlier. Tasks with no file overlap run in parallel.

## Step 3: Execute Tasks

### 3a. Find Executable Tasks

```claude
TaskList  # Shows status and blockedBy for all tasks
```

Identify tasks that are `pending` with all blockers completed.

### 3b. Launch Parallel Tasks

Launch all unblocked tasks in ONE message with `run_in_background: true`:

```claude
Task:
  subagent_type: general-purpose
  model: opus
  description: "Execute Task 1"
  prompt: "[Task content + instructions below]"
  run_in_background: true

Task:
  subagent_type: general-purpose
  model: opus
  description: "Execute Task 3"
  prompt: "[Task content + instructions below]"
  run_in_background: true
```

Mark launched tasks `in_progress` via TaskUpdate.

### 3c. Collect Results

After launching all tasks, collect results:

```claude
TaskOutput:
  task_id: task_1_id
  block: true

TaskOutput:
  task_id: task_3_id
  block: true
```

### 3d. Review and Mark Complete

Review each agent's report. If the report shows clear issues (missing requirements, test failures), dispatch the agent again to fix.

Mark reviewed tasks `completed` via TaskUpdate.

Check TaskList — previously blocked tasks may now be unblocked. Repeat from 3a until all implementation tasks complete.

### Task Agent Prompt Template

If a worktree was created, include `WORKTREE_PATH` so the agent works in the right directory.

```claude
Task:
  subagent_type: general-purpose
  model: opus
  description: "Execute Task [N]"
  prompt: |
    Execute Task [N] from the implementation plan.

    ## Working Directory

    WORKTREE_PATH="{{WORKTREE_PATH}}"

    All bash commands: `cd "$WORKTREE_PATH" && <command>`
    All file paths: absolute, e.g., `{{WORKTREE_PATH}}/src/file.py`

    If WORKTREE_PATH is empty, work in the current directory.

    ## Task Instructions

    [Full task content from plan file]

    ## How to Work

    1. Follow each step exactly as written
    2. After each test step, verify expected output matches
    3. Commit after tests pass
    4. If anything is unclear, ask for clarification — don't guess

    Do not add features not in the spec. Do not skip verification steps.

    ## Self-Review (before reporting back)

    Before reporting, check:

    **Spec compliance:**
    - Did I implement every requirement from the task spec?
    - Did I add anything NOT in the spec?
    - Do test assertions match spec expectations?

    **Code quality:**
    - Functions focused and single-purpose?
    - Names describe WHAT, not HOW?
    - Tests verify behavior, not mocks?
    - Follows existing codebase patterns?

    Fix any issues before reporting.

    ## Report Format

    - What you implemented (specific changes)
    - Files changed (with paths)
    - Test results (command and output)
    - Self-review findings and fixes
  run_in_background: true
```

## Step 4: Post-Completion Actions

After all implementation tasks complete:

### 4a. Code Review

Mark "Code Review" task `in_progress`.

```claude
Task:
  subagent_type: dev-workflow:code-reviewer
  model: opus
  run_in_background: true
  description: "Review all changes"
  prompt: "Review all changes from plan execution. Run: git diff main..HEAD. Focus on cross-cutting concerns and consistency."
```

Collect results with TaskOutput. Process feedback with `Skill("dev-workflow:receiving-code-review")`.

Mark "Code Review" `completed`.

### 4b. Finish Branch

Mark "Finish Branch" task `in_progress`.

Use `Skill("dev-workflow:finishing-a-development-branch")`.

Mark "Finish Branch" `completed`.

## Blocker Handling

If a task fails:

```claude
AskUserQuestion:
  header: "Blocker"
  question: "Task N failed. What to do?"
  multiSelect: false
  options:
    - label: "Retry"
      description: "Re-run the failed task"
    - label: "Skip"
      description: "Continue to next task"
    - label: "Stop"
      description: "Pause workflow, resume later"
```

## Resume

If session ends: re-run `/dev-workflow:execute-plan [plan-file]`. TaskList shows which tasks are complete. Skip completed, continue from first unblocked pending.

- `/dev-workflow:resume` — continue from task state
- `/dev-workflow:abandon` — mark all tasks deleted
```

**Step 2: Run validation**

```bash
make validate
```

Expected: PASS

**Step 3: Commit**

```bash
git add plugins/dev-workflow/commands/execute-plan.md
git commit -m "refactor(execute-plan): collapse two-stage review, cut from 507 to ~250 lines

Remove per-task spec reviewer and quality reviewer agents. Add
self-review checklist to task agent prompt instead. Remove 'WRONG
Pattern' example. Tighten state machine prose."
```

---

### Task 7: Trim testing-anti-patterns skill

**Files:**
- Modify: `plugins/dev-workflow/skills/testing-anti-patterns/SKILL.md`

**Step 1: Remove persuasion patterns**

Remove these sections/patterns from the file:
- Line 9: `**Announce at start:** "I'm using the testing-anti-patterns skill to review this test code."` — delete this line
- Lines 17-23: "The Iron Laws" section with the code block — delete entirely
- Lines 199: `**The Iron Rule:** Mock the COMPLETE data structure...` — replace "Iron Rule" with just the instruction
- Lines 293-301: "Real-World Impact" table — delete entirely

**Step 2: Run validation**

```bash
make validate
```

Expected: PASS

**Step 3: Commit**

```bash
git add plugins/dev-workflow/skills/testing-anti-patterns/SKILL.md
git commit -m "refactor(testing-anti-patterns): remove persuasion framing

Remove announcement, Iron Laws, Iron Rule labels, Real-World Impact
table. Keep all anti-pattern examples and gate functions."
```

---

### Task 8: Trim root-cause-tracing skill

**Files:**
- Modify: `plugins/dev-workflow/skills/root-cause-tracing/SKILL.md`

**Step 1: Remove fabricated statistics and trim**

Remove lines 183-189: "Real-World Impact" section with the fabricated session data.

The rest of the skill is good — concrete examples, no persuasion patterns. Light touch only.

**Step 2: Run validation**

```bash
make validate
```

Expected: PASS

**Step 3: Commit**

```bash
git add plugins/dev-workflow/skills/root-cause-tracing/SKILL.md
git commit -m "refactor(root-cause-tracing): remove fabricated statistics section"
```

---

### Task 9: Update CLAUDE.md and README references

**Files:**
- Modify: `plugins/dev-workflow/CLAUDE.md`
- Modify: `plugins/dev-workflow/README.md` (if it references persuasion-principles.md)

**Step 1: Update CLAUDE.md references**

In `plugins/dev-workflow/CLAUDE.md`, if there are references to `persuasion-principles.md`, update them to `prompt-engineering.md`.

Check for any references to deleted files (`rationales.md`, `rationalizations.md`, `phase-details.md`) and remove them.

**Step 2: Update README.md**

Same — update any references to renamed/deleted files.

**Step 3: Run full validation**

```bash
make check
```

Expected: PASS (all levels)

**Step 4: Commit**

```bash
git add plugins/dev-workflow/CLAUDE.md plugins/dev-workflow/README.md
git commit -m "docs: update references to renamed/deleted files"
```

---

### Task 10: Code Review

Final quality gate. Review all changes across all tasks for consistency and correctness.
