---
title: {RULE_TITLE}
impact: {IMPACT_LEVEL}
impactDescription: {<=8 words, quantified, e.g., "50% memory reduction" or "O(n) -> O(1)"}
tags: {PREFIX}, {TAG_1}, {TAG_2}, {TAG_3}, {TAG_4}
---

## {RULE_TITLE}

{RULE_EXPLANATION - 1-2 sentences starting with IMPACT, not definition. Example: "This pattern reduces memory by 50% for classes with 1000+ instances." NOT "Memory management is important."}

**Incorrect ({INCORRECT_DESCRIPTION}):**

```{LANGUAGE}
// PROBLEM: {Specific cost with numbers, e.g., "Creates 1,583 module imports, ~2.8s overhead"}
{INCORRECT_CODE}
// {Inline comment explaining why this line is problematic with metrics}
```

**Correct ({CORRECT_DESCRIPTION}):**

```{LANGUAGE}
// SOLUTION: {Quantified improvement, e.g., "Reduces imports to 3, saves 2.7s"}
{CORRECT_CODE}
// {Inline comment explaining why this is better with metrics}
```

**Alternative ({ALTERNATIVE_APPROACH_NAME}):**

```{LANGUAGE}
// {When to prefer this alternative over the primary solution}
{ALTERNATIVE_CODE}
```

**When to use:** {1 sentence describing the ideal scenario for this pattern}

**When NOT to use:** {1 sentence describing contraindications, e.g., "For collections under 100 items where overhead exceeds benefit"}

**Trade-off:** {Optional: What you sacrifice for this optimization, e.g., "Faster initial paint vs potential layout shift"}

{CLOSING_CONTEXT - 1-2 sentences of contextual wisdom. Example: "This optimization is especially valuable when the skipped branch is frequently taken, or when the deferred operation is expensive."}

Reference: [{REFERENCE_TEXT}]({REFERENCE_URL})
