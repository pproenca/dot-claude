# Universal Skill Anatomy

Every skill, regardless of discipline, shares these structural patterns and principles. This document is the foundation layer — discipline-specific recipes build on top of it.

## Skill as a Folder

A skill is a folder, not a file. The entire file system is a form of context engineering and progressive disclosure. Tell the agent what files are in your skill, and it will read them at appropriate times.

```
{skill-name}/
├── SKILL.md              # Entry point (always loaded by agent)
├── metadata.json         # Version, discipline, type, references
├── config.json           # User-specific setup (optional)
├── gotchas.md            # Failure points discovered over time (optional)
├── AGENTS.md             # Auto-built TOC navigation (optional, built by script)
└── {discipline-specific}/ # References, scripts, templates, etc.
```

## SKILL.md — The Entry Point

SKILL.md is loaded when the agent triggers the skill. It must be concise and navigational — point to deeper content, don't embed it.

### Required Frontmatter

```yaml
---
name: {skill-name}
description: {trigger description — see "Description Field" below}
---
```

### Required Sections

| Section | Purpose |
|---------|---------|
| **When to Apply** | 3-5 specific scenarios. Derived from the skill's domain. |
| **How to Use** | Navigation instructions — what files to read, what order. |

### Conditional Sections

| Section | When to Include |
|---------|-----------------|
| **Setup** | When `config.json` exists and needs user input on first run. |
| **Gotchas** | When common failure points exist (or pointer to `gotchas.md`). |
| **Quick Reference** | When the skill has many navigable items (rules, templates, queries). |

## The Description Field

The description is the primary triggering mechanism. Claude scans every skill's description to decide relevance — it competes with other skills for attention. Claude currently tends to **undertrigger** skills (not use them when they'd be useful), so descriptions should be slightly "pushy."

**Good:** `Use this skill whenever writing, reviewing, or refactoring Python code for performance — covers async patterns, memory management, data structures, and import optimization. Trigger even if the user doesn't explicitly mention "performance" but is working on Python code that could benefit from optimization.`

**Bad:** `A comprehensive guide to Python best practices.`

**Also bad:** `Python performance optimization guidelines. This skill should be used when writing Python code.` *(too passive, not distinctive)*

