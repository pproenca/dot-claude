---
title: Prefer Generics Over Any
impact: MEDIUM-HIGH
impactDescription: maintains type safety with reusable code
tags: api, generics, type-parameters, constraints
---

## Prefer Generics Over Any

Use generics to maintain type safety while enabling reusable code.

**Incorrect (any for flexibility):**

```typescript
function first(arr: any[]): any {
  return arr[0];
}

const num = first([1, 2, 3]); // Type is any
const str = first(['a', 'b']); // Type is any
```

**Correct (generic constraints):**

```typescript
function first<T>(arr: T[]): T | undefined {
  return arr[0];
}

const num = first([1, 2, 3]); // Type is number | undefined
const str = first(['a', 'b']); // Type is string | undefined

// With constraints
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}

longest('hello', 'world'); // Works with strings
longest([1, 2], [1, 2, 3]); // Works with arrays
```

Reference: [TypeScript Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)
