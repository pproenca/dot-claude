# Distillation Recipe

Distillation turns authoritative sources into a **distilled reference**: the smallest set of decisions a capable model gets wrong by default, each explained so the model can generalize from it. It is the method for **Library/API Reference** and **Code Quality/Review** skills.

Start from this premise: **the model is already competent.** It knows the language. Your job is not to re-teach it — it is to correct the specific points where its default behavior is wrong, outdated, or misaligned with this library/codebase. Everything else is noise that buries the signal.

## What distillation produces

```
{skill-name}/
├── SKILL.md              # Entry point: when to apply + quick reference
├── AGENTS.md             # Auto-built TOC (build-agents-md.js) — never hand-written
├── metadata.json
├── references/
│   ├── _sections.md      # Category definitions, ordered by importance
│   └── {prefix}-{slug}.md # Individual rules
└── assets/templates/_template.md
```

## The one test that matters: does the rule change behavior?

A rule earns its place only if you can name the **wrong default it corrects** — the thing a competent model (or engineer) would otherwise do, that this rule prevents. Apply this to every candidate rule:

1. **What does the model do here without the rule?** State it plainly.
2. **Is that actually wrong — or just not how you'd phrase it?** If the default is already correct, **cut the rule.** Restating what the model already does is hand-holding; it dilutes the rules that matter.
3. **Will the WHY generalize?** A rule that explains the underlying reason covers a dozen situations you never enumerated. A rule that lists scenarios covers only those scenarios.

> Brevity is the soul of wit. Prefer one principle that generalizes over ten rules that enumerate. If you cannot articulate the wrong default a rule corrects, it is not a rule — it is filler. Delete it.

**Proof, not word count.** There is no rule-count target. Completeness is proven *behaviorally*: if the skill makes the model handle the target tasks correctly, it is complete — whether that took 6 rules or 26. Under-coverage shows up as a failed task, not as a low number. Padding to hit a count is the exact failure mode this recipe exists to prevent.

## Explain WHY, never just WHAT

The single highest-leverage habit. The model generalizes from understood reasoning, not from dictation. When it knows *why*, it applies the principle to cases you didn't foresee. When you only dictate, it follows mechanically and breaks at the first edge case.

| Effective — generalizes | Ineffective — brittle |
|-------------------------|-----------------------|
| "Thread a context through every outbound call so a cancelled request also cancels the goroutines it spawned" | "ALWAYS pass `context.Context`" |
| "Return early on the error so the happy path stays unindented and a missing check is visible" | "Handle errors properly" |
| "Mark the dependency array exhaustively; a missing dep captures a stale value from the render it closed over" | "Use `useEffect` correctly" |

If you catch yourself writing ALWAYS / NEVER / MUST in caps, stop and write the consequence instead.

## Examples: one canonical, a foil only when the trap is real

Default to a **single correct, copy-pasteable example** — the canonical way to do the thing. That is usually all the model needs.

Add an **Incorrect / Correct** pair *only* when the wrong way is a genuine, common trap the reader would otherwise fall into. A manufactured "incorrect" example — a strawman nobody would actually write — is worse than none: it costs tokens and teaches nothing. When you do use a foil, keep the diff minimal (same names, only the key line changes) so the contrast is the lesson.

```markdown
## {The decision this rule settles}

{1–3 sentences of WHY — what the default does and why it's wrong, in concrete terms.}

```{language}
{the canonical way — production-realistic names, never foo/bar}
```

Reference: [{source title}]({url})
```

## Categories and ordering

Group rules into 4–8 categories so the reader can navigate. Order by **importance × frequency** — the decisions that come up most and cost most when wrong go first.

**Impact tiers and quantified metrics are optional and apply only to genuinely performance-shaped skills.** For a perf skill, importance often follows the execution lifecycle (earlier stages cascade downstream), and tagging rules with an `impact` level and a quantified `impactDescription` ("2–10× improvement", "O(n)→O(1)") is meaningful. For correctness, idiom, or API-usage skills, **skip the tiers** — ordering by importance is enough. Never invent a "2–10× improvement" for a rule about API correctness; a plain consequence ("prevents silent truncation") is the honest description.

### Category starting points (a performance lens — adapt, don't obey)

These are useful when the skill *is* about performance. They are starting points, not a required taxonomy.

| Domain | Typical high-impact categories (prefixes) |
|--------|-------------------------------------------|
| Web frameworks (React, Vue) | network waterfalls (`async`), bundle size (`bundle`), server work (`server`), rendering (`render`) |
| Systems (C++, Rust, Go) | memory (`mem`), cache locality (`cache`), algorithms (`algo`), concurrency (`conc`) |
| Backend services | I/O patterns (`io`), concurrency (`conc`), serialization (`serial`), caching (`cache`) |
| Databases | query plans (`query`), indexing (`index`), connections (`conn`), transactions (`tx`) |

