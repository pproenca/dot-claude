---
title: Prefer Named Exports
impact: MEDIUM
impactDescription: enables better refactoring and tree-shaking
tags: module, exports, named, imports
---

## Prefer Named Exports

Named exports provide better refactoring support and prevent naming conflicts.

**Incorrect (default exports):**

```typescript
// user.ts
export default class User { }

// consumer.ts
import User from './user'; // Can be named anything
import MyUser from './user'; // Same import, different name
```

**Correct (named exports):**

```typescript
// user.ts
export class User { }

// consumer.ts
import { User } from './user'; // Must use correct name
// import { User as MyUser } from './user'; // Explicit rename
```

Reference: [TypeScript Modules](https://www.typescriptlang.org/docs/handbook/2/modules.html)
