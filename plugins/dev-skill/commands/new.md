---
description: Create a best practices skill for any technology (40+ rules, validated)
argument-hint: <technology> [organization]
allowed-tools: Read, Write, Bash, Glob, Grep, Task, AskUserQuestion, WebFetch, WebSearch, TodoWrite
---

# Performance Best Practices Skill Creator

You are an expert at creating high-quality performance optimization skill files for AI agents and LLMs. Your task is to generate a complete skill following the proven patterns extracted from the Vercel Engineering React Best Practices skill.

**IMPORTANT**: This skill requires the Opus model for high-quality rule generation. Always use `model: opus` when invoking agents for this task.

## Input Required

You will receive:
1. **Technology Name**: The technology/framework to create the skill for
2. **Organization Name**: The organization authoring this skill
3. **Authoritative Sources**: Documentation, repos, and benchmarks to reference

## Step 0: Ask Where to Write the Skill

**Before starting research**, ask the user where to write the skill using `AskUserQuestion`:

```
Question: "Where should I create this skill?"
Header: "Location"
Options:
- "~/.claude/skills/ (Global)" - Available across all projects, personal customizations
- ".claude/skills/ (Project)" - Specific to this project, shared with team via git
```

Store the chosen path as `{output-base}` and use it for all file generation.

---

## Output Structure

Generate a complete skill with the following files:

```
{output-base}/{technology-slug}/
├── SKILL.md              # Entry point with quick reference
├── AGENTS.md             # Compiled comprehensive guide
├── metadata.json         # Version, org, references
├── README.md             # Human-readable overview
├── references/
│   ├── _sections.md      # Category definitions
│   └── {prefix}-{slug}.md # Individual rules (40+ total)
└── assets/
    └── templates/
        └── _template.md  # Rule template for extensions
```

Where `{output-base}` is either `~/.claude/skills` (global) or `.claude/skills` (project) based on user choice.

---

## Optimized Generation Workflow

This workflow uses a **single batched planning checkpoint** instead of multiple interruptions, enabling efficient parallel generation while maintaining quality control.

### Step 1: Research & Analysis (No User Interruption)

Perform all analysis work upfront:

1. **Execution Lifecycle Analysis**
   - Map stages from input to output: `[Stage 1] → [Stage 2] → ... → [Final Stage]`
   - For each stage, identify: performance problems, cascade effects, multiplicative vs additive impact

2. **Category Derivation**
   - Group related problems into 6-8 categories
   - Order by: lifecycle position × impact radius × frequency
   - Assign prefixes (3-8 chars) and impact levels (CRITICAL → LOW)

3. **Source Research**
   Search for authoritative sources in these categories:
   - **Official documentation** - Language/framework maintainers (react.dev, golang.org, docs.python.org)
   - **Style guides** - Google, Airbnb, community-maintained standards
   - **Performance guides** - Optimization documentation, profiling tutorials
   - **Anti-pattern documentation** - Known pitfalls, common mistakes
   - **Engineering blogs** - Benchmark data with real-world measurements

   **Technology-Specific Focus Areas:**

   | Domain | Focus Areas | Canonical Sources |
   |--------|-------------|-------------------|
   | **C++** | Memory management, RAII, move semantics, templates, constexpr | ISO C++ Guidelines, CppCoreGuidelines, Effective Modern C++ |
   | **Rust** | Ownership, borrowing, lifetimes, async, unsafe | The Rust Book, Rust API Guidelines, Rustonomicon |
   | **Go** | Idioms, concurrency, interfaces, error handling | Effective Go, Go Code Review Comments, Go Proverbs |
   | **TypeScript** | Type safety, async patterns, module organization, runtime performance | TypeScript Handbook, ts-eslint docs, Node.js best practices |
   | **Python** | Idioms, performance, memory, async, typing | PEP 8, Effective Python, Python Performance Tips |
   | **React/Next.js** | Server components, data fetching, bundle size, rendering | react.dev, nextjs.org, Vercel engineering blog |
   | **Databases** | Query optimization, indexing, connection management | Official DB docs, Use The Index Luke, High Performance MySQL |
   | **Mobile (iOS/Android)** | Launch time, memory, UI thread, battery | Apple/Google performance guides, WWDC/Google I/O sessions |

   **Source Verification Checklist:**
   - [ ] Sources are from primary maintainers or recognized experts
   - [ ] Documentation is current (within last 2 years for fast-moving tech)
   - [ ] Claims are backed by benchmarks or production data
   - [ ] No tutorial sites, Stack Overflow answers, or outdated blogs

