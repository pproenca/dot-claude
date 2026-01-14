---
title: Leverage Utility Types
impact: MEDIUM
impactDescription: reduces type duplication
tags: pattern, utility-types, partial, pick, omit
---

## Leverage Utility Types

Use TypeScript's built-in utility types for common transformations.

**Incorrect (manual type definitions):**

```typescript
interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
}

interface UserUpdate {
  name?: string;
  email?: string;
}

interface UserWithoutId {
  name: string;
  email: string;
  createdAt: Date;
}
```

**Correct (utility types):**

```typescript
interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
}

type UserUpdate = Partial<Pick<User, 'name' | 'email'>>;
type UserWithoutId = Omit<User, 'id'>;
type UserKeys = keyof User; // 'id' | 'name' | 'email' | 'createdAt'
type ReadonlyUser = Readonly<User>;
```

Reference: [TypeScript Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)
