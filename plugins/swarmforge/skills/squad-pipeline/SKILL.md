---
name: squad-pipeline
description: This skill should be used when the user mentions "the squad", "squad pipeline", "swarmforge", ".squad/", a "story stage", a "story gate", "advance the story", "who owns this artifact", or asks how backlog items become stories and which role writes what. It carries the pipeline contract - stage order, profiles, gates, on-disk state, and role ownership - that the squad-init, squad-backlog, squad-start, squad-status, and squad-approve skills all depend on.
---

# Squad pipeline

A disciplined story pipeline. One backlog item becomes one story; that story walks
an ordered list of stages; each stage is a subagent that owns exactly one artifact
and one concern. Three stages produce artifacts a human approves before work
continues. All state is files under `.squad/` in the target repository.

The main session is the squad leader: it routes, holds gates, merges, and talks to
the human. It never writes a product artifact itself.

## When each part applies

- **Stage order, profiles, gate semantics, isolation** — read `references/pipeline.md`.
- **On-disk layout, `config.json`, `state.json`, approval records, the story packet** — read `references/state.md`.
- **Which agent writes what, and the invariants all of them share** — read `references/roles.md`.

Read the reference that answers the question at hand rather than all three.

## The shape in one pass

```
backlog item  ──Start──▶  story ──▶ analyst ──[plan gate]──▶ gherkin-writer
     │                                                             │
     │                                                      [gherkin gate]
     │                                                             ▼
     └── other items are non-goals            implementer ──▶ cleaner ──▶ architect
```

That is the default `four-pack`. `two-pack` drops everything but implementer and
cleaner; `six-pack` adds qa-procedure-writer, code-reviewer, hardener, qa-runner and
senior-implementer.

## Rules that decide most questions

- **One item, one story.** Nothing in the pipeline decomposes a document into
  stories. Slicing is the operator's job, done by `squad-backlog` before anything
  starts.
- **Agents do not spawn agents.** Every result returns to the main session, which
  decides the next move.
- **Reviewers do not edit.** `code-reviewer` and `architect` emit recommendations;
  `hardener` and `senior-implementer` apply them.
- **Gates belong to humans.** A subagent never records an approval.
- **Verify honestly.** Any stage touching executable code runs the project's test
  command and reports the real result, including failures.
- **This story alone.** Neighbouring backlog items are non-goals and mocked ports,
  never assumed to exist.

## Entry points

| Task | Skill |
|---|---|
| Set the pipeline up in a repository | `/swarmforge:squad-init` |
| Turn intent or a design doc into backlog items | `/swarmforge:squad-backlog` |
| Start an item and drive it through the stages | `/swarmforge:squad-start` |
| See where every story sits | `/swarmforge:squad-status` |
| Approve or reject a pending gate | `/swarmforge:squad-approve` |
