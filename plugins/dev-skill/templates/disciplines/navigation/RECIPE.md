# Navigation Recipe

Navigation maps a technology's information ecosystem: where authoritative answers live, how to query each source, and how to verify what comes back. This is the production method for **Documentation Navigation** skills.

Navigation is the inverse of distillation. A distillation skill bakes knowledge *into* the skill — a snapshot that ages with every release. A navigation skill teaches the agent to *find* current knowledge at answer time, so it never ages: only source locations can go stale, and those are cheap to verify and update.

## The Staleness Litmus Test

The defining constraint of this discipline: **a navigation skill contains zero baked-in technical facts.** Before keeping any line, ask: *would this line need editing when the technology ships a new version?*

- "React's `use()` hook accepts a promise" — a fact about the technology. **Cut it.** The skill must send the agent to react.dev to learn this, not assert it.
- "API behavior questions: fetch `https://react.dev/reference/react/{symbol}`" — a fact about *where authority lives*. **Keep it.** It survives releases.
- "The docs version a page via the URL path (`/docs/v5/...`); a page without a version segment is latest" — navigational metadata about the source. **Keep it.**

Version schemes, URL patterns, repo layouts, and search operators are navigational. API signatures, behavior claims, defaults, and migration steps are facts — the skill's job is to route the agent to them, never to state them.

## What Navigation Produces

```
{skill-name}/
├── SKILL.md              # When to Apply + Source Map quick reference
├── metadata.json         # discipline: "navigation"
├── config.json           # Optional: local doc paths, MCP tools, internal mirrors
├── gotchas.md            # Search dead-ends discovered over time
└── references/
    ├── sources.md        # Ranked authority map with access patterns
    ├── {question}-playbook.md  # One search playbook per question type
    └── verification.md   # Authority + currency checks for found answers
```

## Inputs Needed

1. **Technology**: What library, framework, platform, or domain does this navigate?
2. **Question types**: What does the agent actually need to look up? (API signatures, breaking changes, error messages, configuration, idioms...)
3. **Tool inventory**: What can the agent use to search? (WebFetch, WebSearch, local doc dumps, SDK interface scripts, MCP servers, GitHub code search)
4. **Known sources**: Where does the user already look? Internal mirrors or wikis?

## Discovery Workflow

### Step 1: Interview

Ask the user:
- "What technology (and which parts of it) should this skill cover?"
- "What questions come up most? (API lookups, upgrade/breaking changes, error messages, configuration, examples?)"
- "What search tools are available in your sessions? (web access, local doc directories, doc-search scripts, MCP servers)"
- "Any internal sources — mirrors, wikis, pinned versions — that outrank public docs for your team?"

### Step 2: Source Census

Enumerate candidate sources, then **verify each one live** — fetch it, confirm it's current, and record how to navigate it. Candidates, in default authority order:

| Rank | Source class | Why it outranks the next |
|------|--------------|--------------------------|
| 1 | Official docs / spec | Maintained by the people who define behavior |
| 2 | Source code + type definitions | Ground truth when docs lag or are silent |
| 3 | Changelog / release notes / migration guides | The only authority on what changed between versions |
| 4 | Issue tracker / discussions | Authority on known bugs and intended-vs-actual behavior |
| 5 | Maintainer writing (blogs, talks, RFCs) | Named experts explaining rationale |

Community content (Stack Overflow, Reddit, blog posts) is a *lead generator*, never a terminal answer — anything found there must be traced back to a rank 1–3 source before the agent acts on it.

For each source that survives the census, record:
- **URL patterns**: How to construct deep links (e.g., `https://pkg.go.dev/{module}@{version}`), not just the homepage.
- **Authoritative for / NOT authoritative for**: Both directions. A source map that only says what a source is good for invites misuse ("the changelog is authoritative for what changed, NOT for how to use the current API").
- **Currency signals**: How to tell what version a page describes, where the "last updated" signal lives.
- **Access pattern**: The concrete tool invocation — a WebFetch URL template, a `site:` search operator, a local script, an MCP tool name.

