# Phase: EXPLORE

## Purpose
Understand the codebase before planning. No code modifications allowed.

## First Action
Set phase to EXPLORE:
```bash
source "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/worktree-utils.sh"
STATE_DIR=$(worktree_state_dir)
mkdir -p "$STATE_DIR" && echo "EXPLORE" > "${STATE_DIR}/workflow-phase"
```

## Activities

### 1. Read Relevant Files
- Entry points related to the task
- Similar existing implementations
- Configuration files

### 2. Grep for Patterns
- Find coding conventions
- Locate related functionality
- Identify test patterns

### 3. Document Architecture
- Brief notes on current structure
- Key modules and their responsibilities
- Data flow patterns

### 4. Identify Integration Points
- Where will new code connect?
- What interfaces need to be respected?
- What dependencies exist?

## Output
Write brief exploration notes. Include:
- Key files discovered
- Patterns to follow
- Potential challenges
- Initial task decomposition ideas

## Constraints
- Read-only operations
- No code modifications
- No spawning subagents yet
- No creating plan.md yet

## Duration
Target: Complete exploration before context reaches 30% usage.

## Transition
When exploration is complete, proceed to PLAN phase:
```bash
Read("${CLAUDE_PLUGIN_ROOT}/agents/references/phase-plan.md")
```
