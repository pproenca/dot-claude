# Agent-CLI contract checklist (authoritative review rubric)

Mark each **PASS / FAIL / N-A** with a `file:line` citation. Grouped by who each serves.

## A. External surface — for the agent that DRIVES the CLI
- [ ] **Dual output.** Human text on stdout + `--json` (and/or `--plain`) with a stable
      schema. Exactly one function writes results to stdout.
- [ ] **Stable `--json` schema.** Snapshot/contract test exists so the shape can't drift.
- [ ] **Enumerated exit codes**, one per failure class (e.g. 0 ok · 1 runtime · 2 usage ·
      3 dirty worktree · 4 auth · 5 quota · 6 validation · 7 lock/external-CLI ·
      8 malformed model output).
- [ ] **stdout = result, stderr = progress.** No spinners on non-TTY; `--quiet` mutes
      stderr only.
- [ ] **`--no-input` / non-interactive mode.** Prompts only on a TTY; mutating commands
      need explicit intent (`--yes`).
- [ ] **Stable deterministic IDs** (slug/hash) for diffable reruns + dedupe.
- [ ] **Per-command flag validation** rejects unknown flags (exit 2), not silently ignores.

## B. Internal robustness
- [ ] **Parse `unknown`, fail loud.** Schema validation (zod/JSON Schema) at every model
      and IO boundary; malformed model output → typed error (exit 8) at ONE boundary fn.
- [ ] **List output partitioned**, not all-or-nothing (one bad item dropped, not the batch).
- [ ] **Persisted state**: one file per record under typed dirs; **atomic writes**
      (`tmp + rename`); **schema-validated reads**; `schemaVersion` pinned with
      forward-compatible read defaults.
- [ ] **Malformed state wrapped** in a typed error (not a bare `JSON.parse`/`schema.parse`
      throw → untyped exit 1). *(common gap)*
- [ ] **Locking** via `open(path, "wx")` + a stale-lock cleanup command.
- [ ] **Deterministic core before model calls.** The LLM is a bounded sub-step.
- [ ] **Resumable**: resume skips completed work; crash/Ctrl-C safe.

## C. Author surface — for the swarm that EXTENDS the CLI
- [ ] **Adapter interface** (`{ name, ...methods }`) + a registration array + dispatch +
      dedupe. Adding breadth = one file + one array entry, no core change.
- [ ] **One provider/path proven before any matrix** (matrix-before-one-works is an anti-pattern).
- [ ] **AGENTS.md** present (structure, build/test gate command, style, commit/PR rules, security).
- [ ] **CHANGELOG.md** present, contributor-credited, with an `Unreleased` stub.
- [ ] **CI gate**: `typecheck + lint + format:check + test + build` (+ `pack:smoke`),
      `permissions: contents: read`, pinned toolchain, frozen install.
- [ ] **`source-map.md`** (behavior→files) and authoring handrail docs exist for breadth.
- [ ] **Security workflows** where public: CodeQL + dependency-review + dependabot (SHA-pinned).

## D. Safety (cross-cutting) — see safety-model.md for the deep version
- [ ] **Report-only by default**; mutation only on an explicit subcommand.
- [ ] **Refuse a dirty worktree for mutations**, excluding the tool's own state dir.
- [ ] **Record base SHA at plan time; re-verify before commit** (refuse if HEAD moved or
      unrelated files dirty; `--force` escape hatch).
- [ ] **No destructive git** (`reset --hard`, `clean`, `checkout --`, `restore`); allowlist
      any user-supplied ref before shelling out.
- [ ] **Secrets never as CLI flags, never printed**; doctor reports present/missing only.
- [ ] **Code/state separation** (gitignored state dir or a separate state repo).

## Severity when FAIL
- **Critical:** model holds write creds during analysis; no recheck before an autonomous
  mutation; destructive git; secrets printed.
- **High:** no `--json` / no exit-code classes (blocks agent driving); no boundary
  validation; churn-hot file untested; no dirty-worktree refusal on a mutating tool.
- **Medium:** no atomic writes/locks; no adapter interface (breadth bolted into core);
  no `schemaVersion`.
- **Low:** missing AGENTS.md/CHANGELOG/source-map; style/doc gaps; missing security workflows.
