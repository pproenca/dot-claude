---
title: Use Const Enums
impact: CRITICAL
impactDescription: zero runtime overhead
tags: perf, const, enum, compilation
---

## Use Const Enums

Regular enums generate JavaScript objects at runtime. Const enums are inlined, eliminating runtime overhead.

**Incorrect (runtime enum):**

```typescript
enum Direction {
  Up,
  Down,
  Left,
  Right,
}

function move(dir: Direction) {
  // Compiles to: if (dir === Direction.Up)
  // Direction object exists at runtime
  if (dir === Direction.Up) {
    console.log('Moving up');
  }
}
```

**Correct (const enum - zero runtime):**

```typescript
const enum Direction {
  Up,
  Down,
  Left,
  Right,
}

function move(dir: Direction) {
  // Compiles to: if (dir === 0)
  // No Direction object at runtime
  if (dir === Direction.Up) {
    console.log('Moving up');
  }
}

// Alternative: use union of literal types
type Direction = 'up' | 'down' | 'left' | 'right';
```

Reference: [TypeScript Const Enums](https://www.typescriptlang.org/docs/handbook/enums.html#const-enums)
