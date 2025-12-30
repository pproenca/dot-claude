---
name: google-ts-style
description: Write TypeScript following Google's TypeScript Style Guide. Use when creating, editing, or reviewing TypeScript code. Enforces Google's conventions for imports, exports, naming, types, classes, functions, control flow, and error handling. Read references/patterns.md for destructuring, spread, iteration, type coercion, callbacks, and accessor patterns.
---

# Google TypeScript Style

## Imports & Exports

**Named exports only. No default exports.**
```ts
export class Foo {}
export const BAR = 1;
export function baz() {}
```

**No mutable exports:** `export let` prohibited. Use getter function if mutation needed.

**Minimize exported API surface.** Don't export symbols used only internally.

**No container classes** for namespacing:
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

**Import patterns:**
- `import * as foo from './foo'` — many symbols from large APIs
- `import {Foo} from './foo'` — frequently used symbols with clear names
- `import type {Foo} from './foo'` — type-only (required for isolatedModules)
- Relative imports (`./foo`) over absolute for same project

**Prohibited:** `require()`, `namespace Foo {}`, `/// <reference>`

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

**`unknown` over `any`.** Comment required if `any` used.

**`{}` type prohibited.** Use `unknown`, `object`, or `Record<string, T>`.

**Interfaces for object shapes**, not classes or type aliases:
```ts
interface User { name: string; id: number }
const user: User = { name: 'Jo', id: 1 };
```

**Type annotations on object literals**, not assertions:
```ts
// ✓ Catches typos at declaration
const cfg: Config = { porrt: 8080 }; // Error!
// ✗ Silently accepts typos
const cfg = { porrt: 8080 } as Config;
```

**Arrays:** `T[]` for simple types, `Array<T>` for complex types or unions.

**Optional `?` over `|undefined`** for interface fields and params.

**No nullable type aliases.** Add `|null` at usage site.

**Tuples over Pair interfaces:**
```ts
// ✓
function split(s: string): [string, string] {}
const [left, right] = split(input);
// ✗
interface Pair { first: string; second: string }
```

**Index signatures:** Prefer `Map<K,V>` over `{[key: string]: T}`. If using index signature, use meaningful key name.

**Mapped/conditional types:** Use sparingly. Prefer explicit interfaces when possible.

**Return-type-only generics:** Avoid. Always specify explicitly at call site if API has them.

## Variables

- `const` default. `let` only if reassigned. Never `var`.
- One declaration per statement.
- `CONSTANT_CASE` only for module-level immutable values.
- `readonly` on non-reassigned properties.
- Explicit semicolons. Don't rely on ASI.

## Functions

**Function declarations for named functions:**
```ts
function process(x: number) { return x * 2; }
```

**Arrow functions for callbacks and closures.** No `function` expressions.

**Block body when return value unused:**
```ts
// ✓
promise.then((v) => { console.log(v); });
// ✗ leaks return value
promise.then((v) => console.log(v));
```

**Wrap callbacks in arrows** — don't pass function references directly:
```ts
// ✓
['1', '2'].map((n) => parseInt(n, 10));
// ✗ parseInt receives (value, index, array)
['1', '2'].map(parseInt); // [1, NaN]
```

**Default params:** Simple values only. No side effects, no shared mutable state.

**No `this` in functions** unless arrow function in method, or explicit `this` param.

## Classes

**Parameter properties:**
```ts
class Foo {
  constructor(private readonly bar: Bar) {}
}
```

**Field initializers** at declaration. Initialize optional fields to `undefined` explicitly.

**Blank line** between constructor and methods, between methods.

**No semicolons** after method declarations.

**Visibility:** Omit `public` (default). Use `private`/`protected`. Never `#private` fields.

**No static `this`.** Reference class name directly.

**Getters:** Must be pure. No pass-through accessors without logic.

**No unnecessary constructors.**

**`obj['prop']` prohibited** to bypass visibility.

## Control Flow

**Braces required.** Exception: single-line `if (x) doThing();`

**`===`/`!==` only.** Exception: `== null` for null+undefined check.

**Iteration:**
```ts
// Arrays: for...of
for (const x of arr) {}
// Objects: Object.keys/values/entries
for (const [k, v] of Object.entries(obj)) {}
// Never for...in on arrays
```

**Switch:** `default` case required (last). No fall-through from non-empty cases.

**Assignment in conditions:** Avoid. If needed, double-paren: `while ((x = next())) {}`

**Try blocks:** Keep focused. Move non-throwing code outside.

**Empty catch:** Must have explanatory comment.

## Type Assertions

**Avoid. Prefer runtime checks:**
```ts
if (x instanceof Foo) { x.method(); }
```

**`as` syntax**, not angle brackets. Comment required explaining safety.

**Double assertion** through `unknown` when needed:
```ts
(x as unknown as TargetType)
```

**Non-null `!` assertions:** Avoid. Comment required if used.

## Type Coercion

**Allowed:** `String()`, `Boolean()`, `Number()`, template literals, `!!`

**Enums to boolean prohibited:**
```ts
// ✗
if (status) {}
if (Boolean(status)) {}
// ✓
if (status !== Status.NONE) {}
```

**`Number()` for parsing.** Check `isFinite()`. No unary `+`, no `parseInt` (except non-base-10 with validation).

## Error Handling

- `throw new Error()` only. No `throw 'string'`.
- Only throw `Error` subclasses.
- Catch: assume `Error`, narrow if needed. No defensive non-Error handling unless API known to violate.

## Prohibited

`var`, `any`, `@ts-ignore`, `@ts-expect-error`, `const enum`, `debugger`, `eval`, `with`, default exports, `namespace`, `new String/Boolean/Number`, `#private`, prototype modification, `export let`, `{}` type

## Patterns Reference

See [references/patterns.md](references/patterns.md) for: destructuring, spread syntax, getters/setters, event handlers, callback patterns.