### Step 2: Single Planning Checkpoint

**CRITICAL**: Present ALL analysis results in ONE `AskUserQuestion` call using `multiSelect: false`:

```
Present a comprehensive planning summary:

## Skill Planning Review

### Execution Lifecycle
[Stage diagram and analysis]

### Proposed Categories
| # | Category | Prefix | Impact | Description |
|---|----------|--------|--------|-------------|
| 1 | ... | ... | CRITICAL | ... |
| 2 | ... | ... | HIGH | ... |

### Authoritative Sources
1. [Source 1] - Official docs
2. [Source 2] - Engineering blog
...

### Rule Distribution
- Category 1: ~X rules
- Category 2: ~Y rules
- Total: ~40-50 rules

Does this plan look correct? Select an option or provide feedback.
```

Options:
- "Approve and proceed" - Start generation
- "Adjust categories" - User provides specific changes
- "Change sources" - User provides different sources
- "Major revisions needed" - User describes changes

**Only proceed after user approval.**

After approval, optionally run the `preflight-validator` agent to catch issues early before generating 40+ rules.

### Step 3: Incremental Generation with Early Validation

Generate files in dependency order with validation at each step:

```
┌─────────────────────────────────────────────────┐
│ 1. Generate references/_sections.md             │
│    ↓                                            │
│    Validate: impact ordering, prefix format     │
│    (Fail fast if categories are wrong)          │
├─────────────────────────────────────────────────┤
│ 2. Generate rules in parallel batches           │
│    - Batch 1: CRITICAL rules (highest priority) │
│    - Batch 2: HIGH rules                        │
│    - Batch 3: MEDIUM rules                      │
│    - Batch 4: LOW rules                         │
│    Validate each batch before next              │
├─────────────────────────────────────────────────┤
│ 3. Generate SKILL.md, metadata.json             │
│    Generate assets/templates/_template.md       │
│    (Uses rules count and categories)            │
├─────────────────────────────────────────────────┤
│ 4. Build AGENTS.md (MUST use script)                            │
│    node ${CLAUDE_PLUGIN_ROOT}/scripts/build-agents-md.js <dir>  │
│    ⚠️  NEVER write AGENTS.md manually                           │
│    Required: metadata.json, references/_sections.md             │
├─────────────────────────────────────────────────────────────────┤
│ 5. Final validation                                             │
│    node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js         │
│    skill-reviewer agent                                         │
└─────────────────────────────────────────────────┘
```

### Step 4: Automated Quality Assurance

Run both validation phases:

1. **Automated validation**: `node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js ./skills/{tech-slug}`
   - Fix ALL errors before proceeding
   - Address warnings where feasible
   - Use `--verify-generated` flag to ensure AGENTS.md matches script output

2. **Agent quality review**: Launch `skill-reviewer` agent
   - Reviews teaching effectiveness, code realism, impact accuracy
   - Fix ALL issues identified before release

**If build-agents-md.js fails:**
- `Error: metadata.json not found` → Ensure metadata.json exists in skill root with required fields
- `Error: _sections.md not found` → Create _sections.md under references/ directory following the template
- Malformed output → Check rule files have valid YAML frontmatter (title, impact, impactDescription, tags)

---

## Quick Generation Mode

For experienced users who want to skip the planning checkpoint, use this streamlined workflow:

### When to Use Quick Mode

- You already know the categories from the Reference Hierarchies
- You have authoritative sources ready
- You want faster generation with minimal interruptions

### When NOT to Use Quick Mode

- Technology doesn't closely match any Reference Hierarchy domain
- You're uncertain about category mapping or impact ordering
- Technology is novel, niche, or cross-domain (e.g., WebAssembly + Rust)
- User explicitly asks for guidance or planning review
- First time creating a skill for this technology family

**When in doubt, use the full workflow with planning checkpoint.**

### Quick Workflow

