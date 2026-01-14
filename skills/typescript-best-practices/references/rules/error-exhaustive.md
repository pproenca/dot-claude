---
title: Exhaustive Error Handling
impact: HIGH
impactDescription: catches missing error cases at compile time
tags: error, exhaustive, never, switch
---

## Exhaustive Error Handling

Use the `never` type to ensure all error cases are handled.

**Incorrect (missing error cases):**

```typescript
type ApiError =
  | { type: 'not_found' }
  | { type: 'unauthorized' }
  | { type: 'server_error' };

function handleError(error: ApiError): string {
  switch (error.type) {
    case 'not_found':
      return 'Resource not found';
    case 'unauthorized':
      return 'Please log in';
    // Forgot server_error - no compile error!
  }
}
```

**Correct (exhaustive check with never):**

```typescript
function assertNever(value: never): never {
  throw new Error(`Unhandled case: ${JSON.stringify(value)}`);
}

function handleError(error: ApiError): string {
  switch (error.type) {
    case 'not_found':
      return 'Resource not found';
    case 'unauthorized':
      return 'Please log in';
    case 'server_error':
      return 'Server error, please try again';
    default:
      return assertNever(error); // Compile error if case missing
  }
}
```

Reference: [TypeScript Exhaustiveness Checking](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#exhaustiveness-checking)
