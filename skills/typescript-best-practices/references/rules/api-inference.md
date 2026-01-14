---
title: Design for Inference
impact: MEDIUM-HIGH
impactDescription: reduces boilerplate type annotations
tags: api, inference, generics, design
---

## Design for Inference

Structure APIs so TypeScript can infer types without explicit annotations.

**Incorrect (requires type annotations):**

```typescript
interface Config<T> {
  value: T;
  transform: (v: T) => T;
}

// User must specify generic
const config: Config<number> = {
  value: 42,
  transform: (v) => v * 2,
};
```

**Correct (infers from usage):**

```typescript
function createConfig<T>(config: {
  value: T;
  transform: (v: T) => T;
}) {
  return config;
}

// Type is inferred
const config = createConfig({
  value: 42,
  transform: (v) => v * 2, // v is inferred as number
});
```

Reference: [TypeScript Type Inference](https://www.typescriptlang.org/docs/handbook/type-inference.html)
