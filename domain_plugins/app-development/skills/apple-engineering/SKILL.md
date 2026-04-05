---
name: apple-engineering
description: "End-to-end iOS/iPadOS engineering workflows grounded in Apple documentation: data modeling and persistence strategy (SwiftData/Core Data), performance optimization (Apple's 8 metrics, Instruments, MetricKit), debugging (crash/hang/memory/threading/data corruption), and refactoring existing model decisions. Reads design/ artifacts from app-design when available for richer, design-informed engineering. Use when users ask to design or revise iOS data architecture, choose persistence, profile and optimize performance, create monitoring/performance tests, diagnose app issues, or resume a structured engineering workflow that writes artifacts under engineering/."
---

# Apple Engineering

This skill preserves the original plugin's strict, documentation-first behavior in a Codex-compatible workflow.

## Workflow Router

Choose exactly one workflow based on user intent, then follow that workflow file end-to-end.

- **Full progress check / continue from current state**: Read `references/workflows/engineer.md`.
- **Design data model and persistence**: Read `references/workflows/model.md`.
- **Profile and optimize performance**: Read `references/workflows/optimize.md`.
- **Diagnose and fix issues**: Read `references/workflows/debug.md`.
- **Refactor existing model decisions**: Read `references/workflows/refactor.md`.

If intent is ambiguous, ask one short routing question before proceeding.

## Context and Artifacts

- Use `.codex/app-development.local.md` as persistent project context.
- If `.codex/app-development.local.md` is missing and `.claude/app-development.local.md` exists, read and migrate it.
- Write workflow artifacts into `engineering/` exactly as specified by the selected workflow.

## Design Integration

Engineering workflows read `design/` artifacts produced by the app-design plugin when they exist:

- `design/goals.md` — audience, platforms, pain points
- `design/features.md` — prioritized features and user intents
- `design/screens/*.md` — per-screen specs (fields, states, density, navigation)

Design artifacts are **optional**. Engineering works standalone, but produces richer output when design context is available. When design artifacts exist, workflows ask fewer discovery questions and cross-reference entities back to screens and features.

Engineering artifacts reference design artifacts by filename for traceability — they never copy or duplicate design content.

## Reference Loading Protocol

Always use progressive disclosure:

1. Read the matching index in `indexes/`.
2. Read the full source document(s) from `references/` before recommending APIs, patterns, or optimizations.
3. Quote Apple documentation when justifying decisions.
4. Cite the source file names in your recommendations.
5. Evaluate alternatives before final recommendations.

## Index Map

- Data strategy and persistence selection: `indexes/data-by-need.md` -> `references/data/`
- Performance metrics and tooling: `indexes/performance-by-metric.md` -> `references/performance/`
- Test design and framework choice: `indexes/testing-by-goal.md` -> `references/testing/`
- Swift language and package patterns: `indexes/swift-by-topic.md` -> `references/swift/`

## Workflow Fidelity Rules

- Follow each selected workflow's hard rules without skipping steps.
- Keep all generated documents in the exact templates and paths required by the workflow.
- Ask discovery questions one at a time when the workflow requires user input.
- Preserve current-truth file semantics where specified (especially in refactor workflows).

## Reference Structure

```text
indexes/
  data-by-need.md
  performance-by-metric.md
  testing-by-goal.md
  swift-by-topic.md

references/
  workflows/
    engineer.md
    model.md
    optimize.md
    debug.md
    refactor.md
  data/
  performance/
  testing/
  swift/
```