### Step 3: Derive Question Types

Group the user's real lookups into 3–7 question types. The common set:

| Question type | Example |
|---------------|---------|
| `api-lookup` | "What are the parameters of X? Is it deprecated?" |
| `version-changes` | "What breaks upgrading from v4 to v5?" |
| `error-message` | "What causes error E0507 / this stack trace?" |
| `configuration` | "What config options exist and where do they go?" |
| `examples-idioms` | "What's the idiomatic way to do X?" |

Derive from the interview, don't force this set — a compiler skill may need `diagnostics`, an internal-platform skill may need `ownership` ("who owns this service?"). Each question type gets its own playbook file so the agent loads only the strategy it needs.

### Step 4: Design Playbooks

A playbook is an ordered search strategy for one question type. Rules — the same discipline as investigation decision trees:

- **Every step names a concrete tool and query.** Not "search the web" but "WebSearch: `{error text} site:github.com/{org}/{repo}/issues`". Not "check the docs" but "WebFetch `https://docs.example.com/errors/{code}`".
- **Every step states what a hit looks like.** The agent needs to know when to stop ("the reference page lists the symbol with a signature block") vs. move to the next step.
- **Every path terminates.** The final step is always an explicit escalation: "read the source at `{repo}/src/{area}`" or "ask the user — this may be internal/undocumented." Dead ends are bugs.
- **Every playbook ends in verification.** A found answer isn't done until it passes the checks in `references/verification.md`.
- **Order by hit-rate × cost.** Cheap, high-precision steps first (a deep-link fetch); broad searches later; source-code reading last.

### Step 5: Write Verification Rules

`references/verification.md` defines how the agent judges what it found:

- **Currency check**: Does the page's version match the project's version (state how to determine both)? Is the content dated, and is the date plausible for the current major version?
- **Authority check**: Is this a rank 1–3 source from the source map? If it's community content, has the claim been traced to a primary source?
- **Rejection criteria**: Content farms, listicles, undated blogs, AI-SEO filler, and answers for a different major version are rejected on sight — name the tells (no author, no date, no version, aggregated "top 10" framing).
- **Cross-check rule**: When the answer drives a destructive or hard-to-reverse action, require two independent rank 1–3 sources to agree.

### Step 6: Planning Checkpoint

Display the source map (with authority scopes) and the playbook list as regular text. Ask the user to approve before generating.

## Generation Pipeline

After user approval:

1. **Generate references/sources.md** — Full ranked source map with access patterns
2. **Generate references/{question}-playbook.md** — One per question type
3. **Generate references/verification.md** — Currency, authority, and rejection rules
4. **Generate SKILL.md** — When to Apply, Source Map quick reference, playbook routing table
5. **Generate config.json** — Only if local paths / MCP tools / internal mirrors exist
6. **Generate metadata.json** with `discipline: "navigation"` and `type: "doc-navigation"`
7. **Generate gotchas.md** — Initialize with "No known gotchas yet"
8. **Validate** with navigation RUBRIC.md

## Growth Pattern

Navigation skills grow through use, not through releases:
- A search dead-end (source moved, pattern stopped matching) → update `sources.md`, log the old pattern in `gotchas.md`
- A recurring question with no playbook → add a playbook file
- A source that gave a stale answer that passed verification → tighten `verification.md`

## Navigation vs Distillation: Key Differences

| Aspect | Distillation | Navigation |
|--------|-------------|------------|
| Core output | Reference rules (knowledge baked in) | Source map + search playbooks (knowledge fetched live) |
| Value lives in | The facts and code examples | Knowing where authority lives and how to query it |
| Staleness | Ages with every release | Only source locations can age |
| Validation focus | Factual accuracy of claims | Zero baked-in facts, live sources, terminating playbooks |
| Right choice when | Correcting the model's wrong defaults on stable ground | The ground moves faster than the skill would be updated |

The two compose: a distillation skill corrects wrong defaults the model has *today*; its navigation companion answers the questions no snapshot can.
