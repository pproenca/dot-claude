---
title: Never Use Any
impact: CRITICAL
impactDescription: eliminates type-unsafe code paths
tags: safety, any, unknown, type-safety
---

## Never Use Any

The `any` type defeats TypeScript's purpose. Use `unknown` for truly unknown types, or proper typing with generics.

**Incorrect (using any):**

```typescript
function processData(data: any) {
  // No type checking - anything goes
  return data.foo.bar.baz; // Runtime error if structure is wrong
}

const config: any = loadConfig();
console.log(config.databse.host); // Typo not caught
```

**Correct (proper typing):**

```typescript
interface Config {
  database: {
    host: string;
    port: number;
  };
}

function processData<T>(data: T): T {
  return data;
}

// Use unknown for truly unknown data
function parseJSON(json: string): unknown {
  return JSON.parse(json);
}

// Then narrow the type
const result = parseJSON('{"name": "test"}');
if (isConfig(result)) {
  console.log(result.database.host); // Safe access
}
```

Reference: [TypeScript unknown Type](https://www.typescriptlang.org/docs/handbook/2/functions.html#unknown)
