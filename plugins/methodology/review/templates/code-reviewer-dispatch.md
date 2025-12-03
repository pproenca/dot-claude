# Code Review Dispatch Template

Use this template when dispatching the `review:code-reviewer` agent.

## Placeholders

Replace these placeholders when dispatching:

- `{WHAT_WAS_IMPLEMENTED}` - What you just built
- `{PLAN_OR_REQUIREMENTS}` - What it should do (plan file or requirements)
- `{BASE_SHA}` - Starting commit SHA
- `{HEAD_SHA}` - Ending commit SHA
- `{DESCRIPTION}` - Brief summary of the work

## Dispatch Format

```
Task tool (review:code-reviewer):
  description: "Review [brief description]"
  prompt: |
    Review the implementation against requirements.

    ## Context
    - **What Was Implemented:** {WHAT_WAS_IMPLEMENTED}
    - **Requirements/Plan:** {PLAN_OR_REQUIREMENTS}
    - **Description:** {DESCRIPTION}

    ## Git Range
    - **Base:** {BASE_SHA}
    - **Head:** {HEAD_SHA}

    First, run these commands to see the changes:
    ```bash
    git diff --stat {BASE_SHA}..{HEAD_SHA}
    git diff {BASE_SHA}..{HEAD_SHA}
    ```

    Then review against plugins/methodology/review/references/code-review-standards.md
```

---

## Required Output Format

The code-reviewer agent MUST structure its response as follows:

### Review Summary
[2-3 sentences: What was reviewed, scope, and overall impression]

### Plan Alignment
**Requirements Met:**
- [x] Requirement 1: [brief how it was satisfied]
- [ ] Requirement 2: [what's missing]

**Deviations:**
| Planned | Implemented | Assessment |
|---------|-------------|------------|
| [item] | [actual] | Beneficial/Problematic - [reason] |

### Strengths
[3-5 specific positive findings with file:line references]
- `path/file.ts:45-60` - [What's good and why]

### Issues

#### Critical (Must Fix Before Merge)
[Bugs, security issues, data loss risks, broken functionality]

**Issue N:**
- **Location:** `file.ts:123`
- **Problem:** [Specific description]
- **Impact:** [Why this matters]
- **Fix:** [How to resolve]

#### Important (Should Fix)
[Architecture problems, missing tests, poor error handling]
[Same format as Critical]

#### Minor (Suggestions)
[Style, optimization, documentation improvements]
[Same format, but "Fix" becomes "Suggestion"]

### Recommendations
[1-3 forward-looking improvements for future work]

### Assessment

**Ready to merge:** [Yes / No / With fixes]

**Confidence:** [HIGH / MODERATE / LOW]

**Reasoning:** [2-3 sentences explaining verdict]

---

## Example Dispatch

```
Task tool (review:code-reviewer):
  description: "Review Task 2 implementation"
  prompt: |
    Review the implementation against requirements.

    ## Context
    - **What Was Implemented:** Verification and repair functions for conversation index
    - **Requirements/Plan:** Task 2 from docs/plans/2025-01-15-index-recovery.md
    - **Description:** Added verifyIndex() and repairIndex() with 4 issue types

    ## Git Range
    - **Base:** a7981ec
    - **Head:** 3df7661

    First, run these commands to see the changes:
    ```bash
    git diff --stat a7981ec..3df7661
    git diff a7981ec..3df7661
    ```

    Then review against plugins/methodology/review/references/code-review-standards.md
```
