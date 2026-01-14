---
title: Use Result Pattern
impact: HIGH
impactDescription: makes error states explicit in types
tags: error, result, either, exceptions
---

## Use Result Pattern

Return typed results instead of throwing exceptions for expected error cases.

**Incorrect (exceptions for expected cases):**

```typescript
function parseConfig(json: string): Config {
  try {
    const data = JSON.parse(json);
    if (!isValidConfig(data)) {
      throw new Error('Invalid config format');
    }
    return data;
  } catch (e) {
    throw new Error('Failed to parse config');
  }
}

// Caller must remember to try/catch
try {
  const config = parseConfig(input);
} catch (e) {
  // Type of e is unknown
}
```

**Correct (Result type):**

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

function parseConfig(json: string): Result<Config, ConfigError> {
  try {
    const data = JSON.parse(json);
    if (!isValidConfig(data)) {
      return { ok: false, error: { type: 'invalid_format' } };
    }
    return { ok: true, value: data };
  } catch {
    return { ok: false, error: { type: 'parse_error' } };
  }
}

const result = parseConfig(input);
if (result.ok) {
  console.log(result.value.database.host);
} else {
  console.error(result.error.type); // Typed error
}
```

Reference: [Result Pattern in TypeScript](https://dev.to/darkmavis1980/a-practical-guide-to-the-result-pattern-in-typescript-14h6)
