---
title: {RULE_TITLE}
impact: {IMPACT_LEVEL}
impactDescription: {QUANTIFIED_METRIC}
tags: {PREFIX}, {TAG_1}, {TAG_2}, {TAG_3}
---

## {RULE_TITLE}

{RULE_EXPLANATION - 1-2 sentences explaining WHY this matters, starting with the impact. Use declarative language.}

**Incorrect ({INCORRECT_DESCRIPTION}):**

```{LANGUAGE}
// PROBLEM: {Explain the runtime/compile/memory cost with specific numbers}
{INCORRECT_CODE}
// {Inline comment explaining why this line is problematic}
```

**Correct ({CORRECT_DESCRIPTION}):**

```{LANGUAGE}
// SOLUTION: {Explain the improvement with specific numbers}
{CORRECT_CODE}
// {Inline comment explaining why this is better}
```

**Alternative ({ALTERNATIVE_APPROACH_NAME}):**

```{LANGUAGE}
// {Brief comment explaining when to use this alternative}
{ALTERNATIVE_CODE}
```

**When to use:** {1 sentence describing the ideal scenario for this pattern}

**When NOT to use:** {1 sentence describing contraindications, e.g., "When backward compatibility with X is required" or "For collections under 100 items where overhead exceeds benefit"}

Reference: [{REFERENCE_TEXT}]({REFERENCE_URL})
