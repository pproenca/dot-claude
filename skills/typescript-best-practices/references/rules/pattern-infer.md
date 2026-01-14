---
title: Use Infer for Type Extraction
impact: MEDIUM
impactDescription: extracts types from complex structures
tags: pattern, infer, conditional, extraction
---

## Use Infer for Type Extraction

Use `infer` in conditional types to extract parts of types.

**Incorrect (manual type extraction):**

```typescript
// Have to manually define return types
type GetUserReturn = User;
type GetOrdersReturn = Order[];

function getUser(): Promise<User> { /* ... */ }
function getOrders(): Promise<Order[]> { /* ... */ }
```

**Correct (infer keyword):**

```typescript
// Extract return type from Promise
type Awaited<T> = T extends Promise<infer U> ? U : T;

// Extract function return type
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

// Extract array element type
type ElementType<T> = T extends (infer E)[] ? E : never;

type UserResult = Awaited<ReturnType<typeof getUser>>; // User
type OrderElement = ElementType<Order[]>; // Order
```

Reference: [TypeScript Conditional Types](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html#inferring-within-conditional-types)
