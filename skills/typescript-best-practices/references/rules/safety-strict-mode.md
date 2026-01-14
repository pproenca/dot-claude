---
title: Enable Strict Mode
impact: CRITICAL
impactDescription: catches 10x more bugs at compile time
tags: safety, strict, tsconfig, null-checks
---

## Enable Strict Mode

Enable all strict type-checking options to catch subtle bugs early. Strict mode includes `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`, and more.

**Incorrect (relaxed type checking):**

```typescript
// tsconfig.json with no strict mode
{
  "compilerOptions": {
    "target": "ES2020"
    // strict: false by default
  }
}

// Code that compiles but has runtime errors
function greet(name: string) {
  return `Hello, ${name.toUpperCase()}`;
}

greet(null); // No compile error, but runtime crash!
```

**Correct (strict mode enabled):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "strict": true
  }
}

// Now TypeScript catches the error
function greet(name: string) {
  return `Hello, ${name.toUpperCase()}`;
}

greet(null); // Error: Argument of type 'null' is not assignable
```

Reference: [TypeScript Strict Mode](https://www.typescriptlang.org/tsconfig#strict)