```
User: "Create a Go best practices skill using standard categories"

┌─────────────────────────────────────────────────┐
│ 1. Use Reference Hierarchy for Go (Systems)     │
│    Skip research, use: mem-, cache-, algo-,     │
│    ds-, io-, conc-, opt-, micro-                │
├─────────────────────────────────────────────────┤
│ 2. Generate references/_sections.md immediately │
│    Validate: node validate-skill.js --sections  │
├─────────────────────────────────────────────────┤
│ 3. Generate all rules in parallel in references/│
│    (No batching by impact level needed)         │
├─────────────────────────────────────────────────┤
│ 4. Generate SKILL.md, metadata.json, AGENTS.md  │
│    Generate assets/templates/_template.md       │
├─────────────────────────────────────────────────┤
│ 5. Full validation + skill-reviewer             │
└─────────────────────────────────────────────────┘
```

### Quick Mode Triggers

When the user says any of:
- "Quick generate" or "fast mode"
- "Use standard categories"
- "Skip planning"
- "I already know the categories: ..."

Skip the planning checkpoint and proceed directly to generation.

### Input Format for Quick Mode

```
Technology: {tech-name}
Organization: {org-name}
Categories: {use standard | custom list}
Sources: {list of URLs or "use official docs"}
```

---

## Reference Hierarchies by Technology Domain

### Systems Languages (C++, Rust, Go)
| Priority | Category | Typical Prefix |
|----------|----------|----------------|
| 1 | Memory Allocation | mem- |
| 2 | Cache Efficiency | cache- |
| 3 | Algorithm Complexity | algo- |
| 4 | Data Structure Selection | ds- |
| 5 | I/O Patterns | io- |
| 6 | Concurrency | conc- |
| 7 | Compiler Optimization | opt- |
| 8 | Micro-optimizations | micro- |

### Web Frameworks (React, Vue, Angular)
| Priority | Category | Typical Prefix |
|----------|----------|----------------|
| 1 | Network Waterfalls | async- |
| 2 | Bundle/Payload Size | bundle- |
| 3 | Server-Side Processing | server- |
| 4 | Client-Side Data | client- |
| 5 | Rendering Optimization | render- |
| 6 | DOM Efficiency | dom- |
| 7 | JavaScript Runtime | js- |
| 8 | Advanced Patterns | advanced- |

### Database/Query Systems
| Priority | Category | Typical Prefix |
|----------|----------|----------------|
| 1 | Query Plan Optimization | query- |
| 2 | Index Utilization | index- |
| 3 | Connection Management | conn- |
| 4 | Transaction Patterns | tx- |
| 5 | Caching Strategies | cache- |
| 6 | Data Modeling | model- |
| 7 | Micro-optimizations | micro- |

### Mobile Development (iOS, Android, React Native)
| Priority | Category | Typical Prefix |
|----------|----------|----------------|
| 1 | Launch Time | launch- |
| 2 | Memory Management | mem- |
| 3 | UI Thread | ui- |
| 4 | Network Efficiency | net- |
| 5 | Battery Consumption | battery- |
| 6 | Storage I/O | storage- |
| 7 | Animation | anim- |

### Backend Services (Node.js, Python, Java)
| Priority | Category | Typical Prefix |
|----------|----------|----------------|
| 1 | I/O Patterns | io- |
| 2 | Memory Management | mem- |
| 3 | Concurrency Model | conc- |
| 4 | Serialization | serial- |
| 5 | Caching | cache- |
| 6 | Algorithm Efficiency | algo- |
| 7 | Runtime Tuning | runtime- |

---

## File Generation Templates

### SKILL.md Structure

