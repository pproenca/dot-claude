# Placeholder Reference

This document lists every placeholder used in the starter templates. When generating a new skill, replace ALL placeholders with appropriate values.

---

## Naming Placeholders

| Placeholder | Description | Example (React) | Example (C++) |
|-------------|-------------|-----------------|---------------|
| `{LANGUAGE}` | Lowercase language ID for filenames | `react` | `cpp` |
| `{LANGUAGE_DISPLAY}` | Display name with proper casing | `React and Next.js` | `C++` |
| `{SOURCE}` | Organization/authority name | `Vercel Engineering` | `ISO C++ Guidelines` |
| `{MONTH}` | Publication month | `January` | `January` |
| `{YEAR}` | Publication year | `2026` | `2026` |

---

## Metadata Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{RULE_COUNT}` | Total number of rules (40-50) | `43` |
| `{ARTIFACT_TYPE}` | Primary code artifact | `components` / `classes` |
| `{COMMON_PATTERN_1}` | Common task pattern | `data fetching` / `memory allocation` |
| `{PRIMARY_OPTIMIZATION_TARGET}` | Main optimization goal | `bundle size` / `memory usage` |
| `{KEYWORD}` | Example grep keyword | `cache` / `async` |

---

## Trigger Placeholders

| Placeholder | Description |
|-------------|-------------|
| `{TRIGGER_1}` | First trigger context (e.g., "React components") |
| `{TRIGGER_2}` | Second trigger context (e.g., "Next.js pages") |
| `{TRIGGER_3}` | Third trigger context (e.g., "data fetching") |
| `{TRIGGER_4}` | Fourth trigger context (e.g., "bundle optimization") |
| `{TRIGGER_5}` | Fifth trigger context (e.g., "performance improvements") |

---

## Category Placeholders

Each category (1-8) has these placeholders:

| Placeholder | Description |
|-------------|-------------|
| `{CATEGORY_N_NAME}` | Full category name (e.g., "Eliminating Waterfalls") |
| `{CATEGORY_N_ANCHOR}` | URL anchor (kebab-case, e.g., "eliminating-waterfalls") |
| `{CATEGORY_N_PROBLEM_DOMAIN}` | Problem domain for abstract (e.g., "eliminating render waterfalls", "reducing bundle size by 40-70%") |
| `{CATEGORY_N_DESCRIPTION}` | 2-3 sentence explanation for guidelines.md, starting with IMPACT |
| `{CATEGORY_N_DESCRIPTION_SHORT}` | 1 sentence for _sections.md |
| `{PREFIX_N}` | Filename prefix (3-8 chars, e.g., "async", "bundle") |

**Category Impact Mapping (fixed):**
- Category 1: CRITICAL
- Category 2: CRITICAL
- Category 3: HIGH
- Category 4: MEDIUM-HIGH
- Category 5: MEDIUM
- Category 6: MEDIUM
- Category 7: LOW-MEDIUM
- Category 8: LOW

**IMPORTANT: Abstract Problem Domain Examples:**
| [BAD] Category Name Only | [GOOD] Problem Domain Description |
|----------------------|-------------------------------|
| "Type Safety" | "eliminating runtime type errors" |
| "Performance" | "reducing bundle size by 40-70%" |
| "Memory Management" | "preventing 70% of security vulnerabilities" |
| "Testing" | "catching type regressions at compile time" |

---

## Rule Placeholders

Each rule has these placeholders (replace N with category, M with rule number):

| Placeholder | Description |
|-------------|-------------|
| `{RULE_N_M_TITLE}` | Rule title in Title Case |
| `{RULE_N_M_SUMMARY}` | One-line summary for quick reference |
| `{RULE_N_M_EXPLANATION}` | 1-3 sentence explanation |
| `{RULE_N_M_INCORRECT_DESC}` | Brief description of the problem |
| `{RULE_N_M_INCORRECT_CODE}` | Code showing the anti-pattern |
| `{RULE_N_M_CORRECT_DESC}` | Brief description of the solution |
| `{RULE_N_M_CORRECT_CODE}` | Code showing the correct approach |
| `{RULE_N_M_ADDITIONAL_NOTES}` | Optional extra explanation |

---

## Individual Rule File Placeholders

| Placeholder | Description |
|-------------|-------------|
| `{RULE_TITLE}` | Title matching the H2 heading |
| `{IMPACT_LEVEL}` | One of: CRITICAL, HIGH, MEDIUM-HIGH, MEDIUM, LOW-MEDIUM, LOW |
| `{QUANTIFIED_METRIC}` | Specific metric (e.g., "50% memory reduction", "O(n) -> O(1)", "15-70% faster builds") |
| `{PREFIX}` | Category prefix (first tag) |
| `{TAG_1}`, `{TAG_2}`, `{TAG_3}` | Additional searchable tags |
| `{RULE_EXPLANATION}` | 1-3 sentence explanation starting with IMPACT |
| `{INCORRECT_DESCRIPTION}` | Parenthetical problem description |
| `{INCORRECT_CODE}` | Anti-pattern code with PROBLEM: comment |
| `{CORRECT_DESCRIPTION}` | Parenthetical solution description |
| `{CORRECT_CODE}` | Correct implementation with SOLUTION: comment |
| `{ALTERNATIVE_APPROACH_NAME}` | Name of alternative approach (e.g., "union of literal types") |
| `{ALTERNATIVE_CODE}` | Alternative implementation code |
| `{WHEN_TO_USE}` | 1 sentence describing ideal scenario |
| `{WHEN_NOT_TO_USE}` | 1 sentence describing contraindications |
| `{REFERENCE_TEXT}` | Link text for external reference |
| `{REFERENCE_URL}` | URL for external reference |

