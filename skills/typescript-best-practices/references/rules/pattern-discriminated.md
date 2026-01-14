---
title: Use Discriminated Unions Over Type Assertions
impact: MEDIUM
impactDescription: eliminates type assertions
tags: pattern, discriminated, unions, type-safe
---

## Use Discriminated Unions Over Type Assertions

Discriminated unions provide type-safe branching without assertions.

**Incorrect (type assertions):**

```typescript
interface Shape {
  kind: string;
  radius?: number;
  width?: number;
  height?: number;
}

function area(shape: Shape): number {
  if (shape.kind === 'circle') {
    return Math.PI * (shape.radius as number) ** 2;
  }
  return (shape.width as number) * (shape.height as number);
}
```

**Correct (discriminated union):**

```typescript
type Shape =
  | { kind: 'circle'; radius: number }
  | { kind: 'rectangle'; width: number; height: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2;
    case 'rectangle':
      return shape.width * shape.height;
  }
}
```

Reference: [TypeScript Discriminated Unions](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#discriminated-unions)
