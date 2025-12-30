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

## Validation

1. **Parse flags** from arguments:
   ```
   flags = parse_flags($ARGUMENTS)
   ```

2. **Validate flags**:
   - If any flag is provided that is not `--fix`:
     ```
     Error: Unknown flag '${flag}'

     Valid flags:
     - --fix: Create remediation tasks for issues found
     - (no flag): Run verification only, report issues

     Usage: /verify [--fix]
     ```
     Stop execution.

## Workflow

### Step 1: Identify Files to Verify

If recently modified files exist:
```bash
git diff --name-only HEAD~5 -- '*.py'
```

Otherwise, verify the current working directory.

### Step 2: Launch Verification Agents in Parallel

**CRITICAL**: Include ALL THREE Task tool calls in a SINGLE assistant message for true parallel execution:

```
# In ONE message, invoke all three:

Task(
  description: "Security and patterns review"
  subagent_type: "agentic-workflow:code-reviewer"
  model: opus
  prompt: "Review [files] for security, performance, patterns, test coverage"
  run_in_background: true
)

Task(
  description: "Generalization check"
  subagent_type: "agentic-workflow:anti-overfit-checker"
  model: opus
  prompt: "Check [implementation files only, NO test files] for overfitting"
  run_in_background: true
)

Task(
  description: "Full test suite"
  subagent_type: "agentic-workflow:integration-tester"
  model: opus
  prompt: "Run full test suite, typecheck, lint on [project]"
  run_in_background: true
)
```

### Step 3: Collect Results with TaskOutput

**CRITICAL**: Use TaskOutput to collect results from background agents.

**IMPORTANT**: Collect results in any order, but wait for ALL before synthesizing:

```
# Store the task IDs from Step 2
code_reviewer_id = [id from Task 1]
anti_overfit_id = [id from Task 2]
integration_tester_id = [id from Task 3]

# Wait for each agent to complete and collect results
# The order doesn't matter - they're all running in parallel
result_1 = TaskOutput(task_id: code_reviewer_id, block: true)
result_2 = TaskOutput(task_id: anti_overfit_id, block: true)
result_3 = TaskOutput(task_id: integration_tester_id, block: true)

# Only proceed to Step 4 AFTER all three TaskOutput calls complete
```

All three agents run simultaneously because they're in the same message with `run_in_background: true`.

**Why this pattern works**:
- `run_in_background: true` makes Task return immediately with an agent ID
- All three agents start executing in parallel
- `TaskOutput(block: true)` waits for each to complete
- Results arrive as each finishes (order may vary)

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
