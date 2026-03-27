# Distillation Recipe

Distillation takes authoritative knowledge sources and produces progressive-disclosure reference rules. This is the production method for **Library/API Reference** and **Code Quality/Review** skills.

## What Distillation Produces

```
{skill-name}/
├── SKILL.md              # Entry point with category table + quick reference
├── AGENTS.md             # Auto-built TOC (via build-agents-md.js)
├── metadata.json         # discipline: "distillation"
├── references/
│   ├── _sections.md      # Category definitions ordered by impact
│   └── {prefix}-{slug}.md # Individual rules (40+ total)
└── assets/
    └── templates/
        └── _template.md  # Rule authoring guide for extensions
```

## Core Principle: The Cascade Effect

Performance problems earlier in the execution lifecycle have multiplicative impact on all downstream operations. Optimize from the top of the waterfall.

This principle drives everything: category ordering, impact levels, and rule priority.

## Execution Lifecycle Mapping

For any technology, identify the stages from input to output. Problems at earlier stages cascade:

**Web Applications (React/Next.js):**
```
request → network → build → server → serialize → client → hydrate → render → runtime
```

**Systems Programming (C++/Rust/Go):**
```
preprocess → compile → link → load → execute → allocate → compute → I/O
```

**Database Operations:**
```
connect → parse → plan → optimize → execute → fetch → serialize → return
```

**Mobile Applications:**
```
launch → load → layout → render → interact → background → persist
```

**Backend Services (Node.js, Python, Java):**
```
request → route → validate → process → I/O → serialize → respond
```

## Impact Level Framework

| Level | Criteria | Cascade Effect |
|-------|----------|----------------|
| CRITICAL | Affects ALL downstream operations | Everything waits |
| HIGH | Affects MOST downstream operations | Major path blocked |
| MEDIUM-HIGH | Affects specific downstream paths | Partial blocking |
| MEDIUM | Local impact, high frequency | Common but contained |
| LOW-MEDIUM | Micro-optimization, hot paths | Measurable in loops |
| LOW | Edge cases, expert patterns | Specific scenarios |

## Category Derivation Algorithm

1. **Map the execution lifecycle** of the target technology
2. **Identify where mistakes occur** at each stage
3. **Rank by cascade effect** (how much downstream is blocked)
4. **Rank by frequency** (how often developers make this mistake)
5. **Combine into priority ordering**: Impact x Frequency
6. **Name categories** by the problem domain, not the solution

Target: 6-8 categories. Higher-impact categories get more rules (5-8 for CRITICAL, 3-5 for HIGH, 2-4 for MEDIUM/LOW). Total: 40-60 rules.

## Rule Anatomy

### Required Structure

