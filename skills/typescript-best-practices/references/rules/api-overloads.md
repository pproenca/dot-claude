---
title: Use Function Overloads
impact: MEDIUM-HIGH
impactDescription: provides precise types for different signatures
tags: api, overloads, functions, signatures
---

## Use Function Overloads

Use overloads to provide precise types for different argument combinations.

**Incorrect (union return type):**

```typescript
function createElement(tag: string, props?: object): HTMLElement | SVGElement {
  // Return type is too broad
  // Caller doesn't know which type they get
}

const div = createElement('div'); // Type is HTMLElement | SVGElement
```

**Correct (function overloads):**

```typescript
function createElement(tag: 'div', props?: object): HTMLDivElement;
function createElement(tag: 'span', props?: object): HTMLSpanElement;
function createElement(tag: 'svg', props?: object): SVGSVGElement;
function createElement(tag: string, props?: object): Element;
function createElement(tag: string, props?: object): Element {
  return document.createElement(tag);
}

const div = createElement('div'); // Type is HTMLDivElement
const svg = createElement('svg'); // Type is SVGSVGElement
```

Reference: [TypeScript Function Overloads](https://www.typescriptlang.org/docs/handbook/2/functions.html#function-overloads)
