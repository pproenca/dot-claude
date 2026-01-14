---
title: Use Satisfies Operator
impact: CRITICAL
impactDescription: validates types while preserving inference
tags: safety, satisfies, inference, literals
---

## Use Satisfies Operator

Use `satisfies` to validate types while preserving literal types for better inference.

**Incorrect (type annotation loses literals):**

```typescript
const colors: Record<string, [number, number, number]> = {
  red: [255, 0, 0],
  green: [0, 255, 0],
  blue: [0, 0, 255],
};

// colors.red is [number, number, number], not [255, 0, 0]
// colors.purple would be valid (any string key)
```

**Correct (satisfies preserves literals):**

```typescript
const colors = {
  red: [255, 0, 0],
  green: [0, 255, 0],
  blue: [0, 0, 255],
} satisfies Record<string, [number, number, number]>;

// colors.red is [255, 0, 0] (literal type preserved)
// colors.purple - Error: Property 'purple' does not exist
```

Reference: [TypeScript satisfies Operator](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html#the-satisfies-operator)
