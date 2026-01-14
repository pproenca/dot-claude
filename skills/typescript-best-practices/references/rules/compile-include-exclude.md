---
title: Configure Include/Exclude Properly
impact: CRITICAL
impactDescription: prevents accidental compilation of unwanted files
tags: compile, include, exclude, glob, node_modules
---

## Configure Include/Exclude Properly

Prevent accidentally including node_modules or build artifacts. Proper configuration dramatically improves compilation speed and prevents confusing errors.

**Incorrect (implicit includes):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "outDir": "dist"
  }
  // No include/exclude - TypeScript includes EVERYTHING
  // May accidentally compile node_modules or dist folder
}

// Or overly broad include
{
  "compilerOptions": { },
  "include": ["**/*"]  // Includes node_modules!
}
```

**Correct (explicit configuration):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src/**/*"],
  "exclude": [
    "node_modules",
    "dist",
    "**/*.test.ts",
    "**/*.spec.ts",
    "coverage",
    ".git"
  ]
}

// For monorepos
{
  "include": ["packages/*/src/**/*"],
  "exclude": [
    "**/node_modules",
    "**/dist",
    "**/.turbo"
  ]
}
```

**Best practices:**
- Always specify `include` explicitly
- Exclude build outputs, test files (for production), and tooling directories
- Use `rootDir` to control output structure

Reference: [TypeScript include/exclude](https://www.typescriptlang.org/tsconfig#include)
