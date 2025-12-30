# agentic-workflow

Multi-agent orchestration workflow for Claude Code with anti-abandonment patterns.

## Overview

This plugin implements a comprehensive multi-agent orchestration system that:

- **Scales appropriately** - From trivial tasks (direct guidance) to huge projects (10+ subagents)
- **Follows structured phases** - Explore → Plan → Delegate → Verify → Synthesize
- **Prevents task abandonment** - External state, re-injection, stop hooks
- **Enforces quality** - TDD cycle, verification agents, strict completion criteria

## Installation

```bash
# From the plugin directory
claude --plugin-dir /path/to/agentic-workflow

# Or copy to local project
cp -r agentic-workflow/.claude-plugin .claude-plugin
```

## Commands

| Command | Description |
|---------|-------------|
| `/orchestrate <task>` | Start orchestrated workflow for complex tasks |
| `/verify [--fix]` | Run verification layer (code review + anti-overfit + integration) |
| `/progress [show\|update\|reset]` | Manage todo.md and progress.txt state |
| `/artifact [list\|read\|clean]` | Manage .claude/artifacts/ handoff files |

## Workflow

```
User Request
    ↓
Complexity Assessment
    ↓
┌─────────────────────────────────────────┐
│         LEAD ORCHESTRATOR (IC7)         │
├─────────────────────────────────────────┤
│ 1. EXPLORE - Read, grep, understand     │
│ 2. PLAN - Decompose, get approval       │
│ 3. DELEGATE - Create task packets       │
│ 4. VERIFY - Spawn verification agents   │
│ 5. SYNTHESIZE - Collect, finalize       │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│      TASK EXECUTORS (IC6) - Parallel    │
├─────────────────────────────────────────┤
│ Each follows TDD: RED → GREEN → BLUE    │
│ Writes artifact to .claude/artifacts/   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│     VERIFICATION AGENTS (IC5)           │
├─────────────────────────────────────────┤
│ • Code Reviewer (security, performance) │
│ • Anti-Overfit (generalization check)   │
│ • Integration Tester (tests, lint)      │
└─────────────────────────────────────────┘
    ↓
Complete (or remediation loop)
```

## Anti-Abandonment Patterns

This plugin implements five interlocking patterns to prevent task abandonment:

1. **Explicit Success Criteria** - Every task has measurable completion conditions
2. **Persistent External State** - todo.md and progress.txt survive context compaction
3. **Re-Injection Pattern** - Every 5-10 turns, re-read task checklist
4. **Verification Subagents** - Fresh context catches what you missed
5. **Stop Hook Enforcement** - Block completion until all checks pass

## Skills

| Skill | Triggers When |
|-------|---------------|
| `orchestration-workflow` | Complex tasks, "orchestrate", "multi-step" |
| `tdd-cycle` | "TDD", "test first", "red green blue" |
| `context-management` | "context", "preserve", "compaction" |
| `task-packet-structure` | "task packet", "delegate", "subagent" |
| `anti-abandonment` | "don't abandon", "complete fully" |

## Agents

| Agent | Level | Purpose |
|-------|-------|---------|
| `lead-orchestrator` | IC7 | Coordinate complex implementations |
| `task-executor` | IC6 | Execute single task packet with TDD |
| `code-reviewer` | IC5 | Security, performance, patterns review |
| `anti-overfit-checker` | IC5 | Detect overfitting to tests |
| `integration-tester` | IC5 | Full test suite, typecheck, lint |
| `synthesizer` | IC5 | Collect artifacts, prepare final status |

## Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| SessionStart | Session begins | Check for incomplete work |
| PostToolUse | After Write/Edit | Auto-run typecheck/lint |
| PreCompact | Before compaction | Preserve critical context |
| SubagentStop | Subagent completes | Verify task packet criteria |
| Stop | Before termination | Block if incomplete |

## Configuration

Create `.claude/agentic-workflow.local.md` for project-specific settings:

```markdown
---
test_command: uv run pytest
typecheck_command: ty check
lint_command: uv run ruff check
strict_stop_hook: true
---

# Project Notes

Any project-specific guidance for the orchestrator.
```

## Requirements

- Claude Code CLI
- Python 3.11+ with uv (for Python projects)
- Or Node.js 18+ (for JavaScript/TypeScript projects)

## License

MIT
