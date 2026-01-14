---
title: Use Branded Types
impact: MEDIUM-HIGH
impactDescription: prevents ID confusion bugs, catches type-safe violations at compile time
tags: api, branded, nominal, type-safety, opaque
---

## Use Branded Types

TypeScript uses structural typing - two types with the same shape are interchangeable. This causes bugs when you accidentally pass a `UserId` where an `OrderId` is expected. Branded types add a unique marker that prevents this confusion at compile time.

**Incorrect (structural typing allows ID confusion):**

```typescript
// PROBLEM: Type aliases are just aliases - they don't prevent misuse
// UserId and OrderId are both strings, so TypeScript treats them as identical
// This causes silent data corruption bugs in production

// types.ts
type UserId = string;
type OrderId = string;
type ProductId = string;

// user-service.ts
function getUser(id: UserId): User {
  return database.users.findOne({ id });
}

function getOrder(id: OrderId): Order {
  return database.orders.findOne({ id });
}

function getProduct(id: ProductId): Product {
  return database.products.findOne({ id });
}

// consumer.ts - BUG: Wrong ID passed, compiles fine
const userId: UserId = 'user_abc123';
const orderId: OrderId = 'order_xyz789';

// These are all bugs that TypeScript doesn't catch:
const user = getUser(orderId);      // Passing OrderId as UserId - compiles!
const order = getOrder(userId);     // Passing UserId as OrderId - compiles!
const product = getProduct(userId); // Passing UserId as ProductId - compiles!

// Result: Wrong data returned, possibly data corruption or security issues
// All because TypeScript sees them as the same type: string
```

**Correct (branded types prevent confusion):**

```typescript
// SOLUTION: Branded types add a unique phantom property
// TypeScript sees them as different types even though runtime is identical

// types.ts
type Brand<K, T> = K & { readonly __brand: T };

type UserId = Brand<string, 'UserId'>;
type OrderId = Brand<string, 'OrderId'>;
type ProductId = Brand<string, 'ProductId'>;

// Factory functions to create branded values
function createUserId(id: string): UserId {
  // Validate format if needed
  if (!id.startsWith('user_')) {
    throw new Error('Invalid user ID format');
  }
  return id as UserId;
}

function createOrderId(id: string): OrderId {
  if (!id.startsWith('order_')) {
    throw new Error('Invalid order ID format');
  }
  return id as OrderId;
}

function createProductId(id: string): ProductId {
  if (!id.startsWith('prod_')) {
    throw new Error('Invalid product ID format');
  }
  return id as ProductId;
}

// user-service.ts - functions require correct branded types
function getUser(id: UserId): User {
  return database.users.findOne({ id });
}

function getOrder(id: OrderId): Order {
  return database.orders.findOne({ id });
}

// consumer.ts - TypeScript catches ID confusion
const userId = createUserId('user_abc123');
const orderId = createOrderId('order_xyz789');

const user = getUser(userId);   // OK - correct type
const order = getOrder(orderId); // OK - correct type

// These are now compile errors:
const user2 = getUser(orderId);
// Error: Argument of type 'OrderId' is not assignable to parameter of type 'UserId'

const order2 = getOrder(userId);
// Error: Argument of type 'UserId' is not assignable to parameter of type 'OrderId'
```

**Alternative (using symbols for branded types):**

```typescript
// Symbol-based brands are more unique and don't pollute intellisense
declare const UserIdBrand: unique symbol;
declare const OrderIdBrand: unique symbol;

type UserId = string & { readonly [UserIdBrand]: typeof UserIdBrand };
type OrderId = string & { readonly [OrderIdBrand]: typeof OrderIdBrand };

// Or use a library like ts-brand or zod:
import { z } from 'zod';

const UserId = z.string().brand('UserId');
type UserId = z.infer<typeof UserId>;

const OrderId = z.string().brand('OrderId');
type OrderId = z.infer<typeof OrderId>;

// Zod provides runtime validation + branded types in one
const userId = UserId.parse('user_123'); // Validated and branded
```

**When to use:** Use branded types for any IDs that could be confused (user/order/product IDs), and for values with semantic meaning (email addresses, URLs, currency amounts).

**When NOT to use:** Don't brand primitive types that truly are interchangeable. If a function accepts any string, don't require a branded string.

Reference: [Nominal Typing in TypeScript](https://basarat.gitbook.io/typescript/main-1/nominaltyping)
