---
title: Exhaustive Checks with Never
impact: MEDIUM
impactDescription: catches 100% of missed switch cases at compile time when union variants change
tags: pattern, exhaustive, never, switch, discriminated-unions
---

## Exhaustive Checks with Never

When you add a new variant to a union type, existing switch statements silently ignore it. The exhaustive check pattern uses `never` to force compile-time errors when a case is missing. This catches 100% of forgotten cases instead of discovering them in production.

**Incorrect (default case hides missing variants):**

```typescript
// PROBLEM: Adding a new status silently uses the default case
// You won't know it's broken until a user reports wrong behavior

// types.ts
type OrderStatus = 'pending' | 'processing' | 'shipped' | 'delivered';

// order-display.ts
function getStatusBadge(status: OrderStatus): string {
  switch (status) {
    case 'pending':
      return '🟡 Pending';
    case 'processing':
      return '🔵 Processing';
    case 'shipped':
      return '📦 Shipped';
    default:
      return '⚪ Unknown'; // Catches delivered + any future statuses
  }
}

// Later: Add 'cancelled' and 'refunded' to OrderStatus
type OrderStatus = 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | 'refunded';

// getStatusBadge still compiles! But now:
// - 'delivered' shows "Unknown" (bug!)
// - 'cancelled' shows "Unknown" (bug!)
// - 'refunded' shows "Unknown" (bug!)
// No compile error - these bugs ship to production
```

**Correct (exhaustive check catches all missing cases):**

```typescript
// SOLUTION: Use never in default to force exhaustiveness
// If any case is missing, TypeScript reports a compile error

// utils/exhaustive.ts
function assertNever(value: never, message?: string): never {
  throw new Error(message ?? `Unexpected value: ${JSON.stringify(value)}`);
}

// types.ts
type OrderStatus = 'pending' | 'processing' | 'shipped' | 'delivered';

// order-display.ts
function getStatusBadge(status: OrderStatus): string {
  switch (status) {
    case 'pending':
      return '🟡 Pending';
    case 'processing':
      return '🔵 Processing';
    case 'shipped':
      return '📦 Shipped';
    case 'delivered':
      return '✅ Delivered';
    default:
      // If status is not 'never', a case is missing
      return assertNever(status);
  }
}

// Now add 'cancelled' and 'refunded':
type OrderStatus = 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | 'refunded';

// getStatusBadge immediately shows compile error:
// Error: Argument of type '"cancelled" | "refunded"' is not assignable to parameter of type 'never'

// Fix: Add the missing cases
function getStatusBadge(status: OrderStatus): string {
  switch (status) {
    case 'pending':     return '🟡 Pending';
    case 'processing':  return '🔵 Processing';
    case 'shipped':     return '📦 Shipped';
    case 'delivered':   return '✅ Delivered';
    case 'cancelled':   return '❌ Cancelled';  // New
    case 'refunded':    return '💰 Refunded';   // New
    default:
      return assertNever(status);
  }
}
```

**Alternative (satisfies never for inline checks):**

```typescript
// For simple switches, use satisfies never inline
function getStatusColor(status: OrderStatus): string {
  switch (status) {
    case 'pending':     return 'yellow';
    case 'processing':  return 'blue';
    case 'shipped':     return 'purple';
    case 'delivered':   return 'green';
    case 'cancelled':   return 'red';
    case 'refunded':    return 'gray';
  }
  // No default needed - TypeScript infers exhaustiveness
  // If you add a case, you get: "Not all code paths return a value"

  // Or be explicit:
  status satisfies never; // Compile error if any case missing
}
```

**When to use:** Use exhaustive checks on all switches over discriminated unions, especially status enums, event types, action types (Redux), and any union that may grow over time.

**When NOT to use:** Skip exhaustive checks when handling a subset of cases is intentional, such as logging only error events or processing only certain action types.

Reference: [TypeScript Exhaustiveness Checking](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#exhaustiveness-checking)
