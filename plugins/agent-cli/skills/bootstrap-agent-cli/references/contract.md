# The agent-CLI contract (build checklist)

The invariants a new agent CLI must satisfy. Grouped by *who* each serves. (For the
full review rubric, see the **audit-agent-cli** skill.)

## A. External surface — for the agent that DRIVES the CLI
- **Dual output:** human text on stdout + `--json` (and optionally `--plain`) with a
  **stable schema**. Only one function writes results to stdout.
- **Enumerated exit codes**, one per failure *class*. clawpatch's reconstructed map:
  `0` success · `1` runtime · `2` invalid usage/preconditions · `3` dirty worktree ·
  `4` provider auth/config · `5` provider quota/rate-limit · `6` validation failed ·
  `7` lock conflict / external-CLI failure · `8` malformed model output.
- **stdout = result, stderr = progress/diagnostics.** No spinners on non-TTY.
  `--quiet` mutes stderr only.
- **`--no-input` / non-interactive mode.** Prompts only on a TTY.
- **Stable, deterministic IDs** (slug/hash) so reruns diff cleanly and findings dedupe.

## B. Internal robustness
- **Parse `unknown`, fail loud.** zod (or JSON Schema) at every boundary; malformed
  model output → typed `malformed-output` error (exit 8) at exactly ONE boundary
  function. For list-shaped model output, **partition** valid/dropped rather than
  all-or-nothing.
- **Persisted, append-only-ish, resumable state.** One JSON file per record under
  typed dirs. **Atomic writes** (`tmp + rename`). **Schema-validate every read.** Pin
  `schemaVersion`; use zod `.transform()` defaults for forward-compatible reads. No
  database in v0.
- **Locking** via `open(path, "wx")` lock files; stale-lock cleanup command. Enables
  `--jobs N` parallelism.
- **Deterministic core before model calls.** The LLM step is a bounded sub-step inside
  a deterministic pipeline (e.g. clawpatch maps deterministically; enrichment is opt-in).
- **Code/state separation:** state dir gitignored (or a separate state repo).

## C. Author surface — for the swarm that EXTENDS the CLI
- **Adapter interface** for the thing you'll have many of (providers / backends /
  targets). One implemented first; matrix later (a hard non-goal until one path works).
  Make it a plain object type `{ name, ...methods }`, registered in one array, dispatched
  + deduped by the core. Adding breadth = one file + one array entry, no core changes.
- **AGENTS.md** contract; **CHANGELOG.md** ledger (credit every contributor).
- **CI gate** encoding taste: `typecheck + lint + format:check + test + build + pack:smoke`.

## D. Safety (cross-cutting)
Report-only by default · mutate only on an explicit subcommand · refuse a dirty
worktree for mutations (excluding your own state dir) · record base SHA at plan time
and **re-verify before committing** · never destructive git · allowlist any
user-supplied git ref before shelling out.

## Toolchain defaults (TS/Node)
ESM (`type: module`), single runtime dep where possible (`zod`), `bin → dist/cli.js`,
`engines.node >= 22`, pinned `packageManager`. **Every** TS strictness flag on (not
just `strict`): `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`,
`noImplicitOverride`, `noFallthroughCasesInSwitch`, `noPropertyAccessFromIndexSignature`.
oxc toolchain: `oxlint` (correctness+suspicious as errors) + `oxfmt` (2-space). Vitest.
