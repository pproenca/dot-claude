---
title: Use Type Assertions in Tests
impact: LOW
impactDescription: validates runtime values match types
tags: test, assertions, zod, validation
---

## Use Type Assertions in Tests

Use type assertions to verify runtime values match expected types.

**Incorrect (no runtime type checking):**

```typescript
test('parseUser returns User', () => {
  const result = parseUser('{"id": "1", "name": "John"}');
  expect(result.id).toBe('1');
  // What if result has wrong shape?
});
```

**Correct (validated assertions):**

```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
});

test('parseUser returns valid User', () => {
  const result = parseUser(
    '{"id": "1", "name": "John", "email": "john@example.com"}'
  );

  // Runtime validation
  const validated = UserSchema.parse(result);

  expect(validated.id).toBe('1');
  expect(validated.name).toBe('John');
});
```

Reference: [Zod Schema Validation](https://zod.dev/)
