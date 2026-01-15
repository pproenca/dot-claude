# Skill Generator Mental Model

Extracted from reverse-engineering `react-best-practices`.

## Core Principles

### Fundamental Truths (Technology-Agnostic)

1. **Cascade Effect Principle**: Performance problems earlier in the execution lifecycle have multiplicative impact on all downstream operations. Optimize from the top of the waterfall.

2. **Frequency × Severity = Priority**: A common mistake with medium impact may warrant higher priority than a rare mistake with high impact.

3. **Actionable Over Theoretical**: Guidance must include specific code transformations an AI can apply, not abstract principles to "consider."

4. **Progressive Disclosure**: Present information at the level needed. Quick reference for navigation, full detail on demand.

5. **Quantify When Possible**: "2-10× improvement" is better than "significant improvement." Measurements build trust and guide prioritization.

6. **Show Both States**: Always show incorrect→correct transformation. AI learns patterns by contrast.

## Performance Hierarchy Framework

### Execution Lifecycle Mapping

For any technology, identify the stages from input to output:

**Web Applications (React/Next.js):**
```
request → network → build → server → serialize → client → hydrate → render → runtime
```

**Systems Programming (C++/Rust):**
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

### Impact Level Determination

| Level | Criteria | Cascade Effect |
|-------|----------|----------------|
| CRITICAL | Affects ALL downstream operations | Everything waits |
| HIGH | Affects MOST downstream operations | Major path blocked |
| MEDIUM-HIGH | Affects specific downstream paths | Partial blocking |
| MEDIUM | Local impact, high frequency | Common but contained |
| LOW-MEDIUM | Micro-optimization, hot paths | Measurable in loops |
| LOW | Edge cases, expert patterns | Specific scenarios |

### Category Derivation Algorithm

1. **Map the execution lifecycle** of the technology
2. **Identify where mistakes occur** at each stage
3. **Rank by cascade effect** (how much downstream is blocked)
4. **Rank by frequency** (how often developers make this mistake)
5. **Combine into priority ordering**: Impact × Frequency
6. **Name categories** by the problem domain, not the solution

## Structural Patterns

### File Architecture

```
skills/{skill-name}/
├── SKILL.md              # Entry point (~120 lines)
│   ├── frontmatter       # name, description (always loaded)
│   ├── When to Apply     # 5 trigger scenarios
│   ├── Categories table  # Priority, Impact, Prefix
│   ├── Quick Reference   # 1-line per rule by category
│   └── How to Use        # Navigation instructions
├── AGENTS.md             # Compiled (~2000+ lines)
│   ├── Version block     # Version, org, date
│   ├── Note block        # "For agents and LLMs"
│   ├── Abstract          # Summary paragraph
│   ├── TOC               # Linked categories and rules
│   └── Full rules        # All content with sequential IDs
├── metadata.json         # Build metadata
│   ├── version           # Semantic version
│   ├── organization      # Authoring org
│   ├── date              # Last update
│   ├── abstract          # Summary for compilation
│   └── references        # URL list
└── rules/
    ├── _sections.md      # Category definitions
    ├── _template.md      # Rule authoring guide
    └── {prefix}-{slug}.md # Individual rules
```

### Naming Conventions

| Element | Pattern | Example |
|---------|---------|---------|
| Skill name | `{org}-{tech}-best-practices` | `vercel-react-best-practices` |
| Category prefix | 2-10 char abbreviation | `async`, `bundle`, `rerender` |
| Rule filename | `{prefix}-{slug}.md` | `async-defer-await.md` |
| Rule slug | kebab-case action/pattern | `defer-await`, `barrel-imports` |

### Frontmatter Schemas

**SKILL.md:**
```yaml
---
name: {org}-{tech}-best-practices
description: {Tech} performance optimization guidelines from {Org}. This skill should be used when writing, reviewing, or refactoring {Tech} code to ensure optimal performance patterns. Triggers on tasks involving {keywords}.
---
```

**Rule file:**
```yaml
---
title: {Action-Oriented Title}
impact: CRITICAL|HIGH|MEDIUM-HIGH|MEDIUM|LOW-MEDIUM|LOW
impactDescription: {quantified impact}
tags: {prefix}, {technique1}, {technique2}, ...
---
```

