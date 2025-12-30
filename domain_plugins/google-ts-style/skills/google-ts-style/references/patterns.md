# TypeScript Patterns

## Destructuring

### Arrays
```ts
const [a, b, c, ...rest] = items;
const [, second, , fourth] = items; // skip elements

// Default values on left side
function process([a = 0, b = 0] = []) {}
```

### Objects
```ts
const {name, age} = person;
const {name: userName} = person; // rename

// Single level only in params. Defaults on left side.
function process({num, str = 'default'}: Options = {}) {}

// ✗ No deep destructuring in params
function bad({x: {nested}}: Deep) {}
// ✗ No defaults on right side
function bad({num}: Options = {num: 42}) {}
```

## Spread Syntax

**Type matching required:**
```ts
// Arrays: spread only iterables
const arr = [...foo, ...bar];
const arr = [...(condition ? items : [])]; // conditional

// Objects: spread only objects
const obj = {...defaults, ...overrides};
const obj = {...(condition ? extra : {})}; // conditional
```

**Prohibited patterns:**
```ts
// ✗ Falsy spread
const bad = [...(shouldUse && items)]; // might be false
const bad = {...(shouldUse && obj)};   // might be false

// ✗ Type mismatch
const bad = {...['a', 'b']}; // array into object
const bad = [...{a: 1}];     // object into array
```

## Getters & Setters

**Must have logic.** No pass-through accessors:
```ts
// ✗ Pointless - just make bar public
get bar() { return this._bar; }
set bar(v) { this._bar = v; }

// ✓ Has logic
get bar() { return this._bar ?? 'default'; }
set bar(v) { this._bar = v.trim(); }
```

**Backing field naming:** Prefix with `internal` or `wrapped`:
```ts
private wrappedValue = '';
get value() { return this.wrappedValue || 'default'; }
```

**Getters must be pure.** No side effects, no state changes.

**No `Object.defineProperty`** for accessors.

## Event Handlers

**Arrow properties allowed** when handler needs uninstall:
```ts
class Component {
  // ✓ Arrow property - stable reference for removeEventListener
  private listener = () => { this.handleEvent(); };

  onAttach() {
    window.addEventListener('resize', this.listener);
  }
  onDetach() {
    window.removeEventListener('resize', this.listener);
  }
}
```

**Inline arrows** for non-removable handlers:
```ts
element.addEventListener('click', () => { this.onClick(); });
```

**Never `.bind()` in addEventListener** — creates new reference each call.

## Callbacks

**Always wrap in arrow:**
```ts
// ✓
items.map((x) => transform(x));
items.filter((x) => isValid(x));

// ✗ Passes extra arguments (index, array)
items.map(transform);
items.filter(isValid);
```

**Why:** Higher-order functions pass multiple arguments. Direct references receive all of them:
```ts
['1', '2', '3'].map(parseInt);
// parseInt receives (value, index, array)
// parseInt('1', 0) → 1
// parseInt('2', 1) → NaN (invalid base 1)
// parseInt('3', 2) → NaN (invalid base 2)
```

## `this` Binding

**Arrow functions in methods** access outer `this`:
```ts
class Foo {
  items: string[] = [];

  process() {
    // ✓ Arrow captures this
    this.items.forEach((item) => {
      this.handle(item);
    });
  }
}
```

**Explicit params** over rebinding:
```ts
// ✓
const setText = (el: HTMLElement) => { el.textContent = 'hi'; };
document.body.onclick = () => setText(document.body);

// ✗
function setText() { this.textContent = 'hi'; }
document.body.onclick = setText; // this binding unclear
```

## Iteration

**Arrays:** `for...of` or `.forEach()`:
```ts
for (const item of items) {}
for (const [i, item] of items.entries()) {} // with index
```

**Objects:** `Object.keys/values/entries`:
```ts
for (const key of Object.keys(obj)) {}
for (const value of Object.values(obj)) {}
for (const [key, value] of Object.entries(obj)) {}
```

**`for...in` only for dict-style objects**, with `hasOwnProperty`:
```ts
for (const key in dict) {
  if (!dict.hasOwnProperty(key)) continue;
  // ...
}
```

## Computed Properties

**Symbol keys only** in classes:
```ts
class Iter {
  *[Symbol.iterator]() { yield* this.items; }
}
```

Non-symbol computed keys treated as quoted (dict-style).
