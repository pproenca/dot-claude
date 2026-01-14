---
title: Leverage Discriminated Unions
impact: CRITICAL
impactDescription: makes impossible states unrepresentable, eliminates 100% of state confusion bugs
tags: safety, unions, discriminated, pattern-matching, state-management
---

## Leverage Discriminated Unions

Discriminated unions make impossible states unrepresentable at the type level. Instead of checking `if (data && !error && !loading)`, the type system guarantees only valid state combinations exist. This eliminates entire classes of bugs where conflicting state flags cause undefined behavior.

**Incorrect (ambiguous union allows impossible states):**

```typescript
// PROBLEM: Optional properties allow impossible states like
// { data: user, error: "failed", loading: true } - what does that even mean?
// This pattern causes ~15% of frontend state bugs.

// api-response.ts - tanstack-query style response
interface ApiResponse<T> {
  data?: T;
  error?: string;
  loading?: boolean;
  // BUG: Can have data AND error AND loading all set simultaneously
}

interface User {
  id: string;
  name: string;
  email: string;
}

function UserProfile({ response }: { response: ApiResponse<User> }) {
  // Which condition wins? What if data AND error are both truthy?
  if (response.loading) {
    return <Spinner />;
  }

  if (response.error) {
    // BUG: What if response.data is also set? Should we show it?
    return <ErrorMessage message={response.error} />;
  }

  if (response.data) {
    return <UserCard user={response.data} />;
  }

  // What state is this? None of the above? Silent failure.
  return null;
}

// This compiles but makes no sense:
const badState: ApiResponse<User> = {
  data: { id: '1', name: 'John', email: 'john@example.com' },
  error: 'User not found',
  loading: true,
};
```

**Correct (discriminated union - only valid states compile):**

```typescript
// SOLUTION: Discriminated union guarantees exactly one state at a time
// TypeScript narrows types automatically based on the discriminant

// api-response.ts
type ApiResponse<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: string; retryCount: number };

interface User {
  id: string;
  name: string;
  email: string;
}

function UserProfile({ response }: { response: ApiResponse<User> }) {
  switch (response.status) {
    case 'idle':
      return <Placeholder />;

    case 'loading':
      return <Spinner />;

    case 'success':
      // TypeScript knows response.data exists here
      return <UserCard user={response.data} />;

    case 'error':
      // TypeScript knows response.error and retryCount exist here
      return (
        <ErrorMessage
          message={response.error}
          retryCount={response.retryCount}
        />
      );
  }
}

// Impossible states are now compile errors:
const badState: ApiResponse<User> = {
  status: 'success',
  data: { id: '1', name: 'John', email: 'john@example.com' },
  error: 'User not found', // Error: 'error' does not exist on success state
};
```

**Alternative (using literal types for simpler unions):**

```typescript
// For simpler state machines, literal types work well
type ConnectionState =
  | { type: 'disconnected' }
  | { type: 'connecting'; attempt: number }
  | { type: 'connected'; socket: WebSocket }
  | { type: 'reconnecting'; lastError: Error; attempt: number };

// Works great with exhaustive checks
function getStatusMessage(state: ConnectionState): string {
  switch (state.type) {
    case 'disconnected':
      return 'Not connected';
    case 'connecting':
      return `Connecting (attempt ${state.attempt})...`;
    case 'connected':
      return 'Connected';
    case 'reconnecting':
      return `Reconnecting after: ${state.lastError.message}`;
  }
}
```

**When to use:** Use discriminated unions for any state that has mutually exclusive variants: API responses, form states, authentication states, WebSocket connections, file upload progress, etc.

**When NOT to use:** For simple on/off toggles, a boolean is fine. Discriminated unions add value when there are 3+ states or when states carry different associated data.

Reference: [TypeScript Discriminated Unions](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#discriminated-unions)
