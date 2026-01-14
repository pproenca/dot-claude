---
title: Test Type Inference
impact: LOW
impactDescription: validates generic type inference
tags: test, inference, generics, expect-type
---

## Test Type Inference

Verify that generic functions infer types correctly.

**Incorrect (no inference tests):**

```typescript
function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  // Implementation
}

// How do we know inference works correctly?
```

**Correct (inference tests):**

```typescript
import { expectTypeOf } from 'expect-type';

function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  // Implementation
}

// Test inference
const user = { id: '1', name: 'John', email: 'john@example.com' };
const picked = pick(user, ['id', 'name']);

expectTypeOf(picked).toEqualTypeOf<{ id: string; name: string }>();
expectTypeOf(picked).not.toHaveProperty('email');
```

Reference: [TypeScript Type Inference](https://www.typescriptlang.org/docs/handbook/type-inference.html)