```markdown
---
name: {org-slug}-{tech-slug}-best-practices
description: {Technology} performance optimization guidelines from {Organization}. This skill should be used when writing, reviewing, or refactoring {Technology} code to ensure optimal performance patterns. Triggers on tasks involving {trigger keywords}.
---

# {Organization} {Technology} Best Practices

Comprehensive performance optimization guide for {Technology} applications, maintained by {Organization}. Contains {N} rules across {M} categories, prioritized by impact to guide automated refactoring and code generation.

## When to Apply

Reference these guidelines when:
- Writing new {Technology} code
- {Category 1 specific activity}
- {Category 2 specific activity}
- Reviewing code for performance issues
- Refactoring existing {Technology} code

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | {Category Name} | CRITICAL | `{prefix}-` |
| 2 | {Category Name} | CRITICAL | `{prefix}-` |
| ... | ... | ... | ... |

## Quick Reference

### 1. {Category Name} (CRITICAL)

- [`{prefix}-{slug}`](references/{prefix}-{slug}.md) - {One-line description}
- [`{prefix}-{slug}`](references/{prefix}-{slug}.md) - {One-line description}
...

## How to Use

Read individual reference files for detailed explanations and code examples:

- [Section definitions](references/_sections.md) - Category structure and impact levels
- [Rule template](assets/templates/_template.md) - Template for adding new rules

## Reference Files

| File | Description |
|------|-------------|
| [AGENTS.md](AGENTS.md) | Complete compiled guide with all rules |
| [references/_sections.md](references/_sections.md) | Category definitions and ordering |
| [assets/templates/_template.md](assets/templates/_template.md) | Template for new rules |
| [metadata.json](metadata.json) | Version and reference information |
```

### references/_sections.md Structure

```markdown
# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. {Category Name} ({prefix})

**Impact:** CRITICAL
**Description:** {One sentence explaining why this category matters and its cascade effect}

## 2. {Category Name} ({prefix})

**Impact:** CRITICAL
**Description:** {One sentence explanation}

...continue for all categories...
```

**IMPORTANT**: Use two trailing spaces after `**Impact:** CRITICAL` for proper line breaks.

### Individual Rule Structure

