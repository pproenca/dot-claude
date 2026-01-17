# Skill Creator Reference Files

This directory contains reference files from the `react-best-practices` skill that serve as templates and examples for creating new performance skills.

## Directory Structure

```
references/
├── README.md           # This file
├── AGENTS.md           # Compiled example guide
├── QUALITY_CHECKLIST.md # Authoritative validation checklist
├── COMPLETE_EXAMPLE.md # Full React example with all rule samples
├── metadata.json       # Skill metadata example
└── examples/           # Sample rules and templates
    ├── _sections.md    # Section definitions template
    ├── _template.md    # Rule template with frontmatter
    └── {prefix}-*.md   # Sample rules by category
```

## How to Use These References

### 1. Section Definitions ([examples/_sections.md](examples/_sections.md))

Use this as a template for organizing your skill into categories. Key elements:

- **Section numbering**: `## 1. Category Name (prefix)`
- **Impact levels**: CRITICAL → HIGH → MEDIUM → LOW
- **Prefix**: Used for rule file naming (`prefix-slug.md`)

### 2. Rule Template ([examples/_template.md](examples/_template.md))

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

### 3. Metadata ([metadata.json](metadata.json))

Required fields:
- `version`: Semantic version (e.g., "0.1.0")
- `organization`: Who created this skill
- `date`: Publication date
- `technology`: Full technology name
- `abstract`: 2-3 sentence description
- `references`: Array of authoritative URLs

### 4. Sample Rules

The [examples/](examples/) directory contains 12 sample rules covering all impact levels:

| Impact | Rules |
|--------|-------|
| CRITICAL | [async-parallel](examples/async-parallel.md), [async-dependencies](examples/async-dependencies.md), [bundle-barrel-imports](examples/bundle-barrel-imports.md), [bundle-dynamic-imports](examples/bundle-dynamic-imports.md) |
| HIGH | [server-parallel-fetching](examples/server-parallel-fetching.md) |
| MEDIUM-HIGH | [client-swr-dedup](examples/client-swr-dedup.md), [js-tosorted-immutable](examples/js-tosorted-immutable.md) |
| MEDIUM | [server-cache-react](examples/server-cache-react.md), [rerender-memo](examples/rerender-memo.md), [rendering-content-visibility](examples/rendering-content-visibility.md) |
| LOW-MEDIUM | [js-set-map-lookups](examples/js-set-map-lookups.md) |
| LOW | [advanced-use-latest](examples/advanced-use-latest.md) |

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

Use the build script to compile references into a single document:

```bash
node scripts/build-agents-md.js ./skills/your-skill-name
```

This generates `AGENTS.md` from `metadata.json`, `references/_sections.md`, and all rule files in `references/`.

**Note**: The build script supports both the new `references/` structure and legacy `rules/` directories for backwards compatibility.

## Migrating Legacy Skills

Skills generated before the structure refactor use `rules/` instead of `references/`. Use the migrate command to update them:

```
/dev-skill:migrate <skill-path>
```

**What it does:**
- Moves `rules/*.md` → `references/`
- Moves `rules/_template.md` → `assets/templates/`
- Updates SKILL.md links to use markdown format
- Regenerates AGENTS.md with Source Files footer
- Validates migration with 100% checks

**Old structure:**
```
skill/
├── SKILL.md
├── AGENTS.md
├── metadata.json
├── README.md
└── rules/
    ├── _sections.md
    ├── _template.md
    └── {prefix}-{slug}.md
```

**New structure:**
```
skill/
├── SKILL.md
├── AGENTS.md
├── metadata.json
├── README.md
├── references/
│   ├── _sections.md
│   └── {prefix}-{slug}.md
└── assets/
    └── templates/
        └── _template.md
```

**Requirements:**
- Skill must be in a git repo with committed changes
- Migration preserves all content (move, not rewrite)
- Includes migration-judge validation for 100% accuracy
