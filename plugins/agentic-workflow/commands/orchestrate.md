---
description: Start orchestrated workflow for complex tasks - assesses complexity and launches lead-orchestrator agent
argument-hint: <task description>
allowed-tools: Task, Read, Write, Glob, Grep, TodoWrite, AskUserQuestion, Bash
---

# /orchestrate - Multi-Agent Task Orchestration

You are initiating the orchestrated workflow for a complex task.

## Input

Task description: $ARGUMENTS

## Workflow

### Step 1: Initialize Workflow Phase

**First action - ALWAYS do this**:
```bash
mkdir -p .claude && echo "IDLE" > .claude/workflow-phase
```

### Step 2: Assess Complexity

Analyze the task to determine complexity level:

| Level | Indicators | Approach |
|-------|-----------|----------|
| Trivial | Single file, single function | Direct guidance, no subagent |
| Small | 1-3 files, clear scope | 1 subagent + verification |
| Medium | 3-10 files, multiple modules | 2-3 subagents + integration |
| Large | 10+ files, architectural | 5+ subagents + milestones |
| Huge | Cross-system scope | 10+ subagents + phases |

### Step 3: If Trivial

Provide direct guidance without spawning agents:
1. Read relevant files
2. Make the change
3. Verify tests pass
4. Done

### Step 4: If Small or Above

1. **Create external state files**:
   - Create `todo.md` with initial task breakdown
   - Create `progress.txt` with session state
   - Create `.claude/artifacts/` directory if needed

2. **Set workflow phase to EXPLORE**:
```bash
echo "EXPLORE" > .claude/workflow-phase
```

3. **Launch lead-orchestrator agent**:
   ```
   Use Task tool with:
   - subagent_type: lead-orchestrator
   - prompt: Include the task description and complexity assessment
   - model: opus
   ```

4. **Report to user**:
   - Complexity level assessed
   - What agent was launched
   - How to check progress: `/progress`

### Step 5: Wait for Orchestrator

The lead-orchestrator will:
1. **EXPLORE** - Read codebase, understand context
2. **PLAN** - Create plan.md
3. **WAIT FOR APPROVAL** - Use AskUserQuestion to get human sign-off
4. **DELEGATE** - Spawn task-executor subagents (only after approval)
5. **VERIFY** - Run verification agents
6. **SYNTHESIZE** - Collect results, handle issues

**CRITICAL**: The orchestrator MUST use AskUserQuestion before proceeding from PLAN to DELEGATE phase. This prevents premature execution.

## Example Execution

```
User: /orchestrate Implement user authentication with JWT tokens

Assessment: Medium complexity
- Multiple files: models, services, API, tests
- Multiple modules: auth, api, models
- Estimated: 3 subagents for implementation

Initializing workflow...
- Created .claude/workflow-phase = IDLE
- Created todo.md with task breakdown
- Created progress.txt with session state

Setting phase to EXPLORE...

Launching lead-orchestrator agent (opus) with task:
"Implement user authentication with JWT tokens"

The orchestrator will:
1. Explore the codebase
2. Create a plan for your approval (using AskUserQuestion)
3. Wait for your explicit approval before any implementation
4. Coordinate implementation across focused subagents

Check progress anytime with: /progress
```

## Phase Flow

```
IDLE → EXPLORE → PLAN_WAITING → (user approval) → DELEGATE → VERIFY → COMPLETE
                      ↑                                          ↓
                      └──────────── (if issues found) ───────────┘
```

**Stop hooks only run tests during**: DELEGATE, VERIFY, COMPLETE phases

## If No Arguments Provided

Ask the user to describe the task:

```
What task would you like to orchestrate?

Please describe:
1. What feature/change you want to implement
2. Any specific requirements or constraints
3. Any files you know are relevant

Example: "Implement user authentication with JWT tokens and session management"
```