For non-performance skills, derive categories from the **kinds of decisions** the domain forces: e.g. for an API reference — auth, pagination, error handling, idempotency, rate limits.

## Rule anatomy

```markdown
---
title: {Decision-oriented title}
tags: {prefix}, {concept}, {concept}
# optional — performance skills only:
# impact: CRITICAL|HIGH|MEDIUM|LOW
# impactDescription: 2-10× improvement
---

## {title}

{WHY: the wrong default and its concrete consequence.}

```{language}
{canonical example}
```

Reference: [{source title}]({url})
```

**Required:** `title`; `tags` with the first tag = the category prefix; an H2 matching the title; a WHY; at least one fenced code block with a language; a source link.
**Optional:** `impact`, `impactDescription`; an Incorrect/Correct foil; `**When NOT to use this pattern:**`; `**Alternative ({context}):**`.

### Title patterns

| Pattern | When | Example |
|---------|------|---------|
| `{Verb} {object} {context}` | Recommending an action | `Thread context through outbound calls` |
| `Avoid {anti-pattern}` | Prohibiting a real trap | `Avoid barrel-file imports` |
| `Use {X} for {Y}` | A specific tool/API | `Use errgroup for fan-out` |
| `{X} for {Y}` | API + use case | `Promise.all() for independent work` |

### Tag rules

1. First tag = the category prefix (this is what files are grouped by).
2. Add 2–4 more for concepts/tools. Lowercase, hyphenated.

## Sources: authoritative or nothing

The strength of distillation is that it draws only from sources that are actually right. Hold the line — this is where SEO sludge gets in if you let it.

### Accept
- Primary maintainers' docs (react.dev, go.dev, the library's own README / API reference)
- The library's own source code and type definitions
- Specs and standards (TC39, RFCs, PEPs, ISO, the database's reference manual)
- Named engineering writing with first-hand authority or real data (a maintainer's post; a benchmark that states its methodology)

### Reject on sight — the SEO layer
- Content farms and listicles (geeksforgeeks, w3schools-style pages, "Top 10 …" posts)
- AI-generated SEO filler: no named author, no date, generic phrasing that just restates the docs
- Stack Overflow / Reddit answers *as a primary citation* — fine as a lead, but then cite the doc or code they point to
- Undated blogs, marketing pages, course-seller "ultimate guide" content

### Verify every source you keep
1. **Authority** — written by a maintainer, spec author, or named expert? Or anonymous?
2. **Currency** — does it match the library's current major version? Stale advice is wrong advice.
3. **Support** — does the page actually back the claim, or did the title just sound right?
4. **Traceability** — can you reproduce the claim from a primary source (docs/spec/code)? If you can't trace it, drop it.

When sources conflict, the primary one wins. When in doubt, cite the docs or the code, not a blog.

## Generation workflow

1. **Research** — gather authoritative sources; list the *wrong defaults* worth correcting (this list, not a count, scopes the skill).
2. **Planning checkpoint** — show categories, the wrong-default each rule corrects, and the vetted sources; get approval. Optionally run the `preflight-validator` agent.
3. **Generate** — `references/_sections.md` → rules (apply the earn-its-place test to each; cut anything that restates a correct default) → `SKILL.md`, `metadata.json`, `assets/templates/_template.md`.
4. **Build AGENTS.md** — `node ${CLAUDE_PLUGIN_ROOT}/scripts/build-agents-md.js {skill-dir}`. Never hand-write it.
5. **Validate** — `node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js {skill-dir}`, then the `skill-reviewer` agent with this discipline's `RUBRIC.md`.
6. **Prove** — exercise the skill on its target tasks. Failures reveal genuine gaps; fill those. Do not add rules the tasks don't demand.

## Sections file format

```markdown
# Sections

## 1. {Category Name} ({prefix})

**Description:** {One sentence: what decisions this category covers and why they matter.}

## 2. {Category Name} ({prefix})

**Description:** {…}
```

`**Impact:** {LEVEL}` is optional — include it (with two trailing spaces for the line break) only for performance skills that use tiers. Sections must stay in importance order; if you use impact tiers, that order must be non-increasing (CRITICAL before HIGH, etc.).

## Build system

`AGENTS.md` is a slim, auto-generated table of contents (~60 lines), never the place to put content. Build it with `build-agents-md.js`; use `--verify-generated` in `validate-skill.js` to detect manual edits.
