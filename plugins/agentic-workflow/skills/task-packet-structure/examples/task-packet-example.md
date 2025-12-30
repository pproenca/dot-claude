# Task Packet Examples

## Example 1: Independent Task (Wave 1)

This task has no dependencies on other tasks.

```markdown
# Task Packet A: Token Service

## Objective
Implement JWT token generation service that creates signed tokens with user claims.

## Scope
Create:
- src/auth/token.py
- tests/auth/test_token.py

Modify:
- src/auth/__init__.py (add exports)

Read only:
- src/models/user.py

## Interface
```python
# Input
class UserCredentials(Struct):
    user_id: str
    email: str

# Output
def generate_token(credentials: UserCredentials) -> str: ...
def validate_token(token: str) -> TokenPayload | None: ...

class TokenPayload(Struct):
    sub: str
    email: str
    exp: datetime
```

## Constraints
- DO NOT implement session management
- DO NOT add API endpoints
- DO NOT modify user model

## Success Criteria
- [ ] Both functions implemented
- [ ] 5+ unit tests passing
- [ ] Type check clean
- [ ] Artifact written

## Tools
Read, Write, Edit, Bash, Grep, Glob
```

---

## Example 2: Dependent Task (Wave 2)

This task depends on Task A completing first.

```markdown
# Task Packet C: Auth API Endpoints

## Objective
Implement HTTP endpoints for login and token validation using the token service.

## Dependencies
**Read first**: .claude/artifacts/task-a-token.md
- Provides: generate_token, validate_token, TokenPayload

## Scope
Create:
- src/api/auth.py
- tests/api/test_auth.py

Modify:
- src/api/__init__.py (register routes)

Read only:
- src/auth/token.py (use, don't modify)
- src/auth/session.py (use, don't modify)

## Interface
```python
# Endpoints to implement
POST /auth/login
  Request: {"email": str, "password": str}
  Response: {"token": str}

POST /auth/validate
  Request: {"token": str}
  Response: {"valid": bool, "payload": TokenPayload | null}

POST /auth/logout
  Request: (token in header)
  Response: {"success": bool}
```

## Constraints
- DO NOT modify token service implementation
- DO NOT modify session service implementation
- DO NOT add new authentication methods
- Use existing token/session services as-is

## Success Criteria
- [ ] All 3 endpoints implemented
- [ ] Integration tests passing
- [ ] Proper error responses for invalid input
- [ ] Token in Authorization header for logout
- [ ] Type check clean
- [ ] Artifact written

## Tools
Read, Write, Edit, Bash, Grep, Glob
```

---

## Example 3: Verification Task

This task runs verification on completed implementation.

```markdown
# Task Packet: Code Review

## Objective
Review token service implementation for security, performance, and code quality issues.

## Scope
Read only (NO modifications):
- src/auth/token.py
- tests/auth/test_token.py
- src/models/user.py

## Focus Areas

### Security
- Secret handling (not hardcoded?)
- Token expiration enforced?
- Signature validation correct?

### Performance
- No unnecessary operations?
- Efficient algorithms?

### Code Quality
- Clear naming?
- Proper error handling?
- Type hints complete?
- Docstrings present?

### Test Coverage
- Happy path covered?
- Error cases covered?
- Edge cases covered?

## Output Format
```markdown
## Security Review
- [x] Secrets from environment ✓
- [x] Expiration enforced ✓
- [ ] Issue: Missing check for empty token string

## Performance
- [x] No issues found

## Code Quality
- [x] Good naming
- [ ] Missing docstring on TokenPayload

## Test Coverage
- [x] Happy path ✓
- [x] Expired token ✓
- [ ] Missing: malformed token test

## Recommended Actions
1. Add empty token check in validate_token
2. Add docstring to TokenPayload
3. Add test for malformed token input
```

## Constraints
- DO NOT modify any files
- Report issues only, do not fix them

## Success Criteria
- [ ] All focus areas reviewed
- [ ] Issues documented with severity
- [ ] Recommendations actionable

## Tools
Read, Grep, Glob (no Write or Edit)
```

---

## Example 4: Anti-Overfit Check

```markdown
# Task Packet: Anti-Overfitting Verification

## Objective
Verify implementation is general-purpose and not overfitted to test cases.

## Context
**Implementation files only** (NO test files):
- src/auth/token.py

**Requirements** (from task packet A):
- Generate JWT with user claims
- Validate tokens and return payload or None

## Check For

### Hardcoded Values
- Any magic numbers matching test data?
- Hardcoded user IDs or emails?
- Fixed timestamps?

### Test-Specific Logic
- Conditionals that only work for test inputs?
- Special cases that match test assertions?

### Missing Generalization
- Would this work for any valid input?
- Edge cases the tests didn't cover?

## Output Format
```markdown
## Overfitting Analysis

### Hardcoded Values
- [x] No hardcoded test data found ✓
- [ ] Found: expiration hardcoded to exactly 3600s (matches test)

### Test-Specific Logic
- [x] No conditional test paths ✓

### Generalization Issues
- [ ] Issue: Only handles string user_id, spec allows int

## Verdict
PARTIAL OVERFIT - Some issues found

## Remediation
1. Make expiration configurable
2. Handle both string and int user_id
```

## Constraints
- DO NOT read test files
- DO NOT modify any files
- Focus only on implementation vs requirements

## Tools
Read, Grep (no test file access)
```
