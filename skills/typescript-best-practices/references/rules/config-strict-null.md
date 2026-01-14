---
title: Configure Strict Null Checks
impact: LOW-MEDIUM
impactDescription: catches null/undefined errors at compile time
tags: config, strictNullChecks, null, undefined
---

## Configure Strict Null Checks

Enable strictNullChecks (part of strict mode) to catch null/undefined errors.

**Incorrect (disabled null checks):**

```typescript
// Compiles but crashes at runtime
function getLength(str: string) {
  return str.length;
}

getLength(null); // Runtime error: Cannot read property 'length' of null
```

**Correct (strict null checks):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "strictNullChecks": true
    // Or just "strict": true
  }
}

function getLength(str: string | null): number {
  if (str === null) {
    return 0;
  }
  return str.length; // str is narrowed to string
}
```

Reference: [TypeScript strictNullChecks](https://www.typescriptlang.org/tsconfig#strictNullChecks)
