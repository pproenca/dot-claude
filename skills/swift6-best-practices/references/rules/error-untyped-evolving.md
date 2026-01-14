---
title: Prefer Untyped Throws for Evolving Errors
impact: LOW
impactDescription: Maintains API stability as errors evolve
tags: error, untyped, api, evolution
---

## Prefer Untyped Throws for Evolving Errors

When error cases might change over time, untyped throws avoids breaking changes. Typed throws locks you into a fixed error contract.

**Incorrect (Typed throws for evolving API):**

```swift
// v1.0
enum NetworkError: Error {
    case noConnection
    case timeout
}

public func fetchUser() throws(NetworkError) -> User {
    // ...
}

// v1.1 - Breaking change! Clients must handle new case
enum NetworkError: Error {
    case noConnection
    case timeout
    case serverError  // Added in v1.1 - breaks existing catch blocks
}
```

**Correct (Untyped throws for API stability):**

```swift
// Error type can evolve without breaking callers
public enum NetworkError: Error {
    case noConnection
    case timeout
    case serverError  // Can add freely
}

public func fetchUser() throws -> User {
    // Throws any Error - callers already handle unknown cases
}

// Callers use @unknown default for future-proofing
do {
    try fetchUser()
} catch let error as NetworkError {
    switch error {
    case .noConnection:
        showOfflineUI()
    case .timeout:
        retryWithBackoff()
    @unknown default:
        // Handles future cases gracefully
        showGenericError()
    }
} catch {
    // Other error types
    logUnexpectedError(error)
}

// Use typed throws only for:
// - Internal code where you control all callers
// - Fixed, well-defined error domains
// - Performance-critical embedded code
```

Reference: [SwiftLee - Typed throws in Swift](https://www.avanderlee.com/swift/typed-throws/)
