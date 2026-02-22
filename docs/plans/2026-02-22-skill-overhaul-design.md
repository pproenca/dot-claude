# Dev-Workflow Plugin Overhaul: Token Efficiency & Prompt Engineering

## Problem

The dev-workflow plugin's skills are over-engineered with persuasion psychology, duplicate content, fabricated statistics, and verbose framing that wastes context window tokens without improving model compliance. The execute-plan command spawns 3 Opus agents per task when 1 suffices. The getting-started bootstrap is 402 lines when ~100 would do.

## Goals

1. Cut every skill by ~60% while preserving core instructions
2. Replace persuasion framework with actual prompt engineering techniques
3. Collapse 3-agent-per-task review into implementer self-review + final reviewer
4. Shrink getting-started to ~100 lines
5. Delete redundant reference files
6. Add few-shot examples where they replace verbose prose

## Rewriting Principles

| Current Pattern | Replacement |
|---|---|
| "YOU MUST", "No exceptions", "Iron Law" | Clear imperative: "Do X before Y" |
| Rationalization tables | Remove — don't teach the model excuses |
| Fabricated statistics | Remove |
| "Announce at start: ..." | Remove — tool calls are visible |
| Duplicate content (skill + reference) | Single source of truth in skill |
| Prose "why" paragraphs (20+ lines) | 2-3 sentence rationale, keep core insight |
| "Real-World Impact" tables | Remove |
| "Red Flags" lists (12+ items) | Compress to 3-5 items |
| "Violating the letter..." framing | Remove |

## File Changes

### Skills to Rewrite

#### getting-started (402 → ~100 lines)
- Keep: skill discovery, priority, rigid/flexible, planning overview
- Move: detailed planning methodology → write-plan command
- Remove: duplicate tables (Red Flags + Shortcuts), announcement, meta-commentary

#### test-driven-development (436 → ~170 lines)
- Keep: RED-GREEN-REFACTOR with few-shot examples, "why test-first" (condensed to 15 lines), bug fix walkthrough, verification checklist
- Remove: rationalization table (11 entries), fabricated statistics, dot graph, Iron Law framing, announcement, duplicate "why" subsections

#### systematic-debugging (185 → ~100 lines)
- Keep: four phases, 3+ fixes = architecture problem, quick reference table
- Remove: rationalization table, fabricated statistics, Iron Law framing, announcement

#### verification-before-completion (170 → ~70 lines)
- Keep: gate function, verification patterns table, agent report verification
- Remove: rationalization table, fabricated statistics, moral framing, announcement

#### Other skills (light trim)
- defense-in-depth, receiving-code-review, root-cause-tracing, testing-anti-patterns, pragmatic-architecture: remove persuasion framing, trim

### Files to Delete
- `skills/systematic-debugging/references/rationalizations.md` — duplicate of main skill content
- `skills/test-driven-development/references/rationales.md` — condensed into main skill
- `skills/systematic-debugging/references/phase-details.md` — fold essentials into main skill

### Files to Replace
- `references/persuasion-principles.md` → `references/prompt-engineering.md`
  - Few-shot examples, structured output, concise instructions, trigger-action pairs
  - Anti-patterns: rationalization tables, fabricated stats, "YOU MUST", announcements

### Commands to Restructure

#### execute-plan.md (507 → ~250 lines)
- Remove: two-stage review sections (~70 lines), "WRONG Pattern" example
- Add: self-review checklist in task agent prompt template
- Change: implementer does spec + quality self-review; only final code-reviewer as separate agent

## Agent Reduction

| Current (per task) | New (per task) |
|---|---|
| 1 implementer (Opus) | 1 implementer with self-review (Opus) |
| 1 spec reviewer (Opus) | — |
| 1 quality reviewer (Opus) | — |
| **3 agents/task** | **1 agent/task** |
| + 1 final code-reviewer | + 1 final code-reviewer |
| **5-task plan: 16 agents** | **5-task plan: 6 agents** |

## Prompt Engineering Guide (new reference)

Replace persuasion psychology with techniques that actually improve model behavior:
1. Few-shot examples (show exact pattern 2-3 times)
2. Structured output (constrain format structurally)
3. Concise instructions (50 clear lines > 400 verbose)
4. Trigger-action pairs ("When X, do Y")
5. Positive instructions over prohibitions
