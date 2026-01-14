---
title: Use Type-Only Imports
impact: MEDIUM
impactDescription: eliminates type-only imports from runtime bundle, enables perfect tree-shaking
tags: module, type-only, imports, tree-shaking, verbatimModuleSyntax
---

## Use Type-Only Imports

Regular imports include types in your runtime bundle even when they're only used for type annotations. `import type` tells TypeScript and bundlers to completely erase these imports. This reduces bundle size and prevents circular dependency issues.

**Incorrect (type-only imports pollute runtime):**

```typescript
// PROBLEM: TypeScript can't tell if User is used at runtime or just for types
// The bundler may include the entire user module for one type annotation

// user.ts - large module with runtime code + types
export interface User {
  id: string;
  name: string;
  email: string;
}

export class UserService {
  async getUser(id: string): Promise<User> { /* ... */ }
  async updateUser(id: string, data: Partial<User>): Promise<User> { /* ... */ }
  // ... 500 lines of implementation code
}

export const USER_CACHE_TTL = 3600;

// consumer.ts - only needs User type
import { User, UserService } from './user';
// PROBLEM: Imports entire module (~500 lines) for one type annotation

function displayUser(user: User) {
  // User is only used as a type - never called at runtime
  console.log(`${user.name} (${user.email})`);
}

// But now user.ts is in the bundle because import syntax is ambiguous
// Result: Larger bundle, slower startup, potential circular import issues
```

**Correct (type-only imports are erased):**

```typescript
// SOLUTION: import type tells TypeScript this is type-only
// Bundlers completely erase these imports from output

// consumer.ts - import types separately
import type { User } from './user';
import { UserService } from './user';

function displayUser(user: User) {
  console.log(`${user.name} (${user.email})`);
}

// Alternative: inline type modifier (TS 4.5+)
import { type User, UserService } from './user';

// After compilation, only UserService import remains
// User import is completely erased - zero runtime overhead
```

**Alternative (verbatimModuleSyntax for strict separation):**

```typescript
// tsconfig.json - enforce explicit type imports
{
  "compilerOptions": {
    "verbatimModuleSyntax": true
    // Forces you to use `import type` for type-only imports
    // Errors if you use regular import for types
  }
}

// With verbatimModuleSyntax enabled:
import { User } from './user';  // Error if User is type-only!

// Must be explicit:
import type { User } from './user';  // OK - clearly type-only

// Re-exporting types also needs type modifier:
export type { User } from './user';  // Type-only re-export
```

**When to use:** Always use `import type` for interfaces, type aliases, and types that are never used at runtime. Enable `verbatimModuleSyntax` in new projects to enforce this pattern.

**When NOT to use:** Don't use `import type` for classes or values you construct/call at runtime. Even if you only use a class as a type annotation, you need a regular import if you also use `instanceof`.

Reference: [TypeScript Type-Only Imports](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-8.html#type-only-imports-and-export)
