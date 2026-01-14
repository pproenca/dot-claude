---
title: Use Modern Module Resolution
impact: LOW-MEDIUM
impactDescription: supports package.json exports field
tags: config, moduleResolution, bundler, esm
---

## Use Modern Module Resolution

Use `bundler` module resolution for modern bundler-based projects.

**Incorrect (legacy resolution):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "moduleResolution": "node"
    // Doesn't support package.json exports field
  }
}
```

**Correct (bundler resolution):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "moduleResolution": "bundler",
    "module": "ESNext",
    "noEmit": true  // Bundler handles emit
  }
}

// For Node.js ESM projects
{
  "compilerOptions": {
    "moduleResolution": "node16",
    "module": "node16"
  }
}
```

Reference: [TypeScript moduleResolution](https://www.typescriptlang.org/tsconfig#moduleResolution)
