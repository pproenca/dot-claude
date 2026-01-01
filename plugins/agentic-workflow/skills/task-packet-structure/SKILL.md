---
name: task-packet-structure
description: This skill activates when creating tasks for subagents, delegating work, structuring handoffs, or when phrases like "task packet", "delegate task", "subagent handoff", "create task", "spawn agent" are used. Provides the standard task packet format for subagent delegation.
allowed-tools: Read, Write, Task
---

# Task Packet Structure

Task packets are the atomic units of work delegated to subagents. They contain everything a subagent needs to complete a focused task independently.

## Required Fields

Every task packet MUST include these 6 fields:

### 1. Objective

Single clear goal in one sentence. The subagent should know exactly what success looks like.

✅ Good: "Implement JWT token generation that returns signed tokens with user claims"
❌ Bad: "Work on the auth system"

### 2. Scope

Exact files and modules the subagent is allowed to modify.

```
Files to create:
- src/auth/token.py

Files to modify:
- src/auth/__init__.py (add export)

Files to read (context only):
- src/models/user.py
- src/config.py
```

### 3. Interface

Input and output contracts. What does this component receive? What does it produce?

```python
# Input
class UserCredentials(Struct):
    user_id: str
    email: str

# Output
def generate_token(credentials: UserCredentials) -> str:
    """Returns JWT token string"""
```

### 4. Constraints

What the subagent should NOT do. Critical for preventing scope creep.

```
DO NOT:
- Modify API endpoints (separate task)
- Implement session management (separate task)
- Add refresh token logic (deferred)
- Change user model structure
- Add new dependencies without approval
```

### 5. Success Criteria

Measurable completion conditions. How do we know the task is done?

```
Success when:
- [ ] generate_token function implemented
- [ ] validate_token function implemented
- [ ] Unit tests pass (minimum 5 tests)
- [ ] Handles expired tokens
- [ ] Handles invalid signatures
- [ ] Type check passes
- [ ] Lint clean
```

### 6. Tool Allowlist

Which tools the subagent may use.

```
Allowed tools:
- Read (for reading context files)
- Write (for creating new files)
- Edit (for modifying existing files)
- Bash (for running tests, type check, lint)
- Grep (for finding patterns)
- Glob (for finding files)

NOT allowed:
- Task (no spawning sub-subagents)
- WebSearch/WebFetch (work with local context only)
```

## Complete Example

```markdown
# Task Packet: Token Service Implementation

## Objective
Implement JWT token generation and validation service that creates signed tokens with user claims and validates incoming tokens.

## Scope
Create:
- src/auth/token.py

Modify:
- src/auth/__init__.py (add exports)

Read only:
- src/models/user.py (for UserCredentials type)
- src/config.py (for SECRET_KEY)

## Interface

```python
# Input type (from src/models/user.py)
class UserCredentials(Struct):
    user_id: str
    email: str

# Functions to implement
def generate_token(credentials: UserCredentials) -> str:
    """
    Generate JWT token for user.
    Token contains: sub (user_id), email, exp (1 hour from now)
    """

def validate_token(token: str) -> TokenPayload | None:
    """
    Validate JWT token.
    Returns TokenPayload if valid, None if invalid/expired.
    """

# Output type to define
class TokenPayload(Struct):
    sub: str
    email: str
    exp: datetime
```

## Constraints
DO NOT:
- Implement session management (Task B)
- Add API endpoints (Task C)
- Implement refresh tokens (deferred)
- Modify user model
- Add database operations
- Use any external APIs

## Success Criteria
- [ ] generate_token implemented and tested
- [ ] validate_token implemented and tested
- [ ] TokenPayload struct defined
- [ ] Minimum 5 unit tests
- [ ] Tests cover: valid token, expired token, invalid signature
- [ ] uv run pytest passes
- [ ] ty check passes
- [ ] uv run ruff check passes
- [ ] Artifact written to .claude/artifacts/task-a-token.md

## Tool Allowlist
- Read, Write, Edit, Bash, Grep, Glob
```

## What NOT to Include

Keep task packets focused. Do NOT include:

- Full codebase context
- Other task packets
- Previous conversation history
- Unrelated module contents
- The full plan.md

If subagent needs context from another task, reference the artifact:
"Read .claude/artifacts/task-a-token.md for the TokenPayload interface"

## Context Budget

Target: 15-20K tokens per implementation agent

Breakdown:
- System prompt: ~2K
- Task packet: ~1-2K
- Interface definitions: ~1K
- Relevant existing code: ~5-10K
- Buffer for exploration: ~5K

## Spawning with Task Tool

### Option A: File-Based (Recommended)

Use task-packet-writer to create packet files, then reference by path:

```
# First, create packet files
Task(
  subagent_type: "agentic-workflow:task-packet-writer"
  prompt: |
    PLAN_PATH: .claude/plan.md
    OUTPUT_DIR: .claude/task-packets/
    WORKTREE_BASE: ~/.dot-claude-worktrees
    PROJECT_NAME: myapp
)

# Then spawn executor with file path
Task(
  subagent_type: "agentic-workflow:task-executor"
  prompt: "TASK_PACKET_PATH: .claude/task-packets/task-a-token.md"
)
```

This keeps orchestrator context minimal.

### Option B: Inline (Legacy)

For simple cases or backward compatibility:

```
Use Task tool:
- subagent_type: agentic-workflow:task-executor
- prompt: [Full task packet content]
- model: opus
```

## Background Execution Pattern

For long-running tasks where you want to continue working while waiting:

### Launch in Background

```
Task tool with:
- subagent_type: agentic-workflow:task-executor
- prompt: [task packet]
- run_in_background: true  ← KEY PARAMETER
```

Returns immediately with `task_id`. The subagent runs asynchronously.

### Retrieve Results Later

```
TaskOutput tool with:
- task_id: [returned task_id]
- block: true  ← Wait for completion
- timeout: 300000  ← 5 minutes max
```

### When to Use Background vs Foreground

| Scenario | Use Background? |
|----------|-----------------|
| Single task, need result immediately | No |
| Multiple independent tasks (Wave 1) | Yes - launch all, then wait for all |
| Task while preparing next wave | Yes |
| Verification agents | Optional - parallel foreground is usually fine |

### Pattern: Launch Multiple, Then Collect

```
# Launch 3 tasks in background
task_a_id = Task(executor, Task A, run_in_background: true)
task_b_id = Task(executor, Task B, run_in_background: true)
task_c_id = Task(executor, Task C, run_in_background: true)

# Continue with other prep work here...
# (e.g., prepare Wave 2 task packets)

# Collect results when ready
result_a = TaskOutput(task_a_id, block: true)
result_b = TaskOutput(task_b_id, block: true)
result_c = TaskOutput(task_c_id, block: true)
```

### Alternative: Parallel Foreground (Simpler)

For most cases, parallel foreground is simpler - just include multiple Task tool calls in a single message:

```
Single message with multiple Task tool calls:
- Task(executor, Task A)
- Task(executor, Task B)
- Task(executor, Task C)

All three execute simultaneously and results arrive together.
```

Use background execution when you need to do other work while waiting.

---

For complete task packet examples, see examples/task-packet-example.md
