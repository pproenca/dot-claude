---
title: Avoid Type Assertions
impact: CRITICAL
impactDescription: prevents runtime type mismatches
tags: safety, assertions, as, narrowing
---

## Avoid Type Assertions

Type assertions (`as`) bypass type checking. Narrow types instead using proper control flow.

**Incorrect (assertion without validation):**

```typescript
const input = document.getElementById('email') as HTMLInputElement;
input.value = 'test@example.com'; // Crashes if element doesn't exist

const response = await fetch('/api/user');
const user = await response.json() as User; // No validation
```

**Correct (validated narrowing):**

```typescript
const input = document.getElementById('email');
if (input instanceof HTMLInputElement) {
  input.value = 'test@example.com';
}

const response = await fetch('/api/user');
const data: unknown = await response.json();
const user = validateUser(data); // Throws if invalid

function validateUser(data: unknown): User {
  if (!isUser(data)) {
    throw new Error('Invalid user data');
  }
  return data;
}
```

Reference: [TypeScript Type Assertions](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-assertions)
