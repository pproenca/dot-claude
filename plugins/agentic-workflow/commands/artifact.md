---
description: Manage subagent handoff artifacts in .claude/artifacts/
argument-hint: [list|read|clean] [name]
allowed-tools: Read, Write, Glob, Bash
---

# /artifact - Artifact Management

Manage the subagent handoff artifacts stored in `.claude/artifacts/`.

## Input

Action: $ARGUMENTS
- `list` (default): Show all artifacts
- `read <name>`: Display specific artifact
- `clean`: Remove old artifacts

## Actions

### list (default)

List all artifacts with summaries:

1. **Find artifacts**:
   ```bash
   ls -la .claude/artifacts/
   ```

2. **Show list with dates**:
   ```
   ## Artifacts in .claude/artifacts/

   | File | Modified | Status |
   |------|----------|--------|
   | task-a-token-service.md | 2h ago | Complete |
   | task-b-session-service.md | 1h ago | Complete |
   | task-c-api-endpoints.md | 30m ago | Partial |

   3 artifacts found.
   ```

3. **Quick summary of each** (first ~5 lines):
   ```
   ### task-a-token-service.md
   Status: Complete
   Files: src/auth/token.py
   Interface: generate_token, validate_token
   ```

### read <name>

Display full artifact content:

1. **Find matching artifact**:
   - Exact match: `read task-a-token-service.md`
   - Partial match: `read token` → finds task-a-token-service.md

2. **Display content**:
   ```
   ## Artifact: task-a-token-service.md

   [Full artifact content]
   ```

3. **If not found**:
   ```
   Artifact not found: <name>

   Available artifacts:
   - task-a-token-service.md
   - task-b-session-service.md
   ```

### clean

Remove old or obsolete artifacts:

1. **Show what will be deleted**:
   ```
   Found 5 artifacts:
   - task-a-token-service.md (2 days old)
   - task-b-session-service.md (2 days old)
   - task-c-api-endpoints.md (1 day old)
   - old-experiment.md (1 week old)
   - draft-notes.md (3 days old)
   ```

2. **Ask what to clean** using AskUserQuestion tool:

```
AskUserQuestion({
  questions: [{
    question: "Which artifacts would you like to remove?",
    header: "Clean scope",
    multiSelect: false,
    options: [
      {
        label: "Older than 3 days",
        description: "Remove artifacts older than 3 days, keep recent ones"
      },
      {
        label: "Select specific",
        description: "Choose which specific artifacts to remove"
      },
      {
        label: "All artifacts",
        description: "Clear the entire .claude/artifacts/ directory"
      },
      {
        label: "Cancel",
        description: "Don't remove anything"
      }
    ]
  }]
})
```

3. **Based on response**:
   - "Older than 3 days" → Remove artifacts with modification date > 3 days
   - "Select specific" → Show list, ask user to specify which ones
   - "All artifacts" → Clear entire directory
   - "Cancel" → Exit without changes

4. **Execute cleanup**:
   ```bash
   rm .claude/artifacts/<selected>
   ```

5. **Report**:
   ```
   Removed 2 artifacts:
   - old-experiment.md
   - draft-notes.md

   3 artifacts remaining.
   ```

## Example: list

```
/artifact list

## Artifacts in .claude/artifacts/

| File | Modified | Size |
|------|----------|------|
| task-a-token-service.md | 2h ago | 1.2K |
| task-b-session-service.md | 1h ago | 0.9K |
| task-c-api-endpoints.md | 30m ago | 1.5K |

3 artifacts found.

### Quick Summaries

**task-a-token-service.md**
Status: Complete
Files: src/auth/token.py, tests/auth/test_token.py
Interface: generate_token, validate_token

**task-b-session-service.md**
Status: Complete
Files: src/auth/session.py, tests/auth/test_session.py
Interface: create_session, validate_session, destroy_session

**task-c-api-endpoints.md**
Status: Partial (integration pending)
Files: src/api/auth.py
Interface: POST /login, POST /validate, POST /logout
```

## Example: read

```
/artifact read token

## Artifact: task-a-token-service.md

# Token Service Implementation

## Status
Complete

## Objective
Implement JWT token generation and validation for user authentication.

## Files Modified
- src/auth/token.py (created)
- tests/auth/test_token.py (created)
- src/auth/__init__.py (modified)

## Exported Interface
```python
def generate_token(credentials: UserCredentials) -> str: ...
def validate_token(token: str) -> TokenPayload | None: ...
```

## Test Coverage
- 8 tests passing
- Edge cases: expired, invalid signature, malformed

## Dependencies
- Requires: JWT_SECRET environment variable

## Integration Notes
- Call generate_token after successful login
- Call validate_token on authenticated requests
```

## Example: clean

```
/artifact clean

Found 5 artifacts:
- task-a-token-service.md (current task)
- task-b-session-service.md (current task)
- old-spike-auth.md (1 week old)
- draft-design.md (5 days old)

[AskUserQuestion: Which artifacts would you like to remove?]
Options: Older than 3 days | Select specific | All artifacts | Cancel

User selects: "Older than 3 days"

Removing artifacts older than 3 days:
- old-spike-auth.md
- draft-design.md

Removed 2 artifacts.
2 artifacts remaining.
```

## If No Artifacts Directory

```
/artifact

No artifacts directory found.

Artifacts are created by subagents during orchestrated workflows.
To start an orchestrated workflow: /orchestrate <task>

Or create the directory manually:
mkdir -p .claude/artifacts
```
