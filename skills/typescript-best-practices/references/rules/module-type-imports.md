---
title: Use Type-Only Imports
impact: MEDIUM
impactDescription: reduces bundle size via type erasure
tags: module, type-only, imports, tree-shaking
---

## Use Type-Only Imports

Use `import type` for types to enable better tree-shaking.

**Incorrect (mixing value and type imports):**

```typescript
import { User, UserService } from './user';

// If User is only used as a type, it still gets bundled
function processUser(user: User) {
  // User only used as type annotation
}
```

**Correct (separate type imports):**

```typescript
import type { User } from './user';
import { UserService } from './user';

// Or combined with type modifier
import { type User, UserService } from './user';

function processUser(user: User) {
  // User is erased at compile time
}
```

Reference: [TypeScript Type-Only Imports](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-8.html#type-only-imports-and-export)
