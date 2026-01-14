---
title: Test Error Types
impact: LOW
impactDescription: validates typed error handling
tags: test, errors, typed, instanceof
---

## Test Error Types

Verify that functions throw typed errors.

**Incorrect (generic error testing):**

```typescript
test('throws on invalid input', () => {
  expect(() => parseUser('invalid')).toThrow();
  // What type of error? What message?
});
```

**Correct (typed error testing):**

```typescript
test('throws ValidationError on invalid input', () => {
  expect(() => parseUser('invalid')).toThrow(ValidationError);
});

test('ValidationError contains field info', () => {
  try {
    parseUser('{"id": 123}'); // id should be string
    fail('Should have thrown');
  } catch (error) {
    expect(error).toBeInstanceOf(ValidationError);
    if (error instanceof ValidationError) {
      expect(error.fields).toContain('id');
      expect(error.code).toBe('VALIDATION_ERROR');
    }
  }
});
```

Reference: [Jest Error Testing](https://jestjs.io/docs/expect#tothrowerror)
