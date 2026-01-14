---
title: Enable Source Maps
impact: LOW-MEDIUM
impactDescription: enables TypeScript debugging
tags: config, sourceMap, debugging, development
---

## Enable Source Maps

Enable source maps for debugging TypeScript in development.

**Incorrect (no source maps):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "outDir": "dist"
    // No sourceMap - debugging shows compiled JS
  }
}
```

**Correct (source maps enabled):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "sourceMap": true,
    // Or inline for simpler deployment
    "inlineSourceMap": true,
    "inlineSources": true
  }
}
```

Reference: [TypeScript sourceMap](https://www.typescriptlang.org/tsconfig#sourceMap)
