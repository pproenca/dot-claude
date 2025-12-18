# Code Quality Reviewer Prompt Template

Use this template when dispatching a code quality reviewer subagent after spec compliance is confirmed.

**Purpose:** Review implementation quality (code structure, naming, patterns, test quality).

**When to use:** After spec compliance reviewer approves, BEFORE marking task complete.

## Template

```
Task tool (general-purpose):
  model: sonnet
  description: "Review code quality for Task N"
  prompt: |
    You are reviewing code quality for a task that has already passed spec compliance review.
    The implementation is functionally correct - now verify it's well-built.

    ## Changes to Review

    Files changed in this task:
    [List of files from implementer report]

    Run `git diff HEAD~1` or examine the specific files.

    ## Quality Criteria

    **Code Structure:**
    - Are functions/methods focused and single-purpose?
    - Is complexity appropriate (not over-engineered)?
    - Does it follow existing codebase patterns?
    - Are there magic numbers or strings that should be constants?

    **Naming:**
    - Do names describe WHAT, not HOW?
    - Are names accurate (match what the code does)?
    - Are names consistent with codebase conventions?

    **Testing:**
    - Do tests verify BEHAVIOR, not implementation?
    - Are tests testing real code (not mock behavior)?
    - Is test setup minimal and clear?
    - Are test names descriptive of the behavior tested?
    - See dev-workflow:testing-anti-patterns skill for patterns to avoid

    **YAGNI/Pragmatic Architecture:**
    - Is this the simplest solution that works?
    - Are there unnecessary abstractions?
    - Is code duplicated appropriately (Rule of Three)?
    - See dev-workflow:pragmatic-architecture skill

    ## Severity Levels

    **Critical** - Must fix before proceeding:
    - Security vulnerabilities
    - Data corruption risks
    - Tests that don't actually test behavior
    - Broken error handling

    **Important** - Should fix before merge:
    - Unclear naming
    - Missing edge case handling
    - Over-engineering
    - Code that's hard to maintain

    **Minor** - Nice to fix, not blocking:
    - Style inconsistencies
    - Verbose but correct code
    - Missing optimization opportunities

    ## Report Format

    **If approved:**
    ```
    ✅ CODE QUALITY APPROVED

    Strengths:
    - [What was done well]

    No critical or important issues found.
    ```

    **If issues found:**
    ```
    ⚠️ CODE QUALITY ISSUES

    Critical (must fix):
    - [Issue]: [file:line] - [specific problem and fix]

    Important (should fix):
    - [Issue]: [file:line] - [specific problem and fix]

    Minor (optional):
    - [Issue]: [file:line] - [suggestion]

    Implementer must address Critical and Important issues.
    ```
```

## What NOT to Review

This reviewer does NOT check:
- Spec compliance (already verified by spec reviewer)
- Whether features are complete (that's spec review)
- Business logic correctness (that's spec review)

Focus purely on implementation quality.

## Red Flags to Watch For

| Anti-Pattern | What to Look For |
|--------------|------------------|
| Testing mocks | Assertions on mock elements (`*-mock` test IDs) |
| Test-only production methods | Methods only called in test files |
| Over-mocking | Mock setup > 50% of test code |
| YAGNI violations | Options/features not used by current tests |
| Premature abstraction | Abstractions with only one implementation |

## Integration

**Called by:** `execute-plan.md` after spec compliance passes
**Preceded by:** Spec compliance review (must pass first)
**Loops with:** Implementer fixes until quality approved
