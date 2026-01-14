---
title: Avoid Barrel File Re-exports
impact: CRITICAL
impactDescription: enables tree-shaking
tags: perf, barrel, re-exports, tree-shaking
---

## Avoid Barrel File Re-exports

Barrel files (`index.ts` re-exporting everything) prevent tree-shaking and slow down compilation.

**Incorrect (barrel files):**

```typescript
// utils/index.ts - barrel file
export * from './string';
export * from './number';
export * from './date';
export * from './array';
// ... 50 more modules

// consumer.ts
import { formatDate } from './utils';
// Imports entire utils, even though only formatDate is used
```

**Correct (direct imports):**

```typescript
// consumer.ts - import directly
import { formatDate } from './utils/date';

// Or use specific exports in barrel
// utils/index.ts
export { formatDate } from './date';
export { capitalize } from './string';
// Only export what's commonly needed
```

Reference: [Tree Shaking with TypeScript](https://webpack.js.org/guides/tree-shaking/)
