---
title: Leverage Discriminated Unions
impact: CRITICAL
impactDescription: makes impossible states unrepresentable
tags: safety, unions, discriminated, pattern-matching
---

## Leverage Discriminated Unions

Use a common property (discriminant) to create type-safe unions that TypeScript can narrow automatically.

**Incorrect (ambiguous union):**

```typescript
interface ApiResponse {
  data?: User;
  error?: string;
  loading?: boolean;
}

function handleResponse(response: ApiResponse) {
  // Can't tell which state we're in
  if (response.data) {
    console.log(response.data.name);
  }
  // What if data AND error are both set?
}
```

**Correct (discriminated union):**

```typescript
type ApiResponse =
  | { status: 'loading' }
  | { status: 'success'; data: User }
  | { status: 'error'; error: string };

function handleResponse(response: ApiResponse) {
  switch (response.status) {
    case 'loading':
      return <Spinner />;
    case 'success':
      return <UserCard user={response.data} />;
    case 'error':
      return <Error message={response.error} />;
  }
}
```

Reference: [TypeScript Discriminated Unions](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#discriminated-unions)
