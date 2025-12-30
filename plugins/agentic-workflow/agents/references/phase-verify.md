# Phase: VERIFY

## Purpose
Run independent verification agents to catch issues the implementers might have missed.

## Set Phase
```bash
echo "VERIFY" > "${STATE_DIR}/workflow-phase"
```

## Activities

### Spawn ALL THREE Verification Agents in ONE Message

**CRITICAL**: Include all three Task calls in a SINGLE assistant message for parallel execution:

```
# All THREE in ONE message
Task(
  description: "Security and patterns review"
  subagent_type: "agentic-workflow:code-reviewer"
  prompt: |
    Review implementation for security, performance, and patterns.
    Files: [list modified files from artifacts]
    Tests: [list test files]
    Focus: OWASP vulnerabilities, N+1 queries, error handling
)

Task(
  description: "Generalization check"
  subagent_type: "agentic-workflow:anti-overfit-checker"
  prompt: |
    Check for overfitting to specific inputs.
    Files: [list modified files - NO TEST FILES]
    Look for: hardcoded values, narrow edge-case handling, magic numbers
)

Task(
  description: "Full test suite"
  subagent_type: "agentic-workflow:integration-tester"
  prompt: |
    Run full test suite, typecheck, lint.
    Commands: uv run pytest, ty check, uv run ruff check
    Report: Pass/fail status for each
)
```

### Collect Results

Wait for all verification agents:
```
review_result = TaskOutput(task_id: reviewer_id, block: true)
overfit_result = TaskOutput(task_id: overfit_id, block: true)
test_result = TaskOutput(task_id: tester_id, block: true)
```

### Evaluate Results

| Verdict | Action |
|---------|--------|
| All pass | Proceed to SYNTHESIZE |
| Minor issues | Create remediation task, return to DELEGATE |
| Major issues | Create multiple remediation tasks, return to DELEGATE |

## Constraints
- Verification agents have FRESH context (no implementation bias)
- Anti-overfit checker does NOT receive test files
- Code reviewer is read-only (no modifications)

## Duration
Target: Verification complete before context reaches 85% usage.

## Transition

If all pass:
```bash
Read("${CLAUDE_PLUGIN_ROOT}/agents/references/phase-synthesize.md")
```

If issues found:
```bash
# Create remediation task packets
# Return to DELEGATE phase
echo "DELEGATE" > "${STATE_DIR}/workflow-phase"
Read("${CLAUDE_PLUGIN_ROOT}/agents/references/phase-delegate.md")
```
