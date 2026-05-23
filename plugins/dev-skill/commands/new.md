---
description: Create a skill for any type — from API references to runbooks to CI/CD workflows
argument-hint: <skill-name> [organization]
allowed-tools: Read, Write, Bash, Glob, Grep, Task, AskUserQuestion, WebFetch, WebSearch, TaskCreate, TaskUpdate, TaskList
---

# Skill Creator

You are an expert at creating high-quality skills for AI agents and LLMs. This command routes through four disciplines — Distillation, Composition, Investigation, and Extraction — each with a proven generation pipeline.

**Generation quality benefits from a strong model**, but don't hard-pin one here — the bundled review agents (`skill-reviewer`, `preflight-validator`) declare their own model in frontmatter.

## Input Required

You will receive:
1. **Skill Name**: The name for this skill
2. **Organization Name** (optional): The organization authoring this skill

---

## Step 0: Ask Where to Write the Skill

**Before starting anything else**, ask the user where to write the skill using `AskUserQuestion`:

```
Question: "Where should I create this skill?"
Header: "Location"
Options:
- "~/.claude/skills/ (Global)" - Available across all projects, personal customizations
- ".claude/skills/ (Project)" - Specific to this project, shared with team via git
```

Store the chosen path as `{output-base}` and use it for all file generation.

---

## Step 1: Type Selection

Ask the user what kind of skill they want to create using `AskUserQuestion`:

```
Question: "What type of skill are you creating?"
Header: "Skill Type"
Options:
- "1. Library/API Reference — How to use a library, CLI, or SDK correctly"
- "2. Product Verification — Test and verify code output with assertions"
- "3. Workflow Automation — Automate a repetitive multi-step process"
- "4. Code Scaffolding — Generate boilerplate for your framework"
- "5. Code Quality & Review — Enforce review standards and style"
- "6. CI/CD & Deployment — Build, test, deploy, and monitor"
- "7. Runbook — Diagnose and resolve operational issues"
- "8. Data Analysis — Connect to data sources and run queries"
- "9. Infrastructure Ops — Operational procedures with safety guardrails"
```

---

## Step 2: Route to Discipline

Map the selected type to a discipline and follow its pipeline:

| Type | Discipline | Type Slug |
|------|-----------|-----------|
| 1. Library/API Reference | **Distillation** | `library-reference` |
| 2. Product Verification | **Composition** | `verification` |
| 3. Workflow Automation | **Composition** | `automation` |
| 4. Code Scaffolding | **Extraction** | `scaffolding` |
| 5. Code Quality & Review | **Distillation** | `code-quality` |
| 6. CI/CD & Deployment | **Composition** | `cicd` |
| 7. Runbook | **Investigation** | `runbook` |
| 8. Data Analysis | **Investigation** | `data-analysis` |
| 9. Infrastructure Ops | **Composition** | `infra-ops` |

**Before generating anything**, you MUST:

1. Read `${CLAUDE_PLUGIN_ROOT}/templates/anatomy/ANATOMY.md` for universal skill patterns
2. Read the discipline-specific recipe: `${CLAUDE_PLUGIN_ROOT}/templates/disciplines/{discipline}/RECIPE.md`
3. Follow the recipe's discovery workflow and generation pipeline exactly

---

## Distillation Path (Types 1, 5)

The pipeline for Library/API Reference and Code Quality/Review skills. It produces a **distilled reference** — the smallest set of decisions a capable model gets wrong by default, each explaining the wrong default it corrects and why.

**Read `${CLAUDE_PLUGIN_ROOT}/templates/disciplines/distillation/RECIPE.md` — it is the authority on this discipline.** The doctrine in brief:
- **Provable conciseness, no rule count.** A rule earns its place only if you can name the wrong default it corrects. If the model already does the right thing, cut the rule — restating it is hand-holding. Completeness is proven by `/dev-skill:eval`, never by hitting a count. *Brevity is the soul of wit.*
- **Explain WHY, not just WHAT** — the model generalizes from a reason, not from dictation.
- **One canonical example by default.** Add an Incorrect/Correct foil only when the wrong way is a real, common trap (never a strawman).
- **Impact tiers and quantified metrics are optional — performance skills only.** Don't force "2-10×" onto a correctness rule.
- **Sources: authoritative or nothing.** Primary docs/specs/code/named experts; reject content farms, listicles, undated blogs, and AI SEO filler.

### Output Structure

```
{output-base}/{skill-slug}/
├── SKILL.md              # Entry point with quick reference
├── AGENTS.md             # Compiled TOC navigation doc (built by script)
├── metadata.json         # discipline: "distillation", type: "{type-slug}"
├── references/
│   ├── _sections.md      # Category definitions ordered by importance
│   └── {prefix}-{slug}.md # Individual rules (as few as cover the wrong defaults)
└── assets/
    └── templates/
        └── _template.md  # Rule template for extensions
```

### Step D1: Research & Analysis (No User Interruption)

Perform all analysis work upfront:

1. **Identify the wrong defaults.** List what a capable model does *wrong* by default for this technology — outdated APIs, footguns, library-specific conventions, decisions it gets subtly wrong. This list is the skill's scope. Do not list things the model already handles correctly.

