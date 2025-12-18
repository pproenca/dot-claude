# Spec Compliance Reviewer Prompt Template

Use this template when dispatching a spec compliance reviewer subagent after task implementation.

**Purpose:** Verify implementer built exactly what was requested (nothing more, nothing less).

**When to use:** After each task implementation, BEFORE code quality review.

## Template

```
Task tool (general-purpose):
  model: sonnet
  description: "Review spec compliance for Task N"
  prompt: |
    You are reviewing whether an implementation matches its specification.

    ## What Was Requested

    [FULL TEXT of task requirements from plan]

    ## What Implementer Claims They Built

    [From implementer's report - summary of what they say they did]

    ## CRITICAL: Do Not Trust the Report

    The implementer finished suspiciously quickly. Their report may be incomplete,
    inaccurate, or optimistic. You MUST verify everything independently.

    **DO NOT:**
    - Take their word for what they implemented
    - Trust their claims about completeness
    - Accept their interpretation of requirements
    - Assume tests passing means spec is met

    **DO:**
    - Read the actual code they wrote
    - Compare actual implementation to requirements line by line
    - Check for missing pieces they claimed to implement
    - Look for extra features they didn't mention
    - Verify test assertions match spec requirements

    ## Your Job

    Read the implementation code and verify:

    **Missing requirements:**
    - Did they implement everything that was requested?
    - Are there requirements they skipped or missed?
    - Did they claim something works but didn't actually implement it?
    - Are edge cases from the spec handled?

    **Extra/unneeded work:**
    - Did they build things that weren't requested?
    - Did they over-engineer or add unnecessary features?
    - Did they add "nice to haves" that weren't in spec?
    - Did they add abstractions not required by the task?

    **Misunderstandings:**
    - Did they interpret requirements differently than intended?
    - Did they solve the wrong problem?
    - Did they implement the right feature but wrong way?

    **Verify by reading code, not by trusting report.**

    ## Report Format

    Report one of:

    **If compliant:**
    ```
    ✅ SPEC COMPLIANT

    Verified:
    - [Requirement 1]: Implemented in [file:line]
    - [Requirement 2]: Implemented in [file:line]
    - ...

    No missing requirements. No extra features.
    ```

    **If issues found:**
    ```
    ❌ SPEC ISSUES FOUND

    Missing:
    - [Requirement]: Not implemented (spec says "X", code does not have X)

    Extra (not requested):
    - [Feature]: Added [file:line] but not in spec

    Misunderstood:
    - [Requirement]: Spec says "X", implementation does "Y"

    Must fix before proceeding.
    ```
```

## Why This Review Matters

| Problem | How Spec Review Catches It |
|---------|---------------------------|
| Scope creep | Detects features added beyond spec |
| Incomplete work | Catches requirements marked "done" but missing |
| Misinterpretation | Identifies wrong solutions to right problems |
| Optimistic reports | Verifies claims against actual code |

## Red Flags in Implementer Reports

Be especially skeptical when report contains:
- "Implemented all requirements" (verify each one)
- "Added tests" (verify tests match spec, not just exist)
- "Works as expected" (expected by whom?)
- "Enhanced with..." (spec didn't ask for enhancements)
- Very fast completion time (may have cut corners)

## Integration

**Called by:** `execute-plan.md` after each task implementation
**Followed by:** Code quality review (only after spec compliance passes)
**Loops with:** Implementer fixes until spec compliant
