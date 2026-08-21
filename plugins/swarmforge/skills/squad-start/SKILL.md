---
name: squad-start
description: This skill should be used when the user asks to "start a story", "start item 3", "run the squad", "advance the story", "continue the pipeline", "kick off the backlog item", or wants work executed through the story stages. It starts a backlog item as a story and drives it stage by stage through the role agents, pausing at every approval gate.
argument-hint: "[backlog id or story id]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion
---

# Start and drive a story

Start turns one backlog item into one story and walks it through the stages its
profile names. The main session is the squad leader for the duration: it dispatches
each stage, holds every gate, and never writes a product artifact itself.

Read `../squad-pipeline/references/pipeline.md` and
`../squad-pipeline/references/state.md` before the first dispatch.

## Procedure

### 1. Resolve the target

- A backlog id that is `open` — start it.
- A story id, or a backlog id already `started` — resume it from `state.json`.
- No argument — list open items and stories in flight, and ask which.

Refuse to start a second story while one is mid-stage unless the user asks for
concurrency explicitly. Two stories in flight means worktree isolation applies.

### 2. Start

Create `.squad/stories/<story-id>/`, where `<story-id>` is the backlog id and slug.
Write `story.md` from the item body. Write `state.json` with the stages the active
profile names, empty `completed`, and every gate the stage list implies set to
`pending`. Set the backlog item's `status: started` and its `story_id`.

Record the stages on the story. Later profile changes must not rewrite a story
already in flight.

### 3. Dispatch the next stage

The next stage is the first entry in `stages` not in `completed`.

Before dispatching, verify the previous stage's gate is `approved` or `auto`. If it
is `pending`, stop and hand over to `/swarmforge:squad-approve`. Never approve a
gate while driving.

Dispatch with the Agent tool, `subagent_type` set to `swarmforge:<stage>` —
plugin agents register namespaced, and a bare stage name either errors or, worse,
resolves to an unrelated agent of the same name that happens to be installed.
`state.json` stores the bare stage name; only the dispatch is prefixed. Pass the story
packet as described in `../squad-pipeline/references/state.md`: ids, paths, stage, completed stages,
artifact paths, verify commands, the constitution path, and the working tree. Pass
paths rather than file contents — agents read for themselves.

Apply isolation per `config.json`: with `parallel-only`, add
`isolation: "worktree"` only when stories are advancing concurrently or a batched
stage fans out.

### 4. Absorb the result

On return:

- Write `handoffs/<nn>-<stage>.md` with what the agent reported, including the
  verify command and its actual result.
- If the agent handed back a blocker, write `.squad/blockers/<story-id>-<nn>.md`,
  set `blocked` in `state.json`, stop, and surface it. A blocker is resolved by a
  human decision — usually narrowing or re-slicing — not by retrying.
- Otherwise add the stage to `completed`, set `stage` to the next one, and set that
  stage's gate to `pending` if it owns one.
- If the stage wrote code and `isolation` produced a worktree, merge it. Conflicts
  belong to the main session.

Never record a verify result the agent did not report. If a stage claims a pass
without showing the command output, treat that as a blocker.

### 5. Continue or pause

Continue to the next stage unless a gate is pending, a blocker was recorded, or the
user asked to stop. When `completed` covers `stages`, mark the backlog item `done`
and report the artifacts produced.

Keep the stage list visible as the run progresses so a long story stays legible.

## Recommendation-only stages

`code-reviewer` and `architect` return recommendations and change nothing. Their
output is input to `hardener` and `senior-implementer` respectively. If either of
those stages is not in the profile, surface the recommendations to the user rather
than dropping them.

## Additional resources

- **`../squad-pipeline/references/pipeline.md`** — profiles, gates, isolation, batching.
- **`../squad-pipeline/references/state.md`** — `state.json`, packets, approval records.
- **`../squad-pipeline/references/roles.md`** — what each stage owns.