2. **Category derivation.** Group the wrong defaults into 4–8 categories by decision area (e.g. for an API: auth, pagination, errors, idempotency). Order by importance (frequency × cost). Assign prefixes (2–10 chars). *Performance skills only:* you may add impact tiers (CRITICAL → LOW) and order by lifecycle position, since earlier stages cascade downstream.

3. **Source research.** Gather authoritative sources for each claim (see RECIPE.md "Sources"):
   - **Primary docs / specs / the library's own code** — the default citation
   - **Named-expert writing** — a maintainer's post, a benchmark that states its method
   - **Reject on sight:** content farms, listicles, undated blogs, AI-generated SEO filler, and SO/Reddit answers used as a primary citation

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

   **Source verification (each source):**
   - [ ] Authored by a maintainer, spec author, or named expert — not anonymous SEO content
   - [ ] Current with the library's present major version
   - [ ] Actually supports the claim, and the claim traces back to a primary source (docs/spec/code)
   - [ ] Not a content farm, listicle, undated blog, or AI-generated filler

### Step D2: Single Planning Checkpoint

**CRITICAL**: First output the planning summary as regular text so the user can review it, THEN ask for approval.

**Step D2a — Display the plan** (output as regular markdown text, NOT inside AskUserQuestion):

```markdown
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

### Rules to Write (the wrong defaults to correct)
- Category 1: {the specific wrong defaults this category corrects}
- Category 2: {…}

No rule-count target — the list of wrong defaults worth correcting *is* the scope.
```

**Step D2b — Ask for approval** (use `AskUserQuestion` with `multiSelect: false`):

```
Question: "Does this skill plan look correct? Review the categories, sources, and rule distribution above."
Header: "Plan Review"
Options:
- "Approve and proceed" - Start generation
- "Adjust categories" - User provides specific changes
- "Change sources" - User provides different sources
- "Major revisions needed" - User describes changes
```

**IMPORTANT**: The plan content MUST be displayed as regular output text BEFORE calling AskUserQuestion. Do NOT embed the plan inside the question — users cannot see question content until after they respond.

**Only proceed after user approval.**

After approval, optionally run the `preflight-validator` agent to catch issues early before generating the rules.

### Step D3: Incremental Generation with Early Validation

Generate files in dependency order with validation at each step:

```
┌─────────────────────────────────────────────────┐
│ 1. Generate references/_sections.md             │
│    ↓                                            │
│    Validate: impact ordering, prefix format     │
│    (Fail fast if categories are wrong)          │
├─────────────────────────────────────────────────┤
│ 2. Generate rules in parallel, by category      │
│    Each rule must name the wrong default it      │
│    corrects; cut any that restate a default      │
│    the model already gets right.                 │
│    Validate each batch before the next.          │
├─────────────────────────────────────────────────┤
│ 3. Generate SKILL.md, metadata.json             │
│    Generate assets/templates/_template.md       │
│    (Uses rules count and categories)            │
├─────────────────────────────────────────────────┤
│ 4. Build AGENTS.md                              │
│    node ${CLAUDE_PLUGIN_ROOT}/scripts/build-agents-md.js │
│    (NEVER write AGENTS.md manually)             │
├─────────────────────────────────────────────────┤
│ 5. Final validation                             │
│    node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js  │
│    skill-reviewer agent with distillation RUBRIC.md      │
└─────────────────────────────────────────────────┘
```

### Step D4: Build AGENTS.md

After all rules are generated, build the AGENTS.md navigation document:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/build-agents-md.js {output-base}/{skill-slug}
```

**NEVER write AGENTS.md manually** — always use the build script.

### Step D5: Automated Quality Assurance

Run both validation phases:

1. **Automated validation**: `node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js {output-base}/{skill-slug}`
   - Fix ALL errors before proceeding
   - Address warnings where feasible

2. **Agent quality review**: Launch `skill-reviewer` agent with `${CLAUDE_PLUGIN_ROOT}/templates/disciplines/distillation/RUBRIC.md`
   - Reviews teaching effectiveness, code realism, impact accuracy
   - Fix ALL issues identified before release

### Quick Generation Mode (Distillation Only)

For experienced users who want to skip the planning checkpoint.

**When to Use Quick Mode:**
- You already know the categories from the Reference Hierarchies
- You have authoritative sources ready
- You want faster generation with minimal interruptions

**When NOT to Use Quick Mode:**
- Technology doesn't closely match any Reference Hierarchy domain
- You're uncertain about category mapping or impact ordering
- Technology is novel, niche, or cross-domain (e.g., WebAssembly + Rust)
- User explicitly asks for guidance or planning review
- First time creating a skill for this technology family

**When in doubt, use the full workflow with planning checkpoint.**

**Quick Workflow:**

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
│ 4. Generate SKILL.md, metadata.json             │
│    Generate assets/templates/_template.md       │
├─────────────────────────────────────────────────┤
│ 5. Build AGENTS.md via build-agents-md.js       │
├─────────────────────────────────────────────────┤
│ 6. Full validation + skill-reviewer             │
└─────────────────────────────────────────────────┘
```

