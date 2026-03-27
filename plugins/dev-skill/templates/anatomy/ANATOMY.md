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

The description field is for the model, not for humans. When a session starts, the agent scans every available skill's description to decide relevance. Write it as a trigger description:

**Good:** `Python performance optimization guidelines. This skill should be used when writing, reviewing, or refactoring Python code. Triggers on tasks involving async patterns, memory management, data structures, or import optimization.`

**Bad:** `A comprehensive guide to Python best practices.`

Rules:
- Include specific trigger keywords the user might type
- Use third-person format: "This skill should be used when..."
- Name the technology and activity types explicitly
- Keep under 200 characters for the first sentence (shown in skill listings)

## Progressive Disclosure

Structure information in layers. The agent reads what it needs, when it needs it.

| Layer | What | Size |
|-------|------|------|
| SKILL.md | When to use, navigation, quick reference | ~100-150 lines |
| Top-level references | Category overviews, workflow steps, symptom catalogs | ~50-100 lines each |
| Deep references | Individual rules, scripts, query patterns, templates | Unlimited |

Point to deeper content from shallower layers:
```markdown
See [detailed workflow](references/workflow.md) for step-by-step instructions.
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

## Language Patterns

Across all disciplines, skill content follows these patterns:

| Do | Don't |
|----|-------|
| Direct imperatives: "Run", "Check", "Use" | Hedging: "Consider", "You might want to" |
| Specific: "2-10x improvement" | Vague: "significant improvement" |
| Technical: precise terminology | Marketing: "blazing fast", "revolutionary" |
| Neutral: state facts | Opinionated without evidence |

## Quality Markers (Universal)

Signs of a good skill regardless of discipline:
- Description triggers correctly (agent finds it when relevant)
- Progressive disclosure works (agent reads deeper content when needed)
- Setup handles missing config gracefully
- Gotchas are specific and actionable
- Content is current (references are live, advice matches current versions)

Red flags:
- SKILL.md over 300 lines (too much inline, needs progressive disclosure)
- No gotchas after extended use (gotchas always exist — they haven't been captured)
- Generic advice that could apply to any technology
- Hardcoded secrets or paths
- Description that's a summary, not a trigger description

## Composing Skills

Skills can reference other skills by name. The agent will invoke them if installed. For complementary functionality, suggest related skills in SKILL.md:

```markdown
## Related Skills
- `acme-rollback-runbook` — Diagnosis and rollback procedures for failed deployments
- `acme-deploy-workflow` — The deployment workflow this runbook diagnoses
```

Dependency management between skills is not formalized. Keep skills self-contained and reference others as optional enhancements.
