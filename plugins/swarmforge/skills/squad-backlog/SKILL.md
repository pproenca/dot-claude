---
name: squad-backlog
description: This skill should be used when the user asks to "add a backlog item", "slice this into stories", "turn this doc into stories", "break down this design", "import the vision doc", "load the backlog", or hands over an architecture document, RFC or PRD and wants it turned into work the squad can execute. It slices intent into INVEST-sized items and writes them to .squad/backlog/ without starting any of them.
argument-hint: "[path to a document, or a description of the work]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# Load the backlog

Turn intent into backlog items. One item becomes exactly one story and one
implementation plan, so an item that cannot be built alone is a defect introduced
here, not downstream.

Nothing in the pipeline decomposes a document. This skill is the only place
slicing happens.

## Procedure

### 1. Establish the source

- **A document path** — read it in full before slicing. A long design document
  usually names its own slices: migration plans, acceptance criteria, and
  keep/reshape/retire sections are where stories come from, not the narrative
  chapters.
- **A description** — ask what the observable outcome is, then slice.
- **Neither** — ask which it is.

Refuse to slice from a summary. Read the actual source.

### 2. Slice

Apply the tests in `references/slicing.md`. Each candidate item must state an
observable outcome, be buildable while every other item does not yet exist, and be
verifiable by the project's own test command.

A document of any size usually yields a handful of first items, not thirty. Prefer
depth over coverage: the items that unblock everything else, sliced properly, beat
an exhaustive shallow list.

### 3. Present before writing

Show the proposed items as a table — id, title, one-line outcome, and what it
explicitly does not include. Ask for corrections. Slicing is a judgement the
operator owns; this skill proposes.

### 4. Write the items

One file per item at `.squad/backlog/<id>-<slug>.md`, id zero-padded and sequential
from the highest existing id:

```markdown
---
id: 003
title: Persist review snapshots to the registry
status: open
story_id: null
---

## Outcome

One sentence naming what becomes observably true.

## In scope

The behaviour this item owns.

## Not in scope

Every neighbouring item by name, and the behaviour each of them owns.

## Ports

Behaviour this item must name but not build, and the dummy state that lets it run
alone.

## Acceptance

What must hold for this item to be finished, in terms the project's tests can check.
```

The `Not in scope` and `Ports` sections are what keep the analyst honest later.
An item without them will produce a plan that assumes unbuilt work exists.

### 5. Do not start anything

Writing items never starts them. Report the ids written and point at
`/swarmforge:squad-start`.

## When the source lives elsewhere

Agents read the repository they run in. A document outside the working tree — in
another worktree, or outside the repo — is invisible to them. Either copy it into
the tree, or carry the relevant text into the item bodies, which do travel. Say
which was done.

## Additional resources

- **`references/slicing.md`** — the INVEST tests, vertical-slice heuristics, and
  the failure modes that produce unbuildable items.
- **`../squad-pipeline/references/state.md`** — the backlog item format and the
  rest of the on-disk contract.
