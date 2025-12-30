# progress.txt Template

Copy and adapt this template for session state tracking.

```
=== Session State ===
Last completed: [Last task/milestone completed]
Next task: [What to work on next]
Blockers: [None / List any blockers]
Current phase: [X of Y]
Complexity level: [Trivial/Small/Medium/Large/Huge]

=== Key Decisions ===
- [Decision 1] (reason: [why])
- [Decision 2] (commit: [hash if relevant])

=== Files Modified ===
[List files changed in this session]

=== Files To Modify ===
[List files still needing changes]

=== Interfaces Defined ===
[Key interfaces/contracts established]

=== Known Issues ===
[Any bugs or issues discovered]

=== Notes ===
[Anything else important for next session]
```

## Example

```
=== Session State ===
Last completed: Token generation service with full test coverage
Next task: Session management implementation
Blockers: None
Current phase: 2 of 4 (Implementation)
Complexity level: Medium

=== Key Decisions ===
- JWT for tokens (industry standard, good library support)
- 1h expiration default (can be overridden in config)
- HS256 algorithm (simpler than RS256, sufficient for this use case)
- Refresh tokens: deferred to Phase 3

=== Files Modified ===
src/auth/token.py
src/models/token.py
tests/auth/test_token.py

=== Files To Modify ===
src/auth/session.py (create)
tests/auth/test_session.py (create)
src/api/auth.py (integration)

=== Interfaces Defined ===
TokenPayload(sub: str, email: str, exp: datetime)
generate_token(credentials: UserCredentials) -> str
validate_token(token: str) -> TokenPayload | None

=== Known Issues ===
None

=== Notes ===
- Found existing crypto utils at src/utils/crypto.py - reuse HMAC helpers
- User model already has ID field from previous work
- Environment variable JWT_SECRET must be set
```

## Usage Rules

1. **Update at session end** - Always update before stopping
2. **Read at session start** - First action after resuming
3. **Keep it compact** - This is a summary, not a log
4. **Focus on actionable info** - What do I need to continue?

## When to Update

- After completing a significant milestone
- Before any context compaction
- Before ending a session
- After making key decisions
- When blockers are discovered or resolved
