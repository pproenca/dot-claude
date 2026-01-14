---
title: Use Project References
impact: CRITICAL
impactDescription: 5-10x faster monorepo builds, enables incremental compilation across packages
tags: perf, project-references, monorepo, compilation, composite
---

## Use Project References

Project references enable incremental builds across a monorepo. Instead of recompiling the entire codebase on every change, TypeScript only rebuilds packages that actually changed. For a 10-package monorepo, this can reduce build times from 60 seconds to 6 seconds.

**Incorrect (single tsconfig compiles everything):**

```typescript
// PROBLEM: A single tsconfig.json compiles the entire monorepo
// Every file change triggers a full rebuild of all packages

// tsconfig.json - monorepo root
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "outDir": "dist",
    "strict": true
  },
  "include": ["packages/**/*"]
}

// Project structure:
// packages/
//   core/         (~500 files)
//   utils/        (~200 files)
//   api/          (~300 files)
//   web/          (~1000 files)
//   mobile/       (~800 files)
// Total: ~2800 files

// Changing one file in utils/ triggers:
// - Full type-check of all 2800 files
// - Build time: 45-60 seconds
// - Developer waiting... every single save
```

**Correct (project references - rebuild only changed packages):**

```typescript
// SOLUTION: Each package has its own tsconfig with composite: true
// Root tsconfig references all packages for coordinated builds

// tsconfig.json (root) - coordinates builds
{
  "files": [],
  "references": [
    { "path": "./packages/core" },
    { "path": "./packages/utils" },
    { "path": "./packages/api" },
    { "path": "./packages/web" },
    { "path": "./packages/mobile" }
  ]
}

// packages/core/tsconfig.json
{
  "compilerOptions": {
    "composite": true,           // Required for project references
    "declaration": true,         // Required for composite
    "declarationMap": true,      // Enables go-to-definition across packages
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src/**/*"]
}

// packages/utils/tsconfig.json
{
  "compilerOptions": {
    "composite": true,
    "declaration": true,
    "declarationMap": true,
    "outDir": "dist"
  },
  "references": [
    { "path": "../core" }        // utils depends on core
  ],
  "include": ["src/**/*"]
}

// packages/web/tsconfig.json
{
  "compilerOptions": {
    "composite": true,
    "declaration": true,
    "outDir": "dist"
  },
  "references": [
    { "path": "../core" },
    { "path": "../utils" },
    { "path": "../api" }
  ],
  "include": ["src/**/*"]
}

// Now: Changing a file in utils/ only rebuilds utils + dependents
// Build time: 5-8 seconds instead of 60 seconds
// Use: tsc --build (or tsc -b) for incremental project builds
```

**Alternative (watch mode with project references):**

```typescript
// For development, use watch mode with build
// Terminal command:
// tsc --build --watch

// Or in package.json:
{
  "scripts": {
    "build": "tsc --build",
    "build:watch": "tsc --build --watch",
    "clean": "tsc --build --clean"  // Removes all build outputs
  }
}

// With turborepo or nx, project references integrate seamlessly:
// turbo run build --filter=@myorg/web
// Only builds web and its dependencies
```

**When to use:** Use project references in any monorepo with 2+ packages. The setup cost is minimal and pays off immediately with faster builds and better IDE performance.

**When NOT to use:** Single-package projects don't need project references. Very small monorepos (<1000 files total) may not see significant speedups.

Reference: [TypeScript Project References](https://www.typescriptlang.org/docs/handbook/project-references.html)
