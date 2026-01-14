---
title: Reserve Barrels for Libraries
impact: MEDIUM
impactDescription: appropriate barrel file usage
tags: module, barrel, library, package, exports
---

## Reserve Barrels for Libraries

Barrel files (index.ts re-exports) are appropriate for library entry points but harmful in applications. Use them only when publishing packages.

**Incorrect (barrels in applications):**

```typescript
// src/components/index.ts - Application barrel
export * from './Button';
export * from './Input';
export * from './Modal';
// ... 50 more components

// src/pages/Home.tsx
import { Button } from '../components';
// Loads ALL components even though only Button is used
// Tree-shaking often fails with barrel files
```

**Correct (barrels only for library entry points):**

```typescript
// Application: direct imports
// src/pages/Home.tsx
import { Button } from '../components/Button';
import { Input } from '../components/Input';
// Only loads what's needed

// Library: barrel as package entry point
// packages/ui-kit/src/index.ts
export { Button } from './Button';
export { Input } from './Input';
export type { ButtonProps, InputProps } from './types';

// package.json
{
  "name": "@myorg/ui-kit",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": "./dist/index.js",
    "./Button": "./dist/Button.js"  // Also allow direct imports
  }
}
```

**Guidelines:**
- Applications: Always import directly from source files
- Libraries: Use barrel for main entry, offer direct imports via `exports`
- Internal packages in monorepos: Treat like libraries with barrel entry

Reference: [Package.json exports](https://nodejs.org/api/packages.html#package-entry-points)
