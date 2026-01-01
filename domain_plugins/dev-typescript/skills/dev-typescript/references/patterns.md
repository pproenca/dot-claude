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

<b>Type matching required:</b>
```ts
// Arrays: spread only iterables
const arr = [...foo, ...bar];
const arr = [...(condition ? items : [])]; // conditional

// Objects: spread only objects
const obj = {...defaults, ...overrides};
const obj = {...(condition ? extra : {})}; // conditional
```

<b>Prohibited patterns:</b>
```ts
// ✗ Falsy spread
const bad = [...(shouldUse && items)]; // might be false
const bad = {...(shouldUse && obj)};   // might be false

// ✗ Type mismatch
const bad = {...['a', 'b']}; // array into object
const bad = [...{a: 1}];     // object into array
```

## Getters & Setters

<b>Must have logic.</b> No pass-through accessors:
```ts
// ✗ Pointless - just make bar public
get bar() { return this._bar; }
set bar(v) { this._bar = v; }

// ✓ Has logic
get bar() { return this._bar ?? 'default'; }
set bar(v) { this._bar = v.trim(); }
```

<b>Backing field naming:</b> Prefix with `internal` or `wrapped`:
```ts
private wrappedValue = '';
get value() { return this.wrappedValue || 'default'; }
```

<b>Getters must be pure.</b> No side effects, no state changes.

<b>No `Object.defineProperty`</b> for accessors.

## Event Handlers

<b>Arrow properties allowed</b> when handler needs uninstall:
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

<b>Inline arrows</b> for non-removable handlers:
```ts
element.addEventListener('click', () => { this.onClick(); });
```

<b>Never `.bind()` in addEventListener</b> — creates new reference each call.

## Callbacks

<b>Always wrap in arrow:</b>
```ts
// ✓
items.map((x) => transform(x));
items.filter((x) => isValid(x));

// ✗ Passes extra arguments (index, array)
items.map(transform);
items.filter(isValid);
```

<b>Why:</b> Higher-order functions pass multiple arguments. Direct references receive all of them:
```ts
['1', '2', '3'].map(parseInt);
// parseInt receives (value, index, array)
// parseInt('1', 0) → 1
// parseInt('2', 1) → NaN (invalid base 1)
// parseInt('3', 2) → NaN (invalid base 2)
```

## `this` Binding

<b>Arrow functions in methods</b> access outer `this`:
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

<b>Explicit params</b> over rebinding:
```ts
// ✓
const setText = (el: HTMLElement) => { el.textContent = 'hi'; };
document.body.onclick = () => setText(document.body);

// ✗
function setText() { this.textContent = 'hi'; }
document.body.onclick = setText; // this binding unclear
```

## Iteration

<b>Arrays:</b> `for...of` or `.forEach()`:
```ts
for (const item of items) {}
for (const [i, item] of items.entries()) {} // with index
```

<b>Objects:</b> `Object.keys/values/entries`:
```ts
for (const key of Object.keys(obj)) {}
for (const value of Object.values(obj)) {}
for (const [key, value] of Object.entries(obj)) {}
```

<b>`for...in` only for dict-style objects</b>, with `hasOwnProperty`:
```ts
for (const key in dict) {
  if (!dict.hasOwnProperty(key)) continue;
  // ...
}
```

## Computed Properties

<b>Symbol keys only</b> in classes:
```ts
class Iter {
  *[Symbol.iterator]() { yield* this.items; }
}
```

Non-symbol computed keys treated as quoted (dict-style).
