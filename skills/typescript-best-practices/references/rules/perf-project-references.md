---
title: Use Project References
impact: CRITICAL
impactDescription: enables incremental monorepo builds
tags: perf, project-references, monorepo, compilation
---

## Use Project References

For large codebases, project references enable incremental builds and better organization.

**Incorrect (single huge tsconfig):**

```typescript
// tsconfig.json - compiles entire monorepo
{
  "compilerOptions": {
    "outDir": "dist"
  },
  "include": ["packages/**/*"]  // Rebuilds everything on any change
}
```

**Correct (project references):**

```typescript
// tsconfig.json (root)
{
  "references": [
    { "path": "./packages/core" },
    { "path": "./packages/utils" },
    { "path": "./packages/app" }
  ]
}

// packages/core/tsconfig.json
{
  "compilerOptions": {
    "composite": true,
    "outDir": "dist"
  }
}

// packages/app/tsconfig.json
{
  "compilerOptions": {
    "composite": true
  },
  "references": [
    { "path": "../core" },
    { "path": "../utils" }
  ]
}
```

Reference: [TypeScript Project References](https://www.typescriptlang.org/docs/handbook/project-references.html)