```markdown
---
title: {Action-Oriented Title}
impact: CRITICAL|HIGH|MEDIUM-HIGH|MEDIUM|LOW-MEDIUM|LOW
impactDescription: {quantified impact}
tags: {prefix}, {technique1}, {technique2}
---

## {Title}

{1-3 sentences explaining WHY this matters. Focus on performance implications.}

**Incorrect ({problem label}):**

```{language}
{Bad code — production-realistic, not strawman}
{// Comments explaining the cost}
```

**Correct ({solution label}):**

```{language}
{Good code — minimal diff from incorrect}
{// Comments explaining the benefit}
```

Reference: [{title}]({url})
```

### Optional Sections

| Section | When to Include |
|---------|-----------------|
| `**Alternative ({context}):**` | Multiple valid approaches |
| `**When NOT to use this pattern:**` | Important exceptions exist |
| `**Implementation:**` | Reusable code snippet worth providing |
| `**Benefits:**` | Enumerable advantages |
| `**Common use cases:**` | When listing typical scenarios |
| `**Warning ({context}):**` | Highlighting gotchas |
| `**With {tool}:**` | Tool-specific variation |

### Title Patterns

| Pattern | When | Example |
|---------|------|---------|
| `Avoid {Anti-pattern}` | Prohibiting | Avoid Barrel File Imports |
| `Use {X} for {Y}` | Recommending | Use SWR for Automatic Deduplication |
| `{Verb} {Object} in {Context}` | Contextual | Cache Property Access in Loops |
| `{X} for {Y}` | Tool + use case | Promise.all() for Independent Operations |

### Impact Description Patterns

| Type | Pattern | Example |
|------|---------|---------|
| Multiplier | `N-Mx improvement` | `2-10x improvement` |
| Time | `Nms reduction` | `200-800ms import cost` |
| Complexity | `O(x) to O(y)` | `O(n) to O(1)` |
| Prevention | `prevents {problem}` | `prevents stale closures` |
| Reduction | `reduces {thing} by N%` | `reduces reflows by 80%` |

### Tag Rules

1. First tag MUST be the category prefix
2. Add 2-5 additional tags for techniques, tools, concepts
3. Lowercase, hyphenated for multi-word tags

## Reference Hierarchies

Starting points for category derivation by technology domain.

### Systems Languages (C++, Rust, Go)

| Priority | Category | Prefix | Rationale |
|----------|----------|--------|-----------|
| 1 | Memory Allocation | mem- | Heap vs stack affects everything |
| 2 | Cache Efficiency | cache- | Data locality determines real-world speed |
| 3 | Algorithm Complexity | algo- | O(n) considerations for scalability |
| 4 | Data Structure Selection | ds- | Right container for the job |
| 5 | I/O and Syscall Patterns | io- | Minimize kernel crossings |
| 6 | Concurrency/Threading | conc- | Synchronization overhead |
| 7 | Micro-optimizations | micro- | Branch prediction, vectorization |

### Web Frameworks (React, Vue, Angular)

| Priority | Category | Prefix | Rationale |
|----------|----------|--------|-----------|
| 1 | Network Waterfalls | async- | Sequential requests multiply latency |
| 2 | Bundle/Payload Size | bundle- | Directly affects TTI and LCP |
| 3 | Server-Side Processing | server- | SSR/SSG optimization |
| 4 | Client-Side Data | client- | Caching, deduplication |
| 5 | Rendering Optimization | render- | Virtual DOM, reconciliation |
| 6 | DOM Efficiency | dom- | Batching, layout thrashing |
| 7 | JavaScript Runtime | js- | Micro-optimizations in hot paths |

### Database/Query Systems

| Priority | Category | Prefix | Rationale |
|----------|----------|--------|-----------|
| 1 | Query Plan Optimization | query- | Wrong plan = orders of magnitude slower |
| 2 | Index Utilization | index- | Full scans catastrophic at scale |
| 3 | Connection Management | conn- | Pooling, connection overhead |
| 4 | Transaction Patterns | tx- | Lock contention, isolation |
| 5 | Caching Strategies | cache- | Reduce database load |
| 6 | Data Modeling | model- | Normalization vs denormalization |

### Mobile Development (iOS, Android)

| Priority | Category | Prefix | Rationale |
|----------|----------|--------|-----------|
| 1 | Launch Time | launch- | First impression, retention |
| 2 | Memory Management | mem- | Limited resources, OOM kills |
| 3 | UI Thread | ui- | Janky UI, ANRs |
| 4 | Network Efficiency | net- | Latency, bandwidth constraints |
| 5 | Battery Consumption | battery- | User expectation of all-day |
| 6 | Storage I/O | storage- | Flash wear, read/write |
| 7 | Animation | anim- | 60fps requirement |

### Backend Services (Node.js, Python, Java)

| Priority | Category | Prefix | Rationale |
|----------|----------|--------|-----------|
| 1 | I/O Patterns | io- | Async vs sync, pooling |
| 2 | Memory Management | mem- | GC pressure, heap sizing |
| 3 | Concurrency Model | conc- | Event loop, threads |
| 4 | Serialization | serial- | JSON parsing, protobuf |
| 5 | Caching | cache- | Redis, memoization |
| 6 | Algorithm Efficiency | algo- | O(n) in hot paths |
| 7 | Runtime Tuning | runtime- | JIT, inline caching |

## Source Authority

### Acceptable Sources

| Type | Purpose | Example |
|------|---------|---------|
| Official docs | Authoritative API reference | react.dev, golang.org |
| Tool docs | Library usage | swr.vercel.app |
| GitHub repos | Implementation reference | github.com/... |
| Engineering blogs | Benchmark data + rationale | vercel.com/blog/... |

### Source Criteria

1. **Primary maintainers** — React team for React, Vercel for Next.js
2. **Well-maintained OSS** — Active GitHub, npm downloads
3. **Benchmark-backed claims** — Engineering blogs with data
4. **Production-proven** — Used at scale

### NOT Referenced

- Tutorial sites, Stack Overflow, personal blogs without data, outdated docs

## Generation Workflow

### Full Workflow (recommended)

```
1. Research & Analysis
   - Map execution lifecycle
   - Derive categories
   - Search authoritative sources

2. Planning Checkpoint (user reviews)
   - Display: lifecycle, categories, sources, rule distribution
   - Ask approval via AskUserQuestion
   - Optionally run preflight-validator agent

3. Incremental Generation
   a. Generate references/_sections.md → validate with --sections-only
   b. Generate CRITICAL rules → validate batch
   c. Generate HIGH rules → validate batch
   d. Generate MEDIUM rules → validate batch
   e. Generate LOW rules → validate batch

4. Generate SKILL.md, metadata.json, assets/templates/_template.md

5. Build AGENTS.md
   node ${CLAUDE_PLUGIN_ROOT}/scripts/build-agents-md.js {skill-dir}

6. Validate
   node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js {skill-dir}
   + skill-reviewer agent with distillation RUBRIC.md
```

### Quick Mode

For experienced users who already know the categories:

```
1. Use Reference Hierarchy → generate _sections.md → validate --sections-only
2. Generate all rules in parallel
3. Generate SKILL.md, metadata.json, _template.md
4. Build AGENTS.md
5. Full validation + skill-reviewer
```

Quick mode triggers: "quick generate", "use standard categories", "skip planning", or user provides categories directly.

## Build System

AGENTS.md is BUILT by `build-agents-md.js`, never manually written. It produces a TOC-only navigation document with file links and impact levels (~65 lines vs ~600 with embedded content).

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/build-agents-md.js {skill-dir}
```

Use `--verify-generated` flag in validate-skill.js to detect manual edits.

## Sections File Format

```markdown
# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. {Category Name} ({prefix})

**Impact:** CRITICAL
**Description:** {One sentence why this category matters and its cascade effect}

## 2. {Category Name} ({prefix})

**Impact:** HIGH
**Description:** {One sentence explanation}
```

**IMPORTANT**: Use two trailing spaces after `**Impact:** CRITICAL` for proper markdown line breaks.
