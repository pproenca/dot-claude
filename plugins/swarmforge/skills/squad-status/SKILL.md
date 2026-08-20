---
name: squad-status
description: This skill should be used when the user asks "squad status", "where are we", "what's in flight", "show the board", "what needs approval", "any blockers", or wants to see which stories exist and what stage each has reached. It reads .squad/ and reports the board, pending gates, and blockers without changing anything.
argument-hint: "[story id]"
allowed-tools: Read, Bash, Glob, Grep
---

# Report the board

Read-only. Report what `.squad/` says and change nothing.

## Procedure

### 1. Handle the empty cases

No `.squad/` — say the squad is not initialised here and point at
`/swarmforge:squad-init`. `.squad/` with an empty backlog — say so and point at
`/swarmforge:squad-backlog`.

### 2. Read the state

Read `config.json`, every `backlog/*.md` front matter, and every
`stories/*/state.json`. Do not read story artifacts unless reporting on a single
story.

### 3. Report

Lead with what needs a human:

- **Pending gates** — story, gate, and the artifact path to review. This is the
  first thing the operator needs.
- **Blockers** — story, the obstacle, and where it was recorded.

Then the board, one row per story: id, title, stage reached, stages remaining, gate
status. Then open backlog items not yet started, and finally completed stories as a
count rather than a list.

Close with the single most useful next action — approve a named gate, resolve a
named blocker, or start a named item.

### 4. A single story

When given a story id, report that story only: its stages with each marked done,
current or pending; every artifact written with its path; its gate decisions with
notes; and its handoff history in order.

## Reporting honestly

Report what the files say, including states that look wrong: a story whose stage
cursor disagrees with its completed list, an approval for a gate no stage owns, a
story directory with no `state.json`. Name the inconsistency rather than smoothing
it over — it usually means a run was interrupted mid-stage.