---

## Reference Placeholders

| Placeholder | Description |
|-------------|-------------|
| `{REFERENCE_1_NAME}` | Primary documentation name |
| `{REFERENCE_1_URL}` | Primary documentation URL |
| `{REFERENCE_2_NAME}` | Framework/language official docs |
| `{REFERENCE_2_URL}` | Framework/language official URL |
| `{REFERENCE_3_NAME}` | Relevant library 1 |
| `{REFERENCE_3_URL}` | Library 1 URL |
| `{REFERENCE_4_NAME}` | Blog post or article |
| `{REFERENCE_4_URL}` | Blog/article URL |
| `{REFERENCE_5_NAME}` | Additional reference |
| `{REFERENCE_5_URL}` | Additional reference URL |

---

## Example: React Best Practices Values

```yaml
# Naming
LANGUAGE: react
LANGUAGE_DISPLAY: React and Next.js
SOURCE: Vercel Engineering
MONTH: January
YEAR: 2026

# Metadata
RULE_COUNT: 43
ARTIFACT_TYPE: components
COMMON_PATTERN_1: data fetching
PRIMARY_OPTIMIZATION_TARGET: bundle size

# Triggers
TRIGGER_1: React components
TRIGGER_2: Next.js pages
TRIGGER_3: data fetching
TRIGGER_4: bundle optimization
TRIGGER_5: performance improvements

# Categories
CATEGORY_1_NAME: Eliminating Waterfalls
PREFIX_1: async
CATEGORY_1_DESCRIPTION: "Waterfalls are the #1 performance killer. Each sequential await adds full network latency. Eliminating them yields the largest gains."

CATEGORY_2_NAME: Bundle Size Optimization
PREFIX_2: bundle
CATEGORY_2_DESCRIPTION: "Reducing initial bundle size improves Time to Interactive and Largest Contentful Paint."

CATEGORY_3_NAME: Server-Side Performance
PREFIX_3: server

CATEGORY_4_NAME: Client-Side Data Fetching
PREFIX_4: client

CATEGORY_5_NAME: Re-render Optimization
PREFIX_5: rerender

CATEGORY_6_NAME: Rendering Performance
PREFIX_6: rendering

CATEGORY_7_NAME: JavaScript Performance
PREFIX_7: js

CATEGORY_8_NAME: Advanced Patterns
PREFIX_8: advanced

# Sample Rule
RULE_1_1_TITLE: Defer Await Until Needed
RULE_1_1_SUMMARY: Move await operations into branches where they're actually used
RULE_1_1_EXPLANATION: "Move `await` operations into the branches where they're actually used to avoid blocking code paths that don't need them."
```

---

## Example: C++ Best Practices Values

```yaml
# Naming
LANGUAGE: cpp
LANGUAGE_DISPLAY: C++
SOURCE: ISO C++ Core Guidelines
MONTH: January
YEAR: 2026

# Metadata
RULE_COUNT: 45
ARTIFACT_TYPE: classes and functions
COMMON_PATTERN_1: memory allocation
PRIMARY_OPTIMIZATION_TARGET: memory usage and execution speed

# Triggers
TRIGGER_1: C++ classes
TRIGGER_2: memory management
TRIGGER_3: STL containers
TRIGGER_4: concurrency patterns
TRIGGER_5: template metaprogramming

# Categories
CATEGORY_1_NAME: Memory Management
PREFIX_1: memory
CATEGORY_1_DESCRIPTION: "Memory errors are the #1 source of security vulnerabilities and crashes. Proper RAII and smart pointer usage eliminates entire classes of bugs."

CATEGORY_2_NAME: Compilation Optimization
PREFIX_2: compile
CATEGORY_2_DESCRIPTION: "Move computation to compile-time where possible. constexpr and templates enable zero-runtime-cost abstractions."

CATEGORY_3_NAME: Concurrency
PREFIX_3: concur

CATEGORY_4_NAME: I/O Performance
PREFIX_4: io

CATEGORY_5_NAME: Container Performance
PREFIX_5: container

CATEGORY_6_NAME: Algorithm Optimization
PREFIX_6: algo

CATEGORY_7_NAME: Cache Optimization
PREFIX_7: cache

CATEGORY_8_NAME: Advanced Patterns
PREFIX_8: advanced
```

---

## Validation

After replacing all placeholders:

1. **No curly braces remain**: `grep -r '{' starter/` should return nothing
2. **All prefixes are consistent**: Prefix in _sections.md matches rule filenames
3. **Impact levels match**: Rule impact matches its category's impact
4. **Code compiles/runs**: All code examples are syntactically valid
5. **Tags include prefix**: First tag in every rule file is the category prefix
