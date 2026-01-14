---
title: Mock with Type Safety
impact: LOW
impactDescription: ensures mocks match interfaces
tags: test, mocks, type-safe, jest
---

## Mock with Type Safety

Create type-safe mocks that match interface contracts.

**Incorrect (untyped mocks):**

```typescript
const mockUser = {
  id: '123',
  // Missing required fields - no error
} as User;

const mockService = {
  getUser: jest.fn(),
  // Method signature doesn't match interface
};
```

**Correct (typed mocks):**

```typescript
function createMockUser(overrides: Partial<User> = {}): User {
  return {
    id: 'test-id',
    name: 'Test User',
    email: 'test@example.com',
    createdAt: new Date(),
    ...overrides,
  };
}

// Type-safe mock factory
function createMock<T extends object>(base: T): jest.Mocked<T> {
  return Object.keys(base).reduce((mock, key) => {
    const value = base[key as keyof T];
    mock[key as keyof T] = typeof value === 'function'
      ? jest.fn() as any
      : value;
    return mock;
  }, {} as jest.Mocked<T>);
}
```

Reference: [Jest Mock Functions](https://jestjs.io/docs/mock-functions)
