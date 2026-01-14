---
title: Enable exactOptionalPropertyTypes
impact: LOW-MEDIUM
impactDescription: distinguishes undefined from missing properties
tags: config, exactOptionalPropertyTypes, optional, undefined
---

## Enable exactOptionalPropertyTypes

This flag distinguishes between a property being missing vs. explicitly set to `undefined`. Prevents bugs where `undefined` values overwrite defaults.

**Incorrect (without exactOptionalPropertyTypes):**

```typescript
// tsconfig.json - exactOptionalPropertyTypes: false (default)

interface User {
  name: string;
  nickname?: string;  // Optional property
}

const user: User = {
  name: 'John',
  nickname: undefined  // Allowed! But semantically different from missing
};

// Problem: spreading overwrites defaults
const defaults = { nickname: 'Anonymous' };
const merged = { ...defaults, ...user };
// merged.nickname is undefined, not 'Anonymous'!
```

**Correct (with exactOptionalPropertyTypes):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "exactOptionalPropertyTypes": true,
    "strict": true  // Required for this to work
  }
}

interface User {
  name: string;
  nickname?: string;  // Can be string or missing, NOT undefined
}

const user: User = {
  name: 'John',
  nickname: undefined  // Error! Type 'undefined' is not assignable
};

// Correct ways to create User
const user1: User = { name: 'John' };  // nickname missing - OK
const user2: User = { name: 'John', nickname: 'Johnny' };  // OK

// If you need to allow explicit undefined
interface UserWithNullable {
  name: string;
  nickname?: string | undefined;  // Explicitly allow undefined
}
```

**When to use:**
- APIs where missing vs. undefined have different meanings (PATCH endpoints)
- Configuration objects with defaults
- Database models where null/undefined semantics matter

Reference: [TypeScript exactOptionalPropertyTypes](https://www.typescriptlang.org/tsconfig#exactOptionalPropertyTypes)
