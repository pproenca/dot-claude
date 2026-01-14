---
title: Prefer Objects Over Long Parameter Lists
impact: MEDIUM-HIGH
impactDescription: improves readability and extensibility
tags: api, parameters, objects, options
---

## Prefer Objects Over Long Parameter Lists

Use object parameters for functions with many options.

**Incorrect (long parameter list):**

```typescript
function createUser(
  name: string,
  email: string,
  age?: number,
  isAdmin?: boolean,
  department?: string,
  startDate?: Date
) {
  // Which parameter is which?
}

createUser('John', 'john@example.com', undefined, true, undefined, new Date());
```

**Correct (options object):**

```typescript
interface CreateUserOptions {
  name: string;
  email: string;
  age?: number;
  isAdmin?: boolean;
  department?: string;
  startDate?: Date;
}

function createUser(options: CreateUserOptions) {
  const { name, email, isAdmin = false } = options;
  // Clear what each value is
}

createUser({
  name: 'John',
  email: 'john@example.com',
  isAdmin: true,
  startDate: new Date(),
});
```

Reference: [TypeScript Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)
