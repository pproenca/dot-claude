# swarmforge

A disciplined story pipeline for Claude Code. One backlog item becomes one story;
that story walks an ordered list of stages; each stage is a subagent that owns
exactly one artifact and one concern. Three stages produce artifacts a human
approves before work continues.

The separation is the product. A reviewer that cannot edit, an implementer that
cannot widen scope, and a plan that must name what it is *not* building are what
stop an agent pipeline from confidently building the wrong thing.

## Relationship to upstream SwarmForge

This is a native reimplementation of the workflow from
[unclebob/swarm-forge](https://github.com/unclebob/swarm-forge) (`squad` branch),
not a wrapper around it. Nothing here needs Babashka, tmux, a daemon, a dashboard,
or an external agent CLI — the engine is Claude Code itself, and the state machine
is files under `.squad/`.

What carried over: the role separation and their contracts, the gate discipline,
the one-item-one-story rule, the profiles. What did not: the tmux session model,
the persistent squad leader and troubleshooter (your session is both), the
`squadd` daemon and HTTP dashboard, and the Clojure-specific acceptance-runner
scaffolding baked into the upstream role prompts.

## Install

```sh
claude --plugin-dir ~/.claude/plugins/swarmforge
```

## Use

```
/swarmforge:squad-init            # tailor the pipeline to this repository
/swarmforge:squad-backlog <doc>   # slice intent into INVEST-sized items
/swarmforge:squad-start <id>      # start an item and drive it through the stages
/swarmforge:squad-status          # the board, pending gates, blockers
/swarmforge:squad-approve <id>    # decide a gate
```

`squad-init` first: it detects the repository's real language and test commands and
writes a project-tailored constitution that every agent reads. Running the pipeline
against a generic constitution produces confidently wrong work.

## Pipeline

```
backlog item ──Start──▶ story ──▶ analyst ──[plan gate]──▶ gherkin-writer
     │                                                           │
     │                                                    [gherkin gate]
     │                                                           ▼
     └── other items are non-goals          implementer ──▶ cleaner ──▶ architect
```

| Profile | Stages |
|---|---|
| `two-pack` | implementer → cleaner |
| `four-pack` (default) | analyst → gherkin-writer → implementer → cleaner → architect |
| `six-pack` | analyst → gherkin-writer → qa-procedure-writer → implementer → cleaner → code-reviewer → hardener → qa-runner → architect → senior-implementer |

## Components

| Type | Names |
|---|---|
| Skills | `squad-pipeline` (the contract, loaded when the pipeline is the subject), `squad-init`, `squad-backlog`, `squad-start`, `squad-status`, `squad-approve` |
| Agents | analyst, gherkin-writer, qa-procedure-writer, implementer, cleaner, code-reviewer, hardener, qa-runner, architect, senior-implementer |
| Hooks | `SessionStart` — surfaces in-flight stories and pending gates |

## Configuration

`.squad/config.json`, written by `squad-init`:

```json
{
  "profile": "four-pack",
  "gates": { "plan": true, "gherkin": true, "qa_procedure": true },
  "isolation": "parallel-only",
  "verify": {
    "test": "uv run pytest",
    "lint": "uv run ruff check .",
    "typecheck": "uv run pyright"
  },
  "models": {}
}
```

- **profile** — one of the three above. A `stages` array overrides it entirely.
- **gates** — a gate set `false` records an `auto` approval and never pauses.
- **isolation** — `parallel-only` (default) uses git worktrees only when stories run
  concurrently; `always` isolates every code-writing stage; `never` runs everything
  in the working tree.
- **verify** — the commands agents run before handing back. Results are reported
  verbatim, failures included.

## State

Everything lives in `.squad/` in the target repository — plain markdown and small
JSON, greppable and diffable. Layout and schemas are documented in
`skills/squad-pipeline/references/state.md`.

Whether `.squad/` is committed is asked at init, not decided silently.

## Design rules

- **One item, one story.** Nothing decomposes a document — slicing happens in
  `squad-backlog`, before anything starts.
- **Agents do not spawn agents.** Every result returns to the main session.
- **Reviewers do not edit.** `code-reviewer` and `architect` emit recommendations;
  `hardener` and `senior-implementer` apply them.
- **Gates belong to humans.** A subagent never records an approval.
- **Verify honestly.** No stage reports a pass it did not observe.