Rules:
- Use imperative form: "Use this skill for/whenever..." not "This skill should be used when..."
- Focus on user **intent** (what they're trying to achieve) not implementation details (how the skill works)
- Be specific about trigger contexts — name technologies, activities, and edge cases
- Make it distinctive — if two skills could match a query, the description should make clear why THIS one wins
- Be slightly pushy: "even if the user doesn't explicitly ask for X" helps with undertriggering
- Keep under 200 words — it's injected into every query and there may be many skills
- Descriptions can be tested and optimized with `/dev-skill:eval`'s trigger optimization

## Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata** (name + description) — Always in context. ~100-200 words.
2. **SKILL.md body** — Loaded when the skill triggers. Keep under 500 lines; if approaching this limit, add hierarchy with clear pointers to references.
3. **Bundled resources** — Loaded as needed. Unlimited size. Scripts can execute without being loaded into context.

| Layer | What | Size |
|-------|------|------|
| SKILL.md | When to use, navigation, quick reference | <500 lines |
| Top-level references | Category overviews, workflow steps, symptom catalogs | ~50-100 lines each |
| Deep references | Individual rules, scripts, query patterns, templates | Unlimited |

Point to deeper content from shallower layers with guidance on WHEN to read them:
```markdown
Read [detailed workflow](references/workflow.md) when executing the deployment — it has step-by-step instructions with rollback procedures.
```

For large reference files (>300 lines), include a table of contents at the top.

**Domain organization**: When a skill supports multiple domains/frameworks, organize by variant so Claude reads only the relevant file:
```
cloud-deploy/
├── SKILL.md (workflow + selection logic)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

## Setup & Configuration

Skills that need user-specific context (Slack channels, service URLs, dashboard IDs) use a `config.json` pattern:

```json
{
  "slack_channel": "",
  "service_url": "",
  "_setup_instructions": {
    "slack_channel": "The Slack channel to post standups to (e.g., #team-standup)",
    "service_url": "Base URL of the service this skill monitors"
  }
}
```

If `config.json` exists but has empty required fields, the skill should:
1. Detect missing config on first use
2. Ask the user via `AskUserQuestion`
3. Save their responses to `config.json`
4. Proceed with the workflow

Secrets are NEVER stored in config.json — reference environment variables instead:
```json
{
  "api_key_env": "DATADOG_API_KEY"
}
```

## Gotchas

The highest-signal content in any skill. Gotchas capture failure points the agent hits when using the skill. They should be:
- Specific (not "be careful with X" — say what goes wrong and how to avoid it)
- Accumulated over time (append-only, with dates)
- Stored in `gotchas.md` for progressive disclosure, or inline in SKILL.md if few

Format:
```markdown
## Gotchas

### The Stripe test clock must be advanced before checking invoice state
The checkout-verifier script creates a Stripe test clock but doesn't advance it.
If you check invoice status immediately, it shows "draft" not "paid."
Fix: Call `stripe test_clocks advance` before the assertion step.
Added: 2026-03-15
```

## State & Memory

Skills can persist data across runs. Use `${CLAUDE_PLUGIN_DATA}` for stable storage that survives skill upgrades:

| Pattern | When | Example |
|---------|------|---------|
| Append-only log | Track history of runs | `standups.log` — agent reads its own history |
| JSON state | Track structured state | `last-run.json` — timestamps, counters |
| SQLite | Complex queries on accumulated data | `metrics.db` — query across runs |

Data stored in the skill directory itself may be deleted on upgrade. Always use `${CLAUDE_PLUGIN_DATA}` for persistent state.

## On-Demand Hooks

Skills can include hooks that activate only when the skill is loaded and last for the session. Use for opinionated behavior you don't want globally:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "echo 'Checking for destructive commands...'",
          "timeout": 5
        }]
      }
    ]
  }
}
```

Examples:
- `/careful` — blocks `rm -rf`, `DROP TABLE`, `force-push` via PreToolUse matcher on Bash
- `/freeze` — blocks Edit/Write outside a specific directory

## metadata.json

Every skill has a `metadata.json` with these fields:

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

The `discipline` and `type` fields enable discipline-aware validation and evolution.

## Naming Conventions

| Element | Pattern | Example |
|---------|---------|---------|
| Skill name | `{org}-{domain}-{type-hint}` | `acme-checkout-verifier`, `acme-react-best-practices` |
| Skill directory | kebab-case matching skill name | `acme-checkout-verifier/` |
| File names | kebab-case | `verify-checkout.sh`, `symptom-timeout.md` |
| Config keys | snake_case | `slack_channel`, `service_url` |

## Writing Principles

### Explain the Why

The most important writing principle for skills: **explain WHY, not just WHAT.** LLMs are smart — they generalize better from understood reasoning than from rigid rules. When you explain why a pattern matters, the model can apply the principle to novel situations. When you just dictate "ALWAYS do X," the model follows the rule mechanically and breaks on edge cases.

| Effective | Ineffective |
|-----------|-------------|
| "Use server components for data fetching because client-side fetches create waterfalls — the browser must download JS, parse it, then fetch data sequentially" | "ALWAYS use server components for data fetching" |
| "Run the deploy script instead of manual kubectl commands because the script includes the canary check and auto-rollback that manual deploys skip" | "NEVER deploy manually" |

If you find yourself writing ALWAYS or NEVER in all caps, or building super-rigid structures, that's a signal to reframe. Explain the reasoning so the model understands the tradeoff.

### Language Patterns

| Do | Don't |
|----|-------|
| Imperative form: "Run", "Check", "Use" | Hedging: "Consider", "You might want to" |
| Specific: "2-10x improvement" | Vague: "significant improvement" |
| Technical: precise terminology | Marketing: "blazing fast", "revolutionary" |
| Reasoning: "because X causes Y" | Dictation without reasoning: "MUST do X" |

### Bundle Scripts for Anything Deterministic

Scripts execute without being loaded into context — they cost zero tokens until invoked. For anything deterministic or repetitive, write a script rather than explaining the steps in prose:

- Validation checks → `scripts/validate.sh`
- Data transformation → `scripts/transform.py`
- Report generation → `scripts/generate-report.py`
- Template rendering → `scripts/scaffold.sh`

This applies to ALL disciplines, not just composition. A distillation skill might bundle a linter config. An investigation skill might bundle query scripts. An extraction skill's templates ARE the bundled scripts.

## Safety — Principle of Lack of Surprise

A skill's contents should not surprise the user in their intent if described. Skills must not contain exploit code, data exfiltration, or content that could compromise system security. Do not create skills designed to facilitate unauthorized access or misleading behavior.

## Quality Markers (Universal)

Signs of a good skill regardless of discipline:
- Description triggers correctly (agent finds it when relevant, doesn't trigger when irrelevant)
- Progressive disclosure works (agent reads deeper content when needed, not all at once)
- Instructions explain the WHY — model can generalize to novel situations
- Setup handles missing config gracefully
- Gotchas are specific and actionable
- Content is current (references are live, advice matches current versions)
- Scripts handle anything deterministic (not explained in prose)

Red flags:
- SKILL.md over 500 lines (too much inline, needs progressive disclosure)
- No gotchas after extended use (gotchas always exist — they haven't been captured)
- Generic advice that could apply to any technology
- Lots of ALWAYS/NEVER/MUST without explaining why
- Hardcoded secrets or paths
- Description that's a summary, not an intent-focused trigger description

## Composing Skills

Skills can reference other skills by name. The agent will invoke them if installed. For complementary functionality, suggest related skills in SKILL.md:

```markdown
## Related Skills
- `acme-rollback-runbook` — Diagnosis and rollback procedures for failed deployments
- `acme-deploy-workflow` — The deployment workflow this runbook diagnoses
```

Dependency management between skills is not formalized. Keep skills self-contained and reference others as optional enhancements.