**Quick Mode Triggers** — when the user says any of:
- "Quick generate" or "fast mode"
- "Use standard categories"
- "Skip planning"
- "I already know the categories: ..."

**Quick Mode users MUST still:**
- Run `validate-skill.js --sections-only` after generating `_sections.md`
- Run full validation after all rules are generated
- Run `skill-reviewer` agent before release

### Reference Hierarchies by Technology Domain

#### Systems Languages (C++, Rust, Go)

| Priority | Category | Prefix | Rationale |
|----------|----------|--------|-----------|
| 1 | Memory Allocation | mem- | Heap vs stack affects everything |
| 2 | Cache Efficiency | cache- | Data locality determines real-world speed |
| 3 | Algorithm Complexity | algo- | O(n) considerations for scalability |
| 4 | Data Structure Selection | ds- | Right container for the job |
| 5 | I/O and Syscall Patterns | io- | Minimize kernel crossings |
| 6 | Concurrency/Threading | conc- | Synchronization overhead |
| 7 | Micro-optimizations | micro- | Branch prediction, vectorization |

#### Web Frameworks (React, Vue, Angular)

| Priority | Category | Prefix | Rationale |
|----------|----------|--------|-----------|
| 1 | Network Waterfalls | async- | Sequential requests multiply latency |
| 2 | Bundle/Payload Size | bundle- | Directly affects TTI and LCP |
| 3 | Server-Side Processing | server- | SSR/SSG optimization |
| 4 | Client-Side Data | client- | Caching, deduplication |
| 5 | Rendering Optimization | render- | Virtual DOM, reconciliation |
| 6 | DOM Efficiency | dom- | Batching, layout thrashing |
| 7 | JavaScript Runtime | js- | Micro-optimizations in hot paths |

#### Database/Query Systems

| Priority | Category | Prefix | Rationale |
|----------|----------|--------|-----------|
| 1 | Query Plan Optimization | query- | Wrong plan = orders of magnitude slower |
| 2 | Index Utilization | index- | Full scans catastrophic at scale |
| 3 | Connection Management | conn- | Pooling, connection overhead |
| 4 | Transaction Patterns | tx- | Lock contention, isolation |
| 5 | Caching Strategies | cache- | Reduce database load |
| 6 | Data Modeling | model- | Normalization vs denormalization |

#### Mobile Development (iOS, Android, React Native)

| Priority | Category | Prefix | Rationale |
|----------|----------|--------|-----------|
| 1 | Launch Time | launch- | First impression, retention |
| 2 | Memory Management | mem- | Limited resources, OOM kills |
| 3 | UI Thread | ui- | Janky UI, ANRs |
| 4 | Network Efficiency | net- | Latency, bandwidth constraints |
| 5 | Battery Consumption | battery- | User expectation of all-day |
| 6 | Storage I/O | storage- | Flash wear, read/write |
| 7 | Animation | anim- | 60fps requirement |

#### Backend Services (Node.js, Python, Java)

| Priority | Category | Prefix | Rationale |
|----------|----------|--------|-----------|
| 1 | I/O Patterns | io- | Async vs sync, pooling |
| 2 | Memory Management | mem- | GC pressure, heap sizing |
| 3 | Concurrency Model | conc- | Event loop, threads |
| 4 | Serialization | serial- | JSON parsing, protobuf |
| 5 | Caching | cache- | Redis, memoization |
| 6 | Algorithm Efficiency | algo- | O(n) in hot paths |
| 7 | Runtime Tuning | runtime- | JIT, inline caching |

### Source Authority

**Acceptable Sources:**

| Type | Purpose | Example |
|------|---------|---------|
| Official docs | Authoritative API reference | react.dev, golang.org |
| Tool docs | Library usage | swr.vercel.app |
| GitHub repos | Implementation reference | github.com/... |
| Engineering blogs | Benchmark data + rationale | vercel.com/blog/... |

**Source Criteria:**
1. **Primary maintainers** — React team for React, Vercel for Next.js
2. **Well-maintained OSS** — Active GitHub, npm downloads
3. **Benchmark-backed claims** — Engineering blogs with data
4. **Production-proven** — Used at scale

**NOT Referenced:** Tutorial sites, Stack Overflow, personal blogs without data, outdated docs.

### Distillation File Templates

The authoritative formats live in `${CLAUDE_PLUGIN_ROOT}/templates/disciplines/distillation/` — read and fill them rather than reproducing structures inline:

| Template | Produces |
|----------|----------|
| `SKILL.md.template` | Entry point: `When to Apply`, a category table, `Quick Reference` |
| `_sections.md.template` | Category definitions (impact tier optional — performance skills only) |
| `RULE.md.template` | A rule: `title` + `tags` (first tag = category prefix), a WHY, one canonical example. Foil, impact, and exceptions are all optional |
| `_template.md.template` | The rule template copied into the skill so it can be extended later |

`metadata.json` (shared format: `${CLAUDE_PLUGIN_ROOT}/templates/anatomy/metadata.json.template`) must include `discipline: "distillation"` and the `type`. Keep `abstract` to one or two honest sentences describing scope — not a performance sales pitch.

