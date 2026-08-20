---
name: squad-init
description: This skill should be used when the user asks to "set up the squad", "init swarmforge", "squad init", "initialise the pipeline in this repo", or wants the story pipeline configured for a project for the first time. It detects the repository's real language, test, lint and typecheck commands, writes .squad/config.json and a project-tailored .squad/constitution.md, and creates the backlog and stories directories.
argument-hint: "[profile: two-pack | four-pack | six-pack]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# Initialise the squad in this repository

Create `.squad/` and tailor it to the project actually present. A generic
constitution is worse than none: agents follow it literally, so wrong test commands
and wrong language conventions produce confidently wrong work.

## Procedure

### 1. Refuse to overwrite silently

If `.squad/config.json` already exists, read it, report the current profile and
stage counts, and ask whether to re-tailor or leave it. Never clobber an existing
`.squad/` that has stories in it.

### 2. Detect the project

Establish, from evidence in the repository rather than assumption:

- **Language and package manager** — `pyproject.toml` + `uv.lock`, `package.json`,
  `Cargo.toml`, `go.mod`, `deps.edn`, `Gemfile`.
- **Test command** — the one CI actually runs. Read `.github/workflows/*.yml`,
  `Makefile`, `justfile`, `bb.edn`, or the `[tool.*]` sections of `pyproject.toml`.
  Prefer what CI runs over what a README claims.
- **Lint and typecheck commands** — same sources.
- **House rules** — `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, and any
  nearest-scoped instructions in the subtree being worked on. In a monorepo, the
  per-project instructions outrank the root.

When the repository is a monorepo of independent projects, ask which subtree the
squad will work in and detect against that subtree, not the root.

### 3. Confirm what was found

Present the detected commands and ask for correction before writing. A wrong test
command is the single most damaging thing this skill can record.

### 4. Write config.json

```json
{
  "profile": "four-pack",
  "gates": { "plan": true, "gherkin": true, "qa_procedure": true },
  "isolation": "parallel-only",
  "verify": { "test": "...", "lint": "...", "typecheck": "..." },
  "models": {}
}
```

Use the profile given as an argument, else `four-pack`. See
`squad-pipeline/references/pipeline.md` for what each profile contains.

### 5. Write constitution.md

`.squad/constitution.md` is read by every agent before it writes anything. Keep it
short and specific to this project. Include only rules that change behaviour:

- The language, package manager, and how to run a single test.
- The exact verify commands, and that results are reported verbatim.
- Directory conventions the project already follows, stated as observed facts.
- House rules extracted from `CLAUDE.md` / `AGENTS.md` that constrain code —
  comment policy, naming policy, style guides, forbidden directories.
- What is off limits: paths agents must not touch.

Do not restate the pipeline in the constitution; agents get that from their own
prompts. Do not invent rules the project does not hold. Record numbers as
references to where they live, not as prose values.

### 6. Create directories and ignore state

```bash
mkdir -p .squad/backlog .squad/stories .squad/approvals .squad/blockers
```

Ask whether `.squad/` should be committed or ignored. Committed is the default —
the story record is the point — but a repository whose instructions bar documents
from commits may want it in `.gitignore` instead. Do not decide this silently.

### 7. Report

State the profile, the stages it implies, the gates that will pause, the verify
commands recorded, and the next step: `/swarmforge:squad-backlog`.
