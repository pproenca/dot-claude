# {LANGUAGE_DISPLAY} Best Practices

**Version 0.1.0**
{SOURCE}
{MONTH} {YEAR}

> **Note:**
> This document is mainly for agents and LLMs to follow when maintaining,
> generating, or refactoring {LANGUAGE_DISPLAY} codebases. Humans
> may also find it useful, but guidance here is optimized for automation
> and consistency by AI-assisted workflows.

---

## Abstract

Comprehensive performance optimization guide for {LANGUAGE_DISPLAY} applications, designed for AI agents and LLMs. Contains {RULE_COUNT}+ rules across 8 categories, prioritized by impact from critical ({CATEGORY_1_PROBLEM_DOMAIN}, {CATEGORY_2_PROBLEM_DOMAIN}) to incremental ({CATEGORY_8_PROBLEM_DOMAIN}). Each rule includes detailed explanations, real-world examples comparing incorrect vs. correct implementations, quantified impact metrics (e.g., "50% memory reduction", "O(n) -> O(1)"), and alternative approaches to guide automated refactoring and code generation.

---

## Table of Contents

1. [{CATEGORY_1_NAME}](#1-{CATEGORY_1_ANCHOR}) -- **CRITICAL**
   - 1.1 [{RULE_1_1_TITLE}](#11)
   - 1.2 [{RULE_1_2_TITLE}](#12)
   - 1.3 [{RULE_1_3_TITLE}](#13)
   - 1.4 [{RULE_1_4_TITLE}](#14)
   - 1.5 [{RULE_1_5_TITLE}](#15)
2. [{CATEGORY_2_NAME}](#2-{CATEGORY_2_ANCHOR}) -- **CRITICAL**
   - 2.1 [{RULE_2_1_TITLE}](#21)
   - 2.2 [{RULE_2_2_TITLE}](#22)
   - 2.3 [{RULE_2_3_TITLE}](#23)
   - 2.4 [{RULE_2_4_TITLE}](#24)
   - 2.5 [{RULE_2_5_TITLE}](#25)
3. [{CATEGORY_3_NAME}](#3-{CATEGORY_3_ANCHOR}) -- **HIGH**
   - 3.1 [{RULE_3_1_TITLE}](#31)
   - 3.2 [{RULE_3_2_TITLE}](#32)
   - 3.3 [{RULE_3_3_TITLE}](#33)
   - 3.4 [{RULE_3_4_TITLE}](#34)
4. [{CATEGORY_4_NAME}](#4-{CATEGORY_4_ANCHOR}) -- **MEDIUM-HIGH**
   - 4.1 [{RULE_4_1_TITLE}](#41)
   - 4.2 [{RULE_4_2_TITLE}](#42)
5. [{CATEGORY_5_NAME}](#5-{CATEGORY_5_ANCHOR}) -- **MEDIUM**
   - 5.1 [{RULE_5_1_TITLE}](#51)
   - 5.2 [{RULE_5_2_TITLE}](#52)
   - 5.3 [{RULE_5_3_TITLE}](#53)
   - 5.4 [{RULE_5_4_TITLE}](#54)
   - 5.5 [{RULE_5_5_TITLE}](#55)
   - 5.6 [{RULE_5_6_TITLE}](#56)
6. [{CATEGORY_6_NAME}](#6-{CATEGORY_6_ANCHOR}) -- **MEDIUM**
   - 6.1 [{RULE_6_1_TITLE}](#61)
   - 6.2 [{RULE_6_2_TITLE}](#62)
   - 6.3 [{RULE_6_3_TITLE}](#63)
   - 6.4 [{RULE_6_4_TITLE}](#64)
   - 6.5 [{RULE_6_5_TITLE}](#65)
   - 6.6 [{RULE_6_6_TITLE}](#66)
   - 6.7 [{RULE_6_7_TITLE}](#67)
7. [{CATEGORY_7_NAME}](#7-{CATEGORY_7_ANCHOR}) -- **LOW-MEDIUM**
   - 7.1 [{RULE_7_1_TITLE}](#71)
   - 7.2 [{RULE_7_2_TITLE}](#72)
   - 7.3 [{RULE_7_3_TITLE}](#73)
   - 7.4 [{RULE_7_4_TITLE}](#74)
   - 7.5 [{RULE_7_5_TITLE}](#75)
   - 7.6 [{RULE_7_6_TITLE}](#76)
   - 7.7 [{RULE_7_7_TITLE}](#77)
   - 7.8 [{RULE_7_8_TITLE}](#78)
   - 7.9 [{RULE_7_9_TITLE}](#79)
   - 7.10 [{RULE_7_10_TITLE}](#710)
   - 7.11 [{RULE_7_11_TITLE}](#711)
   - 7.12 [{RULE_7_12_TITLE}](#712)
8. [{CATEGORY_8_NAME}](#8-{CATEGORY_8_ANCHOR}) -- **LOW**
   - 8.1 [{RULE_8_1_TITLE}](#81)
   - 8.2 [{RULE_8_2_TITLE}](#82)

---

## 1. {CATEGORY_1_NAME}

**Impact: CRITICAL**

{CATEGORY_1_DESCRIPTION}

<!-- NOTE: Category descriptions should START with impact, not definition. Example:
     [BAD] "Memory management is fundamental to C++ programming."
     [GOOD] "Memory errors cause 70% of security vulnerabilities. Proper RAII eliminates entire bug classes." -->

### 1.1 {RULE_1_1_TITLE}

{RULE_1_1_EXPLANATION}

**Incorrect ({RULE_1_1_INCORRECT_DESC}):**

```{LANGUAGE}
// PROBLEM: {Explain the specific cost, e.g., "200ms import overhead on cold start"}
{RULE_1_1_INCORRECT_CODE}
```

**Correct ({RULE_1_1_CORRECT_DESC}):**

```{LANGUAGE}
// SOLUTION: {Explain the improvement with metrics}
{RULE_1_1_CORRECT_CODE}
```

**Alternative ({RULE_1_1_ALTERNATIVE_NAME}):**

```{LANGUAGE}
// {When to prefer this alternative over the primary solution}
{RULE_1_1_ALTERNATIVE_CODE}
```

**When NOT to use:** {RULE_1_1_CONTRAINDICATION}

**Trade-off:** {Optional: What you sacrifice, e.g., "Faster paint vs potential layout shift"}

{CLOSING_CONTEXT - 1-2 sentences of contextual wisdom explaining when this optimization is most valuable, edge cases, or caveats. Example: "This optimization is especially valuable when the skipped branch is frequently taken, or when the deferred operation is expensive."}

### 1.2 {RULE_1_2_TITLE}

{Continue pattern for remaining rules...}

---

## 2. {CATEGORY_2_NAME}

**Impact: CRITICAL**

{CATEGORY_2_DESCRIPTION}

{Continue pattern for remaining categories...}

---

## References

1. [{REFERENCE_1_NAME}]({REFERENCE_1_URL})
2. [{REFERENCE_2_NAME}]({REFERENCE_2_URL})
3. [{REFERENCE_3_NAME}]({REFERENCE_3_URL})
4. [{REFERENCE_4_NAME}]({REFERENCE_4_URL})
5. [{REFERENCE_5_NAME}]({REFERENCE_5_URL})