### Rule Writing Guidelines

**Titles** are decision-oriented: `{Verb} {object} {context}` ("Thread context through outbound calls"), `Avoid {real anti-pattern}`, `Use {X} for {Y}`.

**Tags:** first tag = the category prefix; add 2–4 more for concepts/tools, lowercase and hyphenated.

**Impact / impactDescription** are optional and for performance skills only. When used, the description must be honest and traceable — a real number (`O(n)→O(1)`, `2-10× improvement`) or a real consequence (`prevents stale reads`). Never fabricate a metric for a correctness rule.

Full detail (title patterns, sources, sections format) lives in `RECIPE.md`.

### Quality Checklist (Distillation)

Before finalizing, verify against the doctrine:

- [ ] **Every rule names the wrong default it corrects.** Cut any rule that restates what the model already does right (hand-holding).
- [ ] Every rule explains WHY, not just WHAT (no bare ALWAYS/NEVER).
- [ ] One canonical example per rule; an Incorrect/Correct foil only where the wrong way is a real, common trap (no strawmen).
- [ ] Categories ordered by importance; first tag = category prefix; H2 matches `title`.
- [ ] Sources are primary/authoritative; no content farms, listicles, or undated/AI-SEO pages. Each claim traces to a primary source.
- [ ] No vague hedging or marketing language.
- [ ] **Coverage proven by `/dev-skill:eval`, not by a rule count.** There is no minimum or target.

---

## Composition Path (Types 2, 3, 6, 9)

This pipeline produces workflow automation skills — from product verification to CI/CD pipelines to infrastructure operations. The generated skill orchestrates tools, scripts, and multi-step processes.

### Output Structure

```
{output-base}/{skill-slug}/
├── SKILL.md              # Workflow overview + trigger phrases
├── metadata.json         # discipline: "composition", type: "{type-slug}"
├── config.json           # User-specific setup (service URLs, channels, paths)
├── gotchas.md            # Failure points discovered over time
├── scripts/              # Executable scripts the skill uses
│   ├── {step-name}.sh    # Individual workflow steps
│   └── verify.sh         # Verification/assertion script
├── hooks/                # On-demand hooks (if write/destructive)
│   └── hooks.json        # Hook definitions
└── references/
    └── workflow.md        # Detailed workflow documentation
```

### Step C1: Interview

Ask the user with `AskUserQuestion` to confirm the composition type:

```
Question: "What type of composition skill are you creating?"
Header: "Composition Type"
Options:
- "Verification — test and assert that code/features work correctly"
- "Workflow Automation — automate a repetitive multi-step process"
- "CI/CD & Deployment — build, test, deploy, and monitor"
- "Infrastructure Ops — operational procedures with safety guardrails"
```

Then ask free-form:
- "Describe the workflow step by step. What triggers it, what does each step do, and how do you know it worked?"
- "What tools do you use? (CLI commands, MCP servers, APIs, scripts)"

### Step C2: Risk Assessment

Classify the risk level of the workflow:

| Level | Criteria | Guardrails Required |
|-------|----------|---------------------|
| Read-only | Only fetches/analyzes data | None |
| Write | Creates PRs, posts messages, writes files | Confirmation before external side effects |
| Destructive | Deletes resources, force-pushes, drops tables | PreToolUse hook blocks + explicit confirmation + dry-run mode |

### Step C3: Workflow Mapping

Structure the user's description into a workflow diagram:

```
Trigger → Step 1 → Step 2 → ... → Verification → Cleanup
              ↓ (on failure)
         Error handling / Rollback
```

For each step, identify:
- **Action**: What happens (command, API call, tool invocation)
- **Input**: What this step needs from the previous step
- **Output**: What this step produces for the next step
- **Failure mode**: What happens when this step fails
- **Rollback**: How to undo this step (if applicable)

### Step C4: Planning Checkpoint

Display the workflow diagram, tool inventory, risk assessment, and generated file list. Ask user to approve before generating:

```
Question: "Does this workflow plan look correct? Review the steps, tools, and risk assessment above."
Header: "Plan Review"
Options:
- "Approve and proceed" - Start generation
- "Adjust workflow" - User provides changes
- "Major revisions needed" - User describes changes
```

**Only proceed after user approval.**

### Step C5: Generation

After user approval, generate in this order:

