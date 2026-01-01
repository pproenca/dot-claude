---
name: dev-typescript
description: Write TypeScript following Google's TypeScript Style Guide. Use when creating, editing, or reviewing TypeScript code. Enforces Google's conventions for imports, exports, naming, types, classes, functions, control flow, and error handling. Read references/patterns.md for destructuring, spread, iteration, type coercion, callbacks, and accessor patterns.
allowed-tools: Read, Edit, Bash, Glob, Grep
---

# Google TypeScript Style

## Imports & Exports

<b>Named exports only. No default exports.</b>
```ts
export class Foo {}
export const BAR = 1;
export function baz() {}
```

<b>No mutable exports:</b> `export let` prohibited. Use getter function if mutation needed.

<b>Minimize exported API surface.</b> Don't export symbols used only internally.

<b>No container classes</b> for namespacing:
```ts
// ✗
export class Utils {
  static FOO = 1;
  static bar() {}
}
// ✓
export const FOO = 1;
export function bar() {}
```

<b>Import patterns:</b>
- `import * as foo from './foo'` — many symbols from large APIs
- `import {Foo} from './foo'` — frequently used symbols with clear names
- `import type {Foo} from './foo'` — type-only (required for isolatedModules)
- Relative imports (`./foo`) over absolute for same project

<b>Prohibited:</b> `require()`, `namespace Foo {}`, `/// <reference>`

## Naming

| Style | Use for |
|-------|---------|
| `UpperCamelCase` | class, interface, type, enum, decorator, type parameter |
| `lowerCamelCase` | variable, parameter, function, method, property, module alias |
| `CONSTANT_CASE` | module-level constants, `static readonly`, enum values |

- Acronyms as words: `loadHttpUrl` not `loadHTTPURL`
- No `_` prefix/suffix, no Hungarian notation, no `I` prefix on interfaces
- Descriptive names. Single-letter allowed only for ≤10 line scope.

## Types

<b>`unknown` over `any`.</b> Comment required if `any` used.

<b>`{}` type prohibited.</b> Use `unknown`, `object`, or `Record<string, T>`.

<b>Interfaces for object shapes</b>, not classes or type aliases:
```ts
interface User { name: string; id: number }
const user: User = { name: 'Jo', id: 1 };
```

<b>Type annotations on object literals</b>, not assertions:
```ts
// ✓ Catches typos at declaration
const cfg: Config = { porrt: 8080 }; // Error!
// ✗ Silently accepts typos
const cfg = { porrt: 8080 } as Config;
```

<b>Arrays:</b> `T[]` for simple types, `Array<T>` for complex types or unions.

<b>Optional `?` over `|undefined`</b> for interface fields and params.

<b>No nullable type aliases.</b> Add `|null` at usage site.

<b>Tuples over Pair interfaces:</b>
```ts
// ✓
function split(s: string): [string, string] {}
const [left, right] = split(input);
// ✗
interface Pair { first: string; second: string }
```

<b>Index signatures:</b> Prefer `Map<K,V>` over `{[key: string]: T}`. If using index signature, use meaningful key name.

<b>Mapped/conditional types:</b> Use sparingly. Prefer explicit interfaces when possible.

<b>Return-type-only generics:</b> Avoid. Always specify explicitly at call site if API has them.

## Variables

- `const` default. `let` only if reassigned. Never `var`.
- One declaration per statement.
- `CONSTANT_CASE` only for module-level immutable values.
- `readonly` on non-reassigned properties.
- Explicit semicolons. Don't rely on ASI.

## Functions

<b>Function declarations for named functions:</b>
```ts
function process(x: number) { return x * 2; }
```

<b>Arrow functions for callbacks and closures.</b> No `function` expressions.

<b>Block body when return value unused:</b>
```ts
// ✓
promise.then((v) => { console.log(v); });
// ✗ leaks return value
promise.then((v) => console.log(v));
```

<b>Wrap callbacks in arrows</b> — don't pass function references directly:
```ts
// ✓
['1', '2'].map((n) => parseInt(n, 10));
// ✗ parseInt receives (value, index, array)
['1', '2'].map(parseInt); // [1, NaN]
```

<b>Default params:</b> Simple values only. No side effects, no shared mutable state.

<b>No `this` in functions</b> unless arrow function in method, or explicit `this` param.

## Classes

<b>Parameter properties:</b>
```ts
class Foo {
  constructor(private readonly bar: Bar) {}
}
```

<b>Field initializers</b> at declaration. Initialize optional fields to `undefined` explicitly.

<b>Blank line</b> between constructor and methods, between methods.

<b>No semicolons</b> after method declarations.

<b>Visibility:</b> Omit `public` (default). Use `private`/`protected`. Never `#private` fields.

<b>No static `this`.</b> Reference class name directly.

<b>Getters:</b> Must be pure. No pass-through accessors without logic.

<b>No unnecessary constructors.</b>

<b>`obj['prop']` prohibited</b> to bypass visibility.

## Control Flow

<b>Braces required.</b> Exception: single-line `if (x) doThing();`

<b>`===`/`!==` only.</b> Exception: `== null` for null+undefined check.

<b>Iteration:</b>
```ts
// Arrays: for...of
for (const x of arr) {}
// Objects: Object.keys/values/entries
for (const [k, v] of Object.entries(obj)) {}
// Never for...in on arrays
```

<b>Switch:</b> `default` case required (last). No fall-through from non-empty cases.

<b>Assignment in conditions:</b> Avoid. If needed, double-paren: `while ((x = next())) {}`

<b>Try blocks:</b> Keep focused. Move non-throwing code outside.

<b>Empty catch:</b> Must have explanatory comment.

## Type Assertions

<b>Avoid. Prefer runtime checks:</b>
```ts
if (x instanceof Foo) { x.method(); }
```

<b>`as` syntax</b>, not angle brackets. Comment required explaining safety.

<b>Double assertion</b> through `unknown` when needed:
```ts
(x as unknown as TargetType)
```

<b>Non-null `!` assertions:</b> Avoid. Comment required if used.

## Type Coercion

<b>Allowed:</b> `String()`, `Boolean()`, `Number()`, template literals, `!!`

<b>Enums to boolean prohibited:</b>
```ts
// ✗
if (status) {}
if (Boolean(status)) {}
// ✓
if (status !== Status.NONE) {}
```

<b>`Number()` for parsing.</b> Check `isFinite()`. No unary `+`, no `parseInt` (except non-base-10 with validation).

## Error Handling

- `throw new Error()` only. No `throw 'string'`.
- Only throw `Error` subclasses.
- Catch: assume `Error`, narrow if needed. No defensive non-Error handling unless API known to violate.

## Prohibited

`var`, `any`, `@ts-ignore`, `@ts-expect-error`, `const enum`, `debugger`, `eval`, `with`, default exports, `namespace`, `new String/Boolean/Number`, `#private`, prototype modification, `export let`, `{}` type

## Patterns Reference

See [references/patterns.md](references/patterns.md) for: destructuring, spread syntax, getters/setters, event handlers, callback patterns.
