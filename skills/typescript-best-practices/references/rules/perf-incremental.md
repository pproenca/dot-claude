---
title: Enable Incremental Compilation
impact: CRITICAL
impactDescription: 10x faster subsequent builds
tags: perf, incremental, tsbuildinfo, compilation
---

## Enable Incremental Compilation

Incremental compilation caches build information, dramatically speeding up subsequent builds.

**Incorrect (full rebuild every time):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "outDir": "dist"
    // No incremental - rebuilds everything
  }
}
```

**Correct (incremental builds):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "incremental": true,
    "tsBuildInfoFile": ".tsbuildinfo",
    "outDir": "dist"
  }
}

// For composite projects
{
  "compilerOptions": {
    "composite": true,  // Implies incremental
    "declaration": true,
    "declarationMap": true
  }
}
```

Reference: [TypeScript Incremental](https://www.typescriptlang.org/tsconfig#incremental)
