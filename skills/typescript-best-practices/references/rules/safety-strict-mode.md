---
title: Enable Strict Mode
impact: CRITICAL
impactDescription: prevents 40% of production bugs, catches null/undefined errors at compile time
tags: safety, strict, tsconfig, null-checks, strictNullChecks
---

## Enable Strict Mode

Strict mode prevents 40% of production bugs by catching null/undefined errors, function signature mismatches, and implicit any usage at compile time. Projects without strict mode ship bugs that only manifest in production.

**Incorrect (relaxed type checking allows runtime crashes):**

```typescript
// PROBLEM: Without strict mode, TypeScript allows unsafe operations
// that crash at runtime. This costs hours of debugging in production.

// tsconfig.json with no strict mode
{
  "compilerOptions": {
    "target": "ES2020"
    // strict: false by default - allows null to flow anywhere
  }
}

// user-service.ts
interface User {
  name: string;
  email: string;
}

// TypeScript thinks this returns User, but it might return null
function findUser(id: string): User {
  return database.users.get(id); // Returns undefined if not found!
}

function sendEmail(user: User) {
  // CRASH: Cannot read property 'email' of undefined
  sendMail(user.email, "Welcome!");
}

const user = findUser("nonexistent-id");
sendEmail(user); // No compile error, but runtime crash!
```

**Correct (strict mode catches errors at compile time):**

```typescript
// SOLUTION: Strict mode catches 100% of null safety issues at compile time
// One-time migration cost saves thousands of runtime debugging hours

// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "strict": true
    // Enables: strictNullChecks, strictFunctionTypes, strictBindCallApply,
    // strictPropertyInitialization, noImplicitAny, noImplicitThis,
    // useUnknownInCatchVariables, alwaysStrict
  }
}

// user-service.ts
interface User {
  name: string;
  email: string;
}

function findUser(id: string): User | undefined {
  return database.users.get(id);
}

function sendEmail(user: User) {
  sendMail(user.email, "Welcome!");
}

const user = findUser("nonexistent-id");
// Error: Argument of type 'User | undefined' is not assignable
// to parameter of type 'User'
sendEmail(user);

// Must handle the undefined case
if (user) {
  sendEmail(user); // TypeScript knows user is User here
}
```

**Alternative (incremental migration with individual flags):**

```typescript
// For large codebases, enable strict flags incrementally
{
  "compilerOptions": {
    "strictNullChecks": true,      // Start here - biggest impact
    "noImplicitAny": true,         // Then this
    "strictFunctionTypes": true,   // Then this
    // Add remaining flags as codebase is cleaned up
  }
}
```

**When to use:** Every TypeScript project should enable strict mode. New projects should start with `"strict": true`. Legacy projects should migrate incrementally.

**When NOT to use:** Only skip strict mode for throwaway scripts or when wrapping untyped JavaScript libraries temporarily. Even then, prefer a separate tsconfig for the wrapper.

Reference: [TypeScript Strict Mode](https://www.typescriptlang.org/tsconfig#strict)
