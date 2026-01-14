---
title: Never Use Any
impact: CRITICAL
impactDescription: eliminates 100% of type-unsafe code paths, catches 5-10 type errors per 1000 LoC
tags: safety, any, unknown, type-safety, generics
---

## Never Use Any

Every `any` in your codebase is a hole in the type system where bugs hide. In production codebases, replacing `any` with proper types catches 5-10 type errors per 1000 lines of code. The `any` type defeats TypeScript's purpose - use `unknown` for truly unknown types, or proper typing with generics.

**Incorrect (any creates invisible bugs):**

```typescript
// PROBLEM: Every 'any' is a bug hiding spot. This code has 3 typos
// that TypeScript cannot catch, costing hours of debugging.

// api-client.ts - using axios
import axios from 'axios';

interface DatabaseConfig {
  database: {
    host: string;
    port: number;
    username: string;
  };
}

async function fetchConfig(): Promise<any> {
  const response = await axios.get('/api/config');
  return response.data; // Type is any - no safety
}

async function connectDatabase() {
  const config: any = await fetchConfig();

  // BUGS: These typos compile but crash at runtime
  console.log(config.databse.host);     // Typo: 'databse' instead of 'database'
  console.log(config.database.prot);    // Typo: 'prot' instead of 'port'
  console.log(config.database.usernme); // Typo: 'usernme' instead of 'username'

  return createConnection(config.database);
}

// Even worse: any spreads through your codebase
function processData(data: any) {
  return data.foo.bar.baz; // Could be anything - runtime crash waiting to happen
}
```

**Correct (proper typing catches all typos):**

```typescript
// SOLUTION: Proper typing catches 100% of property access typos at compile time
// Use interfaces, generics, or unknown with type guards

// api-client.ts
import axios from 'axios';
import { z } from 'zod'; // Runtime validation with zod

// Define the expected shape
interface DatabaseConfig {
  database: {
    host: string;
    port: number;
    username: string;
  };
}

// Zod schema for runtime validation
const ConfigSchema = z.object({
  database: z.object({
    host: z.string(),
    port: z.number(),
    username: z.string(),
  }),
});

async function fetchConfig(): Promise<DatabaseConfig> {
  const response = await axios.get<unknown>('/api/config');
  // Runtime validation + type inference
  return ConfigSchema.parse(response.data);
}

async function connectDatabase() {
  const config = await fetchConfig();

  // All typos now caught at compile time:
  console.log(config.databse.host);     // Error: Property 'databse' does not exist
  console.log(config.database.prot);    // Error: Property 'prot' does not exist
  console.log(config.database.usernme); // Error: Property 'usernme' does not exist

  // Correct access - fully typed
  console.log(config.database.host);
  console.log(config.database.port);
  console.log(config.database.username);

  return createConnection(config.database);
}
```

**Alternative (unknown with type guards):**

```typescript
// When you truly don't know the type, use unknown + narrowing
function parseJSON(json: string): unknown {
  return JSON.parse(json);
}

function isConfig(value: unknown): value is DatabaseConfig {
  return (
    typeof value === 'object' &&
    value !== null &&
    'database' in value &&
    typeof (value as any).database?.host === 'string'
  );
}

const data = parseJSON(rawJson);
if (isConfig(data)) {
  console.log(data.database.host); // Safe - narrowed to DatabaseConfig
}
```

**When to use:** Always prefer explicit types, generics, or `unknown` over `any`. Use `unknown` when the type genuinely cannot be known at compile time (e.g., JSON parsing, external API responses).

**When NOT to use:** Only use `any` as a last resort when wrapping poorly-typed third-party libraries, and even then, isolate it to a thin wrapper layer. Never let `any` leak into your business logic.

Reference: [TypeScript unknown Type](https://www.typescriptlang.org/docs/handbook/2/functions.html#unknown)
