---
title: Exhaustive Checks with Never
impact: MEDIUM
impactDescription: catches missing switch cases at compile time
tags: pattern, exhaustive, never, switch
---

## Exhaustive Checks with Never

Use `never` to ensure switch statements handle all cases.

**Incorrect (default swallows new cases):**

```typescript
type Status = 'pending' | 'active' | 'completed';

function getStatusColor(status: Status): string {
  switch (status) {
    case 'pending':
      return 'yellow';
    case 'active':
      return 'blue';
    default:
      return 'gray'; // New statuses silently get gray
  }
}
```

**Correct (exhaustive check):**

```typescript
function assertNever(x: never): never {
  throw new Error(`Unexpected value: ${x}`);
}

function getStatusColor(status: Status): string {
  switch (status) {
    case 'pending':
      return 'yellow';
    case 'active':
      return 'blue';
    case 'completed':
      return 'green';
    default:
      return assertNever(status); // Error if case missing
  }
}
```

Reference: [TypeScript Exhaustiveness Checking](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#exhaustiveness-checking)
