---
title: Use Readonly Parameters
impact: MEDIUM-HIGH
impactDescription: prevents accidental mutation
tags: api, readonly, immutable, parameters
---

## Use Readonly Parameters

Mark parameters as readonly to prevent accidental mutation.

**Incorrect (mutable parameters):**

```typescript
function processItems(items: string[]) {
  items.push('extra'); // Mutates caller's array!
  return items.map((s) => s.toUpperCase());
}

const original = ['a', 'b'];
processItems(original);
console.log(original); // ['a', 'b', 'extra'] - surprise!
```

**Correct (readonly parameters):**

```typescript
function processItems(items: readonly string[]): string[] {
  // items.push('extra'); // Error: Property 'push' does not exist
  return items.map((s) => s.toUpperCase());
}

const original = ['a', 'b'];
const result = processItems(original);
console.log(original); // ['a', 'b'] - unchanged
```

Reference: [TypeScript Readonly](https://www.typescriptlang.org/docs/handbook/2/objects.html#readonly-properties)
