# Artifact Template

Subagent handoff summaries should follow this format. Max 1-2K tokens.

```markdown
# Artifact: [Component Name] Implementation

## Status
[Complete / Partial / Blocked]

## Objective
[What this task was supposed to accomplish]

## Files Modified
- path/to/file1.py (created/modified)
- path/to/file2.py (created/modified)

## Exported Interface
```python
# Key functions/classes other code can use
def function_name(param: Type) -> ReturnType: ...
class ClassName:
    def method(self) -> Type: ...
```

## Test Coverage
- X tests passing
- Edge cases covered: [list]
- Edge cases NOT covered: [list if any]

## Dependencies
- Requires: [external deps, env vars]
- Depends on: [other modules]

## Integration Notes
- [How to use this from other code]
- [Any gotchas or special considerations]

## Decisions Made
- [Key decisions made during implementation]
- [Why alternatives were rejected]
```

## Example

```markdown
# Artifact: Token Service Implementation

## Status
Complete

## Objective
Implement JWT token generation and validation for user authentication.

## Files Modified
- src/auth/token.py (created)
- src/models/token.py (created)
- tests/auth/test_token.py (created)

## Exported Interface
```python
def generate_token(credentials: UserCredentials) -> str:
    """Generate JWT token for authenticated user."""
    ...

def validate_token(token: str) -> TokenPayload | None:
    """Validate JWT token. Returns None if invalid/expired."""
    ...

class TokenPayload(Struct):
    sub: str  # User ID
    email: str
    exp: datetime
```

## Test Coverage
- 8 tests passing
- Edge cases covered:
  - Expired token
  - Invalid signature
  - Missing claims
  - Malformed token string
- Edge cases NOT covered:
  - Token revocation (deferred to session management)

## Dependencies
- Requires: JWT_SECRET environment variable
- Depends on: src/models/user.py (UserCredentials)

## Integration Notes
- Call generate_token after successful login
- Call validate_token on every authenticated request
- TokenPayload.exp is UTC datetime
- Tokens expire after 1 hour by default

## Decisions Made
- HS256 algorithm (simpler than RS256, sufficient for single-server)
- 1 hour expiration (balance security vs UX)
- No refresh tokens in this task (separate task)
```

## File Location

Save artifacts to: `.claude/artifacts/[task-id]-[component].md`

Example: `.claude/artifacts/task-a-token-service.md`

## Token Budget

Keep artifacts under 1-2K tokens. This is a summary, not documentation.

Focus on:
- What was built
- How to use it
- What to watch out for

Omit:
- Full code listings
- Detailed implementation explanations
- Test file contents
