---
title: Avoid Excessive Type Complexity
impact: CRITICAL
impactDescription: prevents compiler slowdown
tags: perf, recursive, complexity, compilation
---

## Avoid Excessive Type Complexity

Complex recursive types slow down the compiler. Simplify when possible or add depth limits.

**Incorrect (unbounded recursive type):**

```typescript
// This can make the compiler hang
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object
    ? DeepReadonly<T[K]>
    : T[K];
};

type Deeply = DeepReadonly<HugeNestedType>; // Very slow
```

**Correct (bounded recursion):**

```typescript
// Add depth limit
type DeepReadonly<T, Depth extends number = 5> = Depth extends 0
  ? T
  : {
      readonly [K in keyof T]: T[K] extends object
        ? DeepReadonly<T[K], Decrement[Depth]>
        : T[K];
    };

type Decrement = [never, 0, 1, 2, 3, 4, 5];

// Or use built-in Readonly for shallow cases
type Simple = Readonly<MyType>;
```

Reference: [TypeScript Performance](https://github.com/microsoft/TypeScript/wiki/Performance)
