---
title: Use Appropriate Target
impact: LOW-MEDIUM
impactDescription: matches runtime capabilities
tags: config, target, es2022, lib
---

## Use Appropriate Target

Set the target based on your runtime environment.

**Incorrect (wrong target):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES5"  // Downlevels modern syntax unnecessarily
  }
}

// Or too aggressive
{
  "compilerOptions": {
    "target": "ESNext"  // May use features not supported by runtime
  }
}
```

**Correct (match your environment):**

```typescript
// For modern browsers/Node.js 18+
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM"]
  }
}

// For Node.js 20+
{
  "compilerOptions": {
    "target": "ES2023",
    "lib": ["ES2023"]
  }
}
```

Reference: [TypeScript target](https://www.typescriptlang.org/tsconfig#target)
