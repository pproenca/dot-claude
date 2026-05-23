# Behavior as versioned data

clawsweeper's whole job lives in four data layers over a deterministic engine. This is
the highest-leverage move for an agent CLI: the agent's behavior becomes reviewable,
diffable, and testable instead of buried in string literals.

## `prompts/` — the task spec
A prompt is a versioned markdown file with these parts (from `prompts/review-item.md`):
1. **Role** — one line: "You are reviewing one open item … for conservative cleanup."
2. **Composable context** — "read the target repo's `AGENTS.md` if present and follow it
   when it doesn't conflict with this prompt"; "if `.agents/maintainer-notes/` exists,
   treat matching notes as maintainer decisions." The prompt composes with per-repo and
   per-area instructions it doesn't own.
3. **Scope guardrail + read-only command allowlist** — "This is a read-only review. Do
   not edit files, commit, comment, or mutate. Use only `rg`, `sed`, `nl`, `git log`,
   `git show`, `git diff` …" (explicitly forbids `apply_patch`, `tee`, `cat >`, installs).
4. **Confidence/evidence bar** — "High confidence means you read enough current code,
   docs, tests, history. Do not decide from the title or one `rg` hit. If you cannot
   point to concrete evidence, keep it open."
5. **Field-by-field output contract** — a prose section per schema field + a one-line
   pointer: "Final answer must match `schema/<name>.schema.json`."
6. **Mode layers** — a shared `worker-system.md` + swappable `plan-only.md` / `execute.md`
   / `autonomous.md` that only tighten what may be mutated. Each repeats the core guard:
   "return structured JSON only; do not mutate directly."

## `instructions/` — policy as data
Each policy doc (e.g. `closure-policy.md`, `merge-policy.md`, `dedupe.md`,
`security-boundary.md`) follows the same shape:
1. **Gate** — when this policy applies ("Use this only when the job asks for X. It is not
   the default.").
2. **Positive criteria** — the "only when" list.
3. **Ranked evidence order** — live artifact → bodies/comments → diffs → CI → notes.
4. **Hard "Never" list.**
5. **Literal templates** — the exact comment markdown to post, so output *style* is data
   not code.
6. **Escalation verbs** — `needs_human`, `route_security`, each with an anti-overuse
   clause ("Do not use `needs_human` as a synonym for 'not closable.'").
The model is *told to read these at runtime* (the system prompt: "read
instructions/closure-policy.md; read instructions/merge-policy.md …").

## `schema/` — the output contract
A **closed** JSON Schema (Draft 2020-12, `additionalProperties: false`) that is:
- **handed to the model** as a hard constraint (`codex exec --output-schema schema.json`),
- **AND re-validated on parse** (`parseDecision(JSON.parse(out))`; invalid → throw
  `malformed-output`),
- **provenance-enforcing**: every `evidence[]` item requires `["label","detail","file","line","command","sha"]`,
- **safety-locked** with `const`: a security-sensitive item structurally cannot become a
  job (`security_sensitive: { const: false }`); a merge requires
  `merge_preflight.security_status: { const: "cleared" }` and `findings_addressed: { const: true }`.
Belt-and-suspenders: the schema both *constrains generation* and *gates ingestion*.

## `config/` — per-target profiles + limits
Per-repo/target profiles (apply rules, prompt notes), a deny-list (e.g. never operate on
your own state repo), and hard caps (`workers.max`, `reserve_for_interactive`). Operating
limits are data, enforced by a `check:limits` CI step.

## Why this matters
Changing the agent's behavior becomes a reviewable PR diff in `prompts/`/`instructions/`/
`schema/` — not a code change. You can snapshot-test the schema, lint the policies, and
let non-engineers review the agent's actual decision rules. It also lets one engine serve
many targets by swapping `config/` profiles.
