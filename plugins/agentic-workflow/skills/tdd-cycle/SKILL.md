---
name: tdd-cycle
description: This skill activates when writing tests, implementing features with testing, or when phrases like "TDD", "test-driven", "test first", "red green blue", "write tests before code" are used. Provides the Red-Green-Blue cycle for quality implementations.
allowed-tools: Read, Edit, Write, Bash
---

# Test-Driven Development Cycle

Follow the Red-Green-Blue cycle for all implementations. Write tests first, then implement.

## The Cycle

### 1. RED: Write Failing Test

Write a test that describes the expected behavior. The test MUST fail initially.

```python
def test_generate_token_returns_valid_jwt():
    """Token should be valid JWT with expected claims."""
    credentials = UserCredentials(email="test@example.com", user_id="123")

    token = generate_token(credentials)

    # Verify it's a valid JWT
    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    assert decoded["sub"] == "123"
    assert decoded["email"] == "test@example.com"
    assert "exp" in decoded
```

### 2. Run Tests - Confirm Failure

Execute the test to confirm it fails for the right reason.

```bash
uv run pytest tests/auth/test_token.py -v
```

Expected: Test fails because `generate_token` doesn't exist or returns wrong value.

If test passes without implementation → test is wrong, rewrite it.

### 3. Commit Tests

Commit the test separately from implementation:

```bash
git add tests/
git commit -m "test: add token generation test"
```

This preserves the specification even if implementation changes.

### 4. GREEN: Implement Minimal Code

Write the **minimum** code to make the test pass. No extra features.

```python
def generate_token(credentials: UserCredentials) -> str:
    """Generate JWT token for user credentials."""
    payload = {
        "sub": credentials.user_id,
        "email": credentials.email,
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

### 5. Run Tests - Confirm Pass

```bash
uv run pytest tests/auth/test_token.py -v
```

Expected: Test passes.

### 6. All Tests Pass?

If no → return to step 4, fix implementation.
If yes → proceed to refactor.

### 7. BLUE: Refactor

Now that tests pass, improve code quality without changing behavior:

- Extract helper functions
- Improve naming
- Remove duplication
- Add type hints
- Improve error handling

### 8. Run Tests - Confirm Still Pass

After refactoring:

```bash
uv run pytest tests/auth/test_token.py -v
```

Expected: Tests still pass. If they fail, refactoring broke something.

## Rules

1. **Never skip the failing test step** - If test doesn't fail first, it's not testing anything meaningful.

2. **Commit tests separately** - Keep test commits separate from implementation commits.

3. **Minimal implementation** - Only write enough code to pass current tests. No "while I'm here" additions.

4. **Refactor only after green** - Never refactor while tests are failing.

5. **Run tests frequently** - After every small change.

## Common Mistakes

### Writing Tests After Implementation

❌ Wrong order:
1. Write code
2. Write tests that pass

✅ Correct order:
1. Write test (RED)
2. Watch it fail
3. Write code (GREEN)

### Over-Engineering in GREEN Phase

❌ Wrong:
```python
def generate_token(credentials, options=None, custom_claims=None, ...):
    # 50 lines handling every possible case
```

✅ Correct:
```python
def generate_token(credentials):
    # Minimal implementation for current test
```

Add features only when you have failing tests requiring them.

### Skipping BLUE Phase

❌ Wrong: "Tests pass, I'm done!"

✅ Correct: Review code, look for improvements, THEN commit.

## Test Categories by Phase

### Unit Tests (Per Task)
- Test individual functions/methods
- Mock dependencies
- Fast, isolated
- Run during RED-GREEN cycle

### Integration Tests (After Wave)
- Test module interactions
- Real dependencies where practical
- Run after wave completes

### E2E Tests (Final Phase)
- Test full user flows
- Real or near-real environment
- Run before completion

---

For Python TDD examples, see examples/python-tdd-example.md
