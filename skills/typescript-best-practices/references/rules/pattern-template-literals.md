---
title: Use Template Literal Types
impact: MEDIUM
impactDescription: validates string patterns at compile time
tags: pattern, template-literals, strings, validation
---

## Use Template Literal Types

Use template literal types for string pattern validation.

**Incorrect (plain strings):**

```typescript
function setColor(color: string) {
  // Accepts any string, including invalid colors
}

setColor('not-a-color'); // No error
```

**Correct (template literal types):**

```typescript
type HexDigit = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9'
  | 'a' | 'b' | 'c' | 'd' | 'e' | 'f';
type HexColor = `#${string}`;

type CSSUnit = 'px' | 'em' | 'rem' | '%';
type CSSLength = `${number}${CSSUnit}`;

function setWidth(width: CSSLength) { }

setWidth('100px'); // OK
setWidth('2em'); // OK
setWidth('100'); // Error: not a valid CSSLength
```

Reference: [TypeScript Template Literal Types](https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html)
