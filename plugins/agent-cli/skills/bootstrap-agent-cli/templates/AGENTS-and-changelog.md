# AGENTS.md + CHANGELOG.md templates

## `AGENTS.md` — the "Repository Guidelines" skeleton (clawpatch/crabbox use this verbatim)
```markdown
# Repository Guidelines

## Project Structure & Module Organization
<source in src/, CLI entry src/cli.ts, tests beside impl as *.test.ts, build to dist/
(do not edit), docs in docs/. Flag generated dirs as "should not be edited.">

## Build, Test, and Development Commands
- `pnpm build` / `pnpm typecheck` / `pnpm lint` / `pnpm format` / `pnpm format:check`
- `pnpm test` (and `pnpm test <file>` for one focused file)
- For local CLI checks: build, then `node dist/cli.js <command>`.

## Coding Style & Naming Conventions
ESM TypeScript, small pure helpers, explicit return types on shared functions,
2-space indent (oxfmt). Name files by domain (`provider.ts`, `state.ts`,
`mappers/python.ts`); tests `<module>.test.ts`. Keep generated output and local
state out of commits.

## Testing Guidelines
Vitest. Add/Update a focused test for any behavior change. Prefer targeted runs while
developing, then run `pnpm typecheck && pnpm lint && pnpm test && pnpm build` before
handing off.

## Commit & Pull Request Guidelines
Conventional Commit subjects (`feat(mapper): ...`, `fix(provider): ...`). Scoped,
descriptive commits. PRs explain the behavior change, link issues with full GitHub
URLs, mention docs/changelog updates, and list the exact checks run.

## Security & Configuration Tips
Do not commit `.{tool}/` state, credentials, provider transcripts, or generated dist
edits. Provider output is schema-validated; keep new provider/mapper code conservative
about reading secret-bearing files.
```
For an autonomous bot, swap to clawsweeper's headings instead: `## Structure` ·
`## Operating Model` (proposal-only vs guarded apply) · `## Safety Rules` ·
`## Commands` · `## GitHub Checks`.

## `CHANGELOG.md`
```markdown
# Changelog

## <next> - Unreleased

## 0.1.0 - YYYY-MM-DD

- Added the initial strict TypeScript `<tool>` CLI scaffold with <commands>.
- Added <feature-centered state, provider integration, strict schemas, tests, docs>.
```
Conventions: reverse-chronological; top `## <next> - Unreleased` stub; released
versions `## X.Y.Z - YYYY-MM-DD`; entries start with a past-tense verb (Added / Fixed
/ Improved / Changed / Hardened); **credit every external contributor** with
`thanks @handle`. The changelog is the contributor ledger and the most-edited doc in
the repo — keep it current.

## `SECURITY.md` (recommended; clawpatch ships one)
Private disclosure first (GitHub Security Advisory or a security@ address); state the
security-relevant surfaces (provider command execution, prompt construction, state,
CI, dependency automation, any path that may expose secrets); scanner-only/dep-only
reports without reachable impact are hardening requests, not vulnerabilities.