## Content Generation Rules

### Rule Anatomy (Required)

```markdown
---
title: {Title}
impact: {LEVEL}
impactDescription: {quantified}
tags: {prefix}, {tags...}
---

## {Title}

**Impact: {LEVEL} ({impactDescription})**

{1-3 sentences explaining why this matters}

**Incorrect ({problem label}):**

```{language}
{bad code}
```

{optional explanation}

**Correct ({solution label}):**

```{language}
{good code}
```

{optional explanation}

Reference: [{title}]({url})
```

### Optional Sections (Add When Applicable)

| Section | When to Include |
|---------|-----------------|
| `**Another example:**` | Multiple patterns to show |
| `**Alternative:**` | Multiple valid approaches |
| `**When NOT to use this pattern:**` | Important exceptions |
| `**Common use cases:**` | Enumerable scenarios |
| `**Important notes:**` | Critical caveats |
| `**Implementation:**` | Reusable code snippet |
| `**With {tool}:**` | Tool-specific variation |

### Impact Description Patterns

| Type | Pattern | Example |
|------|---------|---------|
| Multiplier | `N-M× improvement` | `2-10× improvement` |
| Time | `Nms reduction` | `200-800ms import cost` |
| Complexity | `O(x) to O(y)` | `O(n) to O(1)` |
| Operations | `Nk ops to Mk ops` | `1M ops to 2K ops` |
| Outcome | `{verb}s {result}` | `faster initial paint` |
| Prevention | `prevents {problem}` | `prevents stale closures` |

### Title Patterns

| Pattern | When to Use | Example |
|---------|-------------|---------|
| `Avoid {Anti-pattern}` | Prohibiting a practice | Avoid Barrel File Imports |
| `Use {X} for {Y}` | Recommending tool/pattern | Use SWR for Automatic Deduplication |
| `{Verb} {Object} in {Context}` | Contextual action | Prevent Waterfall Chains in API Routes |
| `{Adjective} {Pattern}` | Naming a pattern | Strategic Suspense Boundaries |
| `{Verb} Based on {Trigger}` | Event-driven | Preload Based on User Intent |
| `{Verb} {Object}` | Direct action | Cache Property Access in Loops |

## Language Patterns

### Tone and Voice

- **Direct**: State facts, not opinions
- **Technical**: Use precise terminology
- **Neutral**: No marketing language
- **Confident**: Avoid hedging ("might", "consider")

### Instructional Phrasing

| Good | Bad |
|------|-----|
| "Use Promise.all()" | "Consider using Promise.all()" |
| "Move await into branches" | "You might want to move await" |
| "Each await adds latency" | "Awaits can potentially add latency" |

## Quality Markers

### What Makes a Skill High-Quality

1. **Measurable impact claims**: Every impact level has justification
2. **Authoritative references**: Official docs and established blogs
3. **Complete transformations**: Every rule shows before/after
4. **Actionable code**: AI can generate from examples
5. **Consistent structure**: Predictable rule format
6. **Progressive disclosure**: Quick reference → full detail

### Red Flags (Low Quality Indicators)

- "Consider using..." (non-committal)
- "It depends..." without specifics
- Missing incorrect example (no contrast)
- Placeholder code (`// ...`, `doSomething()`)
- No impact quantification
- Marketing language ("blazing fast", "revolutionary")
- Categories not ordered by impact
- Inconsistent file naming

---

## Appendix A: Detailed Pattern Extraction

### A.1 Optional Rule Sections

Rules may include these optional sections (add when applicable):

| Section Header | When to Include | Example |
|----------------|-----------------|---------|
| **Implementation:** | When providing reusable code snippet | `useLatest` hook implementation |
| **Usage:** | When showing invocation pattern | LRU cache usage |
| **Alternative:** or **Alternative (context):** | When multiple valid approaches exist | "Alternative (Next.js 13.5+):" |
| **When NOT to use this pattern:** | When rule has important exceptions | Suspense boundary exceptions |
| **Common use cases:** | When listing typical scenarios | `after()` use cases |
| **Important notes:** | When adding critical caveats | `after()` behavior notes |
| **Benefits:** | When enumerating advantages | Functional setState benefits |
| **When to use X:** | When listing inclusion criteria | When to use functional updates |
| **When X is fine:** | When listing safe-to-ignore cases | When direct updates are fine |
| **Warning (context):** | When highlighting gotchas | Global regex mutable state |
| **Browser support:** | When noting compatibility | `toSorted()` browser support |
| **Why this matters in X:** | When explaining framework-specific importance | Why immutability matters in React |
| **For X:** | When showing variants | For immutable data, For mutations |
| **With X:** | When showing tool/platform integration | With Vercel's Fluid Compute |

