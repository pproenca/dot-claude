# Mode: AUDIT

**Goal:** locate undefended or misplaced boundaries in *existing* code and
produce a **report**. Audit reads and classifies; it does not rewrite. Fixing
what you find is a separate mode — hand off to `refactor.md` (misplaced
boundary) or to a small `implement.md` pass (genuinely missing defense).

Read `references/model.md` first if you haven't. **A gap = a fingerprint present
without its corresponding defense.** The audit is finite and mechanical because
the fingerprints are physical. Trace data, not control flow.

**Mechanize the grep, judge by hand.** Run `python scripts/scan.py <path>` first
— it applies all the fingerprint patterns below identically and returns
candidates grouped by boundary with hotspot files. That removes the error-prone
manual grepping; your job is then the judgment the script can't do: deciding
which candidates are real gaps and classifying each (undefended / duplicated /
leaked / unsized). The grep commands below document what `scan.py` runs and let
you spot-check or extend it.

## Scope discipline

Audit the scope the user named (a file, a module, a flow, the repo) — no more.
Do not start editing code mid-audit; collect findings first, then propose. If
the user asked you to *build* something, you are in the wrong mode — go to
`implement.md`.

## A1 — Enumerate ingresses

List every place data enters each process: HTTP handlers, queue consumers,
webhook receivers, cron/file readers, env access, DB reads. This is the trust
boundary inventory.

## A2 — Trust gaps (grep the smells)

```bash
rg -n '\bas\s+\w' --type ts            # casts: a boundary DECLARED closed without parsing
rg -n ':\s*any\b|<any>|\bany\[\]' --type ts
rg -n '!\.' --type ts                  # non-null assertions
rg -n 'JSON\.parse' --type ts          # must be immediately followed by a schema parse
rg -n 'req\.(body|query|params)' --type ts
rg -n 'process\.env\.' --type ts       # should be parsed once at boot, not read inline
```
For each hit: **did I construct this value's type, or assert it?** An ingress
with no parse producing a domain type (only a cast + raw field access) is a
trust gap. `?.`/`!` deep in domain logic = untrusted-ness leaked inward because
the parse never happened at the edge.

## A3 — Effect gaps (decide+act tangles)

```bash
rg -n '\bawait\b|\.then\(|fetch\(|fs\.|Date\.now\(|Math\.random\(' --type ts
```
For each effect: **is there a pure decision upstream, or is the rule tangled
into the call?** Heuristic — *anything you must mock to unit-test a business
rule* marks an effect boundary sitting too deep.

## A4 — Consistency gaps (name invariants FIRST)

You cannot audit what you have not named. Write the invariant list explicitly
before grepping (e.g. for a clinic app: no double-booking of
`(practitioner, slot)`; refund ≤ captured amount and only from `Captured`; slot
capacity not exceeded; balance never negative). Then for each: **what enforces
this under two simultaneous requests?**
- DB unique constraint / lock / append → OK
- an `if` in application code → **gap** (race: check and write aren't atomic)
- nothing → worse gap

```bash
rg -n 'findUnique|findFirst|count\(' --type ts   # read... followed later by a create/update?
```

## A5 — Containment gaps

```bash
rg -n 'fetch\(|axios|http\.|new Pool|createClient' --type ts   # any without a timeout?
```
For each external call: **if this dependency goes dark, what else stalls?** No
timeout / shared pool with no bulkhead = containment gap.

## Output format

ALWAYS report as a list of findings, each:

```
- [boundary kind] [gap type] — file:line
  what: <the fingerprint observed>
  risk: <what breaks, and when — runtime? under concurrency? on provider outage?>
  fix → <refactor | add-defense>, target home: <where it belongs>
```

Gap types: **undefended** (fingerprint, no defense) · **duplicated** (defense
repeated → boundary too late) · **leaked** (foreign status inside a unit →
wrong layer) · **unsized** (consistency boundary spans ≠ one invariant). Use the
diagnostics table in `model.md` to classify duplicated/leaked/unsized.

Close with a one-line **maturity estimate** (L0–L4 from `model.md`) and the
single highest-leverage fix. Then stop — do not begin fixing unless asked.
