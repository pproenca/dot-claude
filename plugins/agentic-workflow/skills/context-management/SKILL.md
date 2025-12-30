---
name: context-management
description: This skill activates when managing context across long tasks, handling compaction, preserving critical information, or when phrases like "context", "preserve", "compaction", "JIT loading", "external state", "todo.md", "progress.txt" are used. Provides strategies for maintaining coherence across context windows.
---

# Context Management for Long-Running Tasks

Context windows are finite. Long tasks require careful management to maintain coherence across compaction boundaries and sessions.

## Core Principle: External State

**Internal state (your memory) does NOT persist across compaction.**

Use external files for anything that must survive:
- **todo.md** - Task tracking
- **progress.txt** - Session state
- **NOTES.md** - Key decisions
- **.claude/artifacts/** - Subagent handoffs

## Just-In-Time Loading

Don't load everything upfront. Load what you need, when you need it.

### Strategy

1. **Maintain file path references**, not full content
2. **Grep before full read** - Find relevant sections first
3. **Load only active task context** - 15-20K tokens per subagent

### Example

❌ Wrong:
```
Read all files in src/
Read all files in tests/
Now let me understand this 200K token context...
```

✅ Correct:
```
Grep for "class UserService" → found in src/services/user.py
Read src/services/user.py → 200 lines
This is the file I need to modify.
```

## Context Budget Allocation

| Role | Token Budget | What to Include |
|------|--------------|-----------------|
| Orchestrator | ~50K | Full plan, all artifacts, coordination state |
| Implementation Agent | ~15-20K | Single task packet, interfaces, target files |
| Verification Agent | ~25K | Implementation code, tests, requirements |
| Integration Agent | ~30K | All interfaces, API layer, integration context |

**80% Rule**: Never exceed 80% of context window. When approaching limit, trigger compaction.

## External State File Formats

### todo.md

Track task progress with clear status markers:

```markdown
# [Feature Name]

## Phase 1: Setup
- [x] Read existing code patterns
- [x] Document current architecture
- [x] Create plan.md

## Phase 2: Implementation
- [x] Write token service tests
- [x] Implement token service
- [ ] Write session tests
- [ ] Implement session service

## Phase 3: Integration
- [ ] Wire up API endpoints
- [ ] Integration tests
- [ ] Update documentation
```

Use `[x]` for DONE, `[ ]` for PENDING.

Alternative format with explicit markers:

```markdown
# Authentication Feature

## Phase 1: Setup
DONE Read existing auth code
DONE Document patterns
DONE Create plan.md

## Phase 2: Token Service
DONE Write token tests
DONE Implement token.ts
PENDING Run full test suite

## Phase 3: Integration
PENDING Wire up API endpoints
PENDING Integration tests
```

### progress.txt

Session state for cross-session continuity:

```
=== Session State ===
Last completed: Token generation implementation
Next task: Session management
Blockers: None
Current phase: 2 of 4

=== Key Decisions ===
- JWT for tokens (commit abc123)
- 1h expiration default
- HS256 algorithm

=== Files Modified ===
src/auth/token.py
tests/auth/test_token.py

=== Notes ===
- Found existing crypto utils in src/utils/crypto.py
- User model already has ID field needed
```

### .claude/artifacts/ Structure

Subagent handoff summaries (max 1-2K tokens each):

```markdown
# Artifact: Token Service Implementation

## Status
Complete

## Files Modified
- src/auth/token.py (created)
- tests/auth/test_token.py (created)

## Exported Interface
```python
def generate_token(credentials: UserCredentials) -> str: ...
def validate_token(token: str) -> TokenPayload | None: ...
```

## Test Coverage
- 8 tests passing
- Edge cases: expired token, invalid signature, missing claims

## Integration Notes
- Requires JWT_SECRET environment variable
- Depends on UserCredentials from src/models/user.py
```

## Compression Triggers

Monitor context usage. When approaching 80%:

### Preserve (High Priority)
- Key architectural decisions
- Bugs discovered during implementation
- Critical file paths still needed
- Interface contracts defined
- Current task state and next steps

### Discard (Safe to Remove)
- Exploratory file reads that led nowhere
- Superseded approaches that were abandoned
- Verbose error messages (keep just error type)
- Already-completed task details
- Full file contents (keep path reference)

## Re-Injection Pattern

Long tasks span many conversation turns. Context drifts from original objective.

### Strategy

Every 5-10 turns:
1. Re-read todo.md
2. Re-read progress.txt
3. Identify next incomplete item
4. Explicitly state: "Continuing with: [next item]"

### Prompt

Include this reminder:

```
REMINDER: Re-check external state files.
- Read todo.md - what's next?
- Read progress.txt - any blockers?
- Continue with first incomplete item.
```

## Pre-Compaction Checklist

Before context compaction:

1. ✅ Is todo.md up to date?
2. ✅ Is progress.txt current?
3. ✅ Are key decisions documented?
4. ✅ Are interface contracts captured?
5. ✅ Can I resume from external state alone?

If yes to all, compaction is safe.

## Recovery After Compaction

When resuming after compaction:

1. Read todo.md
2. Read progress.txt
3. Read relevant artifacts from .claude/artifacts/
4. Identify current state
5. Continue with next task

---

For file format templates, see references/
