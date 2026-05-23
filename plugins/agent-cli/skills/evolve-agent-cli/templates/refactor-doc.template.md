# <Area> Refactor

Read when:

- refactoring <dispatch / lifecycle / behavior X>;
- rebasing the <related> pull requests;
- adding a new <breadth thing>;
- changing <config / flags / routing / validation> for <area>.

For step-by-step implementation guidance, read [<Authoring Handrail>](../<area>-backends.md).
This document captures design context and migration notes; the authoring guide is the
handrail for new code.

## Context
<The current shape and why it needs to change. Name the real models/execution paths.>

## Design Principle
<The one rule that resolves most decisions, e.g. "Providers configure backends; core
commands own workflow orchestration.">

## Goals
- <goal 1>

## Non-Goals
- <non-goal 1>

## Interfaces
<The target interface(s), quoted.>

## Migration Plan
1. <Phase 1>. **Status: <pending | implemented for X | done>.**
2. <Phase 2>. **Status: pending.**
3. <Phase 3>. **Status: pending.**

## Tests
<What must be pinned before, and added during, the refactor.>

## Acceptance Criteria
1. <observable criterion 1>
2. <criterion 2>

## Gates
```sh
<exact gate commands, e.g. pnpm typecheck && pnpm lint && pnpm test && pnpm build>
```

## Open Questions
- <unresolved decision — delete as answered>
