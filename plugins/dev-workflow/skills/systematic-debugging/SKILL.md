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
