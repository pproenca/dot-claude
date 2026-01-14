---
title: Enable noUncheckedIndexedAccess
impact: LOW-MEDIUM
impactDescription: catches array out-of-bounds errors that cause 5-10% of runtime exceptions
tags: config, noUncheckedIndexedAccess, arrays, safety, undefined
---

## Enable noUncheckedIndexedAccess

By default, TypeScript assumes array/object indexing always succeeds. `arr[10]` returns `number` even if the array has 3 elements. This causes "Cannot read property of undefined" errors - the most common JavaScript runtime error. Enabling `noUncheckedIndexedAccess` adds `| undefined` to all indexed access.

**Incorrect (TypeScript lies about array access):**

```typescript
// PROBLEM: TypeScript says arr[10] is number, but it's actually undefined
// This causes ~5-10% of production runtime errors

// Without noUncheckedIndexedAccess (default)
const users = ['Alice', 'Bob', 'Charlie'];

// TypeScript says: string
// Reality: undefined
const user = users[10];
console.log(user.toUpperCase()); // CRASH: Cannot read property 'toUpperCase' of undefined

// Same problem with Record types
const cache: Record<string, { data: string }> = {};
const entry = cache['nonexistent'];
console.log(entry.data); // CRASH: Cannot read property 'data' of undefined

// And with for...in loops
const config: { [key: string]: string } = { host: 'localhost' };
for (const key in config) {
  const value = config[key];  // TypeScript: string, Reality: could be undefined
  console.log(value.trim());  // May crash
}
```

**Correct (TypeScript requires undefined checks):**

```typescript
// SOLUTION: Enable noUncheckedIndexedAccess to force undefined handling
// tsconfig.json
{
  "compilerOptions": {
    "noUncheckedIndexedAccess": true
  }
}

const users = ['Alice', 'Bob', 'Charlie'];

// TypeScript now says: string | undefined
const user = users[10];
console.log(user.toUpperCase());  // Error: 'user' is possibly 'undefined'

// Must handle undefined
if (user !== undefined) {
  console.log(user.toUpperCase());  // Safe - TypeScript knows it's string
}

// Or use optional chaining + nullish coalescing
console.log(user?.toUpperCase() ?? 'Unknown user');

// For loops, use the safe array iteration pattern
for (const name of users) {
  // name is string, not string | undefined
  console.log(name.toUpperCase());
}

// Record access is also safe now
const cache: Record<string, { data: string }> = {};
const entry = cache['key'];  // Type: { data: string } | undefined

if (entry) {
  console.log(entry.data);  // Safe
}
```

**Alternative (non-null assertion when you're certain):**

```typescript
// When you KNOW the index is valid, use non-null assertion
// But prefer .at() method or bounds checking

const items = ['a', 'b', 'c'];

// After bounds check
const index = 1;
if (index >= 0 && index < items.length) {
  const item = items[index]!;  // Safe - we checked bounds
  console.log(item.toUpperCase());
}

// Better: use .at() method (ES2022+)
const first = items.at(0);   // Type: string | undefined
const last = items.at(-1);   // Type: string | undefined - also supports negative!

// Or destructuring for first element
const [firstItem, ...rest] = items;
if (firstItem) {
  console.log(firstItem.toUpperCase());  // Safe
}
```

**When to use:** Enable `noUncheckedIndexedAccess` in all projects. The minor inconvenience of undefined checks prevents the most common JavaScript runtime error.

**When NOT to use:** May be verbose in code with heavy array manipulation where bounds are guaranteed (e.g., matrix operations). Consider using assertions or utility functions to reduce noise in those cases.

Reference: [TypeScript noUncheckedIndexedAccess](https://www.typescriptlang.org/tsconfig#noUncheckedIndexedAccess)
