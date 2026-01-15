# Skill Creator Reference Files

This directory contains reference files from the `react-best-practices` skill that serve as templates and examples for creating new performance skills.

## Directory Structure

```
references/
├── README.md           # This file
├── _sections.md        # Section definitions template
├── _template.md        # Rule template with frontmatter
├── metadata.json       # Skill metadata example
└── rules/              # Sample rules by category
    ├── async-parallel.md           # CRITICAL - Basic Promise.all pattern
    ├── async-dependencies.md       # CRITICAL - Dependency-based parallelization
    ├── bundle-barrel-imports.md    # CRITICAL - Barrel file avoidance
    ├── bundle-dynamic-imports.md   # CRITICAL - Dynamic imports
    ├── server-parallel-fetching.md # HIGH - RSC parallel fetching
    ├── server-cache-react.md       # MEDIUM - React.cache() usage
    ├── client-swr-dedup.md         # MEDIUM-HIGH - SWR deduplication
    ├── rerender-memo.md            # MEDIUM - Memoization patterns
    ├── rendering-content-visibility.md # MEDIUM - CSS content-visibility
    ├── js-tosorted-immutable.md    # MEDIUM-HIGH - Immutable array methods
    ├── js-set-map-lookups.md       # LOW-MEDIUM - Data structure optimization
    └── advanced-use-latest.md      # LOW - useLatest pattern
```

## How to Use These References

### 1. Section Definitions (`_sections.md`)

Use this as a template for organizing your skill into categories. Key elements:

- **Section numbering**: `## 1. Category Name (prefix)`
- **Impact levels**: CRITICAL → HIGH → MEDIUM → LOW
- **Prefix**: Used for rule file naming (`prefix-slug.md`)

### 2. Rule Template (`_template.md`)

Every rule file must follow this structure:

```markdown
---
title: Rule Title Here
impact: MEDIUM
impactDescription: Optional (e.g., "20-50% improvement")
tags: tag1, tag2
---

## Rule Title Here

Explanation of the rule.

**Incorrect (description):**

\`\`\`language
// Bad code
\`\`\`

**Correct (description):**

\`\`\`language
// Good code
\`\`\`
```

### 3. Metadata (`metadata.json`)

Required fields:
- `version`: Semantic version (e.g., "0.1.0")
- `organization`: Who created this skill
- `date`: Publication date
- `technology`: Full technology name
- `abstract`: 2-3 sentence description
- `references`: Array of authoritative URLs

### 4. Sample Rules

The rules directory contains 12 examples covering all impact levels:

| Impact | Rules |
|--------|-------|
| CRITICAL | async-parallel, async-dependencies, bundle-barrel-imports, bundle-dynamic-imports |
| HIGH | server-parallel-fetching |
| MEDIUM-HIGH | client-swr-dedup, js-tosorted-immutable |
| MEDIUM | server-cache-react, rerender-memo, rendering-content-visibility |
| LOW-MEDIUM | js-set-map-lookups |
| LOW | advanced-use-latest |

## Rule Naming Convention

```
{prefix}-{slug}.md
```

- **prefix**: Category identifier from _sections.md (e.g., `async`, `bundle`, `server`)
- **slug**: Kebab-case descriptor (e.g., `parallel`, `barrel-imports`, `dynamic-imports`)

## Quality Checklist

When creating new rules:

- [ ] Frontmatter includes all required fields (title, impact, tags)
- [ ] Title is concise and actionable
- [ ] Explanation is brief but complete
- [ ] Incorrect example shows common anti-pattern
- [ ] Correct example is minimal and clear
- [ ] Code examples use proper syntax highlighting
- [ ] Impact level matches lifecycle position and cascade effect
- [ ] Tags include category prefix and relevant keywords

## Building AGENTS.md

Use the build script to compile rules into a single document:

```bash
node output/build-agents-md.js ./skills/your-skill-name
```

This generates `AGENTS.md` from `metadata.json`, `_sections.md`, and all rule files.
