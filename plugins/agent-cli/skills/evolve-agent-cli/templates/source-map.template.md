# Source Map

Read when:

- checking whether docs match implementation;
- changing a feature that is documented in more than one place;
- preparing a release note from source instead of memory.

This page maps user-facing behavior back to implementation files. Keep docs
descriptive; use these files as the source-backed check before changing behavior
claims.

## CLI Surface
- Command router and top-level help: `src/cli.ts`
- Flag parsing, exit codes, error class: `src/cli.ts`, `src/errors.ts`

## <Domain area 1, e.g. State, IDs, Locks>
- <behavior>: `src/state.ts`, `src/fs.ts`
- <behavior>: `src/types.ts`

## Providers / Adapters And Runner Bootstrap
- Adapter interface, registry, dispatch: `src/provider.ts`
- <Concrete provider X>: `src/providers/<x>.ts`

## <Pipeline> (map / review / fix / ...)
- <stage>: `src/<module>.ts`

## Build, CI, Docs, And Release
- CI gate: `.github/workflows/ci.yml`
- Release prep: `docs/release-prep.md`