### A.2 Tag Assignment Pattern

```yaml
tags: {category_prefix}, {technique}, {tool_if_mentioned}, {related_concepts}
```

**Rules:**
- First tag MUST be the category prefix (async, bundle, server, etc.)
- Add 2-5 additional tags covering technique names, tools, anti-patterns
- Use lowercase, hyphenated multi-word tags

**Examples:**
```yaml
# async-parallel.md
tags: async, parallelization, promises, waterfalls

# bundle-barrel-imports.md
tags: bundle, imports, tree-shaking, barrel-files, performance

# js-tosorted-immutable.md
tags: javascript, arrays, immutability, react, state, mutation
```

### A.3 Rule Title Patterns

| Pattern | When to Use | Example |
|---------|-------------|---------|
| Avoid + Anti-pattern | Prohibiting a practice | Avoid Barrel File Imports |
| Use X for Y | Recommending a tool/pattern | Use SWR for Automatic Deduplication |
| Verb + Object + Context | Contextual action | Prevent Waterfall Chains in API Routes |
| Adjective + Concept | Naming a pattern | Strategic Suspense Boundaries |
| Verb + Based on Trigger | Event-driven action | Preload Based on User Intent |
| Verb + Object | Direct action | Cache Property Access in Loops |
| X for Y | Tool + use case | Promise.all() for Independent Operations |

### A.4 "When to Apply" Derivation

Derive 5 scenarios following this pattern:

1. **Core creation activity**: "Writing new {technology} code/components"
2. **Category-specific activity 1**: Map to highest-impact category
3. **Category-specific activity 2**: Map to second-highest category
4. **Review activity**: "Reviewing code for performance issues"
5. **Refactoring activity**: "Refactoring existing {technology} code"

---

## Appendix B: Build System Specification

### B.1 AGENTS.md Generation Algorithm

