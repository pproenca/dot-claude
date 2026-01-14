---
title: Enable skipLibCheck for Speed
impact: CRITICAL
impactDescription: 30-50% faster type checking
tags: compile, skipLibCheck, performance, node_modules
---

## Enable skipLibCheck for Speed

Skip type checking of declaration files (`.d.ts`) in node_modules to dramatically speed up compilation. This trades some type safety for build performance.

**Incorrect (checking all declaration files):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "strict": true
    // skipLibCheck defaults to false
    // TypeScript checks ALL .d.ts files including node_modules
  }
}

// Build times: 45 seconds for medium project
// May catch errors in poorly typed libraries
```

**Correct (skip library checks):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "skipLibCheck": true
    // Only checks your .d.ts files, not node_modules
  }
}

// Build times: 15-25 seconds for same project
// Still catches errors in YOUR code
```

**When to keep skipLibCheck false:**
- Library authors who need to verify their .d.ts output
- Projects with custom declaration files that need validation
- When debugging type issues in dependencies

Reference: [TypeScript skipLibCheck](https://www.typescriptlang.org/tsconfig#skipLibCheck)
