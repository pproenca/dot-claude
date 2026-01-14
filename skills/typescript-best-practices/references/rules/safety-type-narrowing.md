---
title: Use Type Narrowing
impact: CRITICAL
impactDescription: enables safe type-specific operations
tags: safety, narrowing, type-guards, control-flow
---

## Use Type Narrowing

Use type guards and control flow analysis to narrow types safely instead of casting.

**Incorrect (type assertion):**

```typescript
interface Cat { meow(): void; }
interface Dog { bark(): void; }

function makeSound(animal: Cat | Dog) {
  // Dangerous - no runtime check
  (animal as Cat).meow();
}
```

**Correct (type narrowing with guards):**

```typescript
interface Cat { type: 'cat'; meow(): void; }
interface Dog { type: 'dog'; bark(): void; }

function isCat(animal: Cat | Dog): animal is Cat {
  return animal.type === 'cat';
}

function makeSound(animal: Cat | Dog) {
  if (isCat(animal)) {
    animal.meow(); // TypeScript knows it's a Cat
  } else {
    animal.bark(); // TypeScript knows it's a Dog
  }
}
```

Reference: [TypeScript Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
