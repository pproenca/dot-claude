---
title: Use Type Narrowing
impact: CRITICAL
impactDescription: enables safe type-specific operations without runtime crashes
tags: safety, narrowing, type-guards, control-flow, instanceof
---

## Use Type Narrowing

Type narrowing uses runtime checks to refine types at compile time. Instead of casting with `as` (which lies to the compiler), narrowing proves to TypeScript that a value is a specific type. This eliminates the entire class of "method does not exist" runtime errors.

**Incorrect (type assertion bypasses safety):**

```typescript
// PROBLEM: Type assertions (as) tell TypeScript to trust you, but
// if you're wrong, you get runtime crashes. This pattern causes
// ~10% of JavaScript runtime errors.

// payment-processor.ts
interface CreditCard {
  type: 'credit';
  number: string;
  cvv: string;
  expiryDate: string;
}

interface BankTransfer {
  type: 'bank';
  accountNumber: string;
  routingNumber: string;
}

type PaymentMethod = CreditCard | BankTransfer;

function processPayment(method: PaymentMethod) {
  // DANGEROUS: No runtime check - just trusting the assertion
  const card = method as CreditCard;
  console.log(`Processing card ending in ${card.number.slice(-4)}`);
  // CRASH: If method is BankTransfer, card.number is undefined
  // Error: Cannot read property 'slice' of undefined
}

// Even worse with DOM elements
function setupForm() {
  const input = document.getElementById('email') as HTMLInputElement;
  input.value = 'test@example.com';
  // CRASH: If element doesn't exist or isn't an input
}
```

**Correct (type narrowing with runtime checks):**

```typescript
// SOLUTION: Type guards perform runtime checks that TypeScript understands
// The compiler narrows the type based on control flow

// payment-processor.ts
interface CreditCard {
  type: 'credit';
  number: string;
  cvv: string;
  expiryDate: string;
}

interface BankTransfer {
  type: 'bank';
  accountNumber: string;
  routingNumber: string;
}

type PaymentMethod = CreditCard | BankTransfer;

// Custom type guard - returns 'x is Type' predicate
function isCreditCard(method: PaymentMethod): method is CreditCard {
  return method.type === 'credit';
}

function processPayment(method: PaymentMethod) {
  if (isCreditCard(method)) {
    // TypeScript knows method is CreditCard here
    console.log(`Processing card ending in ${method.number.slice(-4)}`);
  } else {
    // TypeScript knows method is BankTransfer here
    console.log(`Processing bank transfer to ${method.accountNumber}`);
  }
}

// Safe DOM element handling with instanceof
function setupForm() {
  const input = document.getElementById('email');

  // Narrowing with instanceof
  if (input instanceof HTMLInputElement) {
    input.value = 'test@example.com'; // Safe - TypeScript knows it's an input
  } else if (input === null) {
    console.error('Email input not found');
  } else {
    console.error('Email element is not an input');
  }
}
```

**Alternative (using in operator for property checks):**

```typescript
// The 'in' operator narrows types by property existence
interface Dog {
  bark(): void;
  breed: string;
}

interface Cat {
  meow(): void;
  color: string;
}

type Pet = Dog | Cat;

function makeSound(pet: Pet) {
  if ('bark' in pet) {
    // TypeScript knows pet is Dog
    pet.bark();
    console.log(`Breed: ${pet.breed}`);
  } else {
    // TypeScript knows pet is Cat
    pet.meow();
    console.log(`Color: ${pet.color}`);
  }
}

// Also works with typeof for primitives
function processValue(value: string | number) {
  if (typeof value === 'string') {
    return value.toUpperCase(); // TypeScript knows it's string
  } else {
    return value.toFixed(2); // TypeScript knows it's number
  }
}
```

**When to use:** Use type narrowing whenever you need to access type-specific properties or methods on union types. Prefer discriminated unions with switch statements for complex state machines.

**When NOT to use:** If you're narrowing the same value repeatedly throughout a function, consider restructuring to narrow once at the top or using discriminated unions.

Reference: [TypeScript Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
