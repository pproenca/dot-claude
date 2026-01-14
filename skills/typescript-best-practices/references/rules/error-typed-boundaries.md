---
title: Type Error Boundaries
impact: HIGH
impactDescription: distinguishes error types at compile time
tags: error, boundaries, typed, classes
---

## Type Error Boundaries

Create typed error boundaries that handle specific error types.

**Incorrect (catch-all error handling):**

```typescript
async function fetchUser(id: string) {
  try {
    const response = await fetch(`/api/users/${id}`);
    return await response.json();
  } catch (e) {
    // What kind of error? Network? Parse? 404?
    console.error('Something went wrong');
  }
}
```

**Correct (typed error boundaries):**

```typescript
class NetworkError extends Error {
  constructor(public readonly status: number) {
    super(`Network error: ${status}`);
  }
}

class ValidationError extends Error {
  constructor(public readonly fields: string[]) {
    super(`Validation failed: ${fields.join(', ')}`);
  }
}

type FetchError = NetworkError | ValidationError;

async function fetchUser(id: string): Promise<Result<User, FetchError>> {
  const response = await fetch(`/api/users/${id}`);

  if (!response.ok) {
    return { ok: false, error: new NetworkError(response.status) };
  }

  const data = await response.json();
  const validation = validateUser(data);

  if (!validation.valid) {
    return { ok: false, error: new ValidationError(validation.errors) };
  }

  return { ok: true, value: data };
}
```

Reference: [TypeScript Error Handling](https://www.typescriptlang.org/docs/handbook/2/classes.html)
