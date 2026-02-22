# Upgrade dev-workflow to Claude Code 2.1.39 + Opus 4.6

> **Execution:** Use `/dev-workflow:execute-plan docs/plans/2026-02-22-upgrade-claude-2139-opus46.md` to implement task-by-task.

**Goal:** Modernize the dev-workflow plugin to use Claude Code 2.1.39 primitives (TaskCreate/TaskUpdate/TaskList/TaskGet, updated ExitPlanMode, TaskStop) and reference Opus 4.6.

**Architecture:** Replace TodoWrite with granular task management primitives. Replace manual group-based parallelism with native `blocks`/`blockedBy` dependency tracking. Remove stale reference docs (tools.md, hooks.md). Clean up Serena MCP references.

---

## Tool Replacement Map

| Old | New | Notes |
|-----|-----|-------|
| `TodoWrite` | `TaskCreate, TaskUpdate, TaskList, TaskGet` | Granular task management |
| `ExitPlanMode(launchSwarm, teammateCount)` | `ExitPlanMode(allowedPrompts)` | Swarm params removed |
| `LS` | *(remove)* | Use Bash ls instead |
| `NotebookRead` | *(remove)* | Read handles .ipynb |
| `KillShell` | `TaskStop` | Renamed |
| `SlashCommand` | `Skill` (with `args` param) | Consolidated |
| `mcp__plugin_serena_serena*` | *(remove)* | Serena no longer used |

## Model Changes

- Text references: "Opus 4.5" -> "Opus 4.6"
- Frontmatter `model: opus` stays (resolves to Opus 4.6 automatically)

## Workflow Changes

### Execute-Plan Redesign

**Before:** Manual `group_tasks_by_dependency()` shell function + TodoWrite
**After:** `TaskCreate` with `addBlockedBy` for native dependency tracking

New flow:
1. Parse plan -> extract tasks
2. `TaskCreate` for each task, using `addBlockedBy` to express file-overlap dependencies
3. Launch unblocked tasks in parallel via `Task(run_in_background: true)`
4. `TaskUpdate` marks completed
5. `TaskList` shows what's next (auto-unblocks)

### Swarm Removal

**Before:** `ExitPlanMode(launchSwarm: true, teammateCount: N)` spawned teammates
**After:** Parallel execution via Task agents (execute-plan already does this)

Native `EnterPlanMode` path: quick/simple features only (1-3 tasks).
For parallel execution: use `/dev-workflow:execute-plan`.

## Files to Delete

- `tools.md` - Stale reference doc duplicating system-level tool definitions
- `hooks.md` - Stale reference doc duplicating system-level hook definitions

## Files to Modify (~20 files)

### Commands (6 files)
- `commands/execute-plan.md` - Major rewrite (TodoWrite->TaskCreate/Update, native deps, remove swarm, remove Serena, Opus 4.6)
- `commands/write-plan.md` - Frontmatter + swarm refs + Serena
- `commands/resume.md` - TodoWrite->TaskList/TaskGet, simplify, remove Serena
- `commands/abandon.md` - TodoWrite->TaskUpdate delete, remove Serena
- `commands/brainstorm.md` - Remove Serena from allowed-tools
- `commands/user-story.md` - TodoWrite->TaskCreate/Update in allowed-tools

### Skills (9 files)
- `skills/getting-started/SKILL.md` - TodoWrite->TaskCreate/Update, remove swarm, remove Serena
- `skills/test-driven-development/SKILL.md` - Remove Serena
- `skills/systematic-debugging/SKILL.md` - Remove Serena
- `skills/receiving-code-review/SKILL.md` - Remove Serena
- `skills/finishing-a-development-branch/SKILL.md` - Remove Serena
- `skills/root-cause-tracing/SKILL.md` - Remove Serena
- `skills/condition-based-waiting/SKILL.md` - Remove Serena
- `skills/testing-anti-patterns/SKILL.md` - Remove Serena
- `skills/simple-git-worktrees/SKILL.md` - Verify (no Serena expected)

### Agents (3 files)
- `agents/code-architect.md` - Clean (no LS in frontmatter tools, but verify)
- `agents/code-explorer.md` - Remove LS reference in body text
- `agents/code-reviewer.md` - Verify clean

### Config/Docs (2 files)
- `CLAUDE.md` - Update valid tools list, remove tools.md/hooks.md references
- `scripts/hook-helpers.sh` - Remove `group_tasks_by_dependency` if unused elsewhere

## Design Decisions

1. **Keep Task-based parallelism** - execute-plan already uses Task(run_in_background) effectively; no need to invent new patterns
2. **Native dependency tracking** - blocks/blockedBy replaces shell-based group parsing, making resume more natural
3. **Delete reference docs** - agents get tool definitions from system prompt; maintaining duplicate docs creates staleness
4. **Remove Serena** - no longer in use, reduces noise in frontmatter
5. **Preserve workflow shape** - brainstorm -> write-plan -> execute-plan flow stays, only internals change
