---
title: Use Result Pattern
impact: HIGH
impactDescription: makes errors visible in types, catches 100% of unhandled error paths at compile time
tags: error, result, either, exceptions, neverthrow
---

## Use Result Pattern

Exceptions are invisible in function signatures - callers have no idea a function can fail. The Result pattern makes errors explicit in the type system, forcing callers to handle them. This catches 100% of unhandled error paths at compile time instead of in production.

**Incorrect (exceptions hide error paths):**

```typescript
// PROBLEM: Callers have no way to know this function can fail
// The signature lies: it claims to always return Config
// This causes silent failures and unhandled exceptions in production

// config-service.ts
interface Config {
  database: { host: string; port: number };
  apiKey: string;
}

async function loadConfig(path: string): Promise<Config> {
  const content = await fs.readFile(path, 'utf-8');  // Can throw!
  const data = JSON.parse(content);                  // Can throw!

  if (!data.database || !data.apiKey) {
    throw new Error('Invalid config: missing required fields');
  }

  return data as Config;
}

// consumer.ts - caller has no idea about error cases
async function startServer() {
  // BUG: No try/catch - exception crashes the entire app
  const config = await loadConfig('./config.json');
  // If file missing or invalid, server crashes with unhelpful stack trace

  await connectDatabase(config.database);
  // Never reached if loadConfig throws
}

// Even with try/catch, the error type is unknown:
try {
  const config = await loadConfig('./config.json');
} catch (e) {
  // What is e? FileNotFound? ParseError? ValidationError?
  // Type is unknown - no autocomplete, no type safety
  console.error('Something went wrong:', e);
}
```

**Correct (Result type makes errors explicit):**

```typescript
// SOLUTION: Result type forces callers to handle errors
// Function signature is honest about what can go wrong

// result.ts - simple Result type (or use neverthrow library)
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

// config-service.ts
interface Config {
  database: { host: string; port: number };
  apiKey: string;
}

type ConfigError =
  | { type: 'file_not_found'; path: string }
  | { type: 'parse_error'; message: string }
  | { type: 'validation_error'; missingFields: string[] };

async function loadConfig(path: string): Promise<Result<Config, ConfigError>> {
  // File reading
  let content: string;
  try {
    content = await fs.readFile(path, 'utf-8');
  } catch {
    return { ok: false, error: { type: 'file_not_found', path } };
  }

  // JSON parsing
  let data: unknown;
  try {
    data = JSON.parse(content);
  } catch (e) {
    return { ok: false, error: { type: 'parse_error', message: String(e) } };
  }

  // Validation
  const missing: string[] = [];
  if (!(data as any)?.database) missing.push('database');
  if (!(data as any)?.apiKey) missing.push('apiKey');

  if (missing.length > 0) {
    return { ok: false, error: { type: 'validation_error', missingFields: missing } };
  }

  return { ok: true, value: data as Config };
}

// consumer.ts - TypeScript forces error handling
async function startServer() {
  const result = await loadConfig('./config.json');

  // MUST handle the error case - TypeScript enforces this
  if (!result.ok) {
    switch (result.error.type) {
      case 'file_not_found':
        console.error(`Config not found: ${result.error.path}`);
        process.exit(1);
      case 'parse_error':
        console.error(`Invalid JSON: ${result.error.message}`);
        process.exit(1);
      case 'validation_error':
        console.error(`Missing: ${result.error.missingFields.join(', ')}`);
        process.exit(1);
    }
  }

  // TypeScript knows result.value is Config here
  await connectDatabase(result.value.database);
}
```

**Alternative (using neverthrow library):**

```typescript
// neverthrow provides Result utilities and better ergonomics
import { ok, err, Result } from 'neverthrow';

async function loadConfig(path: string): Promise<Result<Config, ConfigError>> {
  return fs.readFile(path, 'utf-8')
    .then(content => JSON.parse(content))
    .then(data => validateConfig(data) ? ok(data) : err({ type: 'validation_error' }))
    .catch(() => err({ type: 'file_not_found', path }));
}

// neverthrow provides chainable methods:
const result = await loadConfig('./config.json')
  .map(config => config.database)      // Transform success value
  .mapErr(e => ({ ...e, logged: true })); // Transform error
```

**When to use:** Use Result for operations that can fail in expected ways: file I/O, API calls, validation, parsing. Keep exceptions for truly exceptional/unexpected errors.

**When NOT to use:** Don't wrap every function in Result - only functions with meaningful failure modes. Exceptions are fine for programming errors (null dereference, assertion failures).

Reference: [Result Pattern in TypeScript](https://dev.to/darkmavis1980/a-practical-guide-to-the-result-pattern-in-typescript-14h6)