1. **Generate SKILL.md** — Workflow overview diagram, tool requirements, risk level, quick reference
2. **Generate scripts/** — One script per workflow step (see script requirements below)
3. **Generate hooks/** (if risk level is write or destructive) — Guardrail hooks
4. **Generate config.json** — User-specific setup with `_setup_instructions`
5. **Generate references/workflow.md** — Detailed step-by-step with error handling and rollback
6. **Generate metadata.json** with `discipline: "composition"` and the appropriate `type` field
7. **Generate gotchas.md** — Initialize with "No known gotchas yet"

**Script Requirements:**

Every script MUST include:
- `set -euo pipefail` safety header
- Input validation for required arguments
- Actionable error messages (tell user what to do, not just what failed)
- Exit codes: 0 = success, 1 = error, 2 = skipped (already done)

For verification skills, generate a `scripts/verify.sh` with programmatic assertions:

```bash
#!/usr/bin/env bash
# verify.sh — Assert expected state after workflow execution
set -euo pipefail

PASS=0
FAIL=0

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  if [[ "$expected" == "$actual" ]]; then
    echo "  PASS: $label"
    ((PASS++))
  else
    echo "  FAIL: $label (expected: $expected, got: $actual)"
    ((FAIL++))
  fi
}

# --- Assertions ---
{generated assertions based on success criteria}

# --- Summary ---
echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]] || exit 1
```

For destructive operations, generate guardrail hooks:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/guardrail.sh \"$TOOL_INPUT\"",
          "timeout": 5
        }]
      }
    ]
  }
}
```

### Step C6: Validate

1. **Automated validation**: `node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js {output-base}/{skill-slug}`
2. **Agent quality review**: Launch `skill-reviewer` agent with `${CLAUDE_PLUGIN_ROOT}/templates/disciplines/composition/RUBRIC.md`

### Type-Specific Guidance (Composition)

#### Product Verification Skills (Type 2)

Focus on: assertions, recording, state checking.

- Include `scripts/verify.sh` with programmatic assertions
- Consider recording output (screenshots, logs) for human review
- Assert on STATE, not just output: "the database row exists" not "the command printed success"
- Structure assertions as: setup → action → wait → assert → cleanup

Example workflow:
```
1. Set up test data (seed user, create test card)
2. Drive the UI flow (playwright, tmux)
3. Wait for async operations to complete
4. Assert state (database, API, UI)
5. Clean up test data
```

#### Workflow Automation Skills (Type 3)

Focus on: composition, logging, idempotency.

- Save results in log files for cross-run consistency
- Make workflows idempotent (running twice produces same result)
- Use structured output (JSON) between steps for composability
- Include a `--dry-run` flag that shows what would happen without executing

Example: standup-post skill
```
1. Fetch git log since last standup
2. Fetch ticket tracker updates
3. Merge and format
4. Post to Slack channel
5. Append to standups.log
```

#### CI/CD & Deployment Skills (Type 6)

Focus on: multi-step pipelines with rollback.

- Every deploy step must have a rollback counterpart
- Include error-rate comparison (before/after deploy)
- Support gradual rollout (canary, blue-green)
- Auto-rollback on regression detection

Example: deploy-service skill
```
1. Build and test locally
2. Push to staging → smoke test
3. Deploy canary (10% traffic)
4. Compare error rates (5 min window)
5. If regression: auto-rollback
6. If stable: full rollout
```

#### Infrastructure Ops Skills (Type 9)

Focus on: guardrails, dry-run, soak periods.

- MUST include dry-run mode for destructive operations
- MUST include confirmation prompts before irreversible actions
- Include soak period for cleanup operations (find orphans → wait → confirm → delete)
- Log every destructive action for audit trail

Example: orphan-cleanup skill
```
1. Scan for orphaned resources (dry-run mode)
2. Post findings to Slack for review
3. Wait for soak period (configurable, default 24h)
4. Request explicit confirmation
5. Execute cleanup with audit logging
6. Verify cleanup completed
```

---

## Investigation Path (Types 7, 8)

This pipeline maps a domain's symptom space to diagnostic decision trees, query patterns, and report templates. It produces skills for operational runbooks and data analysis.

### Output Structure

```
{output-base}/{skill-slug}/
├── SKILL.md              # Symptom overview + trigger phrases
├── metadata.json         # discipline: "investigation", type: "{type-slug}"
├── config.json           # Service URLs, dashboard IDs, query endpoints
├── gotchas.md            # Diagnostic dead-ends discovered over time
├── references/
│   ├── symptoms.md       # Symptom catalog with entry points
│   ├── {symptom}-tree.md # Decision tree per symptom class
│   └── queries/          # Reusable query patterns
│       ├── {name}.sql    # SQL query templates
│       ├── {name}.sh     # CLI investigation commands
│       └── {name}.py     # Data analysis scripts (optional)
└── assets/
    └── templates/
        └── report.md     # Investigation report template
```

### Step I1: Interview

Ask the user with `AskUserQuestion` to confirm the investigation type:

```
Question: "What type of investigation skill are you creating?"
Header: "Investigation Type"
Options:
- "Runbook — diagnose and resolve operational issues for a service/system"
- "Data Analysis — connect to data sources, run queries, answer business questions"
```

Then ask free-form:
- "What system or domain does this cover? What are its main components?"
- "What are the top 5-10 symptoms or questions that trigger an investigation?"
- "What tools do you use to investigate? (dashboards, SQL, CLI commands, APIs, log systems)"

### Step I2: Symptom Space Mapping

Structure the user's symptoms into a catalog:

```markdown
## Symptom Catalog

| # | Symptom / Question | Entry Point | Severity |
|---|-------------------|-------------|----------|
| 1 | High latency on /api/checkout | latency-tree.md | P1 |
| 2 | Error rate spike in payment service | error-rate-tree.md | P1 |
| 3 | "Why did conversion drop this week?" | conversion-tree.md | P2 |
```

For each symptom, identify:
- **Entry point**: The first thing to check
- **Investigation tools**: What you query/check at each decision point
- **Terminal states**: Resolution (fix it), Escalation (hand off), or False alarm (not a problem)

### Step I3: Decision Tree Design

Each symptom class gets a decision tree:

```
Symptom: High latency on /api/checkout
│
├── Check: Is it all endpoints or just checkout?
│   ├── All endpoints → Check: Is the database responding?
│   │   ├── DB slow → Check: queries/slow-queries.sql
│   │   │   ├── Long-running query found → Kill query, investigate lock
│   │   │   └── No slow queries → Check connection pool exhaustion
│   │   └── DB fine → Check: Is it upstream dependency?
│   └── Just checkout → Check: Recent deploy?
│       ├── Yes → Compare error rates before/after deploy
│       └── No → Check: Payment provider status page
```

Rules for decision trees:
- **Every path must terminate.** Dead ends are bugs.
- **Terminal states are actions.** "Escalate to {team}", "Run {fix}", or "Not a problem because {reason}".
- **Each node references a specific tool or query.** Not "check the database" but "run queries/slow-queries.sql".
- **Include the expected output at each node.** What does "DB slow" look like? (>200ms p99)

### Step I4: Query Pattern Inventory

Collect reusable queries the agent can compose:

```sql
-- queries/slow-queries.sql
-- Find queries running longer than {threshold}ms
-- Usage: Replace {threshold} with desired ms (default: 1000)
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - pg_stat_activity.query_start > interval '{threshold} milliseconds'
ORDER BY duration DESC;
```

Query patterns must:
- Have a comment header explaining purpose and usage
- Use named parameters (not hardcoded values)
- Be syntactically valid for the target system
- Include expected output format

### Step I5: Planning Checkpoint

Display symptom catalog, decision tree summaries, and query inventory as regular text. Then ask for approval:

```
Question: "Does this investigation plan look correct? Review the symptoms, decision trees, and queries above."
Header: "Plan Review"
Options:
- "Approve and proceed" - Start generation
- "Adjust symptoms" - User provides changes
- "Change tools/queries" - User provides different tools
- "Major revisions needed" - User describes changes
```

**Only proceed after user approval.**

### Step I6: Generation

After user approval, generate in this order:

1. **Generate SKILL.md** — Symptom overview, trigger phrases, quick reference to trees
2. **Generate references/symptoms.md** — Full symptom catalog with entry points
3. **Generate references/{symptom}-tree.md** — One decision tree per symptom class
4. **Generate references/queries/** — Reusable query patterns
5. **Generate assets/templates/report.md** — Investigation report template
6. **Generate config.json** — Service URLs, dashboard IDs, endpoints
7. **Generate metadata.json** with `discipline: "investigation"` and the appropriate `type` field
8. **Generate gotchas.md** — Initialize with "No known gotchas yet"

### Step I7: Validate

1. **Automated validation**: `node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js {output-base}/{skill-slug}`
2. **Agent quality review**: Launch `skill-reviewer` agent with `${CLAUDE_PLUGIN_ROOT}/templates/disciplines/investigation/RUBRIC.md`

### Type-Specific Guidance (Investigation)

#### Runbook Skills (Type 7)

Focus on: symptom → investigation → resolution.

- Every decision tree path terminates in an action (fix, escalate, or dismiss)
- Include severity assessment at each node (is this getting worse?)
- Reference specific dashboards and alert thresholds
- Include "usual suspects" — the top 3 causes for each symptom, ordered by frequency
- Store investigation history in `${CLAUDE_PLUGIN_DATA}/investigations.log`

Runbook SKILL.md should include:
```markdown
## Common Symptoms

| Symptom | Usual Cause | Quick Check |
|---------|-------------|-------------|
| High latency | Database locks | `queries/slow-queries.sql` |
| Error spike | Failed deploy | `git log --oneline -5` |
| OOM kills | Memory leak in {service} | `queries/memory-usage.sh` |
```

#### Data Analysis Skills (Type 8)

Focus on: query composition and data access patterns.

- Provide helper functions/queries the agent can compose for complex analysis
- Include table/schema documentation (what columns exist, what they mean)
- Define canonical IDs (which table has the authoritative `user_id`?)
- Include common joins and aggregation patterns
- Store query results in structured format for cross-query analysis

Data Analysis SKILL.md should include:
```markdown
## Available Data Sources

| Source | Access | Key Tables |
|--------|--------|------------|
| Analytics DB | `queries/analytics-*.sql` | events, users, sessions |
| Billing API | `queries/billing-*.sh` | invoices, subscriptions |
```

---

## Extraction Path (Type 4)

This pipeline analyzes frameworks, codebases, or conventions and derives parameterized templates and scaffolding instructions. It produces skills that eliminate boilerplate and enforce conventions.

### Output Structure

```
{output-base}/{skill-slug}/
├── SKILL.md              # Template catalog + trigger phrases
├── metadata.json         # discipline: "extraction", type: "scaffolding"
├── config.json           # Project-specific overrides (paths, naming)
├── gotchas.md            # Scaffolding edge cases discovered over time
├── assets/
│   └── templates/
│       ├── {component-type}.template   # Parameterized templates
│       └── {another-type}.template
└── references/
    └── conventions.md    # Conventions the templates enforce + rationale
```

### Step E1: Interview

Ask the user:
- "What framework are you scaffolding for?"
- "What types of files/components do you create repeatedly?"
- "What varies between instances? (e.g., name, type, options)"
- "Are there conventions you want enforced? (naming, structure, patterns)"

Optionally ask to see an existing example:
- "Can you point me to a well-written example of each component type? I'll extract the pattern."

### Step E2: Pattern Analysis

If the user provides example files, analyze them for:
- **Fixed structure**: Parts that stay the same across all instances
- **Variable parts**: Names, types, options that change per instance
- **Conventions**: Import ordering, naming patterns, file placement
- **Boilerplate**: Repetitive code that the template eliminates

If no examples: derive templates from framework documentation and best practices.

### Step E3: Template Design

For each component type, design a parameterized template:

```markdown
# Template: {Component Type}

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| name | yes | — | Component name (PascalCase) |
| type | no | "default" | Variant type |
| features | no | [] | Feature flags to include |

## Output Files

| File | Path | Description |
|------|------|-------------|
| Component | `src/{module}/{name}.tsx` | Main component file |
| Test | `src/{module}/{name}.test.tsx` | Test file |
| Index | `src/{module}/index.ts` | Re-export (if new module) |

## Template Content

{The actual template with parameter placeholders}
```

Design principles:
- **Minimal viable scaffold.** Generate the structure, not the implementation.
- **Convention-enforced.** The template enforces naming, import order, file placement.
- **Parameterized, not hardcoded.** Every instance-specific value is a named parameter.
- **Documented rationale.** The conventions doc explains WHY.

### Step E4: Convention Documentation

Write a conventions document explaining WHY each convention exists:

```markdown
## File Naming: kebab-case
Files use kebab-case (e.g., `user-profile.tsx`).
**Why:** Filesystem case sensitivity across OS. Prevents "works on Mac, breaks on Linux."

## Import Order: external → internal → relative
**Why:** Consistent visual grouping. Auto-formatters preserve this order.
```

### Step E5: Planning Checkpoint

Display template list, parameters, and conventions as regular text. Then ask for approval:

```
Question: "Does this scaffolding plan look correct? Review the templates, parameters, and conventions above."
Header: "Plan Review"
Options:
- "Approve and proceed" - Start generation
- "Adjust templates" - User provides changes
- "Change conventions" - User provides different conventions
- "Major revisions needed" - User describes changes
```

**Only proceed after user approval.**

### Step E6: Generation

After user approval, generate in this order:

1. **Generate SKILL.md** — Template catalog with parameters and usage examples
2. **Generate assets/templates/*.template** — Parameterized template files
3. **Generate references/conventions.md** — Convention documentation with rationale
4. **Generate config.json** — Project-specific overrides (output paths, naming preferences)
5. **Generate metadata.json** with `discipline: "extraction"` and `type: "scaffolding"`
6. **Generate gotchas.md** — Initialize with "No known gotchas yet"

### Step E7: Validate

1. **Automated validation**: `node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js {output-base}/{skill-slug}`
2. **Agent quality review**: Launch `skill-reviewer` agent with `${CLAUDE_PLUGIN_ROOT}/templates/disciplines/extraction/RUBRIC.md`

### Type-Specific Guidance (Extraction)

#### Framework Scaffolding

- Include templates for the 3-5 most common component types
- Each template produces all related files (component + test + types + index)
- Include a "new module" variant that also creates the directory structure
- Reference the framework's official scaffolding if it exists (e.g., `rails generate`)

#### Migration Scaffolding

- Template includes common gotchas (irreversible operations, data backfill)
- Include both "up" and "down" migration templates
- Reference the migration framework's documentation
- Flag operations that require special handling (column renames, index creation on large tables)

#### Internal Platform Scaffolding

- Templates pre-wire authentication, logging, and deployment config
- Include environment-specific configuration (dev, staging, prod)
- Reference the internal platform's documentation and CLI

---

## Common Elements (All Paths)

### Output Location

All generated files go under `{output-base}/{skill-slug}/` where `{output-base}` is the path chosen in Step 0.

### metadata.json

Every skill's metadata.json MUST include `discipline` and `type` fields:

```json
{
  "version": "0.1.0",
  "organization": "{Organization}",
  "technology": "{Technology or Domain}",
  "discipline": "{distillation|composition|extraction|investigation}",
  "type": "{library-reference|verification|automation|scaffolding|code-quality|cicd|runbook|data-analysis|infra-ops}",
  "date": "{Month Year}",
  "abstract": "{1-2 sentence summary}",
  "references": ["{url1}", "{url2}"]
}
```

### Validation (Always Required)

Every path ends with the same two-phase validation:

1. **Structural validation**: `node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js {output-base}/{skill-slug}`
   - Fix ALL errors before proceeding
   - Address warnings where feasible

2. **Discipline-specific review**: Launch `skill-reviewer` agent with the discipline's RUBRIC.md:
   - Distillation: `${CLAUDE_PLUGIN_ROOT}/templates/disciplines/distillation/RUBRIC.md`
   - Composition: `${CLAUDE_PLUGIN_ROOT}/templates/disciplines/composition/RUBRIC.md`
   - Investigation: `${CLAUDE_PLUGIN_ROOT}/templates/disciplines/investigation/RUBRIC.md`
   - Extraction: `${CLAUDE_PLUGIN_ROOT}/templates/disciplines/extraction/RUBRIC.md`

### Complementary Skill Suggestions

After completing generation, suggest related skills from other disciplines:

| Created Skill Type | Suggested Complement |
|--------------------|---------------------|
| CI/CD & Deployment | "Consider creating a Runbook skill for rollback diagnostics." |
| Library/API Reference | "Consider creating a Code Scaffolding skill for this framework's boilerplate." |
| Product Verification | "Consider creating a Workflow Automation skill to run this verification as part of CI." |
| Runbook | "Consider creating a Data Analysis skill for the metrics this runbook references." |
| Code Scaffolding | "Consider creating a Code Quality skill to enforce the conventions these templates produce." |
| Workflow Automation | "Consider creating a Product Verification skill to assert the workflow's output." |
| Data Analysis | "Consider creating a Runbook skill for when query results reveal problems." |
| Infrastructure Ops | "Consider creating a Runbook skill for incident response on this infrastructure." |
| Code Quality & Review | "Consider creating a Code Scaffolding skill to generate code that passes these reviews." |

---

## Reference Files

### Anatomy and Recipes
```
${CLAUDE_PLUGIN_ROOT}/templates/
├── anatomy/
│   └── ANATOMY.md                    # Universal skill patterns (READ FIRST)
└── disciplines/
    ├── distillation/
    │   ├── RECIPE.md                 # Distillation methodology
    │   └── RUBRIC.md                 # Distillation validation rubric
    ├── composition/
    │   ├── RECIPE.md                 # Composition methodology
    │   └── RUBRIC.md                 # Composition validation rubric
    ├── investigation/
    │   ├── RECIPE.md                 # Investigation methodology
    │   └── RUBRIC.md                 # Investigation validation rubric
    └── extraction/
        ├── RECIPE.md                 # Extraction methodology
        └── RUBRIC.md                 # Extraction validation rubric
```

### Automation Scripts
```
${CLAUDE_PLUGIN_ROOT}/scripts/
├── validate-skill.js   # Validates generated skill against guidelines
└── build-agents-md.js  # Builds AGENTS.md for distillation skills
```

### Validation Agents
```
${CLAUDE_PLUGIN_ROOT}/agents/
├── preflight-validator.md  # Validates planning before generation (distillation)
└── skill-reviewer.md       # Reviews quality criteria (all disciplines)
```

### Reference Examples (Distillation)
```
${CLAUDE_PLUGIN_ROOT}/references/
├── QUALITY_CHECKLIST.md # Authoritative validation checklist
├── COMPLETE_EXAMPLE.md  # Full React example with all rule samples
├── metadata.json        # Full metadata example
└── examples/            # 12 sample rules across all categories
    ├── _sections.md     # Complete sections template (8 categories)
    ├── _template.md     # Rule template with frontmatter
    └── {prefix}-*.md    # Sample rule files
```

---

## Mandatory Requirements

**NEVER:**
- Skip validation steps (automated or agent-based)
- Generate without user-approved planning
- Release without running `validate-skill.js` AND `skill-reviewer` agent
- Use generic placeholder names (foo, bar, MyComponent) in code examples
- Write AGENTS.md manually (use build-agents-md.js)

**ALWAYS:**
- Read `${CLAUDE_PLUGIN_ROOT}/templates/anatomy/ANATOMY.md` before generating any skill
- Read the discipline's `RECIPE.md` before generating
- Use the discipline's `RUBRIC.md` for the `skill-reviewer` agent
- Include `discipline` and `type` in metadata.json
- Display planning summaries as regular text BEFORE calling AskUserQuestion

**Every rule (distillation) MUST include:**
- YAML frontmatter: `title` and `tags` (first tag = category prefix). `impact`/`impactDescription` are optional (performance skills only).
- A 1-3 sentence WHY that names the wrong default it corrects and the consequence.
- At least one code example (a single canonical example by default), with a language specifier and realistic names.

An Incorrect/Correct foil is **optional** — include it only when the wrong way is a real, common trap, and never as a strawman. A rule that restates what the model already does right should not exist at all.

---

## After Generation: Suggest Eval

After the skill passes structural validation and agent review, offer functional testing:

Display as text, then ask via `AskUserQuestion`:

```
"The skill is structurally valid and passes quality review. Want to test it on real prompts before shipping? This runs the skill on realistic tasks, compares against a baseline, and lets you review actual outputs."
Options:
- "Yes, run evals" — Launch /dev-skill:eval
- "No, ship as-is" — Done
```

If the user chooses evals, suggest: **`/dev-skill:eval {skill-path}`**

---

Now create the skill based on the user's selections, following the discipline-specific pipeline exactly.