AGENTS.md is **COMPILED** from rules/*.md, not manually written.

**Build algorithm:**

```
1. Read metadata.json for version, org, date, abstract, references

2. Read rules/_sections.md for category definitions

3. For each category (in order defined in _sections.md):
   a. Find all rules/{prefix}-*.md files matching this category
   b. Sort rules alphabetically by title from frontmatter
   c. Assign sequential IDs (1.1, 1.2, ... for category 1)

4. Generate document:
   - Title, version block, note block
   - Abstract from metadata.json
   - TOC with auto-generated anchors
   - Each category section with all its rules
   - References section from metadata.json
```

### B.2 Anchor Generation

- Category anchor: `#{n}-{slugified-category-name}` → `#1-eliminating-waterfalls`
- Rule anchor: `#{nm}-{slugified-rule-title}` → `#11-defer-await-until-needed`
- Slugify: lowercase, replace spaces with hyphens, remove special characters

### B.3 TOC Format

```markdown
## Table of Contents

1. [{Category Name}](#{n}-{slug}) — **{IMPACT}**
   - {n}.1 [{Rule Title}](#{n1}-{rule-slug})
   - {n}.2 [{Rule Title}](#{n2}-{rule-slug})
```

### B.4 Abstract Template

```markdown
## Abstract

Comprehensive performance optimization guide for {{TECHNOLOGY}} applications,
designed for AI agents and LLMs. Contains {{RULE_COUNT}}+ rules across
{{CATEGORY_COUNT}} categories, prioritized by impact from critical
({{CRITICAL_CATEGORY_EXAMPLES}}) to incremental ({{LOW_CATEGORY_EXAMPLES}}).
Each rule includes detailed explanations, real-world examples comparing
incorrect vs. correct implementations, and specific impact metrics to guide
automated refactoring and code generation.
```

---

## Appendix C: Technology Adaptation Reference

Use these reference hierarchies as starting points when creating skills for different technology domains.

### C.1 Systems Languages (C++, Rust, Go)

Performance hierarchy typically follows:

| Priority | Category | Rationale |
|----------|----------|-----------|
| 1 | Memory Allocation | Heap vs stack, allocation frequency affects everything |
| 2 | Cache Efficiency | Data locality, access patterns determine real-world speed |
| 3 | Algorithm Complexity | O(n) considerations for scalability |
| 4 | Data Structure Selection | Containers, iterators, right tool for the job |
| 5 | I/O and Syscall Patterns | Buffering, async I/O, minimize kernel crossings |
| 6 | Concurrency/Threading | Synchronization overhead, contention |
| 7 | Micro-optimizations | Branch prediction, vectorization, hot paths |

### C.2 Web Frameworks (React, Vue, Angular)

Performance hierarchy typically follows:

| Priority | Category | Rationale |
|----------|----------|-----------|
| 1 | Network Waterfall Patterns | Sequential requests multiply latency |
| 2 | Bundle/Payload Size | Directly affects TTI and LCP |
| 3 | Server-Side Processing | SSR/SSG optimization |
| 4 | Client-Side Data Management | Caching, deduplication |
| 5 | Rendering Optimization | Virtual DOM, reconciliation |
| 6 | DOM Manipulation Efficiency | Batching, layout thrashing |
| 7 | JavaScript Runtime | Micro-optimizations in hot paths |

### C.3 Database/Query Systems

Performance hierarchy typically follows:

| Priority | Category | Rationale |
|----------|----------|-----------|
| 1 | Query Plan Optimization | Wrong plan = orders of magnitude slower |
| 2 | Index Utilization | Full table scans are catastrophic at scale |
| 3 | Connection Management | Pooling, connection overhead |
| 4 | Transaction Patterns | Lock contention, isolation levels |
| 5 | Caching Strategies | Reduce database load |
| 6 | Data Modeling | Normalization vs denormalization |
| 7 | Micro-optimizations | Query rewriting, hints |

### C.4 Mobile Development (iOS, Android)

Performance hierarchy typically follows:

| Priority | Category | Rationale |
|----------|----------|-----------|
| 1 | Launch Time Optimization | First impression, user retention |
| 2 | Memory Management | Limited resources, OOM kills |
| 3 | UI Thread Blocking | Janky UI, ANRs |
| 4 | Network Efficiency | Latency, bandwidth constraints |
| 5 | Battery Consumption | User expectation of all-day battery |
| 6 | Storage I/O | Flash wear, read/write speeds |
| 7 | Animation Performance | 60fps requirement |

### C.5 Backend Services (Node.js, Python, Java)

Performance hierarchy typically follows:

| Priority | Category | Rationale |
|----------|----------|-----------|
| 1 | I/O Patterns | Async vs sync, connection pooling |
| 2 | Memory Management | GC pressure, heap sizing |
| 3 | Concurrency Model | Event loop, threads, processes |
| 4 | Serialization | JSON parsing, protobuf |
| 5 | Caching | Redis, in-memory, memoization |
| 6 | Algorithm Efficiency | O(n) in hot paths |
| 7 | JIT/Compiler Optimization | Warmup, inline caching |

---

## Appendix D: Reference Source Categories

### D.1 Reference Types

| Type | Purpose | Example |
|------|---------|---------|
| Official docs | Authoritative API reference | react.dev, nextjs.org |
| Tool docs | Library usage | swr.vercel.app |
| GitHub repos | Implementation reference | github.com/shuding/better-all |
| Engineering blogs | Benchmark data + rationale | vercel.com/blog/... |

### D.2 Criteria for Authoritative Sources

1. **Primary maintainers** - React team for React, Vercel for Next.js
2. **Well-maintained OSS** - Active GitHub, npm downloads
3. **Benchmark-backed claims** - Engineering blogs with data
4. **Production-proven** - Used at scale companies

### D.3 What's NOT Referenced

- Tutorial sites
- Stack Overflow
- Personal blogs without data
- Outdated documentation
