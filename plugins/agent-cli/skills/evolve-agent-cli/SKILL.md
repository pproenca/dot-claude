---
name: evolve-agent-cli
description: Use this skill when refactoring, adding a feature, adding a provider/adapter/backend, or hardening an EXISTING command-line tool that AI agents drive. Triggers on "refactor this CLI", "add a provider to", "add a feature to the CLI", "harden the mapper", "evolve this tool", "extend the agent CLI", "the CLI keeps breaking on". Diagnose with repo-health, write a "Read when:" effort doc, pin behavior with tests, then execute in the matching mode and update the contract docs. TS/Node-first.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# Evolve an agent CLI

Change an existing agent CLI the way the OpenClaw repos do — entered through
diagnosis, not a blank page. Same mental models as bootstrap; different entry point.

The work here is *mostly hardening*: across clawpatch/crabbox/clawsweeper, `fix` is
the #1 commit type (43–49%) and mappers run ~1 feat : 4 fix. Budget for it; a stream
of small `fix` commits is the system working, not thrashing.

## B0 — Diagnose (run the bundled tool)
```sh
python3 <plugin>/scripts/repo-health.py <repo>                 # swarm/single-author repo
python3 <plugin>/scripts/repo-health.py <repo> --bots-separate # autonomous-loop repo
```
Read the signals (full guide: [`references/diagnose-and-pin.md`](references/diagnose-and-pin.md)):
- **feat:fix per scope** → worst ratio = your fragile subsystem (test-sweep or redesign it).
- **Churn concentration** → the top file is *where the real spec lives*; over-invest in
  pinning it before touching it.
- **Deletion bursts** → flat-zero means debt is accruing; schedule a refactor burst.

Then audit against the contract — if invariants are missing (no `--json`, no exit-code
classes, model holds write creds, state mixed into the code repo), hand off to
**audit-agent-cli** first.

## B1 — Write a "Read when:" effort doc  🔶 DECISION GATE (mode)
Before coding, **ask the human which mode** (one `AskUserQuestion`), because each runs
differently:
- **Add a feature (breadth)** — new language/provider/route/target.
- **Add a provider/adapter** — a new implementation behind the existing interface.
- **Harden** — grind edge cases on an existing subsystem.
- **Refactor** — restructure without behavior change.

Then create the matching doc using the templates (convention from crabbox, which uses
a `Read when:` trigger header on 70+ docs — see
[`references/read-when-docs.md`](references/read-when-docs.md)):
- refactor → [`templates/refactor-doc.template.md`](templates/refactor-doc.template.md)
  (design context + migration phases with `Status:` lines + acceptance criteria + gate commands)
- feature → [`templates/plan-doc.template.md`](templates/plan-doc.template.md)
  (goal + ownership split + CLI surface + implementation file checklist + gates)

The effort doc links to the *authoring handrail* (the durable how-to-add-one guide,
e.g. `docs/provider-backends.md`). Keep the two separate: the effort doc is
design-context-and-migration; the handrail is the reusable template.

## B2 — Pin behavior FIRST
Add characterization tests to the churn-hot file so behavior is locked before you
change it. You cannot safely refactor what isn't pinned. (This is why the OpenClaw
repos move fast — the test file IS the contract; clawpatch's `mapper.test.ts` is
touched in 144/372 commits.) See [`references/diagnose-and-pin.md`](references/diagnose-and-pin.md).

## B3 — Execute in the matching mode
- **Feature / adapter:** implement through the interface, never as a special case in
  the core (`{ name, ...methods }` + one array entry). One focused test + one
  CHANGELOG credit line. For adapter specifics, see **audit-agent-cli**'s contract and
  the bootstrap `scaffold.md` interface pattern.
- **Harden:** one edge case per commit, each with a test. Expect many small `fix`es.
- **Refactor:** do it as a **burst** (extract helpers, derive schemas from a single
  source, decompose a monolith) with behavior tests unchanged. Don't dribble refactors
  across weeks — clawpatch did all 8 refactor commits in one day (66% of all deletions).
- **Change agent behavior:** that's data, not code → hand off to **agent-spec-kit**
  (edit `prompts/`/`instructions/`/`schema/`, snapshot the output contract).

## B4 — Update the contract docs  🔶 DECISION GATE (schema bump)
- `source-map.md` must still map behavior→files correctly (regenerate the touched
  sections — [`templates/source-map.template.md`](templates/source-map.template.md)).
- CHANGELOG entry with contributor credit.
- **If the persisted/output schema changed, ask the human before bumping
  `schemaVersion`** and confirm the read-migration (zod `.transform()` defaults) keeps
  old state loadable.

## B5 — Gate
CI green · the contract checklist still holds · `source-map.md` matches the tree ·
re-run `repo-health.py` and confirm feat:fix and churn didn't regress.

## Definition of done
- [ ] repo-health run; fragile scope identified
- [ ] effort doc written with `Read when:` header + gates
- [ ] behavior pinned with characterization tests before the change
- [ ] change made in the matching mode (interface for breadth; burst for refactor)
- [ ] source-map + CHANGELOG updated; schema bump confirmed if needed
- [ ] CI green; health signals stable
