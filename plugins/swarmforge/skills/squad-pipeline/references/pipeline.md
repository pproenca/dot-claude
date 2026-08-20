# The pipeline

## Profiles

A profile is an ordered stage list. `.squad/config.json` names the active profile;
a story records the stages it was started with, so changing the profile never
rewrites a story already in flight.

| Profile | Stages |
|---|---|
| `two-pack` | implementer → cleaner |
| `four-pack` (default) | analyst → gherkin-writer → implementer → cleaner → architect |
| `six-pack` | analyst → gherkin-writer → qa-procedure-writer → implementer → cleaner → code-reviewer → hardener → qa-runner → architect → senior-implementer |

A `stages` array in `config.json` overrides the profile entirely. Stage names must
match agent names exactly.

## Gates

Three stages produce artifacts a human approves before the next stage may start.

| Producing stage | Gate | Artifact |
|---|---|---|
| analyst | `plan` | `plan.md` |
| gherkin-writer | `gherkin` | `<story-id>.feature` |
| qa-procedure-writer | `qa_procedure` | `qa-procedure.md` + `implementer-notes.md` |

`config.json.gates` turns each on or off. A gate that is off records an
`auto` approval and the pipeline continues without pausing.

A gate is never approved by a subagent. Only the main session, acting on an
explicit human answer, writes an approval record.

## Advancing a story

1. Read `state.json`. The next stage is the first entry in `stages` not in `completed`.
2. If the previous stage owns a gate and that gate is not `approved`, stop and ask.
3. Dispatch the stage's agent with the story packet (see `state.md`).
4. On return, write the handoff, mark the stage complete, and record any blocker.
5. Repeat until `completed` covers `stages`. The story is then done.

A stage that hands back a blocker does not advance. Record it under
`.squad/blockers/` and surface it; a blocker is resolved by a human decision,
usually by narrowing the story or re-slicing it.

## Batching

In `six-pack`, hardener, qa-runner, architect and senior-implementer may process every
story that has reached them, rather than one story at a time. Batch only when more
than one story is waiting at the same stage.

## Isolation

`config.json.isolation`:

- `parallel-only` (default) — stages run in the working tree. Worktree isolation
  (`isolation: "worktree"` on the Agent tool) applies only when two or more stories
  advance concurrently, or when a batched stage fans out.
- `always` — every stage that writes code gets its own worktree; the main session
  merges each result.
- `never` — everything in the working tree, strictly sequential.

Read-only stages (code-reviewer, architect) never need a worktree.

## Ownership

The main session is the squad leader. It routes work, holds the gates, merges, and
talks to the human. It never writes a product artifact itself — no plans, no
Gherkin, no production code, no reviews. Every artifact comes from the agent that
owns it.

Agents hand back only to the main session. Agents never dispatch other agents.
