---
title: Prefer Const Assertions
impact: MEDIUM
impactDescription: preserves literal types
tags: pattern, const, assertions, readonly
---

## Prefer Const Assertions

Use `as const` to preserve literal types and make objects readonly.

**Incorrect (widened types):**

```typescript
const config = {
  api: 'https://api.example.com',
  timeout: 5000,
};
// Type: { api: string; timeout: number }

const routes = ['/', '/about', '/contact'];
// Type: string[]
```

**Correct (const assertion):**

```typescript
const config = {
  api: 'https://api.example.com',
  timeout: 5000,
} as const;
// Type: { readonly api: "https://api.example.com"; readonly timeout: 5000 }

const routes = ['/', '/about', '/contact'] as const;
// Type: readonly ["/", "/about", "/contact"]

type Route = typeof routes[number]; // "/" | "/about" | "/contact"
```

Reference: [TypeScript Const Assertions](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-4.html#const-assertions)
