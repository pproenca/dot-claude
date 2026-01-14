---
title: Use Type-Level Tests
impact: LOW
impactDescription: catches type regressions
tags: test, type-level, expect-type, compile-time
---

## Use Type-Level Tests

Test types at compile time using assertion utilities.

**Incorrect (no type tests):**

```typescript
// Types might silently break without tests
type ExtractId<T> = T extends { id: infer I } ? I : never;

// Did refactoring break this? Who knows!
```

**Correct (type-level assertions):**

```typescript
// Using expect-type or similar
import { expectTypeOf } from 'expect-type';

type ExtractId<T> = T extends { id: infer I } ? I : never;

// Compile-time type tests
expectTypeOf<ExtractId<{ id: string }>>().toEqualTypeOf<string>();
expectTypeOf<ExtractId<{ id: number }>>().toEqualTypeOf<number>();
expectTypeOf<ExtractId<{ name: string }>>().toEqualTypeOf<never>();
```

Reference: [expect-type](https://github.com/mmkal/expect-type)
