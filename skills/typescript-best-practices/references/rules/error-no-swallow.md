---
title: Never Swallow Errors
impact: HIGH
impactDescription: prevents hidden failures
tags: error, catch, logging, handling
---

## Never Swallow Errors

Empty catch blocks hide bugs. Always handle or re-throw errors.

**Incorrect (swallowed errors):**

```typescript
async function loadData() {
  try {
    const data = await fetchData();
    return data;
  } catch {
    // Silently fails - caller has no idea
  }
}

function parseNumber(str: string): number {
  try {
    return parseInt(str, 10);
  } catch {
    return 0; // Hides the error
  }
}
```

**Correct (explicit error handling):**

```typescript
async function loadData(): Promise<Result<Data, Error>> {
  try {
    const data = await fetchData();
    return { ok: true, value: data };
  } catch (error) {
    console.error('Failed to load data:', error);
    return {
      ok: false,
      error: error instanceof Error ? error : new Error(String(error))
    };
  }
}

function parseNumber(str: string): number | null {
  const num = parseInt(str, 10);
  return Number.isNaN(num) ? null : num;
}
```

Reference: [Error Handling Best Practices](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#using-type-predicates)
