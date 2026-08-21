---
name: squad-approve
description: This skill should be used when the user asks to "approve the plan", "approve the gate", "review the Gherkin", "reject the QA procedure", "sign off the story", or when a story is waiting at a plan, gherkin or qa_procedure gate and a decision is needed. It presents the artifact for review and records an approval or rejection under .squad/approvals/.
argument-hint: "[story id] [approve | reject]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# Decide a gate

A gate is the point where a human decides whether the pipeline has understood the
work. Only the main session, acting on an explicit human answer, records a
decision. A subagent never approves its own artifact, and neither does an agent
acting on the human's behalf without asking.

## Procedure

### 1. Find the gate

With a story id, read its `state.json` and take the `pending` gate. Without one,
list every story with a pending gate and ask which. If nothing is pending, say so
and report the board instead.

### 2. Present the artifact

Read the artifact the gate owns — `plan.md`, the `.feature` file, or
`qa-procedure.md` with `implementer-notes.md`. Present it for a decision:

- What it commits the story to, in a few lines.
- The specific things worth checking for that gate:
  - **plan** — is the story buildable alone? Are the ports and dummy state named?
    Is the acceptance observable? Are the other backlog items listed as non-goals?
  - **gherkin** — do the scenarios describe behaviour rather than implementation?
    Is every scenario checkable by the project's tests? Is anything in scope missing?
  - **qa_procedure** — can a human follow it without reading the code? Do the
    implementer notes name the seams, the runnable entry point, and the flags?
- Anything that looks wrong, stated plainly.

Then ask for the decision. Do not assume approval from silence or from a vague
affirmative about something else.

### 3. Record it

Write `.squad/approvals/<story-id>-<gate>.json` per
`../squad-pipeline/references/state.md`, and set the gate in `state.json` to
`approved` or `rejected`.

On rejection, also write `.squad/blockers/<story-id>-<nn>.md` with the reason, and
set `blocked`. A rejected gate does not advance: the owning stage runs again with
the reason as input, or the story goes back to the backlog to be re-sliced.

### 4. Continue

After an approval, offer to continue with `/swarmforge:squad-start`. After a
rejection, offer to re-run the stage that produced the artifact, with the rejection
note included in its packet.

## Gates that are off

When `config.json.gates` has a gate `false`, `squad-start` records an `auto`
decision and never pauses. Do not record an `auto` decision here — this skill only
runs when a human is deciding.
