---
title: Use Const Enums
impact: CRITICAL
impactDescription: zero runtime overhead, ~200-500 bytes saved per enum in bundle
tags: perf, const, enum, compilation, tree-shaking
---

## Use Const Enums

Regular enums generate JavaScript objects at runtime that cannot be tree-shaken. Const enums are completely inlined - they generate zero runtime code. For a codebase with 20 enums, this saves 4-10KB of bundle size and improves startup time.

**Incorrect (runtime enum creates overhead):**

```typescript
// PROBLEM: Regular enums generate JavaScript objects that ship to production
// Each enum adds ~200-500 bytes to your bundle, and they can't be tree-shaken

// direction.ts
enum Direction {
  Up = 0,
  Down = 1,
  Left = 2,
  Right = 3,
}

enum HttpStatus {
  OK = 200,
  NotFound = 404,
  ServerError = 500,
}

// Compiles to this JavaScript (shipped to browser):
// var Direction;
// (function (Direction) {
//     Direction[Direction["Up"] = 0] = "Up";
//     Direction[Direction["Down"] = 1] = "Down";
//     Direction[Direction["Left"] = 2] = "Left";
//     Direction[Direction["Right"] = 3] = "Right";
// })(Direction || (Direction = {}));

function move(dir: Direction) {
  if (dir === Direction.Up) {  // Compiles to: if (dir === Direction.Up)
    console.log('Moving up');  // Requires Direction object at runtime
  }
}

// Result: ~400 bytes for Direction enum alone, times 20 enums = 8KB overhead
```

**Correct (const enum - zero runtime code):**

```typescript
// SOLUTION: Const enums are completely inlined at compile time
// No runtime object, no bundle size cost, perfect tree-shaking

// direction.ts
const enum Direction {
  Up = 0,
  Down = 1,
  Left = 2,
  Right = 3,
}

const enum HttpStatus {
  OK = 200,
  NotFound = 404,
  ServerError = 500,
}

function move(dir: Direction) {
  if (dir === Direction.Up) {  // Compiles to: if (dir === 0)
    console.log('Moving up');  // No Direction object needed at runtime
  }
}

function handleResponse(status: HttpStatus) {
  if (status === HttpStatus.OK) {        // Compiles to: if (status === 200)
    return 'Success';
  } else if (status === HttpStatus.NotFound) {  // Compiles to: if (status === 404)
    return 'Not found';
  }
  return 'Error';
}

// Result: Zero bytes added to bundle - values inlined directly
```

**Alternative (union of literal types):**

```typescript
// Union types work at compile time only, like const enums
// Better for string-based enums that need runtime debugging

type Direction = 'up' | 'down' | 'left' | 'right';

// Useful for HTTP methods, event types, etc.
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

function request(method: HttpMethod, url: string) {
  // method is typed, but keeps string value for debugging
  console.log(`${method} ${url}`);  // Logs: "GET /api/users"
}

// Prefer union literals when:
// - You need readable runtime values for logging/debugging
// - You're working with string-based APIs
// - You want to avoid TypeScript's enum quirks
```

**When to use:** Use const enums for numeric enums that don't need runtime introspection. Use union literal types for string-based enums that benefit from readable runtime values.

**When NOT to use:** Don't use const enums if you need to iterate over enum values at runtime, or if the enum is exported from a library (const enums don't work across package boundaries with `isolatedModules`).

Reference: [TypeScript Const Enums](https://www.typescriptlang.org/docs/handbook/enums.html#const-enums)
