---
name: capability-ledger
description: >-
  Track DEMONSTRATED problem-solving capability and compute the autonomy it has
  EARNED — so accumulated competence expands what may be attempted without a
  human gate and what may be delegated, the way a proven junior is handed bigger
  problems and a team. Use this when finishing a spike or feature whose result
  can be judged against a floor, when deciding whether Claude may proceed on a
  problem class without plan-gate confirmation, or when deciding whether a class
  may be delegated to a sub-agent. It maintains a repo-local ledger
  (capability-ledger.jsonl): per problem class, the demonstrated solves with
  their floor-ratios and domains, a computed maturity (novice, practiced,
  proven), and the proven playbook for delegation. Authority is the MEASURED
  outcome against the floor, never self-assessment: license is earned by
  demonstrated results, climbs slowly across solves and domains, and is demoted
  instantly on a near-miss. This is how the harness turns learning-from-failure
  into growing capability and delegation.
---

# Capability Ledger

The entity layer. The three knowledge skills cache what Claude *knows* (facts,
craft, insight). This tracks what Claude can *do* — demonstrated capability — and
turns it into **earned autonomy**: the license to attempt a bigger thing, skip a
gate, or delegate. It is the difference between a tool that gets faster and an
entity that grows.

## Why earned, never declared (the safety spine)
A system that expands its own authority is gameable if the evidence is
self-assessed. So capability here is computed ONLY from **measured outcomes
against a floor** — the same un-fakeable signal the spike floor gate uses to
prevent false victory now doubles as the promotion oracle. Claude cannot write
"I am good at this"; the ledger counts only spikes/features that actually landed
near their declared floor with a recorded benchmark. Competence is un-fakeable by
the agent itself.

## The unit: a capability (a demonstrated ability to solve a problem CLASS)
`capability-ledger.jsonl`, keyed by `problem_class` (e.g.
`render-perf-optimization`, `idempotent-write-boundary`, `state-machine-design`):
- `solves` — each: `{ floor_ratio, domain, date, benchmark_ref }`. The evidence.
- `maturity` — computed: novice / practiced / proven (never hand-set).
- `playbook` — the proven approach (reframings used, floor to beat, boundaries to
  respect) — what makes the capability DELEGABLE, not just a score.
- `last_demotion` — provenance of any instant drop (a near-miss).

## The autonomy ladder (mirrors the enforcement ladder, pointed at license)
- **novice** (0–2 near-floor solves): full gates. Human confirms spec AND result.
  The default for every new class.
- **practiced** (>=3 near-floor solves in ONE domain): the PLAN gate may auto-pass
  for this class — proceed without plan confirmation; verify gate + human result
  review still stand.
- **proven** (>=3 near-floor solves across >=2 domains): licensed to DELEGATE this
  class to a sub-agent under the recorded playbook, and to attempt larger blast
  radius — because the playbook is demonstrated, not guessed.

"Near-floor" = within the class's agreed ratio of the floor (default <=2x),
proven by a recorded benchmark. No benchmark -> not a solve -> no credit.

## The asymmetry (the guardrail)
License climbs SLOWLY (multiple demonstrated solves, multiple domains) and falls
INSTANTLY (a single near-miss in a class demotes it one rung, recorded in
`last_demotion`). The cost of over-licensing (attempting/delegating beyond real
competence) dwarfs the cost of under-licensing (an extra gate), so the ladder is
deliberately asymmetric. Demotion is real here — unlike the code maturity ladder,
this one must walk back.

## Workflow
- **Record a solve (truth-checked):** `cap_record.py --class <c> --floor-ratio <r>
  --domain <d> --benchmark <ref>` after a spike/feature lands. Refuses a solve
  with no benchmark ref. Recomputes maturity from the full solve history.
- **Check license (before acting):** `cap_check.py --class <c>` returns the
  current maturity and what it licenses (gate auto-pass? delegate?). The feature/
  spike loops consult this to decide whether the plan gate may auto-pass.
- **Demote (on a near-miss):** `cap_record.py --class <c> --miss --floor-ratio <r>`
  records a failure and drops the rung immediately.

## Composition
- The spike floor gate is the promotion ORACLE — its measured ratio is the solve
  evidence. No floor, no capability credit.
- `mental-models` supplies the playbook's reframings; a proven capability's
  playbook references the models that made its solves work.
- `knowledge-ratchet` governs nothing here — capability promotion is outcome-driven
  and automatic, not friction-driven; this is a distinct, stricter ladder.
- The feature/spike loops READ `cap_check.py` to decide gate auto-pass; they never
  WRITE their own license. Read-only consumption keeps the loop from self-licensing.

## The one law here
License reflects DEMONSTRATED outcome, never intention or self-report. A
capability with no benchmarked near-floor solves is novice no matter how confident
the agent feels. Earned, measured, and instantly revocable.

## Files
- `references/licensing.md` — the maturity computation, near-floor rule, demotion.
- `scripts/store.py` — ledger storage port (JSONL).
- `scripts/cap_record.py` — record a truth-checked solve or a demoting miss.
- `scripts/cap_check.py` — read current maturity + what it licenses.
