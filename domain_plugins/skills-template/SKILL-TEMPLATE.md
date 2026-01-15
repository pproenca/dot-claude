# Best Practices Skill Template

This template defines the exact structure and content patterns for creating language/framework best practices skills. Follow this template precisely to ensure consistency across all generated skills.

---

## OVERVIEW

A best practices skill consists of **5 required file types** organized in a specific directory structure. The skill provides AI agents with prioritized, actionable guidelines for writing optimal code.

**Target Output:** 40-50 rules across 8 categories, prioritized by impact from CRITICAL to LOW.

---

## DIRECTORY STRUCTURE

```
skills/
  {language}-best-practices/              # Directory name: kebab-case
    SKILL.md                              # Main entry point (REQUIRED)
    references/
      {language}-performance-guidelines.md  # Comprehensive guide (REQUIRED)
      rules/
        _sections.md                      # Category definitions (REQUIRED)
        _template.md                      # Rule template (REQUIRED)
        {prefix}-{rule-name}.md           # Individual rule files (40-50 files)
  {language}-best-practices.zip           # Distribution package (REQUIRED)
```

**Naming Rules:**
- Skill directory: `{language}-best-practices` (e.g., `cpp-best-practices`, `typescript-best-practices`)
- All filenames: kebab-case with `.md` extension
- Rule files: `{category-prefix}-{descriptive-name}.md`

---

## FILE 1: SKILL.md

**Purpose:** Entry point loaded by the AI agent. Must be concise (<150 lines) while providing complete quick reference.

**Critical Requirements:**
- YAML frontmatter with `name` and `description`
- Description must include trigger phrases for when to activate
- Priority table must list all 8 categories with impact levels
- Quick Reference must summarize key rules from each category
- Rule Categories section must document the prefix naming convention

```markdown
---
name: {language}-best-practices
description: {Language/Framework} performance optimization guidelines from {Source/Authority}. This skill should be used when writing, reviewing, or refactoring {Language/Framework} code to ensure optimal performance patterns. Triggers on tasks involving {list 5-7 specific trigger contexts like: components, data fetching, memory management, compilation, etc.}.
---

# {Language/Framework} Best Practices

## Overview

Comprehensive performance optimization guide for {Language/Framework} applications, containing {N}+ rules across 8 categories. Rules are prioritized by impact to guide automated refactoring and code generation.

## When to Apply

Reference these guidelines when:
- Writing new {Language/Framework} {primary artifact type, e.g., "components", "modules", "classes"}
- Implementing {common pattern 1, e.g., "data fetching", "memory allocation", "async operations"}
- Reviewing code for performance issues
- Refactoring existing {Language/Framework} code
- Optimizing {primary optimization target, e.g., "bundle size", "memory usage", "compilation time"}

## Priority-Ordered Guidelines

Rules are prioritized by impact:

| Priority | Category | Impact |
|----------|----------|--------|
| 1 | {Category 1 - Most impactful problem domain} | CRITICAL |
| 2 | {Category 2 - Second most impactful} | CRITICAL |
| 3 | {Category 3 - High impact server/compile-time} | HIGH |
| 4 | {Category 4 - High-medium impact runtime} | MEDIUM-HIGH |
| 5 | {Category 5 - Medium impact optimization} | MEDIUM |
| 6 | {Category 6 - Medium impact optimization} | MEDIUM |
| 7 | {Category 7 - Micro-optimizations} | LOW-MEDIUM |
| 8 | {Category 8 - Advanced/edge cases} | LOW |

## Quick Reference

### Critical Patterns (Apply First)

**{Category 1 Name}:**
- {Rule 1.1 one-line summary - imperative verb + what to do}
- {Rule 1.2 one-line summary}
- {Rule 1.3 one-line summary}
- {Rule 1.4 one-line summary}
- {Rule 1.5 one-line summary}

**{Category 2 Name}:**
- {Rule 2.1 one-line summary}
- {Rule 2.2 one-line summary}
- {Rule 2.3 one-line summary}
- {Rule 2.4 one-line summary}
- {Rule 2.5 one-line summary}

### High-Impact {Category 3 Short Name} Patterns

- {Rule 3.1 one-line summary}
- {Rule 3.2 one-line summary}
- {Rule 3.3 one-line summary}
- {Rule 3.4 one-line summary}

### Medium-Impact {Category 4 Short Name} Patterns

- {Rule 4.1 one-line summary}
- {Rule 5.1 one-line summary}
- {Rule 5.2 one-line summary}
- {Rule 5.3 one-line summary}
- {Rule 5.4 one-line summary}

### {Category 6 Short Name} Patterns

- {Rule 6.1 one-line summary}
- {Rule 6.2 one-line summary}
- {Rule 6.3 one-line summary}
- {Rule 6.4 one-line summary}

### {Category 7 Short Name} Patterns

- {Rule 7.1 one-line summary}
- {Rule 7.2 one-line summary}
- {Rule 7.3 one-line summary}
- {Rule 7.4 one-line summary}

## References

Full documentation with code examples is available in:

- `references/{language}-performance-guidelines.md` - Complete guide with all patterns
- `references/rules/` - Individual rule files organized by category

To look up a specific pattern, grep the rules directory:
```
grep -l "{keyword1}" references/rules/
grep -l "{keyword2}" references/rules/
grep -l "{keyword3}" references/rules/
```

## Rule Categories in `references/rules/`

- `{prefix1}-*` - {Category 1 name} patterns
- `{prefix2}-*` - {Category 2 name} optimization
- `{prefix3}-*` - {Category 3 name} performance
- `{prefix4}-*` - {Category 4 name} patterns
- `{prefix5}-*` - {Category 5 name} optimization
- `{prefix6}-*` - {Category 6 name} performance
- `{prefix7}-*` - {Category 7 name} micro-optimizations
- `{prefix8}-*` - {Category 8 name} patterns
```

