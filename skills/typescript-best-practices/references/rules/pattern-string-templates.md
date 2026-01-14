---
title: Use Template Literal Types for String Patterns
impact: MEDIUM
impactDescription: validates string formats at compile time
tags: pattern, template-literal, strings, validation
---

## Use Template Literal Types for String Patterns

Template literal types enforce string patterns at compile time, catching invalid strings before runtime.

**Incorrect (plain string types):**

```typescript
type ApiEndpoint = string;
type EventName = string;
type CssColor = string;

function fetchData(endpoint: ApiEndpoint) { }
function emit(event: EventName) { }
function setColor(color: CssColor) { }

// All of these compile but are wrong
fetchData('not-an-endpoint');
emit('InvalidEvent');
setColor('not-a-color');
```

**Correct (template literal types):**

```typescript
// API routes must start with /api/
type ApiEndpoint = `/api/${string}`;

// Events follow namespace:action pattern
type EventName = `${string}:${string}`;

// CSS colors
type HexColor = `#${string}`;
type RgbColor = `rgb(${number}, ${number}, ${number})`;
type CssColor = HexColor | RgbColor | 'transparent' | 'currentColor';

function fetchData(endpoint: ApiEndpoint) { }
function emit(event: EventName) { }
function setColor(color: CssColor) { }

fetchData('/api/users');        // OK
fetchData('/users');            // Error: doesn't match pattern

emit('user:created');           // OK
emit('invalid');                // Error: missing colon

setColor('#ff0000');            // OK
setColor('rgb(255, 0, 0)');     // OK
setColor('blue');               // Error: not in union
```

**Advanced patterns:**

```typescript
// Extract parts from template literals
type ExtractParams<T extends string> =
  T extends `${infer _Start}:${infer Param}/${infer Rest}`
    ? Param | ExtractParams<Rest>
    : T extends `${infer _Start}:${infer Param}`
      ? Param
      : never;

type Params = ExtractParams<'/users/:id/posts/:postId'>;
// Type is 'id' | 'postId'
```

Reference: [TypeScript Template Literal Types](https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html)
