---
name: harness-setup
description: >-
  Run this FIRST when installing or onboarding the boundary-discipline,
  feature-workflow, and verify-and-diagnose skills into a repository. It
  establishes and validates boundary.config.json — the shared config every one
  of those skills' scripts (scan, shelf_index, promote, verify) reads to learn
  this repo's conventions: which directories map to which substrate layer, the
  file extensions, the feature roots, and the verify-gate check commands. Use
  this whenever setting up the skills in a new repo, when boundary.config.json is
  missing or stale, when the harness scripts return empty or clearly wrong
  results (a symptom of misconfiguration), or when the repo's structure has
  changed. The config is the trust boundary of the whole harness — this skill is
  how you parse it once, correctly, so every later stage can assume it. Detect,
  propose, confirm with the human, validate, record.
---

# Harness Setup

The boot stage of the harness. Every other skill's script reads
`boundary.config.json` and *assumes* it is correct; a wrong config fails
silently (shelf_index returns empty, the shelf-check ungrounds, duplication
returns). This skill is "parse, don't validate" applied to the config itself:
establish a *proven* config once, so every downstream stage can trust it.

It configures all skills, so it sits above the federation as its installer. Run
it before the first feature goes through feature-workflow.

### The `.harness/` mirror layout (namespaced — required)
When a repo's verify checks reference harness scripts, they are mirrored into a
local `.harness/` so the project is self-contained. **Mirror per skill, never
flat:** `.harness/<skill-name>/<script>.py`. This is mandatory because more than
one skill ships a `scripts/store.py` (library-knowledge, specialist-knowledge,
mental-models all have their own storage port), and a flat `.harness/` would let
one skill's `store.py` clobber another's — silently breaking the other skill's
tools. Config and verify commands reference the namespaced path
(`.harness/library-knowledge/lib_lookup.py`, etc.). One obvious home per skill's
scripts; no same-named module can collide.

## The setup workflow

### 1. Detect (a PREDICTION, never an assumption)
Run `python scripts/config_init.py --repo <path> --skills-root <where skills are
installed>`. It identifies the **substrate** from an unambiguous marker file
(`go.mod` → Go, `Cargo.toml` → Rust, `pyproject.toml` → Python, `package.json` →
Node/TS, …), then proposes that substrate's conventional layer directories, verify
commands, and exclude globs. It writes a **draft** `boundary.config.json` with a
`_substrate` field and a confidence report.

The discipline that matters here: **detection is a prediction shaped by the tool's
defaults, not a fact about the repo.** The boundary model (trust, effect,
consistency, containment) is universal, but conventions are not, and the failure to
avoid is assuming one ecosystem's layout is the universe — guessing TypeScript on a
Go repo and writing a confident config for a project that does not exist. So the
tool does two honest things: it reports a *confidence*, and when it cannot recognize
the substrate it **refuses to default** — it writes an explicit `UNKNOWN` skeleton
with `FILL` markers rather than a disguised guess. If you see `SUBSTRATE UNKNOWN` or
a low confidence, treat the whole draft as a hypothesis to falsify (this is the
`inquiry` faculty: predict the layout, then make the cheapest observation — what
marker files and directories actually exist? — that would prove the prediction
wrong, *before* ratifying).

### 2. Propose & confirm (judgment — the important step)
The draft's layer→directory mapping encodes the repo's *architecture*, which a
detector can only predict. Read the confidence report's REVIEW items and the
draft, and reason over the actual repo: does each layer glob point at the
directories that really hold that layer (atomic tokens/value-objects,
primitives, seams/ports, patterns, pipelines, scaffolds)? Where the repo's
conventions differ from the probes, fix the globs. Confirm the mapping with the
human — they own the architecture; setup ratifies it, it does not invent it.

Use the substrate model in the **feature-workflow** skill (`references/shelf.md`)
as the definition of each layer while mapping.

### 3. Validate (mechanical — the gate)
Run `python scripts/config_check.py --repo <path>`. This is the doctor: it
proves the config resolves against the real repo — every layer glob matches real
paths, feature_roots exist, verify commands are well-formed, and any script path
referenced in a check actually exists. It **fails closed**: ERRORs (placeholder
paths, missing scripts, invalid globs) must be fixed; WARNs (an empty layer) are
reviewed. Do not consider setup done until the doctor exits 0.

### 4. Record
The validated `boundary.config.json` lives at the repo root. Then write the
repo's agent charter: `python scripts/agents_init.py --repo <path>` generates
`AGENTS.md` (the loop, the shelf-check rungs, the layer map, the verify gate —
all from `boundary.config.json`, so it describes THIS repo) and links `CLAUDE.md`
to it, so Claude Code and AGENTS.md-convention tools read one source of truth.
The harness-owned content sits in a managed block that re-runs regenerate; the
"Repo conventions & learnings" section below it is never touched — it is the
durable home for the outer-loop ratchet's output.

Optionally wire the gates as hooks for L3 enforcement (the maturity ladder
applied to the workflow): `config_check` and `feature-workflow`'s `plan_check` as
pre-commit, `verify` as pre-push. Re-run the doctor (step 3) periodically, or in
CI, to catch config **drift** as the repo's structure evolves — stale config is
the same dialect-drift failure the workflow warns about, one level up.

## When to engage

- Installing the skills in a new repo → **run this first.**
- A harness script returns empty/wrong results → re-run the doctor; the config
  has likely drifted from the repo.
- Repo restructured (layers moved/added) → re-detect and re-validate.

## Files

- `scripts/config_init.py` — detect stack + layout, scaffold a draft config,
  report confidence. (Scaffolds, like plan_new.)
- `scripts/config_check.py` — the doctor: validate the config resolves against
  the repo. Fails closed, gate-able. (Validates, like plan_check.) Exit 0 = pass.
- `scripts/agents_init.py` — write `AGENTS.md` from the config and link `CLAUDE.md`
  to it (the RECORD step's charter). Idempotent; preserves edits outside the managed block.

## What this configures

One `boundary.config.json` at the repo root, read by:
`layers` → feature-workflow/shelf_index.py · `feature_roots` →
feature-workflow/promote.py · `verify` → feature-workflow/verify.py ·
`include_ext`/`exclude_globs` → boundary-discipline/scan.py and shelf_index.py.
