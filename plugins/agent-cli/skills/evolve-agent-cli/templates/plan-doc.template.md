# <Feature> Plan

Read when:

- implementing `<flag / subcommand>`;
- changing <subsystem the feature touches>;
- reviewing the <security / safety> boundary for <feature>.

## Goal
<What the feature does and the user value, in 2–3 sentences.>

## Ownership Split
<What this tool owns vs what callers/other tools own. Keep the boundary explicit.>

## Capability / Flags
- `--<flag>`: <meaning, default>

## CLI Surface
```
tool <command> [--<flag>] ...
```
<New/changed output shape, including the `--json` field additions.>

## Safety / Security Boundary
<What new trust boundary this introduces; how it stays report-only / guarded.>

## Implementation Files   ← literal checklist
- [ ] `src/<file>.ts` — <what changes>
- [ ] `src/<file>.test.ts` — <new focused test>
- [ ] `docs/source-map.md` — map the new behavior
- [ ] `CHANGELOG.md` — entry (+ credit)

## Tests
<New focused tests, the fixtures they need.>

## Gates
```sh
pnpm typecheck && pnpm lint && pnpm format:check && pnpm test && pnpm build
```

## Acceptance Criteria
1. <observable criterion 1>
2. <criterion 2>

## Deferred
- <explicitly out of scope for this feature>
