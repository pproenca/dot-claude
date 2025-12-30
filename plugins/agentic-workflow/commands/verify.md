---
description: Run verification layer - launches code-reviewer, anti-overfit-checker, and integration-tester agents
argument-hint: [--fix]
allowed-tools: Task, Bash, Read, Write, Glob
---

# /verify - Verification Layer

Run the verification layer to check implementation quality.

## Input

Arguments: $ARGUMENTS
- `--fix` flag: Create remediation tasks for issues found

## Workflow

### Step 1: Identify Files to Verify

If recently modified files exist:
```bash
git diff --name-only HEAD~5 -- '*.py'
```

Otherwise, verify the current working directory.

### Step 2: Launch Verification Agents in Parallel

Spawn three verification agents simultaneously:

**Agent 1: Code Reviewer**
```
Task tool:
- subagent_type: code-reviewer
- model: opus
- prompt: Review [files] for security, performance, patterns, test coverage
```

**Agent 2: Anti-Overfit Checker**
```
Task tool:
- subagent_type: anti-overfit-checker
- model: opus
- prompt: Check [implementation files only, NO test files] for overfitting
```

**Agent 3: Integration Tester**
```
Task tool:
- subagent_type: integration-tester
- model: opus
- prompt: Run full test suite, typecheck, lint on [project]
```

### Step 3: Collect Results

Wait for all three agents to complete. Collect their reports.

### Step 4: Summarize Findings

```markdown
## Verification Results

### Code Review
- Security: [PASS/ISSUES]
- Performance: [PASS/ISSUES]
- Patterns: [PASS/ISSUES]
- Coverage: [PASS/ISSUES]

### Anti-Overfit Check
- Status: [PASS/ISSUES]
- [Details if issues found]

### Integration Tests
- Tests: [X passing, Y failing]
- Type check: [PASS/FAIL]
- Lint: [PASS/FAIL]

### Summary
[Overall status and recommendations]
```

### Step 5: If --fix Flag Present

For each issue found:
1. Create a remediation task in todo.md
2. Optionally spawn task-executor to fix

```markdown
## Remediation Tasks Added

1. [ ] Fix security issue: [description]
2. [ ] Address overfit: [description]
3. [ ] Fix failing test: [description]
```

## Example Output

```
Running verification layer...

Spawning 3 verification agents in parallel:
- code-reviewer (security, performance, patterns)
- anti-overfit-checker (generalization check)
- integration-tester (tests, types, lint)

=== Results ===

Code Review: PASS
- Security: No issues
- Performance: No issues
- Patterns: Consistent with codebase
- Coverage: 85% (acceptable)

Anti-Overfit Check: PASS
- No hardcoded test values found
- Implementation appears general-purpose

Integration Tests: ISSUES
- Tests: 12 passing, 1 failing
- Type check: PASS
- Lint: 2 warnings

Overall: 1 failing test, 2 lint warnings

Run with --fix to create remediation tasks.
```

## Without Arguments

Run verification on the entire project with default settings.