```markdown
---
title: {Rule Title}
impact: {CRITICAL|HIGH|MEDIUM-HIGH|MEDIUM|LOW-MEDIUM|LOW}
impactDescription: {Quantified impact, e.g., "2-10× improvement", "200ms savings"}
tags: {prefix}, {technique}, {tool-if-mentioned}, {related-concepts}
---

## {Rule Title}

{1-3 sentences explaining WHY this matters. Focus on performance implications.}

**Incorrect ({what's wrong}):**

```{language}
{Bad code example - production-realistic, not strawman}
{// Comments explaining the cost}
```

**Correct ({what's right}):**

```{language}
{Good code example - minimal diff from incorrect}
{// Comments explaining the benefit}
```

{Optional sections as needed:}

**Alternative ({context}):**
{Alternative approach when applicable}

**When NOT to use this pattern:**
- {Exception 1}
- {Exception 2}

**Benefits:**
- {Benefit 1}
- {Benefit 2}

Reference: [{Reference Title}]({Reference URL})
```

### metadata.json Structure

```json
{
  "version": "0.1.0",
  "organization": "{Organization Name}",
  "technology": "{Technology Name}",
  "date": "{Month Year}",
  "abstract": "Comprehensive performance optimization guide for {Technology} applications, designed for AI agents and LLMs. Contains {N}+ rules across {M} categories, prioritized by impact from critical ({critical categories}) to incremental ({low categories}). Each rule includes detailed explanations, real-world examples comparing incorrect vs. correct implementations, and specific impact metrics to guide automated refactoring and code generation.",
  "references": [
    "{url1}",
    "{url2}"
  ]
}
```

---

## Rule Writing Guidelines

### Title Patterns

| Pattern | When to Use | Example |
|---------|-------------|---------|
| Avoid + Anti-pattern | Prohibiting a practice | Avoid Barrel File Imports |
| Use X for Y | Recommending a tool/pattern | Use SWR for Deduplication |
| Verb + Object + Context | Contextual action | Cache Property Access in Loops |
| X for Y | Tool + use case | Promise.all() for Independent Operations |

### Impact Description Patterns

| Type | Pattern | Example |
|------|---------|---------|
| Multiplier | N-M× improvement | 2-10× improvement |
| Time | Nms reduction/cost | 200-800ms import cost |
| Complexity | O(x) to O(y) | O(n) to O(1) |
| Prevention | prevents {problem} | prevents stale closures |
| Reduction | reduces {thing} by N% | reduces reflows by 80% |

### Tag Assignment Rules

1. **First tag MUST be the category prefix**
2. Add 2-5 additional tags for techniques, tools, concepts
3. Use lowercase, hyphenated for multi-word tags

Example: `tags: async, parallelization, promises, waterfalls`

---

## Mandatory Requirements

**NEVER:**
- Skip validation steps (automated or agent-based)
- Generate rules without user-approved planning
- Release without running `validate-skill.js` AND `skill-reviewer` agent
- Use generic placeholder names (foo, bar, MyComponent) in code examples

**Every rule MUST include:**
- YAML frontmatter: `title`, `impact`, `impactDescription`, `tags` (first tag = category prefix)
- 1-3 sentence explanation of WHY it matters (performance implications)
- **Incorrect** code example with parenthetical annotation explaining what's wrong
- **Correct** code example with parenthetical annotation explaining what's right
- Code blocks with language specifier (```typescript, ```python, etc.)

**Quick Mode users MUST still:**
- Run `validate-skill.js --sections-only` after generating `_sections.md`
- Run full validation after all rules are generated
- Run `skill-reviewer` agent before release

---

## Core Principles (Must Follow)

1. **Lifecycle-Driven Priority**: Earlier stages = higher impact (cascade effect)
2. **Multiplicative Problems First**: Waterfalls and N×M issues are CRITICAL
3. **Actionable Over Theoretical**: Show exact code transformation
4. **Minimal Diff Philosophy**: Correct differs minimally from incorrect
5. **Quantify Where Possible**: Use metrics, not vague claims
6. **Progressive Detail**: Quick reference → detailed rules → compiled doc

---

## Language Patterns

**DO use:**
- Imperative verbs: Use, Avoid, Cache, Extract, Defer
- Quantified claims: "2-10× improvement"
- Definitive statements: "is the #1 performance killer"

**DON'T use:**
- Hedging: "consider", "might", "perhaps"
- Marketing: "amazing", "revolutionary"
- Vague: "faster" without quantification

---

## Quality Checklist

Before finalizing, verify:

### Structure
- [ ] All categories derived from execution lifecycle analysis
- [ ] Categories ordered by impact (CRITICAL → LOW)
- [ ] File prefixes are consistent (3-8 chars)
- [ ] SKILL.md provides quick reference navigation
- [ ] Individual rules have full detail
- [ ] AGENTS.md compiles everything correctly

### Content
- [ ] Each rule has incorrect AND correct examples
- [ ] Examples are production-realistic (not strawman)
- [ ] Impact is quantified where possible
- [ ] References are authoritative (see "Technology-Specific Focus Areas" above)
- [ ] No vague guidance ("consider", "might want to")
- [ ] First tag is always category prefix

### Language
- [ ] Imperative mood ("Use", "Avoid", "Cache")
- [ ] Consistent terminology
- [ ] No marketing fluff
- [ ] Annotations in parenthetical style

### Completeness
- [ ] Major performance issues covered
- [ ] 3-7 rules per major category, 1-3 for minor
- [ ] 40+ rules total
- [ ] External tools referenced where helpful

---

## Reference Files

### Automation Scripts
```
${CLAUDE_PLUGIN_ROOT}/scripts/
├── validate-skill.js   # Validates generated skill against guidelines
├── build-agents-md.js  # Compiles references into AGENTS.md
└── README.md           # Script documentation
```

### Validation Agents
```
${CLAUDE_PLUGIN_ROOT}/agents/
├── preflight-validator.md  # Validates planning before generation (run early)
└── skill-reviewer.md       # Reviews subjective quality criteria (run after generation)
```

### Reference Examples
```
${CLAUDE_PLUGIN_ROOT}/references/
├── QUALITY_CHECKLIST.md # Authoritative validation checklist
├── COMPLETE_EXAMPLE.md  # Full React example with all rule samples
├── README.md            # Documentation for reference files
├── metadata.json        # Full metadata example
└── examples/            # 12 sample rules across all categories
    ├── _sections.md     # Complete sections template (8 categories)
    ├── _template.md     # Rule template with frontmatter
    └── {prefix}-*.md    # Sample rule files
```

### Templates and Mental Model
```
templates/skill-generator/
├── MENTAL_MODEL.md       # Core principles and cascade effect
└── *.template files      # Scaffolding templates
```

**IMPORTANT**:
1. Always read `${CLAUDE_PLUGIN_ROOT}/references/COMPLETE_EXAMPLE.md` before generating a new skill
2. Run `node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js` after generation to ensure compliance
3. Check against `${CLAUDE_PLUGIN_ROOT}/references/QUALITY_CHECKLIST.md` before release

---

Now generate the complete skill for the provided technology, following these examples exactly.
