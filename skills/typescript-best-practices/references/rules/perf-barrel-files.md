---
title: Avoid Barrel File Re-exports
impact: CRITICAL
impactDescription: prevents 30-70% bundle bloat, enables tree-shaking
tags: perf, barrel, re-exports, tree-shaking, imports, webpack
---

## Avoid Barrel File Re-exports

Barrel files (`index.ts` that re-export everything) defeat tree-shaking and cause massive bundle bloat. When you import one function from a barrel, bundlers often include all exports. A single `import { formatDate } from './utils'` can pull in 50+ unused modules.

**Incorrect (barrel files defeat tree-shaking):**

```typescript
// PROBLEM: Barrel files cause the entire module graph to be included
// This pattern adds 30-70% bundle bloat in typical applications

// utils/index.ts - barrel file re-exporting everything
export * from './string';     // 20 functions
export * from './number';     // 15 functions
export * from './date';       // 25 functions
export * from './array';      // 30 functions
export * from './object';     // 20 functions
export * from './validation'; // 40 functions
// Total: 150 functions exported

// icons/index.ts - another common barrel pattern
export { AlertCircle } from 'lucide-react';
export { Check } from 'lucide-react';
export { ChevronDown } from 'lucide-react';
// ... 100 more icons re-exported

// consumer.ts - only needs one function
import { formatDate } from './utils';
// PROBLEM: Bundler may include all 150 functions from utils

import { Check } from './icons';
// PROBLEM: May import entire lucide-react library (~200KB)

// With webpack-bundle-analyzer:
// - Expected: ~2KB for formatDate + Check icon
// - Actual: ~150KB due to barrel files pulling in everything
```

**Correct (direct imports enable tree-shaking):**

```typescript
// SOLUTION: Import directly from the source module
// Bundlers can now tree-shake unused exports

// consumer.ts - import directly from source
import { formatDate } from './utils/date';
import { Check } from 'lucide-react';

// Result: Only formatDate and Check are included in bundle
// Bundle size: ~2KB instead of ~150KB (98% reduction)

// For icons, import directly from lucide-react
// Each icon is ~400 bytes instead of entire 200KB library
import { Check, AlertCircle, ChevronDown } from 'lucide-react';

// Your internal utils should be imported the same way
import { capitalize, truncate } from './utils/string';
import { formatCurrency } from './utils/number';
```

**Alternative (curated barrel for common exports only):**

```typescript
// If you must use a barrel, export only the most common items
// Don't use export * - be explicit

// utils/index.ts - curated exports only
// These 10 are used in >50% of files
export { formatDate, parseDate } from './date';
export { capitalize, truncate } from './string';
export { formatCurrency } from './number';
export { debounce, throttle } from './function';
export { isEmail, isUrl } from './validation';

// Less common utilities should be imported directly:
// import { obscureDateFunction } from './utils/date';

// Alternative: Re-export individual modules as namespaces
export * as dateUtils from './date';
export * as stringUtils from './string';
// Usage: import { dateUtils } from './utils';
// dateUtils.formatDate() - IDE autocomplete still works
```

**When to use:** Import directly from source modules in application code. Use curated barrels (explicit exports, not `export *`) for library entry points where you control the public API.

**When NOT to use:** Don't avoid barrels in library packages where you need a clean public API. But ensure the library uses `"sideEffects": false` in package.json and explicit exports.

Reference: [Tree Shaking with TypeScript](https://webpack.js.org/guides/tree-shaking/)
