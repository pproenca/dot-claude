---
description: Regenerate AGENTS.md as a slim TOC-only navigation document
argument-hint: <skill-path>
allowed-tools: Bash, Read
---

# Shrink AGENTS.md Command

Regenerate the AGENTS.md file for a skill as a slim Table of Contents with links to individual rule files, removing embedded content.

## What This Does

Runs the `build-agents-md.js` script which transforms AGENTS.md from a 600+ line document with all rule content embedded into a ~65 line navigation document containing:

- Header, Abstract, Note block
- Table of Contents with **file links** and **impact levels** for each rule
- References section
- Source Files footer

## Usage

```
/dev-skill:shrink <skill-path>
```

**Examples:**
- `/dev-skill:shrink ~/.claude/skills/react-best-practices`
- `/dev-skill:shrink ./my-skill`

## Execution

Run the build script:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/build-agents-md.js" "<skill-path>"
```

The script will:
1. Find rule files in `references/`, `examples/`, or `rules/` directory
2. Generate TOC with links to each rule file
3. Include impact level and description for each rule
4. Output statistics (sections, rules, line count)

## Before/After Example

**Before (embedded content, ~600 lines):**
```markdown
## Table of Contents
1. [Eliminating Waterfalls](#1-eliminating-waterfalls) — **CRITICAL**
   - 1.1 [Dependency-Based Parallelization](#11-dependency-based-parallelization)

---

## 1. Eliminating Waterfalls

**Impact: CRITICAL**

Waterfalls are the #1 performance killer...

### 1.1 Dependency-Based Parallelization

**Impact: CRITICAL (2-10× improvement)**

For operations with partial dependencies...
[full rule content continues for hundreds of lines]
```

**After (TOC-only, ~65 lines):**
```markdown
## Table of Contents
1. [Eliminating Waterfalls](examples/_sections.md#1-eliminating-waterfalls) — **CRITICAL**
   - 1.1 [Dependency-Based Parallelization](examples/async-dependencies.md) — CRITICAL (2-10× improvement)
   - 1.2 [Promise.all() for Independent Operations](examples/async-parallel.md) — CRITICAL (2-10× improvement)
```

## Benefits

- **90% smaller** AGENTS.md file
- **Faster agent parsing** - quick priority scan without scrolling through content
- **Direct navigation** - click to open specific rule file
- **Clear prioritization** - impact level visible for every rule in TOC
