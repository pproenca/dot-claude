---
name: audit-agent-cli
description: Use this skill to review an existing command-line tool against the agent-CLI contract and safety model — before extending it, before trusting it in an autonomous loop, or as a quality gate. Triggers on "audit this CLI", "review this tool for agents", "is this CLI safe for agents", "check the agent CLI against best practices", "contract review", "safety review of the CLI". Produces a findings report graded against the invariants and the guarded-mutation model. Read-only.
allowed-tools: Read, Bash, Glob, Grep, AskUserQuestion
---

# Audit an agent CLI

Review an existing CLI against the contract that makes a tool safe to be **driven and
extended by agents**. Read-only — produce a findings report, do not change code.

## Step 1 — Establish intent  🔶 DECISION GATE
Ask the human ONE thing (one `AskUserQuestion`): **what safety posture should this tool
have?**
- *Report-only* (never mutates) — audit that it truly never writes.
- *Guarded mutation* (mutates only on explicit command, with recheck) — audit the full
  safety model.
- *Autonomous loop* (an agent runs it unattended) — audit the strictest bar
  (token split, recheck-before-mutate, proposal/apply separation).

The posture sets the bar for the Safety section. Everything else is read from the repo.

## Step 2 — Metrics pass
```sh
python3 <plugin>/scripts/repo-health.py <repo>   # or --bots-separate for loops
```
Capture: feat:fix per scope (fragile subsystems), churn concentration (the de-facto
spec), deletion cadence. These become the "fragility" section of the report.

## Step 3 — Contract pass
Walk [`references/contract-checklist.md`](references/contract-checklist.md) group by
group (External surface · Internal robustness · Author surface · Safety). For each
invariant, grep/read for evidence and mark **PASS / FAIL / N-A** with a file:line
citation. Don't guess — cite the code or mark it FAIL.

Quick greps that find most gaps:
- `--json` handling + a single stdout writer; stderr for progress
- a typed error class carrying `exitCode` + `code`; a top-level catch converting it
- `safeParse` / schema validation at model/IO boundaries (not bare `JSON.parse` of model output)
- atomic writes (`rename`) + `open(..., "wx")` locks
- a `{ name, ...methods }` adapter interface + a registration array (breadth pluggable)
- `.gitignore` of the state dir / a separate state repo

## Step 4 — Safety pass
For guarded/autonomous posture, audit against
[`references/safety-model.md`](references/safety-model.md): the credential boundary
(does the model ever hold write creds during analysis?), proposal-vs-apply separation,
recheck-live-state-before-mutate (drift check), single deterministic apply path, and
marker-backed idempotent side effects. These are the patterns that prevent an
autonomous agent from doing damage.

## Step 5 — Report
Emit a findings report:
- **Summary:** posture audited, overall PASS/FAIL count.
- **Contract findings:** table of invariant · status · evidence (file:line) · severity.
- **Safety findings:** the credential/recheck/apply-path findings (highest severity).
- **Fragility:** the repo-health signals + the 1–2 scopes that need a test sweep.
- **Recommended next steps:** ordered, each pointing at **evolve-agent-cli** or
  **agent-spec-kit** for the fix.

Severity guide: a missing credential boundary or recheck on a mutating autonomous tool
is **critical**; missing `--json`/exit-code classes is **high** (blocks agent driving);
missing tests on a churn-hot file is **high**; style/doc gaps are **low**.

## Definition of done
- [ ] posture confirmed with the human
- [ ] repo-health metrics captured
- [ ] every contract invariant marked PASS/FAIL/N-A with a citation
- [ ] safety model audited for the stated posture
- [ ] findings report with ordered, skill-routed next steps
