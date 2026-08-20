# State on disk

All state lives under `.squad/` in the target repository. There is no daemon and no
server; the files are the state machine. Everything is plain markdown or small JSON
so it stays greppable and diffable.

```
.squad/
  config.json                       # profile, gates, isolation, verify commands
  constitution.md                   # project-tailored engineering rules
  backlog/<id>-<slug>.md            # one item = one story-to-be
  stories/<story-id>/
    story.md                        # the started story text
    state.json                      # stage cursor, gate status, history
    plan.md                         # analyst
    <story-id>.feature              # gherkin-writer
    qa-procedure.md                 # qa-procedure-writer
    implementer-notes.md            # qa-procedure-writer
    review.md                       # code-reviewer
    architecture.md                 # architect
    handoffs/<nn>-<role>.md         # what each stage returned
  approvals/<story-id>-<gate>.json
  blockers/<story-id>-<nn>.md
```

## config.json

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

`verify` commands are written by `squad-init` from what the repository actually
uses. Every agent that touches executable code runs `verify.test` before handing
back and reports the result verbatim. `models` optionally pins a model per agent
name.

## Backlog item

```markdown
---
id: 003
title: Persist review snapshots to the registry
status: open
story_id: null
---

Body: the story text. What is in scope, what is explicitly not, and any
acceptance the operator already knows.
```

`status` is `open`, `started`, or `done`.

## state.json

```json
{
  "story_id": "003-persist-review-snapshots",
  "title": "Persist review snapshots to the registry",
  "profile": "four-pack",
  "stages": ["analyst", "gherkin-writer", "implementer", "cleaner", "architect"],
  "completed": ["analyst"],
  "stage": "gherkin-writer",
  "gates": { "plan": "approved", "gherkin": "pending" },
  "blocked": null,
  "updated_at": "2026-08-20T19:40:00Z"
}
```

Gate values: `pending`, `approved`, `rejected`, `auto`, or absent when the stage
that owns it is not in `stages`.

## Approval record

```json
{
  "story_id": "003-persist-review-snapshots",
  "gate": "plan",
  "decision": "approved",
  "artifact": ".squad/stories/003-persist-review-snapshots/plan.md",
  "note": "Narrowed to the write path only.",
  "decided_at": "2026-08-20T19:40:00Z"
}
```

`decision` is `approved`, `rejected`, or `auto`. A rejection carries the reason in
`note` and creates a blocker.

## Story packet

The packet is what a stage's agent receives. Assemble it as literal text in the
agent prompt — agents read files themselves, so pass paths, not contents, for
anything large:

- story id and title
- absolute path to the story directory
- the stage being executed and the stages already complete
- paths to every artifact produced so far
- the `verify` commands from config
- the path to `.squad/constitution.md`
- the working tree (repository root, or the assigned worktree)
