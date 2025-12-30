---
name: anti-abandonment
description: This skill activates when there's risk of incomplete work, premature task completion, context drift, or when phrases like "don't abandon", "complete the task", "finish fully", "premature stop", "all items done" are used. Provides patterns to prevent task abandonment and ensure full completion.
---

# Anti-Abandonment Patterns

Prevent the common failure mode where complex tasks are partially completed with a summary like "I have set up the basic structure..." when work remains.

## The Problem

```
Claude receives complex task
    ↓
Partial implementation
    ↓
Premature summary: "I have set up the basic structure..."
    ↓
Task incomplete
    ↓
User frustrated
```

## Solution Architecture

Five interlocking patterns prevent abandonment:

### 1. Explicit Success Criteria

Every task includes a mandatory completion checklist. Task is complete ONLY when ALL criteria are verified.

```markdown
## Success Criteria
- [ ] All tests pass
- [ ] Type check clean
- [ ] Lint clean
- [ ] All todo.md items marked DONE
- [ ] PR description created
- [ ] Documentation updated
```

**Rule**: Do NOT stop until ALL criteria verified.

### 2. Persistent External State

Claude's internal todo does NOT persist across context compaction.

**Solution**: Use external files.

```bash
# Create external todo
echo "# Task Progress" > todo.md

# Update after each step
# Edit todo.md, change [ ] to [x]

# Before stopping, always check
grep "\[ \]" todo.md  # Find incomplete items
```

**Pattern**:
1. Create todo.md with all tasks
2. Update after completing each step
3. Before claiming done, read todo.md and verify no [ ] remain

### 3. Re-Injection Pattern

Long tasks span 10+ conversation turns. Context drifts from original objective.

**Solution**: Every 5-10 turns, re-inject the original checklist.

```markdown
REMINDER: Re-checking original task checklist.

Reading todo.md...
Found 3 incomplete items:
- [ ] Wire up API endpoints
- [ ] Integration tests
- [ ] Update documentation

Continuing with: Wire up API endpoints
```

**Implementation**:
- Set mental checkpoint every 5-10 turns
- Re-read todo.md and progress.txt
- Explicitly state what you're continuing with

### 4. Verification Subagents

Launch independent agents with FRESH context to review work.

**Why fresh context?** Same context that produced the code may have blind spots. Fresh eyes catch issues.

**Verification agents catch**:
- Hardcoded test values
- Missing edge cases
- Incomplete features
- Security issues
- Performance problems

**Pattern**:
```
Implementation complete
    ↓
Spawn verification subagent with:
  - Implementation code
  - Original requirements
  - NO test files (for anti-overfit)
    ↓
Agent reports issues
    ↓
Create remediation tasks
    ↓
Loop until clean
```

### 5. Stop Hook Enforcement

Claude Code hooks intercept before agent termination.

**The check sequence**:
```
Agent signals completion
    ↓
Stop hook triggers
    ↓
Check: todo.md all done? → No → Continue working
    ↓
Check: Tests pass? → No → Continue working
    ↓
Check: Type check clean? → No → Continue working
    ↓
Check: Lint clean? → No → Continue working
    ↓
All pass → Allow completion
```

**If blocked**: Hook injects message explaining what's incomplete. Agent continues until resolved.

## Failure Modes Addressed

| Failure Mode | Solution |
|--------------|----------|
| Internal todo lost in compaction | External todo.md |
| Context drift from objective | Re-injection pattern |
| Premature "done" claim | Stop hooks |
| Tests pass but overfitted | Verification subagent |
| Errors accumulate unnoticed | PostToolUse hooks |
| Cross-session amnesia | progress.txt |

## Implementation Checklist

When starting any significant task:

1. ✅ Create todo.md with all required items
2. ✅ Create progress.txt with session state
3. ✅ Define explicit success criteria
4. ✅ Plan verification approach

During execution:

5. ✅ Update todo.md after each completed item
6. ✅ Every 5-10 turns, re-read todo.md
7. ✅ Run tests/typecheck/lint frequently
8. ✅ Update progress.txt before any long pause

Before claiming completion:

9. ✅ Read todo.md - any [ ] remaining?
10. ✅ Run full test suite
11. ✅ Run type check
12. ✅ Run lint
13. ✅ Spawn verification if warranted
14. ✅ Update progress.txt with final state

## Anti-Overfit Verification

Special case: tests pass but implementation is overfitted.

**Signs of overfitting**:
- Hardcoded values matching test data
- Magic numbers that happen to pass tests
- Conditionals that only work for test inputs
- Narrow solution that won't generalize

**Prevention**:
```
Spawn anti-overfit checker:
- Give it: implementation code + requirements
- Do NOT give it: test files
- Ask: "Would this work for ANY valid input?"
```

If overfitting detected, create remediation task to generalize the solution.

## Example: Applying All Patterns

```markdown
## Starting Task: Implement User Authentication

### Step 1: Create External State
Created todo.md:
- [ ] Read existing auth code
- [ ] Design token service
- [ ] Implement generate_token
- [ ] Implement validate_token
- [ ] Write unit tests
- [ ] Integration tests
- [ ] Update API docs

Created progress.txt with initial state.

### Step 5: Re-Injection Check
Turn 7 of conversation. Re-reading todo.md...
- [x] Read existing auth code
- [x] Design token service
- [x] Implement generate_token
- [ ] Implement validate_token ← Next
- [ ] Write unit tests
- [ ] Integration tests
- [ ] Update API docs

Continuing with: validate_token implementation

### Step 10: Before Completion
Reading todo.md... All items [x]
Running tests... ✓ Pass
Running typecheck... ✓ Clean
Running lint... ✓ Clean
Spawning verification agent... ✓ No issues

All criteria met. Task complete.
```

---

Apply these patterns consistently to eliminate premature task abandonment.
