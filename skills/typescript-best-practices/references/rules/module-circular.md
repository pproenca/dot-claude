---
title: Avoid Circular Dependencies
impact: MEDIUM
impactDescription: prevents initialization issues
tags: module, circular, dependencies, architecture
---

## Avoid Circular Dependencies

Circular imports cause initialization issues and make code harder to understand.

**Incorrect (circular dependency):**

```typescript
// user.ts
import { Order } from './order';
export class User {
  orders: Order[] = [];
}

// order.ts
import { User } from './user';
export class Order {
  user: User; // Circular!
}
```

**Correct (dependency inversion):**

```typescript
// types.ts - shared interfaces
export interface IUser {
  id: string;
  name: string;
}

export interface IOrder {
  id: string;
  userId: string;
}

// user.ts
import type { IOrder } from './types';
export class User implements IUser {
  orders: IOrder[] = [];
}

// order.ts
import type { IUser } from './types';
export class Order implements IOrder {
  userId: string;
}
```

Reference: [Circular Dependencies in TypeScript](https://www.typescriptlang.org/docs/handbook/project-references.html)