---

## FILE 2: references/{language}-performance-guidelines.md

**Purpose:** Comprehensive reference document with all rules, detailed explanations, and code examples. This is the authoritative source.

**Critical Requirements:**
- Version number, source attribution, and date in header
- Note explaining this is optimized for AI agents
- Abstract summarizing scope and structure
- Table of Contents with all sections and subsections
- Each category has impact level and description
- Each rule has Incorrect/Correct code examples
- Code examples must be realistic and production-quality
- References section at end with external links

**Length Target:** 1500-2500 lines depending on rule count

```markdown
# {Language/Framework} Best Practices

**Version 0.1.0**
{Source Organization}
{Month Year}

> **Note:**
> This document is mainly for agents and LLMs to follow when maintaining,
> generating, or refactoring {Language/Framework} codebases at {Organization}. Humans
> may also find it useful, but guidance here is optimized for automation
> and consistency by AI-assisted workflows.

---

## Abstract

Comprehensive performance optimization guide for {Language/Framework} applications, designed for AI agents and LLMs. Contains {N}+ rules across 8 categories, prioritized by impact from critical ({category 1}, {category 2}) to incremental ({category 8}). Each rule includes detailed explanations, real-world examples comparing incorrect vs. correct implementations, and specific impact metrics to guide automated refactoring and code generation.

---

## Table of Contents

1. [{Category 1 Full Name}](#{anchor}) -- **CRITICAL**
   - 1.1 [{Rule 1.1 Title}](#{anchor})
   - 1.2 [{Rule 1.2 Title}](#{anchor})
   - 1.3 [{Rule 1.3 Title}](#{anchor})
   - 1.4 [{Rule 1.4 Title}](#{anchor})
   - 1.5 [{Rule 1.5 Title}](#{anchor})
2. [{Category 2 Full Name}](#{anchor}) -- **CRITICAL**
   - 2.1 [{Rule 2.1 Title}](#{anchor})
   - 2.2 [{Rule 2.2 Title}](#{anchor})
   - 2.3 [{Rule 2.3 Title}](#{anchor})
   - 2.4 [{Rule 2.4 Title}](#{anchor})
   - 2.5 [{Rule 2.5 Title}](#{anchor})
3. [{Category 3 Full Name}](#{anchor}) -- **HIGH**
   - 3.1 [{Rule 3.1 Title}](#{anchor})
   - 3.2 [{Rule 3.2 Title}](#{anchor})
   - 3.3 [{Rule 3.3 Title}](#{anchor})
   - 3.4 [{Rule 3.4 Title}](#{anchor})
4. [{Category 4 Full Name}](#{anchor}) -- **MEDIUM-HIGH**
   - 4.1 [{Rule 4.1 Title}](#{anchor})
   - 4.2 [{Rule 4.2 Title}](#{anchor})
5. [{Category 5 Full Name}](#{anchor}) -- **MEDIUM**
   - 5.1 [{Rule 5.1 Title}](#{anchor})
   - 5.2 [{Rule 5.2 Title}](#{anchor})
   - 5.3 [{Rule 5.3 Title}](#{anchor})
   - 5.4 [{Rule 5.4 Title}](#{anchor})
   - 5.5 [{Rule 5.5 Title}](#{anchor})
   - 5.6 [{Rule 5.6 Title}](#{anchor})
6. [{Category 6 Full Name}](#{anchor}) -- **MEDIUM**
   - 6.1 [{Rule 6.1 Title}](#{anchor})
   - 6.2 [{Rule 6.2 Title}](#{anchor})
   - 6.3 [{Rule 6.3 Title}](#{anchor})
   - 6.4 [{Rule 6.4 Title}](#{anchor})
   - 6.5 [{Rule 6.5 Title}](#{anchor})
   - 6.6 [{Rule 6.6 Title}](#{anchor})
   - 6.7 [{Rule 6.7 Title}](#{anchor})
7. [{Category 7 Full Name}](#{anchor}) -- **LOW-MEDIUM**
   - 7.1 [{Rule 7.1 Title}](#{anchor})
   - 7.2 [{Rule 7.2 Title}](#{anchor})
   - 7.3 [{Rule 7.3 Title}](#{anchor})
   - 7.4 [{Rule 7.4 Title}](#{anchor})
   - 7.5 [{Rule 7.5 Title}](#{anchor})
   - 7.6 [{Rule 7.6 Title}](#{anchor})
   - 7.7 [{Rule 7.7 Title}](#{anchor})
   - 7.8 [{Rule 7.8 Title}](#{anchor})
   - 7.9 [{Rule 7.9 Title}](#{anchor})
   - 7.10 [{Rule 7.10 Title}](#{anchor})
   - 7.11 [{Rule 7.11 Title}](#{anchor})
   - 7.12 [{Rule 7.12 Title}](#{anchor})
8. [{Category 8 Full Name}](#{anchor}) -- **LOW**
   - 8.1 [{Rule 8.1 Title}](#{anchor})
   - 8.2 [{Rule 8.2 Title}](#{anchor})

---

## 1. {Category 1 Full Name}

**Impact: CRITICAL**

{2-3 sentence explanation of why this category is critical. Explain the fundamental problem and quantify the impact where possible. Example: "Waterfalls are the #1 performance killer. Each sequential await adds full network latency. Eliminating them yields the largest gains."}

### 1.1 {Rule Title}

{1-2 sentence explanation of what the rule addresses and why it matters.}

**Incorrect: {brief description of the problem}**

```{language}
{Realistic code example showing the anti-pattern}
{Include inline comments explaining what's wrong}
{Use realistic variable/function names}
{Show 5-15 lines of code typically}
```

**Correct: {brief description of the solution}**

```{language}
{Realistic code example showing the correct approach}
{Include inline comments explaining why it's better}
{Mirror the structure of the incorrect example where possible}
{Show the transformation clearly}
```

{Optional: Additional example showing a variation or edge case}

**Another example: {variation description}**

```{language}
// Incorrect: {brief description}
{code}

// Correct: {brief description}
{code}
```

{Optional: Closing sentence explaining when this optimization is most valuable or any caveats}

### 1.2 {Rule Title}

{Continue pattern for all rules in category...}

---

## 2. {Category 2 Full Name}

**Impact: CRITICAL**

{Category description...}

{Continue for all 8 categories...}

---

## References

1. [{Primary documentation}]({URL})
2. [{Framework/Language official docs}]({URL})
3. [{Relevant library 1}]({URL})
4. [{Relevant library 2}]({URL})
5. [{Blog post or article 1}]({URL})
6. [{Blog post or article 2}]({URL})
```

---

## FILE 3: references/rules/_sections.md

**Purpose:** Defines all categories, their file prefixes, impact levels, and descriptions. Used as reference for organizing rules.

**Critical Requirements:**
- Section number matches priority (1 = highest priority)
- Prefix in parentheses is the filename prefix for that category's rules
- Impact level must match the main guidelines document
- Description should be 1 sentence explaining the optimization target

```markdown
# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. {Category 1 Full Name} ({prefix1})

**Impact:** CRITICAL
**Description:** {1 sentence explaining why this is critical and what problem domain it addresses.}

## 2. {Category 2 Full Name} ({prefix2})

**Impact:** CRITICAL
**Description:** {1 sentence description.}

## 3. {Category 3 Full Name} ({prefix3})

**Impact:** HIGH
**Description:** {1 sentence description.}

## 4. {Category 4 Full Name} ({prefix4})

**Impact:** MEDIUM-HIGH
**Description:** {1 sentence description.}

## 5. {Category 5 Full Name} ({prefix5})

**Impact:** MEDIUM
**Description:** {1 sentence description.}

## 6. {Category 6 Full Name} ({prefix6})

**Impact:** MEDIUM
**Description:** {1 sentence description.}

## 7. {Category 7 Full Name} ({prefix7})

**Impact:** LOW-MEDIUM
**Description:** {1 sentence description.}

## 8. {Category 8 Full Name} ({prefix8})

**Impact:** LOW
**Description:** {1 sentence description.}
```

---

## FILE 4: references/rules/_template.md

**Purpose:** Template for individual rule files. Copy this when creating new rules.

**Critical Requirements:**
- YAML frontmatter with title, impact, impactDescription, tags
- Title matches the H2 heading exactly
- Impact matches the category's impact level
- impactDescription is a short metric (e.g., "O(n) to O(1)", "50% faster")
- Tags include: category prefix, relevant technologies, pattern type

```markdown
---
title: Rule Title Here
impact: MEDIUM
impactDescription: Optional description of impact (e.g., "20-50% improvement")
tags: tag1, tag2
---

## Rule Title Here

**Impact: MEDIUM (optional impact description)**

Brief explanation of the rule and why it matters. This should be clear and concise, explaining the performance implications.

**Incorrect (description of what's wrong):**

```{language}
// Bad code example here
const bad = example()
```

**Correct (description of what's right):**

```{language}
// Good code example here
const good = example()
```

Reference: [Link to documentation or resource](https://example.com)
```

---

## FILE 5: Individual Rule Files

**Purpose:** Each rule gets its own file for granular loading and searchability.

**File Naming:** `{prefix}-{descriptive-kebab-case-name}.md`

**Examples:**
- `async-defer-await.md` - Category: async, Rule: defer await
- `bundle-barrel-imports.md` - Category: bundle, Rule: barrel imports
- `server-cache-react.md` - Category: server, Rule: cache with React
- `js-set-map-lookups.md` - Category: js, Rule: Set/Map lookups
- `advanced-use-latest.md` - Category: advanced, Rule: useLatest hook

**Critical Requirements:**
- Filename prefix matches category prefix from _sections.md
- YAML frontmatter is complete and accurate
- Tags always include the category prefix as first tag
- Code examples are self-contained and runnable
- Incorrect/Correct examples should be parallel in structure

**Rule File Template (60-100 lines):**

```markdown
---
title: {Descriptive Rule Title - Title Case}
impact: {CRITICAL|HIGH|MEDIUM-HIGH|MEDIUM|LOW-MEDIUM|LOW}
impactDescription: {QUANTIFIED metric, e.g., "50% memory reduction", "O(n) -> O(1)"}
tags: {prefix}, {technology1}, {technology2}, {pattern-type}
---

## {Descriptive Rule Title - matches frontmatter exactly}

{1-3 sentences explaining what this rule addresses. START WITH IMPACT, not definition. Example: "This pattern reduces memory by 50% for classes with 1000+ instances." NOT "Memory management is important."}

**Incorrect ({parenthetical description of the problem}):**

```{language}
// PROBLEM: {Explain the specific cost with numbers, e.g., "Creates 1,583 module imports, ~2.8s overhead"}
{10-20 lines of realistic code showing the anti-pattern}
{Use REAL library names like lucide-react, pydantic, abseil - NOT generic utils/}
// {Inline comment explaining why this line is problematic}
```

**Correct ({parenthetical description of the solution}):**

```{language}
// SOLUTION: {Explain the improvement with metrics}
{10-20 lines of realistic code showing the fix}
{Mirror structure of incorrect example}
// {Inline comment explaining the improvement}
```

**Alternative ({name of alternative approach}):**

```{language}
// {When to prefer this alternative over the primary solution}
{5-10 lines showing alternative approach}
```

**When to use:** {1 sentence describing ideal scenario for this pattern}

**When NOT to use:** {1 sentence describing contraindications, e.g., "For collections under 100 items where overhead exceeds benefit"}

Reference: [{Descriptive link text}]({URL})
```

**Note:** Not every rule needs Alternative and "When NOT to use" sections, but aim for:
- At least 30% of rules have Alternative sections
- At least 20% of rules have "When NOT to use" sections

---

## CATEGORY PREFIX MAPPING

When creating a new skill, define 8 category prefixes. These must be:
- Short (3-8 characters)
- Lowercase
- Descriptive of the category

**React Example (for reference):**

| Category | Prefix | Description |
|----------|--------|-------------|
| Eliminating Waterfalls | `async` | Async operation ordering |
| Bundle Size Optimization | `bundle` | Import and chunk optimization |
| Server-Side Performance | `server` | SSR and data fetching |
| Client-Side Data Fetching | `client` | Browser-side data patterns |
| Re-render Optimization | `rerender` | Component update reduction |
| Rendering Performance | `rendering` | DOM and paint optimization |
| JavaScript Performance | `js` | Language-level optimization |
| Advanced Patterns | `advanced` | Complex patterns and edge cases |

**C++ Example (suggested):**

| Category | Prefix | Description |
|----------|--------|-------------|
| Memory Management | `memory` | Allocation, ownership, RAII |
| Compilation Optimization | `compile` | Templates, constexpr, inlining |
| Concurrency | `concur` | Threading, atomics, locks |
| I/O Performance | `io` | File, network, async I/O |
| Container Performance | `container` | STL containers, iteration |
| Algorithm Optimization | `algo` | Complexity, caching, branching |
| Cache Optimization | `cache` | CPU cache, memory layout |
| Advanced Patterns | `advanced` | Metaprogramming, SFINAE |

**TypeScript Example (suggested):**

| Category | Prefix | Description |
|----------|--------|-------------|
| Async Patterns | `async` | Promises, async/await |
| Module Organization | `module` | Imports, tree-shaking |
| Type System | `types` | Type inference, generics |
| Runtime Performance | `runtime` | Hot paths, micro-opts |
| Build Optimization | `build` | Compilation, bundling |
| Error Handling | `error` | Exceptions, Result types |
| Data Structures | `data` | Collections, immutability |
| Advanced Patterns | `advanced` | Decorators, metaprogramming |

---

## IMPACT LEVEL DEFINITIONS

Use these definitions consistently:

| Impact | Criteria | Typical Improvement |
|--------|----------|---------------------|
| **CRITICAL** | Blocking issues, architectural problems, order-of-magnitude gains | 50-90%+ improvement, seconds saved |
| **HIGH** | Significant performance wins, measurable user impact | 20-50% improvement |
| **MEDIUM-HIGH** | Notable benefits, cumulative gains | 10-30% improvement |
| **MEDIUM** | Good practices, quality-of-life improvements | 5-20% improvement |
| **LOW-MEDIUM** | Micro-optimizations, hot path improvements | 1-10% improvement |
| **LOW** | Edge cases, specific scenarios, advanced patterns | Variable, situational |

---

## RULE DISTRIBUTION GUIDELINES

Aim for this approximate distribution across categories:

| Impact Level | Categories | Rules per Category | Total Rules |
|--------------|------------|-------------------|-------------|
| CRITICAL | 2 | 5 each | 10 |
| HIGH | 1 | 4 | 4 |
| MEDIUM-HIGH | 1 | 2-3 | 2-3 |
| MEDIUM | 2 | 6-7 each | 12-14 |
| LOW-MEDIUM | 1 | 10-12 | 10-12 |
| LOW | 1 | 2-3 | 2-3 |

**Total: 40-46 rules**

---

## CODE EXAMPLE REQUIREMENTS

### General Rules

1. **Realistic code** - Use production-quality patterns, not toy examples
2. **Complete snippets** - Code should be understandable without external context
3. **Parallel structure** - Incorrect/Correct examples should mirror each other
4. **Inline comments** - Explain what's happening and why it matters
5. **Type annotations** - Include types in typed languages
6. **Error handling** - Show realistic error handling where relevant
7. **Real library names** - Use actual packages, not generic `utils/` or `helpers/`

### Real Library Examples (REQUIRED for CRITICAL rules)

CRITICAL rules must reference production libraries to feel grounded in real-world usage. Generic `utils/` or `helpers/` imports signal academic examples rather than battle-tested patterns.

**Language-specific library examples:**

| Language | Production Libraries (USE) | Generic Patterns (AVOID) |
|----------|---------------------------|--------------------------|
| **React/TS** | lucide-react, @mui/material, swr, react-query, zustand, zod | utils/, helpers/, components/shared/ |
| **Python** | pydantic, httpx, sqlalchemy, pytest, FastAPI, typer | utils.py, helpers.py, common.py |
| **C++** | absl::, folly::, Boost, fmt::, spdlog::, nlohmann::json | utils.h, helpers.hpp, common/ |
| **Go** | uber-go/zap, gorilla/mux, stretchr/testify, spf13/cobra | utils/, helpers/, common/ |
| **Rust** | serde, tokio, anyhow, thiserror, clap, tracing | utils.rs, helpers.rs |

**Example transformation:**

```markdown
<!-- [BAD] GENERIC (feels academic) -->
import { formatDate } from '../utils/helpers';
import { Button } from '../components/shared';

<!-- [GOOD] PRODUCTION (feels real) -->
import { format } from 'date-fns';
import { Button } from '@radix-ui/react-button';
```

**Validation:** Grep your CRITICAL rule files for `utils/`, `helpers/`, `common/`. Replace with real library imports.

### Length Guidelines

- Simple rules: 10-15 lines per example
- Complex rules: 15-25 lines per example
- Multi-example rules: 2-3 complete examples
- **Total rule file: 60-100 lines** (not 30-50)

### Comment Style

```{language}
// PROBLEM: {quantified cost, e.g., "200ms import overhead", "O(n^2) complexity"}
{code line}  // {why this is problematic with specific impact}

// SOLUTION: {quantified improvement}
{code line}  // {why this is better with metrics}
```

### impactDescription Requirements

The `impactDescription` field in YAML frontmatter must be **short, punchy, and quantified**. AI agents use this to quickly compare rule impacts.

**Constraint:** <=8 words, with a measurable metric.

| [BAD] Too Verbose / Vague | [GOOD] Short and Quantified |
|------------------------|-------------------------|
| "eliminates memory leaks and dangling pointers" | "prevents 70% of memory bugs" |
| "improves performance significantly" | "40-60% faster load time" |
| "enables tree-shaking for smaller bundles" | "15-70% smaller bundles" |
| "makes the code more efficient" | "O(n) -> O(1) lookup" |
| "reduces memory usage considerably" | "73% memory reduction" |
| "avoids blocking unused code paths" | "avoids blocking unused paths" |
| "improves type safety at compile time" | "catches 5-10 errors per 1000 LoC" |

### Quantified Code Comment Examples

Use specific metrics in code comments (PROBLEM/SOLUTION lines):

| [BAD] Vague Comment | [GOOD] Quantified Comment |
|-----------------|----------------------|
| "improves performance" | "reduces load time by 40-60%" |
| "enables tree-shaking" | "15-70% faster dev boot, 28% faster builds" |
| "more efficient" | "O(n) -> O(1) lookup, 50x faster for 1000+ items" |
| "reduces memory" | "~150 bytes -> ~40 bytes per instance (73% reduction)" |

### Alternative Approaches (Required for 30% of rules)

After the Correct example, include an alternative when applicable:

```markdown
**Alternative (union of literal types):**

```typescript
// Prefer this when the enum is used for type discrimination only
type Direction = 'up' | 'down' | 'left' | 'right';
`` `
```

### When NOT to Use (Required for 20% of rules)

Include contraindications for non-obvious patterns:

```markdown
**When NOT to use:** For collections under 100 items where the O(1) lookup overhead exceeds the O(n) scan benefit.
```

---

## TAG CONVENTIONS

Tags serve as searchable metadata. Include:

1. **Category prefix** (required, first tag)
2. **Primary technology/API** (required)
3. **Pattern type** (required): `optimization`, `caching`, `deduplication`, `async`, `memory`, etc.
4. **Secondary technologies** (optional)
5. **Problem domain** (optional): `performance`, `memory-safety`, `thread-safety`, etc.

**Examples:**
- `async, await, conditional, optimization`
- `bundle, imports, tree-shaking, barrel-files, performance`
- `server, cache, react-cache, deduplication`
- `memory, smart-pointers, raii, ownership`
- `concur, mutex, lock-guard, thread-safety`

---

## ADVANCED QUALITY PATTERNS

These patterns differentiate expert-level skills from structurally complete but shallow ones. Study the examples carefully.

### Closing Context Sentences

Every rule should end with a contextual wisdom sentence that helps AI agents understand **when** and **why** to apply the pattern. This is the "so what?" that connects the technical pattern to real-world decision-making.

**Pattern:** Add 1-2 sentences after the code examples explaining when the optimization is most valuable, edge cases, or trade-offs.

**Examples:**

```markdown
<!-- [GOOD] Ends with contextual wisdom -->
This optimization is especially valuable when the skipped branch is frequently taken,
or when the deferred operation is expensive.

<!-- [GOOD] Explains trade-off -->
Trade-off: Faster initial paint vs potential layout shift. Choose based on your UX priorities.

<!-- [GOOD] Provides frequency guidance -->
Apply this pattern when you have 3+ sequential awaits. For 2 awaits with dependencies,
the overhead of Promise.all() may not justify the complexity.

<!-- [BAD] Ends abruptly after code example -->
[Code example ends, no closing context]
```

**Target:** At least 50% of rules should have closing context sentences.

---

### Trade-off Documentation

Many optimization choices involve trade-offs. Document these explicitly to help AI agents make informed decisions rather than blindly applying patterns.

**Pattern:** Add a "Trade-off:" statement when the optimization sacrifices one quality for another.

**Examples:**

```markdown
<!-- [GOOD] Explicit trade-off -->
**Trade-off:** Faster initial paint vs potential layout shift. Choose based on your UX priorities.

**Trade-off:** Lower memory usage vs increased code complexity. Use for collections >10K items.

**Trade-off:** Compile-time checking vs runtime flexibility. Prefer compile-time unless dynamic dispatch is required.
```

**Target:** At least 20% of rules should document trade-offs.

---

### "Another Example" vs "Alternative"

These serve different purposes:

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **Another example** | Showing a *variation* of the same pattern in a different context | "Another example (with error handling):" |
| **Alternative** | Showing a *different approach* that solves the same problem | "Alternative (compile-time approach):" |

**Examples:**

```markdown
<!-- "Another example" - Same pattern, different context -->
**Another example (with network requests):**
```typescript
// Same defer-await pattern, but with fetch instead of file I/O
```

<!-- "Alternative" - Different approach entirely -->
**Alternative (compile-time const):**
```typescript
// Completely different solution using constexpr instead of runtime cache
```
```

---

### Quantified Code Comments

Comments in code examples should include specific, memorable metrics rather than vague descriptions. This makes examples more compelling and helps AI agents understand magnitude.

**Pattern:** Include specific numbers in PROBLEM and SOLUTION comments.

**Examples:**

| [BAD] Generic Comment | [GOOD] Quantified Comment |
|-------------------|----------------------|
| `// This is slow` | `// Runtime cost: 200-800ms on every cold start` |
| `// Lots of imports` | `// Loads 1,583 modules, takes ~2.8s extra in dev` |
| `// Memory overhead` | `// Each instance: ~150 bytes; with slots: ~40 bytes (73% reduction)` |
| `// Easy to forget` | `// Causes memory leak: 8MB/hour under typical load` |

---

### Problem-First Writing Style

Rule explanations should start with the **impact** of the problem, not a definition or description. This creates urgency and helps AI agents prioritize.

**Examples:**

```markdown
<!-- [BAD] DEFINITION-FIRST (weak) -->
Raw pointers require manual memory management and can lead to issues.

<!-- [GOOD] PROBLEM-FIRST (strong) -->
Raw pointers cause 70% of security vulnerabilities in C++ codebases. Every manual
delete is a potential double-free, and every forgotten delete is a memory leak.

<!-- [BAD] DEFINITION-FIRST (weak) -->
Barrel files re-export modules from a directory.

<!-- [GOOD] PROBLEM-FIRST (strong) -->
Barrel files force bundlers to load every module in the directory--even for a
single import. One `import { Button }` can trigger 1,583 module loads.
```

---

### Inline References

References can appear in two places:
1. **End-of-rule reference:** Standard `Reference: [text](url)` at the rule end
2. **Inline reference:** Embedded within explanations for immediate context

**Pattern:** Use inline references when citing specific documentation within the explanation.

**Example:**

```markdown
The [React docs on useMemo](https://react.dev/reference/react/useMemo) recommend
memoizing expensive calculations, but note that the overhead of memoization itself
can exceed the savings for simple computations.

Reference: [React Performance Optimization](https://react.dev/learn/render-and-commit)
```

---

### Rule File Length Flexibility

**Quality over quantity.** The original guidance of "60-100 lines" is a target, not a requirement.

- **Simple rules:** 30-50 lines if the concept is straightforward
- **Complex rules:** 60-100 lines if alternatives, trade-offs, and edge cases are needed
- **Very complex rules:** Up to 120 lines for multi-faceted patterns

**Key principle:** Every line should add value. Padding rules to meet line counts degrades quality.

---

### Quick Reference Constraints

The Quick Reference section in SKILL.md must remain scannable--it's a summary, not a comprehensive list.

**Hard limits:**
- **Per section:** <=5 bullets maximum
- **Total:** 20-25 bullets across all sections
- **Format:** Every bullet starts with an imperative verb ("Defer", "Use", "Avoid", "Prefer")

**Why this matters:** When Quick Reference exceeds ~25 bullets, it loses its "quick" nature and becomes redundant with the full guidelines. AI agents should be able to scan it in seconds.

**Collapsing guidance:** If a category has 7 rules but only 5 Quick Reference slots, prioritize:
1. CRITICAL/HIGH impact rules first
2. Most frequently applicable patterns
3. Patterns that prevent common mistakes

**Example of collapsing:**

```markdown
<!-- Category has 7 rules, but Quick Reference shows 4: -->
**Memory Management:**
- Prefer unique_ptr for single ownership (covers rules 1.1, 1.2)
- Use RAII for resource management (covers rules 1.3, 1.4, 1.5)
- Avoid raw new/delete in application code (covers rule 1.6)
- Profile before optimizing allocations (rule 1.7)
```

**Validation:** Count your bullets. If any section exceeds 5 or total exceeds 25, collapse patterns.

---

## VALIDATION CHECKLIST

Before finalizing a skill, verify:

### SKILL.md
- [ ] YAML frontmatter has `name` and `description`
- [ ] Description includes 5+ trigger phrases
- [ ] Priority table has exactly 8 categories
- [ ] Impact levels match _sections.md
- [ ] Quick Reference covers all categories
- [ ] **Quick Reference has <=5 bullets per section (total 20-25 bullets)**
- [ ] Rule Categories documents all 8 prefixes
- [ ] Total line count < 150

### {language}-performance-guidelines.md
- [ ] Header has version, source, date
- [ ] Note mentions AI/LLM optimization
- [ ] **Abstract mentions PROBLEM DOMAINS, not just category names**
- [ ] Abstract includes rule count and category count
- [ ] Table of Contents lists all rules
- [ ] Each category has Impact label
- [ ] **Category descriptions START with impact, not definition**
- [ ] Each rule has Incorrect/Correct examples
- [ ] **At least 30% of rules have Alternative sections**
- [ ] **At least 20% of rules have "When NOT to use" sections**
- [ ] **At least 50% of rules have closing context sentences**
- [ ] **At least 20% of rules document trade-offs**
- [ ] References section has 5+ external links
- [ ] Total line count: 1500-2500

### _sections.md
- [ ] 8 sections numbered 1-8
- [ ] Each has prefix in parentheses
- [ ] Impact levels: 2 CRITICAL, 1 HIGH, 1 MEDIUM-HIGH, 2 MEDIUM, 1 LOW-MEDIUM, 1 LOW
- [ ] Descriptions are 1 sentence each

### _template.md
- [ ] YAML frontmatter shows all fields
- [ ] **impactDescription placeholder shows quantified metric example (<=8 words)**
- [ ] **Alternative and "When NOT to use" sections included**
- [ ] **Trade-off placeholder included**
- [ ] **Closing context placeholder included**
- [ ] Code fence uses `{language}` placeholder

### Individual Rules
- [ ] 40-50 rule files total
- [ ] **Rule file length: 30-120 lines (quality over quantity)**
- [ ] Filenames match `{prefix}-{name}.md` pattern
- [ ] YAML frontmatter is complete
- [ ] **impactDescription <=8 words, quantified (e.g., "50% memory reduction", "O(n) -> O(1)")**
- [ ] Title matches H2 heading
- [ ] Impact matches category level
- [ ] Tags include category prefix first (4-5 tags total)
- [ ] Incorrect/Correct examples present
- [ ] **Code comments include quantified metrics (not vague descriptions)**
- [ ] **CRITICAL rules use real library names (not generic utils/)**
- [ ] Code is realistic and complete
- [ ] **Rule explanations start with problem impact, not definitions**

### Category Balance
- [ ] No category has >12 rules
- [ ] No category has <2 rules
- [ ] CRITICAL categories have 5-7 rules each
- [ ] LOW-MEDIUM category has 8-12 rules

---

## EXAMPLE: GENERATING A NEW SKILL

To generate `cpp-best-practices`:

1. **Define categories** based on C++ performance domains
2. **Assign prefixes** (memory, compile, concur, io, container, algo, cache, advanced)
3. **Determine impact levels** for each category
4. **Identify 40-50 rules** distributed across categories
5. **Write SKILL.md** with quick reference to all rules
6. **Write guidelines.md** with full explanations and examples
7. **Write _sections.md** with category definitions
8. **Copy _template.md** with C++ code fence
9. **Create individual rule files** for each rule
10. **Validate** against checklist above
11. **Create zip** for distribution

---

## REFERENCE: react-best-practices STRUCTURE

Use this as the gold standard for any new skill:

```
skills/react-best-practices/
+-- SKILL.md (107 lines)
`-- references/
    +-- react-performance-guidelines.md (1947 lines)
    `-- rules/
        +-- _sections.md (47 lines)
        +-- _template.md (29 lines)
        +-- async-api-routes.md
        +-- async-defer-await.md
        +-- async-dependencies.md
        +-- async-parallel.md
        +-- async-suspense-boundaries.md
        +-- bundle-barrel-imports.md
        +-- bundle-conditional.md
        +-- bundle-defer-third-party.md
        +-- bundle-dynamic-imports.md
        +-- bundle-preload.md
        +-- server-cache-lru.md
        +-- server-cache-react.md
        +-- server-parallel-fetching.md
        +-- server-serialization.md
        +-- client-event-listeners.md
        +-- client-swr-dedup.md
        +-- rerender-defer-reads.md
        +-- rerender-dependencies.md
        +-- rerender-derived-state.md
        +-- rerender-lazy-state-init.md
        +-- rerender-memo.md
        +-- rerender-transitions.md
        +-- rendering-activity.md
        +-- rendering-animate-svg-wrapper.md
        +-- rendering-conditional-render.md
        +-- rendering-content-visibility.md
        +-- rendering-hoist-jsx.md
        +-- rendering-hydration-no-flicker.md
        +-- rendering-svg-precision.md
        +-- js-batch-dom-css.md
        +-- js-cache-function-results.md
        +-- js-cache-property-access.md
        +-- js-cache-storage.md
        +-- js-combine-iterations.md
        +-- js-early-exit.md
        +-- js-hoist-regexp.md
        +-- js-index-maps.md
        +-- js-length-check-first.md
        +-- js-min-max-loop.md
        +-- js-set-map-lookups.md
        +-- js-tosorted-immutable.md
        +-- advanced-event-handler-refs.md
        `-- advanced-use-latest.md
```

**Category Distribution:**
- async: 5 rules (CRITICAL)
- bundle: 5 rules (CRITICAL)
- server: 4 rules (HIGH)
- client: 2 rules (MEDIUM-HIGH)
- rerender: 6 rules (MEDIUM)
- rendering: 7 rules (MEDIUM)
- js: 12 rules (LOW-MEDIUM)
- advanced: 2 rules (LOW)

**Total: 43 rules**

---

## GOLDEN STANDARD COMPARISON

This section shows side-by-side comparisons between expert-level (golden standard) patterns and structurally complete but shallow implementations. Study these to internalize the quality difference.

### Example 1: Rule Explanation Quality

| Aspect | [BAD] Shallow | [GOOD] Golden Standard |
|--------|------------|-------------------|
| **Opening sentence** | "Barrel files re-export modules from a directory." | "Barrel files force bundlers to load every module in the directory--even for a single import. One `import { Button }` can trigger 1,583 module loads." |
| **Why it's better** | Defines the term but doesn't explain impact | Immediately shows the problem with quantified impact |

### Example 2: impactDescription Quality

| Aspect | [BAD] Shallow | [GOOD] Golden Standard |
|--------|------------|-------------------|
| **impactDescription** | "eliminates memory leaks and dangling pointers throughout the codebase" | "prevents 70% of memory bugs" |
| **Word count** | 9 words | 5 words |
| **Quantification** | None (vague "eliminates") | Yes ("70%") |

### Example 3: Code Comment Quality

| Aspect | [BAD] Shallow | [GOOD] Golden Standard |
|--------|------------|-------------------|
| **PROBLEM comment** | `// This approach is slow and inefficient` | `// PROBLEM: Loads 1,583 modules, takes ~2.8s extra in dev` |
| **SOLUTION comment** | `// This is better` | `// SOLUTION: Direct import loads 3 modules, saves 2.7s` |

### Example 4: Closing Context Quality

| Aspect | [BAD] Shallow | [GOOD] Golden Standard |
|--------|------------|-------------------|
| **Rule ending** | [Ends after code example] | "This optimization is especially valuable when the skipped branch is frequently taken, or when the deferred operation is expensive." |
| **Value added** | None | Helps AI agents understand WHEN to apply |

### Example 5: Category Description Quality

| Aspect | [BAD] Shallow | [GOOD] Golden Standard |
|--------|------------|-------------------|
| **Description** | "Memory management is fundamental to C++ programming. Proper patterns ensure stability." | "Memory errors cause 70% of security vulnerabilities. Proper RAII eliminates entire bug classes--no manual cleanup, no leaks, no double-frees." |
| **Why it's better** | Definition-first, vague | Impact-first, quantified, specific benefits |

### Example 6: Quick Reference Bullet Quality

| Aspect | [BAD] Shallow | [GOOD] Golden Standard |
|--------|------------|-------------------|
| **Bullet format** | "Memory Management - use smart pointers" | "Prefer unique_ptr for single ownership" |
| **Why it's better** | Noun-first, generic | Imperative verb, actionable |

### Self-Assessment Checklist

Before finalizing, compare each rule against these golden standard characteristics:

1. **Does my explanation start with impact?**
   - Can a reader understand why they should care in the first sentence?

2. **Is my impactDescription punchy and quantified?**
   - Can it be compared at a glance with other rules?

3. **Do my code comments have specific metrics?**
   - Would a reader remember the numbers?

4. **Does my rule end with contextual wisdom?**
   - Would an AI agent know when/why to apply this pattern?

5. **Do my Quick Reference bullets start with verbs?**
   - Can they be scanned as a todo list?

6. **Do my CRITICAL rules use real libraries?**
   - Would a production developer recognize these imports?
