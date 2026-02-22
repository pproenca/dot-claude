---
name: test-driven-development
description: Use this skill when implementing any feature, bug fix, or plan task. Triggers on "write tests", "add a test", "do TDD", "test-driven", "implement with tests", "implement task", or when dispatched as a subagent for plan execution. Write test first, watch it fail, write minimal code to pass.
allowed-tools: Read, Edit, Bash
---

# Test-Driven Development (TDD)

Write the test first. Watch it fail. Write minimal code to pass.

If you wrote implementation code before the test, discard it and start fresh from the test.

## The Cycle: Red → Green → Refactor

### RED — Write Failing Test

Write one minimal test showing what should happen.

**Good:**

```typescript
test("retries failed operations 3 times", async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error("fail");
    return "success";
  };

  const result = await retryOperation(operation);

  expect(result).toBe("success");
  expect(attempts).toBe(3);
});
```

Clear name, tests real behavior, one thing.

**Bad:**

```typescript
test("retry works", async () => {
  const mock = jest
    .fn()
    .mockRejectedValueOnce(new Error())
    .mockRejectedValueOnce(new Error())
    .mockResolvedValueOnce("success");
  await retryOperation(mock);
  expect(mock).toHaveBeenCalledTimes(3);
});
```

Vague name, tests mock not code.

Requirements:
- One behavior per test
- Clear name describing behavior
- Real code (mocks only if unavoidable)

### Verify RED — Run and Confirm Failure

```bash
npm test path/to/test.test.ts
```

Confirm:
- Test fails (not errors from typos)
- Failure is because the feature is missing
- If test passes immediately: you're testing existing behavior — fix the test

### GREEN — Minimal Code

Write the simplest code to pass the test. Nothing more.

**Good:**

```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === 2) throw e;
    }
  }
  throw new Error("unreachable");
}
```

**Bad:**

```typescript
async function retryOperation<T>(
  fn: () => Promise<T>,
  options?: {
    maxRetries?: number;
    backoff?: "linear" | "exponential";
    onRetry?: (attempt: number) => void;
  }
): Promise<T> { /* YAGNI */ }
```

Don't add features, refactor other code, or "improve" beyond the test.

### Verify GREEN — Run and Confirm Pass

```bash
npm test path/to/test.test.ts
```

Confirm: test passes, other tests still pass, output clean.

If test fails: fix code, not test. If other tests fail: fix now.

### REFACTOR — Clean Up (Green Only)

Remove duplication, improve names, extract helpers. Keep tests green.

### Repeat

Next failing test for next behavior.

## Why Test-First Matters

Tests written after code pass immediately — proving nothing. You never see them catch the bug they're supposed to catch. Test-first forces you to see the failure, proving the test actually validates behavior.

Tests-after are biased by your implementation: you test what you built, not what's required. Tests-first force edge case discovery before implementing.

If the test is hard to write, the design is telling you something — the interface is too complex.

## Good Tests

| Quality | Good | Bad |
|---------|------|-----|
| Minimal | One thing per test | `test('validates email and domain and whitespace')` |
| Clear | Name describes behavior | `test('test1')` |
| Shows intent | Demonstrates desired API | Obscures what code should do |
| Real code | Tests actual behavior | Tests mock behavior |

## When Stuck

| Problem | Solution |
|---------|----------|
| Don't know how to test | Write wished-for API. Write assertion first. |
| Test too complicated | Design too complicated. Simplify interface. |
| Must mock everything | Code too coupled. Use dependency injection. |
| Test setup huge | Extract helpers. Still complex? Simplify design. |

## Bug Fix Example

**Bug:** Empty email accepted

**RED:**
```typescript
test("rejects empty email", async () => {
  const result = await submitForm({ email: "" });
  expect(result.error).toBe("Email required");
});
```

**Verify RED:** `FAIL: expected 'Email required', got undefined`

**GREEN:**
```typescript
function submitForm(data: FormData) {
  if (!data.email?.trim()) {
    return { error: "Email required" };
  }
  // ...
}
```

**Verify GREEN:** `PASS`

**REFACTOR:** Extract validation for multiple fields if needed.

## Verification Checklist

Before marking work complete:

- [ ] Every new function has a test
- [ ] Watched each test fail before implementing
- [ ] Each test failed for expected reason (feature missing, not typo)
- [ ] Wrote minimal code to pass each test
- [ ] All tests pass, output clean
- [ ] Tests use real code (mocks only if unavoidable)
- [ ] Edge cases and errors covered

## Integration

- **testing-anti-patterns** — reviewing existing test quality
- **systematic-debugging** — write failing test reproducing bug
- **verification-before-completion** — verify tests pass before claiming done
