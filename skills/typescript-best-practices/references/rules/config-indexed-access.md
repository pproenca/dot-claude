---
title: Enable noUncheckedIndexedAccess
impact: LOW-MEDIUM
impactDescription: catches undefined array access
tags: config, noUncheckedIndexedAccess, arrays, safety
---

## Enable noUncheckedIndexedAccess

Enable this flag to make array/object indexing return `T | undefined`.

**Incorrect (assumed index access):**

```typescript
// tsconfig.json - noUncheckedIndexedAccess: false (default)
const arr = [1, 2, 3];
const item = arr[10]; // Type is number, but value is undefined!

const obj: Record<string, string> = {};
const value = obj['missing']; // Type is string, but value is undefined!
```

**Correct (checked index access):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "noUncheckedIndexedAccess": true
  }
}

const arr = [1, 2, 3];
const item = arr[10]; // Type is number | undefined

if (item !== undefined) {
  console.log(item.toFixed(2)); // Safe
}
```

Reference: [TypeScript noUncheckedIndexedAccess](https://www.typescriptlang.org/tsconfig#noUncheckedIndexedAccess)
