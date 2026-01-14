---
title: Use Branded Types
impact: MEDIUM-HIGH
impactDescription: prevents accidental type confusion
tags: api, branded, nominal, type-safety
---

## Use Branded Types

Use branded types for nominal typing when structural typing isn't safe enough.

**Incorrect (type aliases are structural):**

```typescript
type UserId = string;
type OrderId = string;

function getUser(id: UserId) { /* ... */ }
function getOrder(id: OrderId) { /* ... */ }

const userId: UserId = 'user_123';
const orderId: OrderId = 'order_456';

getUser(orderId); // No error! Both are just strings
```

**Correct (branded types):**

```typescript
type Brand<K, T> = K & { __brand: T };

type UserId = Brand<string, 'UserId'>;
type OrderId = Brand<string, 'OrderId'>;

function createUserId(id: string): UserId {
  return id as UserId;
}

function createOrderId(id: string): OrderId {
  return id as OrderId;
}

function getUser(id: UserId) { /* ... */ }

const userId = createUserId('user_123');
const orderId = createOrderId('order_456');

getUser(userId); // OK
getUser(orderId); // Error: OrderId is not assignable to UserId
```

Reference: [Nominal Typing in TypeScript](https://basarat.gitbook.io/typescript/main-1/nominaltyping)
