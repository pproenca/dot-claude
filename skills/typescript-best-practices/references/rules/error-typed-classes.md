---
title: Use Typed Error Classes
impact: HIGH
impactDescription: enables programmatic error handling
tags: error, classes, typed, custom
---

## Use Typed Error Classes

Create custom error classes with typed properties for structured error handling.

**Incorrect (plain Error objects):**

```typescript
throw new Error('User not found: 123');
// Can't programmatically extract the user ID
// Can't distinguish from other errors

try {
  await createUser(data);
} catch (e) {
  if (e.message.includes('duplicate')) {
    // Fragile string matching
  }
}
```

**Correct (typed error classes):**

```typescript
class UserNotFoundError extends Error {
  readonly code = 'USER_NOT_FOUND' as const;

  constructor(public readonly userId: string) {
    super(`User not found: ${userId}`);
    this.name = 'UserNotFoundError';
  }
}

class DuplicateEmailError extends Error {
  readonly code = 'DUPLICATE_EMAIL' as const;

  constructor(public readonly email: string) {
    super(`Email already exists: ${email}`);
    this.name = 'DuplicateEmailError';
  }
}

type UserError = UserNotFoundError | DuplicateEmailError;

function isUserError(error: unknown): error is UserError {
  return error instanceof UserNotFoundError ||
         error instanceof DuplicateEmailError;
}
```

Reference: [Custom Error Classes](https://www.typescriptlang.org/docs/handbook/2/classes.html#extends-clauses)
