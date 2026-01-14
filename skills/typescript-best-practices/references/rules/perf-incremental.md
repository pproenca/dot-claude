---
title: Enable Incremental Compilation
impact: CRITICAL
impactDescription: 90% faster subsequent builds (30s to 3s), caches type information
tags: perf, incremental, tsbuildinfo, compilation, caching
---

## Enable Incremental Compilation

Incremental compilation caches type-checking information between builds. Instead of re-analyzing every file, TypeScript only rechecks files that changed and their dependents. This reduces typical rebuild times from 30 seconds to 3 seconds - a 90% improvement.

**Incorrect (full rebuild every time):**

```typescript
// PROBLEM: Without incremental, TypeScript rebuilds everything from scratch
// Every `tsc` invocation pays the full type-checking cost

// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "outDir": "dist",
    "strict": true
    // No incremental - pays full cost every build
  }
}

// Project with 1000 files:
// - First build: 30 seconds
// - Second build (no changes): 30 seconds (same!)
// - Build after changing 1 file: 30 seconds (still same!)

// In CI, this adds up:
// - 100 builds/day × 30s = 50 minutes/day wasted
// - Developer flow interrupted by slow feedback
```

**Correct (incremental builds - only rebuild what changed):**

```typescript
// SOLUTION: Enable incremental to cache type information
// TypeScript stores analysis in .tsbuildinfo file

// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "outDir": "dist",
    "strict": true,

    // Enable incremental builds
    "incremental": true,
    "tsBuildInfoFile": ".tsbuildinfo"  // Cache file location
  }
}

// Same project with 1000 files:
// - First build: 30 seconds (creates .tsbuildinfo cache)
// - Second build (no changes): 2 seconds (reads cache, no work)
// - Build after changing 1 file: 3 seconds (rechecks only affected)

// .tsbuildinfo is a JSON file containing:
// - File versions (hashes)
// - Dependency graph
// - Cached diagnostics
// Add to .gitignore - it's machine-specific
```

**Alternative (composite for library packages):**

```typescript
// For packages that other packages depend on, use composite
// Composite implies incremental and adds declaration file generation

// packages/core/tsconfig.json
{
  "compilerOptions": {
    "composite": true,           // Implies incremental: true
    "declaration": true,         // Required for composite
    "declarationMap": true,      // Enables go-to-definition
    "outDir": "dist",
    "rootDir": "src"
  }
}

// Benefits of composite:
// 1. Automatically incremental
// 2. Generates .d.ts files for consumers
// 3. Works with project references for monorepos
// 4. declarationMap enables IDE navigation across packages

// For app packages (no consumers), incremental alone is sufficient:
// packages/web/tsconfig.json
{
  "compilerOptions": {
    "incremental": true,         // Just incremental, no declarations needed
    "noEmit": true               // Bundler handles output
  }
}
```

**When to use:** Enable incremental for every TypeScript project. The `.tsbuildinfo` cache adds <1MB to disk but saves hours of build time. For monorepo packages, use `composite: true` instead.

**When NOT to use:** In ephemeral CI environments that don't persist artifacts, incremental provides less benefit (though still helps within the same build). Consider caching `.tsbuildinfo` between CI runs.

Reference: [TypeScript Incremental](https://www.typescriptlang.org/tsconfig#incremental)
