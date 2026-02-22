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
