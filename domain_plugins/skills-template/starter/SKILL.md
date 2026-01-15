---
name: {LANGUAGE}-best-practices
description: {LANGUAGE_DISPLAY} performance optimization guidelines from {SOURCE}. This skill should be used when writing, reviewing, or refactoring {LANGUAGE_DISPLAY} code to ensure optimal performance patterns. Triggers on tasks involving {TRIGGER_1}, {TRIGGER_2}, {TRIGGER_3}, {TRIGGER_4}, {TRIGGER_5}.
---

# {LANGUAGE_DISPLAY} Best Practices

## Overview

Comprehensive performance optimization guide for {LANGUAGE_DISPLAY} applications, containing {RULE_COUNT}+ rules across 8 categories. Rules are prioritized by impact to guide automated refactoring and code generation.

## When to Apply

Reference these guidelines when:
- Writing new {LANGUAGE_DISPLAY} {ARTIFACT_TYPE}
- Implementing {COMMON_PATTERN_1}
- Reviewing code for performance issues
- Refactoring existing {LANGUAGE_DISPLAY} code
- Optimizing {PRIMARY_OPTIMIZATION_TARGET}

## Priority-Ordered Guidelines

Rules are prioritized by impact:

| Priority | Category | Impact |
|----------|----------|--------|
| 1 | {CATEGORY_1_NAME} | CRITICAL |
| 2 | {CATEGORY_2_NAME} | CRITICAL |
| 3 | {CATEGORY_3_NAME} | HIGH |
| 4 | {CATEGORY_4_NAME} | MEDIUM-HIGH |
| 5 | {CATEGORY_5_NAME} | MEDIUM |
| 6 | {CATEGORY_6_NAME} | MEDIUM |
| 7 | {CATEGORY_7_NAME} | LOW-MEDIUM |
| 8 | {CATEGORY_8_NAME} | LOW |

## Quick Reference

<!-- IMPORTANT: Each section below must have <=5 bullets. Total: 20-25 bullets. -->
<!-- Pick the TOP patterns from each category - the rest go in references/ -->

### Critical Patterns (Apply First)

**{CATEGORY_1_NAME}:** <!-- MAX 5 bullets -->
- {RULE_1_1_SUMMARY}
- {RULE_1_2_SUMMARY}
- {RULE_1_3_SUMMARY}
- {RULE_1_4_SUMMARY}
- {RULE_1_5_SUMMARY}

**{CATEGORY_2_NAME}:** <!-- MAX 5 bullets -->
- {RULE_2_1_SUMMARY}
- {RULE_2_2_SUMMARY}
- {RULE_2_3_SUMMARY}
- {RULE_2_4_SUMMARY}
- {RULE_2_5_SUMMARY}

### High-Impact Patterns

<!-- MAX 4 bullets -->
- {RULE_3_1_SUMMARY}
- {RULE_3_2_SUMMARY}
- {RULE_3_3_SUMMARY}
- {RULE_3_4_SUMMARY}

### Medium-Impact Patterns

<!-- MAX 5 bullets - pick best from categories 4, 5, 6 -->
- {RULE_4_1_SUMMARY}
- {RULE_4_2_SUMMARY}
- {RULE_5_1_SUMMARY}
- {RULE_5_2_SUMMARY}
- {RULE_6_1_SUMMARY}

### Lower-Impact Patterns

<!-- MAX 3 bullets - pick best from categories 7, 8 -->
- {RULE_7_1_SUMMARY}
- {RULE_7_2_SUMMARY}
- {RULE_8_1_SUMMARY}

## References

Full documentation with code examples is available in:

- `references/{LANGUAGE}-performance-guidelines.md` - Complete guide with all patterns
- `references/rules/` - Individual rule files organized by category

To look up a specific pattern, grep the rules directory:
```
grep -l "{KEYWORD_1}" references/rules/
grep -l "{KEYWORD_2}" references/rules/
grep -l "{KEYWORD_3}" references/rules/
```

## Rule Categories in `references/rules/`

- `{PREFIX_1}-*` - {CATEGORY_1_NAME} patterns
- `{PREFIX_2}-*` - {CATEGORY_2_NAME} optimization
- `{PREFIX_3}-*` - {CATEGORY_3_NAME} performance
- `{PREFIX_4}-*` - {CATEGORY_4_NAME} patterns
- `{PREFIX_5}-*` - {CATEGORY_5_NAME} optimization
- `{PREFIX_6}-*` - {CATEGORY_6_NAME} performance
- `{PREFIX_7}-*` - {CATEGORY_7_NAME} micro-optimizations
- `{PREFIX_8}-*` - {CATEGORY_8_NAME} patterns
